#!/usr/bin/env python3
import argparse
import json
import pathlib


def verify_case(case):
    required = case.get("claim", {}).get("required_bindings", {})
    observed = case.get("evidence", {}).get("bindings", {})
    scope = case.get("scope", {})
    declared_observable = scope.get("observable_bindings")
    observable = (
        set(required) if declared_observable is None else set(declared_observable)
    )
    counterexamples = []
    coverage_gaps = []

    for key, expected in sorted(required.items()):
        if key not in observable:
            coverage_gaps.append(
                {
                    "binding": key,
                    "kind": "UNOBSERVABLE_BINDING",
                }
            )
            continue
        if key not in observed:
            counterexamples.append(
                {
                    "binding": key,
                    "kind": "MISSING_BINDING",
                    "expected": expected,
                    "observed": None,
                }
            )
            continue
        actual = observed[key]
        if actual != expected:
            counterexamples.append(
                {
                    "binding": key,
                    "kind": "BINDING_MISMATCH",
                    "expected": expected,
                    "observed": actual,
                }
            )

    if counterexamples:
        scope_status = "UNSAFE"
        disposition = "REJECT"
    elif coverage_gaps:
        scope_status = "UNOBSERVABLE_AT_THIS_LAYER"
        disposition = "DEFER"
    else:
        scope_status = "SAFE_WITHIN_SCOPE"
        disposition = "ACCEPT"

    return {
        "id": case.get("id"),
        "domain": case.get("domain"),
        "scope_status": scope_status,
        "disposition": disposition,
        "counterexamples": counterexamples,
        "coverage_gaps": coverage_gaps,
    }


def verify_corpus(payload):
    return [verify_case(case) for case in payload.get("cases", [])]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=pathlib.Path)
    args = parser.parse_args()
    payload = json.loads(args.corpus.read_text())
    print(json.dumps(verify_corpus(payload), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
