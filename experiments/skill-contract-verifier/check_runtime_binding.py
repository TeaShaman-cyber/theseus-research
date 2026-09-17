#!/usr/bin/env python3
import argparse
import json
import pathlib


def check(payload):
    relations = [r for r in payload.get("relations", []) if r.get("kind") == "RUNTIME_BINDING"]
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
        transport = relation.get("transport", {}).get("kind")
        if transport == "process_local":
            counterexamples.append(
                {
                    "kind": "RUNTIME_BINDING_NOT_TRANSPORTED",
                    "binding": relation.get("binding"),
                    "producer_step": relation.get("producer_step", {}).get("index"),
                    "consumer_step": relation.get("consumer_step", {}).get("index"),
                    "transport": transport,
                }
            )
        elif transport == "unknown":
            coverage_gaps.append(
                {
                    "kind": "UNOBSERVABLE_ROUTING",
                    "binding": relation.get("binding"),
                    "consumer_step": relation.get("consumer_step", {}).get("index"),
                }
            )
        elif transport != "github_env_next_steps":
            coverage_gaps.append(
                {
                    "kind": "UNOBSERVABLE_ROUTING",
                    "binding": relation.get("binding"),
                    "transport": transport,
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
