#!/usr/bin/env python3
import argparse
import json
import pathlib


def check(payload):
    relations = [r for r in payload.get("relations", []) if r.get("kind") == "TRANSPORT_BOUNDARY"]
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
        encoding = relation.get("encoding", {}).get("kind")
        source = relation.get("source_semantics", {})
        if encoding != "github_env_simple_line":
            coverage_gaps.append(
                {"kind": "UNOBSERVABLE_ROUTING", "binding": relation.get("binding"), "encoding": encoding}
            )
            continue
        if source.get("kind") != "literal_string":
            coverage_gaps.append(
                {"kind": "UNOBSERVABLE_ROUTING", "binding": relation.get("binding"), "encoding": encoding}
            )
            continue
        if source.get("contains_line_break"):
            counterexamples.append(
                {
                    "kind": "TRANSPORT_SEMANTIC_LOSS",
                    "binding": relation.get("binding"),
                    "encoding": encoding,
                    "reason": "line_break_not_preserved_by_simple_env_line",
                    "span": relation.get("encoding", {}).get("span"),
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
