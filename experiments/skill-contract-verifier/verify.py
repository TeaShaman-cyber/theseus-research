#!/usr/bin/env python3
import argparse
import json
import pathlib


def verify_case(case):
    required = case.get("claim", {}).get("required_bindings", {})
    observed = case.get("evidence", {}).get("bindings", {})
    counterexamples = []

    for key, expected in sorted(required.items()):
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

    return {
        "id": case.get("id"),
        "domain": case.get("domain"),
        "disposition": "REJECT" if counterexamples else "ACCEPT",
        "counterexamples": counterexamples,
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
