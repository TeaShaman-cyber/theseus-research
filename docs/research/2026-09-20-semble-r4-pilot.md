# Semble R4 failure-class retrieval pilot

**Date:** 2026-09-20

**Tracking:** `TeaShaman-cyber/theseus-research#57`

**Roadmap node:** `semble-failure-class-pilot`

**Disposition:** COMPLETE / KEEP AS ADVISORY CANDIDATE WITH THIN PROJECTION / NO THRESHOLD PROMOTED

Machine-readable receipt:
`docs/research/2026-09-20-semble-r4-pilot-receipt.json`

## Question

Can upstream Semble retrieve previously learned Theseus failure classes from the
frozen R2 historical cases without a hosted inference API or a custom embedding,
vector-store, nearest-neighbor, or chunk-search implementation?

R4 evaluates retrieval only. It does not turn semantic similarity into a
correctness decision.

## Execution route

The preferred MarcoPolo route became unavailable during this slice: after the
R4 worktree was created, the write route returned HTTP 403.

The bounded fallback used native GitHub writes plus GitHub-hosted Actions.
Repository authority, issue #57, the frozen fixture, and upstream identities
were unchanged. The route change is operational evidence, not a change in
project governance.

## Frozen identities

Fixture digest:

`df3bf51cee0a7a57786b140979586ae28f4df7951fb2968e2a39eb1a1ed7048b`

Semble:

- source commit: `8e40653de0d62526b62301dcc4d087ac19f86663`;
- reported version: 0.6.0;
- Python: 3.12.3.

Model:

- repository: `minishlab/potion-code-16M-v2`;
- exact revision: `e9d2a44ca6a05ac6685f3b23709ea57eb7352d5b`;
- snapshot size: 33,523,226 bytes.

The model snapshot was fetched at that exact revision, passed to Semble as a
local path, and retrieval ran with `HF_HUB_OFFLINE=1`. No inference API key was
required.

## First pass: canonical failure-class document unchanged

The first pass indexed the canonical
`docs/qa/failure-classes.md` as ordinary Semble `docs` content.

No custom pre-chunking was applied.

Result over the four historical positives:

| metric | result |
| --- | ---: |
| inclusive top-1 | 4 / 4 |
| inclusive top-3 | 4 / 4 |
| inclusive MRR | 1.00 |
| strict top-1 | 3 / 4 |
| strict top-3 | 3 / 4 |
| strict MRR | 0.75 |

“Inclusive” means the returned chunk contains the expected class. “Strict”
means the chunk maps only to that expected class.

The only strict ambiguity was the boundary/transport case. Semble's normal
Markdown chunking returned lines 18-19 as one top-ranked chunk, so the result
contained both:

- `boundary-transport-contract`;
- `derived-state-heuristic-coverage`.

This was a measured corpus/provenance ambiguity, not a retrieval failure hidden
by a new threshold.

Raw-corpus cold and warm result order was identical.

## Second pass: minimal class-record projection

Because the first pass demonstrated a concrete provenance ambiguity, R4 tested
one minimal repository-specific projection.

Canonical table lines 12-19 were copied exactly, one line per anonymous record:

`record-01.md` through `record-08.md`.

The record text was not rewritten, summarized, embedded, scored, or otherwise
transformed by project code. The class-ID mapping stayed outside record text.

Semble remained responsible for chunking/indexing, Model2Vec embeddings,
BM25/RRF retrieval, ranking, cache management, and result scoring.

Projected result:

| metric | result |
| --- | ---: |
| strict top-1 | 4 / 4 |
| strict top-3 | 4 / 4 |
| strict MRR | 1.00 |

Expected top-1 results were:

- authority/provenance -> `record-02.md`, score 0.0163934426;
- claim/status -> `record-05.md`, score 0.0163934426;
- identity grammar -> `record-04.md`, score 0.0163934426;
- boundary/transport -> `record-07.md`, score 0.0162612374.

This supports a thin projection for stable provenance if Semble survives the
later cross-pilot comparison. It does not justify a custom retrieval engine.

## Negative controls and score semantics

All three frozen negatives also received ranked failure-class candidates.

Examples from the projected corpus:

- AutoMem resource prose had an exact top-score tie between identity grammar
  and phase/DAG at 0.0162612374;
- the benign JSON loader ranked authority/provenance first at 0.0160010241;
- broad program-mission prose ranked identity preservation first at
  0.0162612374.

These scores overlap the positive cases.

Therefore the observed Semble score is useful for ordering candidates inside the
retrieval result, but this fixture provides no evidence for treating it as a
confidence, abstention, MATCH/NOVEL, PASS/FAIL, or correctness threshold.

R4 promotes no threshold.

## Repeatability and ties

The raw canonical corpus produced identical cold/warm rankings.

The projected corpus preserved all four positive top-1 results and their scores
across cold/warm runs, but the full ranking was not byte-identical.

The differences were equal-score tie ordering:

- in the boundary case, two lower-tail records at score 0.0149286988 swapped;
- in the AutoMem negative, the two top records tied at 0.0162612374 and swapped.

This is retrieval-order tie instability, not evidence that the positive
classification changed.

Any later receipt contract should preserve scores and provenance and avoid
pretending an arbitrary order among exact-score ties carries semantic meaning.

## Runtime

Final hosted run:

`35533735274`

Artifact:

`10611593337`

Observed setup:

- exact-source Semble install: 12,303 ms;
- exact model prefetch: 1,902 ms;
- model snapshot: 33,523,226 bytes;
- Semble index cache after the pilot: 51,323 bytes;
- complete hosted run: approximately 42 s.

The raw seven-query pass took about 4.83 s cold and 4.68 s warm.
The projected pass took about 4.67 s cold and 4.67 s warm.

These numbers include launching the Semble CLI separately for every query.
They are not measurements of the persistent Python-library or MCP path.

## Dependency reproducibility gap

R4 pinned the exact Semble source and exact model revision, but installed the
Python package with `pip install` from the pinned source.

Observed dependency versions are preserved in the raw artifact and machine
receipt, but transitive PyPI resolution was not frozen.

Upstream contains `uv.lock` at blob:

`04ba3abab08d32da390f7d3d30a0195b56035664`

If Semble survives cross-pilot comparison, CI integration should evaluate the
upstream lock or another exact dependency environment rather than treating this
pilot's floating resolver result as a durable runtime profile.

## Interpretation

### FACT

- exact-source Semble with an exact local model snapshot completed on a normal
  GitHub CPU runner without an inference API key;
- the raw canonical document placed the expected class top-1 for all four
  positive cases under inclusive provenance;
- one raw Markdown chunk joined two adjacent failure-class rows;
- the minimal one-row-per-class projection produced strict top-1 for all four
  positives;
- negatives also received high-ranked class candidates at overlapping scores;
- projected positive top-1 results were stable across cold/warm runs;
- full projected ranking order changed only where exact-score ties existed.

### INFERENCE

Semble is a strong advisory candidate for the known-failure retrieval layer.

If retained, the smallest useful Theseus-specific layer appears to be a stable
failure-class record projection plus provenance/receipt normalization. There is
still no evidence for building a custom embedding or vector-search subsystem.

### UNKNOWN

- generalization to a larger historical failure corpus;
- a valid abstention or confidence threshold;
- persistent Python/MCP latency on the same fixture;
- cross-platform tie behavior;
- whether Semble remains useful relative to Needle 3 after R5.

## R4 disposition

Keep Semble as an advisory candidate with a thin repository-owned projection.

Represent its result as ranked top-k evidence with provenance.

Do not promote a MATCH/NOVEL, PASS/FAIL, or blocking threshold from the score.

The roadmap now continues independently to R5 Needle 3 before the required
cross-pilot comparison.
