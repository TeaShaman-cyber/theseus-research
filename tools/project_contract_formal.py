#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "governance" / "formal" / "project-contract-v12-model.json"


class FormalError(ValueError):
    pass


def _reachable(
    adjacency: dict[str, set[str]],
    start: str,
    target: str,
    removed: str | None = None,
) -> bool:
    if start == removed or target == removed:
        return False
    seen: set[str] = set()
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


def _has_cycle(
    adjacency: dict[str, set[str]],
    states: set[str],
    removed_edge: tuple[str, str] | None = None,
) -> bool:
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
    transition_by_edge: dict[tuple[str, str], dict] = {}
    for edge in transitions:
        src, dst, guard = edge["from"], edge["to"], edge["guard"]
        if src not in states or dst not in states or not guard:
            raise FormalError(f"invalid transition: {edge}")
        key = (src, dst)
        if key in transition_by_edge:
            raise FormalError(f"duplicate transition: {src}->{dst}")
        if not isinstance(edge.get("progress_delta"), int):
            raise FormalError(f"transition missing integer progress_delta: {edge}")
        adjacency[src].add(dst)
        transition_by_edge[key] = edge

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
        raise FormalError(
            f"nonterminals without terminal reachability: {unreachable_terminal}"
        )

    missing_required = [
        required
        for required in data["success_requires"]
        if _reachable(adjacency, start, success, removed=required)
    ]
    if missing_required:
        raise FormalError(
            f"SUCCESS reachable while bypassing required states: {missing_required}"
        )

    progress = data.get("fallback_progress")
    if not isinstance(progress, dict):
        raise FormalError("fallback_progress must be declared")

    if progress.get("measure") != "remaining_untried_routes":
        raise FormalError("unexpected fallback progress measure")
    if progress.get("domain") != "finite_nonnegative_integer":
        raise FormalError("fallback progress measure is not well-founded")
    if progress.get("return_enabled_when") != "positive":
        raise FormalError("fallback return must require positive remaining rank")
    if progress.get("exhausted_enabled_when") != "zero":
        raise FormalError("fallback exhaustion must require zero remaining rank")

    return_spec = progress.get("return_edge")
    exhausted_spec = progress.get("exhausted_edge")
    if not isinstance(return_spec, dict) or not isinstance(exhausted_spec, dict):
        raise FormalError("fallback return/exhausted edges must be declared")

    return_edge = (return_spec["from"], return_spec["to"])
    exhausted_edge = (exhausted_spec["from"], exhausted_spec["to"])
    if return_edge == exhausted_edge:
        raise FormalError("fallback return and exhausted edges must differ")

    return_transition = transition_by_edge.get(return_edge)
    exhausted_transition = transition_by_edge.get(exhausted_edge)
    if return_transition is None:
        raise FormalError("declared fallback return edge is missing")
    if exhausted_transition is None:
        raise FormalError("declared fallback exhausted edge is missing")

    if return_transition["guard"] != return_spec["guard"]:
        raise FormalError("fallback return guard mismatch")
    if exhausted_transition["guard"] != exhausted_spec["guard"]:
        raise FormalError("fallback exhausted guard mismatch")

    return_delta = progress.get("return_delta")
    other_delta = progress.get("other_edge_delta")
    if not isinstance(return_delta, int) or return_delta >= 0:
        raise FormalError("fallback return must strictly decrease progress rank")
    if other_delta != 0:
        raise FormalError("non-fallback transitions must preserve progress rank")
    if return_transition["progress_delta"] != return_delta:
        raise FormalError("fallback return progress delta mismatch")

    for key, edge in transition_by_edge.items():
        if key != return_edge and edge["progress_delta"] != other_delta:
            raise FormalError(
                f"non-return transition changes fallback progress rank: {key}"
            )

    fallback_state = return_edge[0]
    outgoing = {
        key for key in transition_by_edge
        if key[0] == fallback_state
    }
    if outgoing != {return_edge, exhausted_edge}:
        raise FormalError(
            "fallback state must have exactly return and exhausted exits"
        )

    if not _has_cycle(adjacency, states):
        raise FormalError("expected fallback cycle is absent")
    if _has_cycle(adjacency, states, removed_edge=return_edge):
        raise FormalError("cycle exists outside the declared fallback return edge")

    incoming_fallback = [
        edge
        for edge in transitions
        if edge["to"] == fallback_state and edge["from"] != fallback_state
    ]
    allowed = set(data["allowed_fallback_entry_guards"])
    bad_guards = sorted(
        edge["guard"] for edge in incoming_fallback if edge["guard"] not in allowed
    )
    if bad_guards:
        raise FormalError(
            f"fallback entries without observed-failure guard: {bad_guards}"
        )

    # Termination proof obligation:
    # every raw graph cycle contains the return edge; that edge strictly decreases
    # a finite nonnegative rank; all other edges preserve it; at zero the return
    # edge is disabled and the only fallback exit is terminal exhaustion.
    bounded_fallback = True

    return {
        "status": "PASS",
        "revision": data["revision"],
        "states": len(states),
        "transitions": len(transitions),
        "terminals": sorted(terminals),
        "success_requires": data["success_requires"],
        "fallback_return_edge": f"{return_edge[0]}->{return_edge[1]}",
        "fallback_progress_measure": progress["measure"],
        "fallback_return_delta": return_delta,
        "bounded_fallback": bounded_fallback,
    }


def main() -> int:
    receipt = verify_model(json.loads(MODEL.read_text(encoding="utf-8")))
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
