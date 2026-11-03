#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "governance" / "formal" / "project-contract-v11-model.json"


class FormalError(ValueError):
    pass


def _reachable(adjacency: dict[str, set[str]], start: str, target: str, removed: str | None = None) -> bool:
    if start == removed or target == removed:
        return False
    seen = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node in seen or node == removed:
            continue
        seen.add(node)
        stack.extend(n for n in adjacency.get(node, set()) if n != removed)
    return False


def _has_cycle(adjacency: dict[str, set[str]], states: set[str], removed_edge: tuple[str, str] | None = None) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for nxt in adjacency.get(node, set()):
            if removed_edge == (node, nxt):
                continue
            if dfs(nxt):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(dfs(node) for node in states if node not in visited)


def verify_model(data: dict) -> dict:
    states = set(data["states"])
    terminals = set(data["terminals"])
    start = data["start"]
    success = data["success_terminal"]
    transitions = data["transitions"]

    if start not in states or success not in terminals or not terminals <= states:
        raise FormalError("invalid start/terminal declaration")

    adjacency = {state: set() for state in states}
    guards = {}
    for edge in transitions:
        src, dst, guard = edge["from"], edge["to"], edge["guard"]
        if src not in states or dst not in states or not guard:
            raise FormalError(f"invalid transition: {edge}")
        if (src, dst) in guards:
            raise FormalError(f"duplicate transition: {src}->{dst}")
        adjacency[src].add(dst)
        guards[(src, dst)] = guard

    nonterminals = states - terminals
    deadlocks = sorted(state for state in nonterminals if not adjacency[state])
    if deadlocks:
        raise FormalError(f"deadlocked nonterminals: {deadlocks}")

    unreachable_terminal = sorted(
        state
        for state in nonterminals
        if not any(_reachable(adjacency, state, terminal) for terminal in terminals)
    )
    if unreachable_terminal:
        raise FormalError(f"nonterminals without terminal reachability: {unreachable_terminal}")

    missing_required = [
        required
        for required in data["success_requires"]
        if _reachable(adjacency, start, success, removed=required)
    ]
    if missing_required:
        raise FormalError(f"SUCCESS reachable while bypassing required states: {missing_required}")

    fallback = data["fallback_return_edge"]
    fallback_edge = (fallback["from"], fallback["to"])
    if guards.get(fallback_edge) != fallback["guard"]:
        raise FormalError("fallback return edge/guard mismatch")
    if not _has_cycle(adjacency, states):
        raise FormalError("expected bounded fallback cycle is absent")
    if _has_cycle(adjacency, states, removed_edge=fallback_edge):
        raise FormalError("cycle exists outside the declared fallback return edge")

    incoming_fallback = [
        edge
        for edge in transitions
        if edge["to"] == fallback["from"] and edge["from"] != fallback["from"]
    ]
    allowed = set(data["allowed_fallback_entry_guards"])
    bad_guards = sorted(edge["guard"] for edge in incoming_fallback if edge["guard"] not in allowed)
    if bad_guards:
        raise FormalError(f"fallback entries without observed-failure guard: {bad_guards}")

    return {
        "status": "PASS",
        "revision": data["revision"],
        "states": len(states),
        "transitions": len(transitions),
        "terminals": sorted(terminals),
        "success_requires": data["success_requires"],
        "fallback_return_edge": f"{fallback_edge[0]}->{fallback_edge[1]}",
    }


def main() -> int:
    receipt = verify_model(json.loads(MODEL.read_text(encoding="utf-8")))
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
