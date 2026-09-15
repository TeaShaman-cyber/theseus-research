#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict, deque
from pathlib import Path

NODE_ROLES = {"problem", "reformulation", "reduction", "bridge_theorem", "construction", "invariant", "repair", "verification", "consequence", "analogy"}
EDGE_ROLES = {"depends_on", "reduces_to", "bridges", "constructs", "repairs", "verifies", "implies", "analogy"}
EVIDENCE = {"kernel_checked", "established_theorem", "primary_exposition", "historical_record", "analogy_only", "unknown"}
BASELINE_EVIDENCE = {"kernel_checked", "established_theorem", "primary_exposition"}
THEOREM_LEVEL = {"kernel_checked", "established_theorem"}


def load_case(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_case(data, path)
    return data


def validate_case(data, path="<memory>"):
    required = {"schema_version", "case_id", "label", "outcome_class", "sources", "nodes", "edges"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"{path}: missing keys {sorted(missing)}")
    if data["schema_version"] != "1.0":
        raise ValueError(f"{path}: unsupported schema_version")
    source_ids = [s["id"] for s in data["sources"]]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError(f"{path}: duplicate source ids")
    node_ids = [n["id"] for n in data["nodes"]]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError(f"{path}: duplicate node ids")
    node_set = set(node_ids)
    source_set = set(source_ids)
    for n in data["nodes"]:
        if n["role"] not in NODE_ROLES:
            raise ValueError(f"{path}: invalid node role {n['role']}")
    for e in data["edges"]:
        if e["source"] not in node_set or e["target"] not in node_set:
            raise ValueError(f"{path}: dangling edge {e['source']} -> {e['target']}")
        if e["role"] not in EDGE_ROLES or e["evidence"] not in EVIDENCE:
            raise ValueError(f"{path}: invalid edge role/evidence")
        if not set(e["source_refs"]).issubset(source_set):
            raise ValueError(f"{path}: unknown source ref")
        if e["role"] == "analogy":
            if e["evidence"] not in {"analogy_only", "historical_record"}:
                raise ValueError(f"{path}: analogy edge has overstrong evidence")
        elif not e["source_refs"]:
            raise ValueError(f"{path}: non-analogy edge must cite a source")


def adjacency(case, edge_filter=None):
    adj = defaultdict(list)
    rev = defaultdict(list)
    nodes = [n["id"] for n in case["nodes"]]
    for n in nodes:
        adj[n]; rev[n]
    for i, e in enumerate(case["edges"]):
        if edge_filter is None or edge_filter(e):
            adj[e["source"]].append((e["target"], i))
            rev[e["target"]].append((e["source"], i))
    return nodes, adj, rev


def topo(case):
    nodes, adj, rev = adjacency(case)
    indeg = {n: len(rev[n]) for n in nodes}
    q = deque(sorted(n for n in nodes if indeg[n] == 0))
    order = []
    while q:
        n = q.popleft()
        order.append(n)
        for m, _ in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)
    return order if len(order) == len(nodes) else None


def weak_components(case):
    nodes, adj, rev = adjacency(case)
    seen = set(); count = 0
    for start in nodes:
        if start in seen:
            continue
        count += 1
        stack = [start]; seen.add(start)
        while stack:
            n = stack.pop()
            for m, _ in adj[n] + rev[n]:
                if m not in seen:
                    seen.add(m); stack.append(m)
    return count


def longest_path(case, order):
    if order is None:
        return None
    _, adj, _ = adjacency(case)
    dist = {n: 0 for n in order}
    for n in order:
        for m, _ in adj[n]:
            dist[m] = max(dist[m], dist[n] + 1)
    return max(dist.values(), default=0)


def baseline(case):
    roles = {n["id"]: n["role"] for n in case["nodes"]}
    problems = [n for n, r in roles.items() if r == "problem"]
    consequences = {n for n, r in roles.items() if r == "consequence"}
    edges = case["edges"]
    nodes, adj, _ = adjacency(case, lambda e: e["role"] != "analogy" and e["evidence"] in BASELINE_EVIDENCE)
    for start in problems:
        stack = [(start, [], set())]
        seen_states = set()
        while stack:
            n, path_edges, refs = stack.pop()
            state = (n, tuple(path_edges))
            if state in seen_states:
                continue
            seen_states.add(state)
            if n in consequences and path_edges:
                path = [edges[i] for i in path_edges]
                path_refs = set().union(*(set(e["source_refs"]) for e in path))
                has_kernel = any(e["evidence"] == "kernel_checked" for e in path)
                if len(path_refs) >= 2 or (has_kernel and len(path_refs) >= 1):
                    return {"pass": True, "path_edge_indexes": path_edges, "source_refs": sorted(path_refs)}
            for m, idx in adj[n]:
                if m not in [start] + [edges[i]["target"] for i in path_edges]:
                    stack.append((m, path_edges + [idx], refs | set(edges[idx]["source_refs"])))
    return {"pass": False, "path_edge_indexes": [], "source_refs": []}


def metrics(case):
    order = topo(case)
    edges = case["edges"]
    analogy = sum(e["role"] == "analogy" for e in edges)
    theorem = sum(e["evidence"] in THEOREM_LEVEL for e in edges)
    cited = set(r for e in edges for r in e["source_refs"])
    total = len(edges)
    return {
        "case_id": case["case_id"],
        "label": case["label"],
        "outcome_class": case["outcome_class"],
        "node_count": len(case["nodes"]),
        "edge_count": total,
        "is_dag": order is not None,
        "weak_component_count": weak_components(case),
        "longest_directed_path": longest_path(case, order),
        "analogy_edge_count": analogy,
        "analogy_edge_fraction": analogy / total if total else 0,
        "theorem_level_edge_count": theorem,
        "theorem_level_edge_fraction": theorem / total if total else 0,
        "repair_edge_count": sum(e["role"] == "repairs" for e in edges),
        "verification_edge_count": sum(e["role"] == "verifies" for e in edges),
        "distinct_edge_source_refs": len(cited),
        "cheap_baseline": baseline(case),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    files = sorted(args.cases.glob("*.json"))
    if len(files) != 3:
        raise SystemExit(f"expected exactly 3 frozen cases, found {len(files)}")
    cases = [load_case(p) for p in files]
    result = {
        "schema_version": "1.0",
        "experiment": "issue-37-evidence-graph-first-pass",
        "case_count": len(cases),
        "metrics": [metrics(c) for c in cases],
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
