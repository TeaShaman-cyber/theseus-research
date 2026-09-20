from __future__ import annotations

import array
import hashlib
import json
import math
import os
import resource
import shutil
import struct
import sys
import time
import zipfile
from pathlib import Path

SNAPSHOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

HDR_FMT = "<48If"
REC_FMT = "<BBHIIIIQQII"
REC_SIZE = struct.calcsize(REC_FMT)
TAG = 0x05E12A84
FP16 = 1
RAW = 4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_head_manifest(path: Path) -> dict:
    raw = path.read_bytes()
    hdr_size = struct.calcsize(HDR_FMT)
    hdr = struct.unpack_from(HDR_FMT, raw, 0)
    if hdr[0] != TAG:
        raise RuntimeError(f"unexpected cact tag: 0x{hdr[0]:08x}")

    num_tensors = int(hdr[1])
    cb_n = int(hdr[2])
    num_layers = int(hdr[10])
    qkv_conv_taps = int(hdr[19])
    num_sites = int(hdr[31])

    off = hdr_size + cb_n * 4
    records = []
    for _ in range(num_tensors):
        rec = struct.unpack_from(REC_FMT, raw, off)
        off += REC_SIZE
        dtype, ndim = int(rec[0]), int(rec[1])
        shape = tuple(int(x) for x in rec[3 : 3 + ndim])
        records.append(
            {
                "dtype": dtype,
                "shape": shape,
                "offset": int(rec[7]),
                "nbytes": int(rec[8]),
                "group": int(rec[9]),
                "bits": int(rec[10]),
            }
        )

    per_layer = 24 + (3 if qkv_conv_taps else 0)
    through_final_norm = (
        1
        + num_layers * per_layer
        + 9
        + 2
        + num_sites * 4
        + 1
    )
    raw_attachments = sum(1 for r in records if r["dtype"] == RAW)
    extra = num_tensors - through_final_norm - raw_attachments

    head_codes: list[int] = []
    manifest_record = None
    if extra > 0:
        manifest_record = records[through_final_norm]
        if manifest_record["dtype"] != FP16:
            raise RuntimeError("expected FP16 heads.manifest")
        count = math.prod(manifest_record["shape"]) if manifest_record["shape"] else 0
        blob = raw[
            manifest_record["offset"] :
            manifest_record["offset"] + manifest_record["nbytes"]
        ]
        head_codes = [
            int(round(struct.unpack_from("<e", blob, i * 2)[0]))
            for i in range(count)
        ]

    return {
        "num_tensors": num_tensors,
        "num_layers": num_layers,
        "qkv_conv_taps": qkv_conv_taps,
        "num_engram_sites": num_sites,
        "raw_attachment_count": raw_attachments,
        "through_final_norm_tensor_count": through_final_norm,
        "optional_head_tensor_count": extra,
        "head_codes": head_codes,
        "has_embedding_head": 1 in head_codes,
        "has_confidence_head": 2 in head_codes,
        "has_router_head": 3 in head_codes,
        "manifest_record": manifest_record,
    }


weights = SNAPSHOT / "needle3.cact"
if not weights.is_file():
    raise FileNotFoundError(weights)

wheels = sorted(
    (SNAPSHOT / "python").glob(
        "cactus_needle-3.0.1-py3-none-manylinux2014_x86_64.whl"
    )
)
if len(wheels) != 1:
    raise RuntimeError(f"expected one linux-x86_64 engine wheel, got: {wheels}")
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
        raise RuntimeError(f"expected one libneedle3.so in engine wheel: {candidates}")
    engine_member = candidates[0]
    engine_path = engine_dir / "libneedle3.so"
    engine_path.write_bytes(zf.read(engine_member))

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

started = time.perf_counter()
agent = needle.Needle(tools=[], auto_date=False)
first = agent.embed("authority drift requires exact remote readback")
second = agent.embed("authority drift requires exact remote readback")
other = agent.embed("render a bilingual projection table")
embed_wall_ms = (time.perf_counter() - started) * 1000

if not first or len(first) != len(second) or len(first) != len(other):
    raise RuntimeError("invalid embedding dimensions")

max_repeat_delta = max(abs(a - b) for a, b in zip(first, second))
norm_first = math.sqrt(sum(x * x for x in first))
norm_other = math.sqrt(sum(x * x for x in other))


def vector_hash(values: list[float]) -> str:
    packed = array.array("f", values).tobytes()
    return hashlib.sha256(packed).hexdigest()


agent.close()

catalogue = [
    {
        "name": f"failure_class_{i:02d}",
        "description": description,
        "parameters": {"type": "object", "properties": {}, "required": []},
    }
    for i, description in enumerate(
        [
            "Verification target mismatch between claimed and observed repository state.",
            "Authority and provenance closure requiring exact remote readback.",
            "Identity preservation across projections and downstream consumers.",
            "Identity grammar mismatch against the authoritative downstream grammar.",
            "Claim and status semantics requiring complete search before absence.",
            "Phase and DAG closure across atomic contract revision surfaces.",
            "Boundary and transport contract must fail closed on ambiguity.",
            "Derived state and heuristic coverage must remain reproducible.",
        ],
        start=1,
    )
]
tool_index = OUT / "tools.idx"
catalogue_agent = needle.Needle(
    tools=catalogue,
    tool_index_path=tool_index,
    auto_date=False,
)
catalogue_agent.close()

manifest = parse_head_manifest(weights)

receipt = {
    "schema_version": 1,
    "needle_version": needle.__version__,
    "weights": {
        "path": str(weights),
        "bytes": weights.stat().st_size,
        "sha256": sha256(weights),
    },
    "engine_wheel": {
        "path": str(wheel.relative_to(SNAPSHOT)),
        "bytes": wheel.stat().st_size,
        "sha256": sha256(wheel),
        "member": engine_member,
    },
    "engine_library": {
        "bytes": engine_path.stat().st_size,
        "sha256": sha256(engine_path),
    },
    "cache": {
        "weights_path": str(cached_weights),
        "weights_bytes": cached_weights.stat().st_size,
        "weights_sha256": sha256(cached_weights),
        "tool_index_path": str(tool_index),
        "tool_index_exists_after_init": tool_index.exists(),
        "tool_index_bytes": tool_index.stat().st_size if tool_index.exists() else 0,
        "tool_index_sha256": sha256(tool_index) if tool_index.exists() else None,
    },
    "manifest": manifest,
    "embedding_probe": {
        "dimension": len(first),
        "first_norm": norm_first,
        "other_norm": norm_other,
        "repeat_max_abs_delta": max_repeat_delta,
        "first_sha256_f32": vector_hash(first),
        "repeat_sha256_f32": vector_hash(second),
        "other_sha256_f32": vector_hash(other),
        "repeat_byte_identical_f32": vector_hash(first) == vector_hash(second),
        "wall_ms_three_calls": embed_wall_ms,
    },
    "python_surface": {
        "needle_has_search": hasattr(needle, "search"),
        "needle_has_retrieve_tools": hasattr(needle, "retrieve_tools"),
        "Needle_has_search": hasattr(needle.Needle, "search"),
        "Needle_has_retrieve_tools": hasattr(needle.Needle, "retrieve_tools"),
        "Needle_has_embed": hasattr(needle.Needle, "embed"),
    },
    "runtime": {
        "hf_hub_offline": os.environ["HF_HUB_OFFLINE"],
        "needle_telemetry": os.environ["NEEDLE_TELEMETRY"],
        "needle3_lib_path": os.environ["NEEDLE3_LIB_PATH"],
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    },
}
(OUT / "needle3-r5-probe.json").write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n"
)
print(json.dumps(receipt, indent=2, sort_keys=True))
