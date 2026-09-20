from __future__ import annotations

import array
import hashlib
import json
import os
import shutil
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import sklearn
from sklearn.neighbors import NearestNeighbors

SNAPSHOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
FIXTURE = Path(os.environ["GITHUB_WORKSPACE"]) / "docs/qa/semantic-fixture-v1"
FAILURE_CLASSES = Path(os.environ["GITHUB_WORKSPACE"]) / "docs/qa/failure-classes.md"
OUT.mkdir(parents=True, exist_ok=True)

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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector_hash(values: list[float]) -> str:
    return hashlib.sha256(array.array("f", values).tobytes()).hexdigest()


weights = SNAPSHOT / "needle3.cact"
wheels = sorted(
    (SNAPSHOT / "python").glob(
        "cactus_needle-3.0.1-py3-none-manylinux2014_x86_64.whl"
    )
)
if not weights.is_file() or len(wheels) != 1:
    raise RuntimeError("exact Needle 3 weights/engine artifacts missing")
wheel = wheels[0]

engine_dir = OUT / "engine"
engine_dir.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(wheel) as zf:
    candidates = [
        name
        for name in zf.namelist()
        if name.endswith("/libneedle3.so") or name == "needle/libneedle3.so"
    ]
    if len(candidates) != 1:
        raise RuntimeError(f"expected one libneedle3.so, got {candidates}")
    engine_path = engine_dir / "libneedle3.so"
    engine_path.write_bytes(zf.read(candidates[0]))

cache_dir = Path.home() / ".cache" / "cactus-needle" / "v3" / "3.0.1"
cache_dir.mkdir(parents=True, exist_ok=True)
cached_weights = cache_dir / "needle3.cact"
shutil.copyfile(weights, cached_weights)

os.environ["NEEDLE3_LIB_PATH"] = str(engine_path)
os.environ["NEEDLE_TELEMETRY"] = "0"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:9"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:9"
os.environ["ALL_PROXY"] = "http://127.0.0.1:9"

import needle  # noqa: E402

manifest = json.loads((FIXTURE / "manifest.json").read_text())
cases = [
    c
    for c in manifest["cases"]
    if c["kind"] in {"retrieval_positive", "retrieval_negative"}
]
failure_lines = FAILURE_CLASSES.read_text().splitlines()
corpus_texts = [failure_lines[line_no - 1] for line_no in range(12, 20)]


def run_pass(name: str) -> dict:
    started = time.perf_counter()
    agent = needle.Needle(tools=[], auto_date=False)
    corpus_vectors = [agent.embed(text) for text in corpus_texts]
    query_vectors = [
        agent.embed((FIXTURE / case["candidate_file"]).read_text()) for case in cases
    ]
    agent.close()

    matrix = np.asarray(corpus_vectors, dtype=np.float32)
    queries = np.asarray(query_vectors, dtype=np.float32)
    ranker = NearestNeighbors(
        n_neighbors=len(CLASS_IDS),
        algorithm="brute",
        metric="cosine",
        n_jobs=1,
    )
    ranker.fit(matrix)
    distances, indices = ranker.kneighbors(queries, return_distance=True)

    observed = []
    for case, query_vector, row_dist, row_idx in zip(
        cases, query_vectors, distances, indices
    ):
        results = [
            {
                "rank": rank,
                "class_id": CLASS_IDS[int(idx)],
                "cosine_distance": float(distance),
            }
            for rank, (distance, idx) in enumerate(zip(row_dist, row_idx), start=1)
        ]
        expected = case["oracle"].get("expected_failure_class")
        expected_rank = None
        if expected is not None:
            expected_rank = next(
                (
                    result["rank"]
                    for result in results
                    if result["class_id"] == expected
                ),
                None,
            )
        observed.append(
            {
                "id": case["id"],
                "kind": case["kind"],
                "expected_failure_class": expected,
                "expected_rank": expected_rank,
                "query_vector_sha256_f32": vector_hash(query_vector),
                "results": results,
            }
        )

    return {
        "name": name,
        "wall_ms": (time.perf_counter() - started) * 1000,
        "corpus_vector_sha256_f32": [
            vector_hash(vector) for vector in corpus_vectors
        ],
        "cases": observed,
    }


def aggregate(pass_result: dict) -> dict:
    positives = [
        case for case in pass_result["cases"] if case["kind"] == "retrieval_positive"
    ]
    negatives = [
        case for case in pass_result["cases"] if case["kind"] == "retrieval_negative"
    ]

    def reciprocal(rank: int | None) -> float:
        return 0.0 if rank is None else 1.0 / rank

    return {
        "positive_count": len(positives),
        "negative_count": len(negatives),
        "top1_accuracy": sum(case["expected_rank"] == 1 for case in positives)
        / len(positives),
        "top3_recall": sum(
            (case["expected_rank"] or 999) <= 3 for case in positives
        )
        / len(positives),
        "mrr": sum(reciprocal(case["expected_rank"]) for case in positives)
        / len(positives),
        "negative_top1": [
            {
                "id": case["id"],
                "class_id": case["results"][0]["class_id"],
                "cosine_distance": case["results"][0]["cosine_distance"],
            }
            for case in negatives
        ],
    }


cold = run_pass("cold")
warm = run_pass("warm")

normalized_cold = [
    {
        "id": case["id"],
        "expected_rank": case["expected_rank"],
        "query_vector_sha256_f32": case["query_vector_sha256_f32"],
        "results": case["results"],
    }
    for case in cold["cases"]
]
normalized_warm = [
    {
        "id": case["id"],
        "expected_rank": case["expected_rank"],
        "query_vector_sha256_f32": case["query_vector_sha256_f32"],
        "results": case["results"],
    }
    for case in warm["cases"]
]

receipt = {
    "schema_version": 1,
    "fixture_digest": "df3bf51cee0a7a57786b140979586ae28f4df7951fb2968e2a39eb1a1ed7048b",
    "needle_source_sha": os.environ["NEEDLE_SOURCE_SHA"],
    "model_repo": os.environ["MODEL_REPO"],
    "model_revision": os.environ["MODEL_REVISION"],
    "needle_version": needle.__version__,
    "ranker": {
        "library": "scikit-learn",
        "version": sklearn.__version__,
        "class": "sklearn.neighbors.NearestNeighbors",
        "metric": "cosine",
        "algorithm": "brute",
        "n_neighbors": len(CLASS_IDS),
        "n_jobs": 1,
    },
    "corpus": {
        "source_path": "docs/qa/failure-classes.md",
        "source_lines": list(range(12, 20)),
        "class_ids": CLASS_IDS,
        "texts_sha256": [
            hashlib.sha256(text.encode()).hexdigest() for text in corpus_texts
        ],
    },
    "cold": cold,
    "warm": warm,
    "cold_metrics": aggregate(cold),
    "warm_metrics": aggregate(warm),
    "cold_warm_identical": normalized_cold == normalized_warm,
    "artifacts": {
        "weights_sha256": sha256(weights),
        "engine_wheel_sha256": sha256(wheel),
        "engine_library_sha256": sha256(engine_path),
    },
}
(OUT / "needle3-r5b-ranking.json").write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n"
)
print(json.dumps(receipt, indent=2, sort_keys=True))
