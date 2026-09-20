from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

root = Path(os.environ["GITHUB_WORKSPACE"])
fixture = root / os.environ["FIXTURE_ROOT"]
corpus = Path(sys.argv[1])
out = Path(sys.argv[2])
manifest = json.loads((fixture / "manifest.json").read_text())

class_ranges = {
    "verification-target-mismatch": [(12, 12)],
    "authority-provenance-closure": [(13, 13)],
    "identity-preservation": [(14, 14)],
    "identity-grammar-mismatch": [(15, 15), (33, 66)],
    "claim-status-semantics": [(16, 16)],
    "phase-dag-closure": [(17, 17)],
    "boundary-transport-contract": [(18, 18)],
    "derived-state-heuristic-coverage": [(19, 19)],
}

cases = [
    c
    for c in manifest["cases"]
    if c["kind"] in {"retrieval_positive", "retrieval_negative"}
]


def hit_classes(start: int, end: int) -> list[str]:
    hits: list[str] = []
    for class_id, ranges in class_ranges.items():
        if any(start <= b and end >= a for a, b in ranges):
            hits.append(class_id)
    return hits


def run_pass(name: str, broken_proxy: bool) -> dict:
    env = os.environ.copy()
    if broken_proxy:
        env.update(
            {
                "HTTP_PROXY": "http://127.0.0.1:9",
                "HTTPS_PROXY": "http://127.0.0.1:9",
                "ALL_PROXY": "http://127.0.0.1:9",
            }
        )
    pass_started = time.perf_counter()
    observed: list[dict] = []
    for case in cases:
        query = (fixture / case["candidate_file"]).read_text()
        started = time.perf_counter()
        cp = subprocess.run(
            [
                "semble",
                "search",
                query,
                str(corpus),
                "--content",
                "docs",
                "--top-k",
                "10",
                "--format",
                "json",
            ],
            text=True,
            capture_output=True,
            env=env,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        entry: dict = {
            "id": case["id"],
            "kind": case["kind"],
            "exit_code": cp.returncode,
            "elapsed_ms": elapsed_ms,
            "stderr": cp.stderr,
            "expected_failure_class": case["oracle"].get("expected_failure_class"),
        }
        if cp.returncode == 0:
            payload = json.loads(cp.stdout)
            results: list[dict] = []
            for result in payload.get("results", []):
                start = int(result["start_line"])
                end = int(result["end_line"])
                results.append(
                    {
                        "file_path": result["file_path"],
                        "start_line": start,
                        "end_line": end,
                        "score": result["score"],
                        "class_hits": hit_classes(start, end),
                        "content_sha256": hashlib.sha256(
                            result.get("content", "").encode()
                        ).hexdigest(),
                    }
                )
            entry["results"] = results
            expected = entry["expected_failure_class"]
            if expected:
                entry["inclusive_expected_rank"] = next(
                    (
                        i + 1
                        for i, result in enumerate(results)
                        if expected in result["class_hits"]
                    ),
                    None,
                )
                entry["strict_expected_rank"] = next(
                    (
                        i + 1
                        for i, result in enumerate(results)
                        if result["class_hits"] == [expected]
                    ),
                    None,
                )
        else:
            entry["stdout"] = cp.stdout
        observed.append(entry)
    return {
        "name": name,
        "broken_proxy": broken_proxy,
        "wall_ms": (time.perf_counter() - pass_started) * 1000,
        "cases": observed,
    }


def aggregates(pass_result: dict) -> dict:
    positives = [c for c in pass_result["cases"] if c["kind"] == "retrieval_positive"]
    negatives = [c for c in pass_result["cases"] if c["kind"] == "retrieval_negative"]

    def rr(rank: int | None) -> float:
        return 0.0 if rank is None else 1.0 / rank

    return {
        "positive_count": len(positives),
        "negative_count": len(negatives),
        "inclusive_top1": sum(c.get("inclusive_expected_rank") == 1 for c in positives),
        "inclusive_top3": sum(
            (c.get("inclusive_expected_rank") or 999) <= 3 for c in positives
        ),
        "inclusive_mrr": sum(
            rr(c.get("inclusive_expected_rank")) for c in positives
        )
        / len(positives),
        "strict_top1": sum(c.get("strict_expected_rank") == 1 for c in positives),
        "strict_top3": sum(
            (c.get("strict_expected_rank") or 999) <= 3 for c in positives
        ),
        "strict_mrr": sum(rr(c.get("strict_expected_rank")) for c in positives)
        / len(positives),
        "negative_top_results": [
            {
                "id": c["id"],
                "top": (c.get("results") or [None])[0],
            }
            for c in negatives
        ],
    }


cold = run_pass("cold-index", False)
warm = run_pass("warm-index-broken-proxy", True)

receipt = {
    "schema_version": 1,
    "fixture_digest": "df3bf51cee0a7a57786b140979586ae28f4df7951fb2968e2a39eb1a1ed7048b",
    "semble_source_sha": os.environ["SEMBLE_SOURCE_SHA"],
    "model_repo": os.environ["MODEL_REPO"],
    "model_revision": os.environ["MODEL_REVISION"],
    "corpus_mode": "raw canonical docs/qa/failure-classes.md",
    "class_ranges": class_ranges,
    "cold": cold,
    "warm": warm,
    "cold_metrics": aggregates(cold),
    "warm_metrics": aggregates(warm),
}
(out / "retrieval.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(json.dumps(receipt, indent=2, sort_keys=True))
