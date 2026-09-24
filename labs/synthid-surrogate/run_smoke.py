#!/usr/bin/env python3
"""Small deterministic SynthID mechanics lab for theseus-research issue #78.

This exercises a public SynthID-compatible logits processor with a known lab key.
It does NOT detect Anthropic's production watermark and never reads private corpus data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import SynthIDTextWatermarkLogitsProcessor

STATUS = "SURROGATE_ONLY"
KEYS = [654, 400, 836, 123, 340, 443, 597, 160, 57]
NGRAM_LEN = 5
TABLE_SIZE = 2**16
TABLE_SEED = 0
CONTEXT_HISTORY = 1024
VOCAB_SIZE = 256
DEFAULT_SAMPLES = 12
DEFAULT_TOKENS = 160


def processor() -> SynthIDTextWatermarkLogitsProcessor:
    return SynthIDTextWatermarkLogitsProcessor(
        ngram_len=NGRAM_LEN,
        keys=KEYS,
        sampling_table_size=TABLE_SIZE,
        sampling_table_seed=TABLE_SEED,
        context_history_size=CONTEXT_HISTORY,
        device=torch.device("cpu"),
        skip_first_ngram_calls=True,
        debug_mode=False,
    )


def generate_tokens(*, watermarked: bool, seed: int, tokens: int) -> torch.Tensor:
    proc = processor() if watermarked else None
    ids = torch.empty((1, 0), dtype=torch.long)
    gen = torch.Generator(device="cpu").manual_seed(seed)
    for _ in range(tokens):
        # Uniform pseudo-model: isolates watermark mechanics from model weights/downloads.
        logits = torch.zeros((1, VOCAB_SIZE), dtype=torch.float32)
        scored = proc(ids, logits) if proc is not None else logits
        token = torch.multinomial(torch.softmax(scored, dim=-1), 1, generator=gen)
        ids = torch.cat((ids, token), dim=1)
    return ids


def weighted_mean_score(ids: torch.Tensor) -> float:
    """Torch equivalent of DeepMind's public weighted_mean_score reference."""
    proc = processor()
    g = proc.compute_g_values(ids).to(torch.float32)
    mask = proc.compute_context_repetition_mask(ids).to(torch.float32)
    depth = g.shape[-1]
    weights = torch.linspace(10.0, 1.0, depth)
    weights = weights * depth / weights.sum()
    weighted = g * weights.reshape(1, 1, -1)
    denom = depth * mask.sum(dim=1)
    if torch.any(denom == 0):
        raise RuntimeError("no unmasked ngrams")
    score = (weighted * mask.unsqueeze(-1)).sum(dim=(1, 2)) / denom
    return float(score.item())


def perturb(ids: torch.Tensor, *, seed: int, rate: float = 0.10) -> torch.Tensor:
    """Fixed mild robustness probe; not an optimized watermark-removal procedure."""
    out = ids.clone()
    gen = torch.Generator(device="cpu").manual_seed(seed)
    count = max(1, round(out.shape[1] * rate))
    positions = torch.randperm(out.shape[1], generator=gen)[:count]
    replacements = torch.randint(0, VOCAB_SIZE, (count,), generator=gen)
    out[0, positions] = replacements
    return out


def summarize(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    n = len(ordered)
    return {
        "min": round(ordered[0], 6),
        "median": round((ordered[(n - 1) // 2] + ordered[n // 2]) / 2, 6),
        "mean": round(sum(ordered) / n, 6),
        "max": round(ordered[-1], 6),
    }


def run(samples: int, tokens: int) -> dict:
    wm: list[float] = []
    plain: list[float] = []
    edited: list[float] = []
    for index in range(samples):
        seed = 1000 + index
        wm_ids = generate_tokens(watermarked=True, seed=seed, tokens=tokens)
        plain_ids = generate_tokens(watermarked=False, seed=seed, tokens=tokens)
        wm.append(weighted_mean_score(wm_ids))
        plain.append(weighted_mean_score(plain_ids))
        edited.append(weighted_mean_score(perturb(wm_ids, seed=9000 + index)))

    wm_summary = summarize(wm)
    plain_summary = summarize(plain)
    edited_summary = summarize(edited)
    separation = wm_summary["mean"] - plain_summary["mean"]

    # This gates only the deterministic surrogate mechanics, not Claude attribution.
    passed = separation >= 0.08 and wm_summary["mean"] > 0.60 and plain_summary["mean"] < 0.60
    return {
        "schema": "theseus.synthid-surrogate-smoke.v1",
        "status": STATUS,
        "samples_per_class": samples,
        "tokens_per_sample": tokens,
        "watermark_config": {
            "ngram_len": NGRAM_LEN,
            "depth": len(KEYS),
            "sampling_table_size": TABLE_SIZE,
            "sampling_table_seed": TABLE_SEED,
            "context_history_size": CONTEXT_HISTORY,
            "key_scope": "public-lab-only",
        },
        "scores": {
            "watermarked": wm_summary,
            "unwatermarked": plain_summary,
            "watermarked_after_fixed_10pct_token_substitution": edited_summary,
            "mean_separation": round(separation, 6),
        },
        "gate": {
            "passed": passed,
            "meaning": "public surrogate mechanics only; not Anthropic production watermark detection",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=DEFAULT_SAMPLES)
    ap.add_argument("--tokens", type=int, default=DEFAULT_TOKENS)
    ap.add_argument("--receipt", type=Path)
    args = ap.parse_args()
    if args.samples < 4 or args.tokens < 32:
        ap.error("samples must be >=4 and tokens >=32")
    receipt = run(args.samples, args.tokens)
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    print(encoded, end="")
    if args.receipt:
        args.receipt.write_text(encoded, encoding="utf-8")
    if not receipt["gate"]["passed"]:
        return 1
    print("SYNTHID_SURROGATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
