# Needle 3 R5b ready-made ranker correction

**Date:** 2026-09-20

**Tracking:** `TeaShaman-cyber/theseus-research#57`

**Roadmap node:** `needle3-bounded-pilot`

**Disposition:** COMPLETE / READY-MADE RANKER WORKS / CURRENT NEEDLE FALLBACK GEOMETRY IS WEAKER ON THIS FIXTURE

Machine-readable receipt:
`docs/research/2026-09-20-needle3-r5b-ranking-receipt.json`

## Why R5b exists

R5 correctly established that the frozen Needle 3 release has no native
contrastive retrieval head and no public ranked-search API.

It made one inference too early: that evaluating `Needle.embed()` for
failure-class retrieval would require Theseus to write its own cosine or
nearest-neighbor checker.

That is not necessary.

A mature off-the-shelf library can consume arbitrary precomputed vectors
directly. R5b therefore uses:

`Needle.embed() -> sklearn.neighbors.NearestNeighbors -> top-k`

Needle produces every vector. scikit-learn performs exact cosine ranking.
Theseus glue only binds class IDs/provenance and computes the already-frozen
top-1, top-3 and MRR metrics.

No cosine implementation, vector database, ANN index, classifier, learned
reranker, or score threshold was added.

## Frozen inputs

Needle source:

`fc5bae0f9b6138828fe7589f6b531fb9a26968de`

Needle model revision:

`b274efcb211a9eef48c9a88da4b43bd569696a39`

Ranker:

- scikit-learn 1.9.1;
- `NearestNeighbors`;
- `metric="cosine"`;
- `algorithm="brute"`;
- exact search over eight failure-class vectors.

Fixture digest:

`df3bf51cee0a7a57786b140979586ae28f4df7951fb2968e2a39eb1a1ed7048b`

The corpus is the same eight canonical failure-class rows, lines 12-19 of
`docs/qa/failure-classes.md`.

## Result

Expected positive ranks:

| case | expected class rank |
| --- | ---: |
| authority / remote readback | 2 |
| claim / search completeness | 6 |
| identity grammar | 1 |
| boundary / reserved markers | 3 |

Aggregates:

- top-1 accuracy: **1 / 4 = 0.25**;
- top-3 recall: **3 / 4 = 0.75**;
- MRR: **0.50**.

The claim/search-completeness case is the clear miss: its expected
`claim-status-semantics` class ranked sixth.

The result is not random noise. Three of four expected classes land in the top
three, and the identity-grammar case is correctly top-1. But it is materially
weaker than the R4 Semble result on the same frozen positives.

## Negative controls

The negatives also receive close neighbors:

- AutoMem resource prose -> identity grammar, cosine distance 0.03237;
- benign JSON loader -> identity grammar, 0.03538;
- broad program mission -> identity preservation, 0.03214.

Those distances overlap the positive cases. As with Semble, no confidence,
abstention, PASS/FAIL, or blocking threshold is justified.

## Repeatability

Cold and warm ranking receipts were identical.

All four expected ranks were stable across both passes.

Observed pass times:

- cold: about 7.02 s;
- warm: about 6.85 s.

These passes include loading Needle, embedding eight corpus rows plus seven
queries, and exact scikit-learn ranking. They are not isolated ranker latency
benchmarks.

## What this corrects

### R5 facts that remain valid

- the exact Needle archive has no native contrastive retrieval head;
- the exact Python surface has no native `search` or `retrieve_tools`;
- `tool_index_path` did not materialize a native retrieval index;
- `Needle.embed()` returns deterministic 3072-dimensional local vectors.

### R5 inference that is corrected

A failure-class ranking experiment does **not** require Theseus to implement
similarity search.

The ranking layer can be delegated entirely to a mature general-purpose
nearest-neighbor library.

So the observed limitation moves one layer down:

`not: missing ranker -> cannot evaluate`

`but: ready-made ranker works -> current Needle fallback vector geometry is only moderately useful on this fixture`

## Comparison context

R4 Semble with the minimal stable-record projection produced:

- strict top-1: 4 / 4;
- strict top-3: 4 / 4;
- MRR: 1.00.

R5b Needle + exact scikit-learn cosine ranking produced:

- top-1: 1 / 4;
- top-3: 3 / 4;
- MRR: 0.50.

This does not prove a universal ranking between the tools. It is one tiny
frozen fixture, and the current Needle release is missing the dedicated
contrastive head that a future release may add.

It does show that the absence of a native Needle search API was **not** the
important blocker we initially thought it was.

## Interpretation

### FACT

- a ready-made exact ranker can consume Needle vectors directly;
- no project-owned cosine/search implementation is required;
- the R5b hosted witness completed successfully;
- top-1 was 1/4, top-3 3/4, MRR 0.50;
- cold and warm ranking receipts were identical;
- negative distances overlap positive distances.

### INFERENCE

The current Needle fallback embedding space contains some relevant semantic
signal, but it is not as useful as the observed Semble pipeline for this
particular known-failure routing task.

Needle remains worth keeping in R6 as a measured alternative and lineage/local
embedding primitive, not as a failed experiment caused by missing ranking
infrastructure.

### UNKNOWN

- performance of a future Needle release with the real contrastive head;
- behavior on a larger historical corpus;
- whether a different standard metric would improve this specific fallback
  representation;
- whether the dedicated future head changes the score separation of negatives.

## Disposition

R5b is COMPLETE.

The earlier stop rationale is corrected.

Needle 3 proceeds to R6 with an actual retrieval measurement rather than a
capability-only placeholder.

No threshold or blocking gate is promoted.
