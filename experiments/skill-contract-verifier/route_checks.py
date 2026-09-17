#!/usr/bin/env python3
import argparse
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

CHECKERS = {
    "CLAIM_PROVENANCE": "check_claim_provenance.py",
    "RUNTIME_BINDING": "check_runtime_binding.py",
    "TDD_RUNNER_WITNESS": "check_tdd.py",
    "TRANSPORT_BOUNDARY": "check_transport_boundary.py",
}


def load_checker(relation_kind):
    filename = CHECKERS[relation_kind]
    path = ROOT / filename
    spec = importlib.util.spec_from_file_location(
        "skill_contract_router_" + relation_kind.lower(), path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def route(payload):
    relation_kinds = sorted(
        {
            relation.get("kind")
            for relation in payload.get("relations", [])
            if relation.get("kind")
        }
    )
    known = [kind for kind in relation_kinds if kind in CHECKERS]
    unrouted = [kind for kind in relation_kinds if kind not in CHECKERS]

    family_results = {}
    for kind in known:
        family_results[kind] = load_checker(kind).check(payload)

    statuses = [result.get("scope_status") for result in family_results.values()]
    if "UNSAFE" in statuses:
        scope_status = "UNSAFE"
        disposition = "REJECT"
    elif unrouted or "UNOBSERVABLE_AT_THIS_LAYER" in statuses or not family_results:
        scope_status = "UNOBSERVABLE_AT_THIS_LAYER"
        disposition = "DEFER"
    else:
        scope_status = "SAFE_WITHIN_EXTRACTED_RELATIONS"
        disposition = "ACCEPT_SCOPED"

    return {
        "scope_status": scope_status,
        "disposition": disposition,
        "family_results": family_results,
        "unrouted_relation_kinds": unrouted,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("projection", type=pathlib.Path)
    args = parser.parse_args()
    payload = json.loads(args.projection.read_text())
    print(json.dumps(route(payload), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
