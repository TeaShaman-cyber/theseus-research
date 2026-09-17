#!/usr/bin/env python3
import argparse
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent


def load_provenance_checker():
    path = ROOT / "verify.py"
    spec = importlib.util.spec_from_file_location("claim_provenance_verify", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(payload):
    relations = [
        relation
        for relation in payload.get("relations", [])
        if relation.get("kind") == "CLAIM_PROVENANCE"
    ]
    if not relations:
        return {
            "scope_status": "UNOBSERVABLE_AT_THIS_LAYER",
            "disposition": "DEFER",
            "counterexamples": [],
            "coverage_gaps": [{"kind": "UNOBSERVABLE_ROUTING"}],
        }

    verifier = load_provenance_checker()
    counterexamples = []
    coverage_gaps = []
    statuses = []
    for index, relation in enumerate(relations, start=1):
        case = {
            "id": f"extracted-provenance-{index}",
            "domain": "extracted-plan",
            "claim": relation.get("claim", {}),
            "evidence": relation.get("evidence", {}),
            "scope": relation.get("scope", {}),
        }
        result = verifier.verify_case(case)
        statuses.append(result["scope_status"])
        span = relation.get("contract", {}).get("span")
        for item in result["counterexamples"]:
            counterexamples.append({**item, "contract_span": span})
        for item in result["coverage_gaps"]:
            coverage_gaps.append({**item, "contract_span": span})

    if "UNSAFE" in statuses:
        scope_status = "UNSAFE"
        disposition = "REJECT"
    elif "UNOBSERVABLE_AT_THIS_LAYER" in statuses:
        scope_status = "UNOBSERVABLE_AT_THIS_LAYER"
        disposition = "DEFER"
    else:
        scope_status = "SAFE_WITHIN_SCOPE"
        disposition = "ACCEPT"

    return {
        "scope_status": scope_status,
        "disposition": disposition,
        "counterexamples": counterexamples,
        "coverage_gaps": coverage_gaps,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("projection", type=pathlib.Path)
    args = parser.parse_args()
    payload = json.loads(args.projection.read_text())
    print(json.dumps(check(payload), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
