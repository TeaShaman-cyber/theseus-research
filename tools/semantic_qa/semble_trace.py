from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

CLASS_IDS = [
    "verification-target-mismatch",
    "authority-provenance-closure",
    "identity-preservation",
    "identity-grammar-mismatch",
    "claim-status-semantics",
    "phase-dag-closure",
    "boundary-transport-contract",
    "derived-state-heuristic-coverage",
]


def _dir_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.exists() else 0


def _normalize_results(payload: dict, mapping: dict[str, str], top_k: int) -> list[dict]:
    out = []
    for rank, item in enumerate(payload.get("results", [])[:top_k], start=1):
        name = Path(item["file_path"]).name
        out.append(
            {
                "rank": rank,
                "class_id": mapping.get(name),
                "score": item["score"],
                "record": name,
                "start_line": int(item["start_line"]),
                "end_line": int(item["end_line"]),
            }
        )
    return out


def _run_pass(
    cases: list[dict],
    input_root: Path,
    corpus: Path,
    mapping: dict[str, str],
    top_k: int,
) -> tuple[list[dict], list[dict], float]:
    started = time.perf_counter()
    observed = []
    errors = []
    for case in cases:
        query = (input_root / case["patch_file"]).read_text(errors="replace")
        cp = subprocess.run(
            [
                "semble",
                "search",
                query,
                str(corpus),
                "--content",
                "docs",
                "--top-k",
                str(top_k),
                "--format",
                "json",
            ],
            text=True,
            capture_output=True,
        )
        if cp.returncode != 0:
            errors.append(
                {
                    "id": case["id"],
                    "returncode": cp.returncode,
                    "stderr": cp.stderr[-2000:],
                }
            )
            continue
        payload = json.loads(cp.stdout)
        observed.append(
            {
                "id": case["id"],
                "source_path": case["source_path"],
                "patch_sha256": case["sha256"],
                "results": _normalize_results(payload, mapping, top_k),
            }
        )
    return observed, errors, (time.perf_counter() - started) * 1000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--failure-classes", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    manifest = json.loads(args.input_manifest.read_text())
    profile = json.loads(args.profile.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)

    if manifest["status"] == "NO_SIGNAL":
        receipt = {
            "schema_version": 1,
            "tool": "semble",
            "status": "NO_SIGNAL",
            "repository": manifest["repository"],
            "task_id": manifest["task_id"],
            "base_sha": manifest["base_sha"],
            "candidate_sha": manifest["candidate_sha"],
            "profile_sha256": hashlib.sha256(args.profile.read_bytes()).hexdigest(),
            "acceptance_authority": False,
            "matches": [],
        }
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        return 0

    lines = args.failure_classes.read_text().splitlines()
    if len(lines) < 19:
        raise RuntimeError("failure-class corpus no longer contains canonical lines 12-19")

    with tempfile.TemporaryDirectory(prefix="semble-field-corpus-") as temp:
        corpus = Path(temp)
        mapping = {}
        for idx, (class_id, line_no) in enumerate(zip(CLASS_IDS, range(12, 20)), start=1):
            name = f"record-{idx:02d}.md"
            (corpus / name).write_text(lines[line_no - 1] + "\n")
            mapping[name] = class_id

        cache_path = Path(os.environ["SEMBLE_CACHE_LOCATION"])
        cache_before = _dir_bytes(cache_path)
        cold, cold_errors, cold_ms = _run_pass(
            manifest["selected"], args.input_root, corpus, mapping, args.top_k
        )
        cache_after_cold = _dir_bytes(cache_path)
        warm, warm_errors, warm_ms = _run_pass(
            manifest["selected"], args.input_root, corpus, mapping, args.top_k
        )
        cache_after_warm = _dir_bytes(cache_path)

    failures = len(cold_errors) + len(warm_errors)
    if cold_errors and len(cold_errors) == len(manifest["selected"]):
        status = "UNAVAILABLE"
    elif failures or manifest["status"] == "DEGRADED":
        status = "DEGRADED"
    else:
        status = "OK"

    normalized_cold = [(x["id"], x["results"]) for x in cold]
    normalized_warm = [(x["id"], x["results"]) for x in warm]
    receipt = {
        "schema_version": 1,
        "tool": "semble",
        "status": status,
        "repository": manifest["repository"],
        "task_id": manifest["task_id"],
        "base_sha": manifest["base_sha"],
        "candidate_sha": manifest["candidate_sha"],
        "profile_sha256": hashlib.sha256(args.profile.read_bytes()).hexdigest(),
        "tool_profile": profile["semble"],
        "input_status": manifest["status"],
        "input_manifest_sha256": hashlib.sha256(args.input_manifest.read_bytes()).hexdigest(),
        "selected_change_count": len(manifest["selected"]),
        "cold": {"wall_ms": cold_ms, "matches": cold, "errors": cold_errors},
        "warm": {"wall_ms": warm_ms, "matches": warm, "errors": warm_errors},
        "cold_warm_results_identical": normalized_cold == normalized_warm,
        "cache": {
            "bytes_before": cache_before,
            "bytes_after_cold": cache_after_cold,
            "bytes_after_warm": cache_after_warm,
            "warm_delta": cache_after_warm - cache_after_cold,
        },
        "acceptance_authority": False,
        "score_semantics": "rank-only advisory evidence; not confidence or correctness",
    }
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
