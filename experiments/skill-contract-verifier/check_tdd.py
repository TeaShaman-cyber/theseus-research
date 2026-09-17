#!/usr/bin/env python3
import argparse
import json
import pathlib


def check(payload):
    relations = [r for r in payload.get("relations", []) if r.get("kind") == "TDD_RUNNER_WITNESS"]
    if not relations:
        return {
            "scope_status": "UNOBSERVABLE_AT_THIS_LAYER",
            "disposition": "DEFER",
            "counterexamples": [],
            "coverage_gaps": [{"kind": "UNOBSERVABLE_ROUTING"}],
        }

    counterexamples = []
    coverage_gaps = []
    for relation in relations:
        witnesses = relation.get("witnesses", [])
        if not witnesses:
            coverage_gaps.append(
                {
                    "kind": "UNOBSERVABLE_ROUTING",
                    "consumer_step": relation.get("consumer_step", {}).get("number"),
                    "runner": relation.get("runner", {}).get("kind"),
                    "span": relation.get("runner", {}).get("span"),
                }
            )
            continue
        for witness in witnesses:
            if not witness.get("discoverable", False):
                counterexamples.append(
                    {
                        "kind": "RED_WITNESS_UNDISCOVERABLE",
                        "runner": relation.get("runner", {}).get("kind"),
                        "witness": witness.get("name"),
                        "form": witness.get("form"),
                        "span": witness.get("span"),
                    }
                )

    if counterexamples:
        return {
            "scope_status": "UNSAFE",
            "disposition": "REJECT",
            "counterexamples": counterexamples,
            "coverage_gaps": coverage_gaps,
        }
    if coverage_gaps:
        return {
            "scope_status": "UNOBSERVABLE_AT_THIS_LAYER",
            "disposition": "DEFER",
            "counterexamples": [],
            "coverage_gaps": coverage_gaps,
        }
    return {
        "scope_status": "SAFE_WITHIN_SCOPE",
        "disposition": "ACCEPT",
        "counterexamples": [],
        "coverage_gaps": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("projection", type=pathlib.Path)
    args = parser.parse_args()
    payload = json.loads(args.projection.read_text())
    print(json.dumps(check(payload), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
