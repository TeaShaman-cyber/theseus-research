# Local semantic QA roadmap

**Date:** 2026-09-20

**Tracking:** `TeaShaman-cyber/theseus-research#57`

**Graph verification method:** `TeaShaman-cyber/theseus-research#43`

**Graph snapshot:** `docs/plans/2026-09-20-semantic-qa-roadmap.json`

**Graph SHA-256:** `00ab191eeb29510350943d41320fd3ebd79148381838ef04b26189fff84e7ac3`

## Goal

Strengthen Heavy QA with existing local semantic-analysis tools before writing
custom embedding infrastructure.

The roadmap deliberately separates three roles:

1. **semantic duplication / reimplementation detection** - evaluate `semdup`;
2. **known-failure-class retrieval** - evaluate `Semble` as the retrieval
   substrate instead of building a vector/search layer;
3. **lineage / alternative local retrieval** - run a bounded Needle 3 pilot
   because Theseus already has substantial Needle 2 laboratory history.

Custom code is limited to repository-specific adapters, provenance, fixtures,
and receipts that a selected upstream tool does not already provide. A custom
embedding checker is not a roadmap item.

## Working invariants

- No hosted inference account or API key is required for the core semantic QA path.
- No hidden fallback from local inference to OpenAI, Voyage, hosted Hugging Face inference, or another provider.
- Similarity is advisory evidence unless a later verifier proves a narrower deterministic proposition.
- Tool/model/chunking/profile identity is pinned before measurements are accepted.
- Fixtures and metrics are frozen before comparing tools.
- One tool does not need to solve every semantic-QA problem.
- Consumer proof precedes shared infrastructure extraction.
- Second-repository reuse precedes any claim that the runner is generic.
- Promotion to a blocking gate is a separate decision, not an automatic result of a successful pilot.

## Roadmap

### R0 - Evidence baseline - DONE

Inputs already recorded:

- #55 Codex-review vs heavy-CI observational comparison;
- #57 local semantic witness design;
- AutoMem local FastEmbed/cache/re-embed evidence;
- ecosystem scan identifying `semdup`, `Semble`, Slopo, reDUP and Needle 3.

Output: enough evidence exists to test upstream tools before building new semantic infrastructure.

### R1 - Freeze tool identities - NEXT

For each serious candidate, record current exact revision/tag, license,
installation surface, local model identity, cache behavior, machine-readable
output, CI/diff support and external-service requirements.

Initial candidates:

- `niklebedenko/semdup` - semantic duplication/diff QA;
- `MinishLab/semble` - local semantic retrieval over code/docs/config;
- Needle 3 - bounded comparison against the local retrieval role;
- Slopo/reDUP - references or fallback candidates only unless the primary candidates expose a concrete gap.

Acceptance: exact upstream identities and capability receipts exist; no choice is made from mutable README claims alone.

### R2 - Freeze fixtures and metrics

Build one small historical fixture set before tool comparison.

Required positive classes:
- authority / provenance closure;
- claim / status semantics;
- boundary / transport contract;
- identity grammar mismatch;
- known near-duplicate/reimplementation examples where available.

Required negatives:
- unrelated changes;
- intentionally similar but acceptable code;
- docs/config changes with no relevant failure class.

Metrics:
- useful top-1/top-k retrieval;
- false/diagnostic matches;
- semantic-duplicate precision on reviewed examples;
- cold/warm runtime;
- cache size and reuse;
- exact-SHA/profile reproducibility;
- operational dependency/failure modes;
- attention cost for triage.

No arbitrary score threshold is promoted before the fixture is observed.

### R3 - semdup advisory pilot

Use upstream `semdup` without forking if possible.

Evaluate:
- local CPU ONNX path;
- tree-sitter extraction;
- `diff --base ... --check` / GitHub Action behavior;
- content-hash/model cache;
- machine-readable or annotation output;
- threshold calibration against the frozen fixture.

Output remains advisory during the pilot.

### R4 - Semble failure-class pilot

Use upstream `Semble` as the retrieval engine over the existing
`docs/qa/failure-classes.md` corpus.

Prefer upstream capabilities:
- tree-sitter chunking;
- Model2Vec local semantic retrieval;
- BM25/RRF hybrid retrieval;
- incremental cache;
- JSON/Python structured results with path/line/score.

Project-owned glue should contain only missing pieces: candidate diff selection,
stable failure-class IDs, exact source/profile provenance and receipt mapping.

Do not recreate embeddings, cosine search, nearest-neighbor storage or generic
chunking unless a measured upstream limitation requires it.

### R5 - Needle 3 bounded pilot

Treat Needle 3 as a comparison/lineage experiment, not an automatic dependency.

Questions:
- can its local embedding/search surface run without account-bound inference?
- what is its cache/profile model?
- can it produce stable path/range/provenance suitable for CI receipts?
- does it improve retrieval or operational simplicity over Semble for this bounded corpus?
- which requirements developed around Needle 2 are now native in Needle 3?

Stop if it adds infrastructure without measurable benefit for the fixture.

### R6 - Compare pilot receipts

No winner by brand or benchmark. Compare all pilots on the same frozen
fixture/profile rules.

Default retention policy: keep all pilots that provide distinct observable
signal while their runner cost, cache footprint and failure rate remain small
enough not to interfere with primary repository work. Comparison assigns roles
and measures cost; it does not require eliminating a tool.

Needle 3 run receipts and raw advisory outputs are also a future analytics
trace for `theseus-needle-lab`. Preserve exact source/model/profile identities
and task provenance so later lab work can study behavior on real repository
tasks rather than reconstructing synthetic history. These traces remain
research evidence, not acceptance authority.

### R7 - Select advisory roles

Assign non-exclusive advisory roles. Prefer the smallest composition that adds
independent signal, but do not retire a low-cost tool merely because another
tool scores better on one frozen fixture.

Expected shape after R3-R5b:

    deterministic lint/static/AST
            |
            +--> semdup semantic duplication witness
            |
            +--> Semble known-failure retrieval witness
            |
            +--> Needle 3 measured embedding/retrieval trace
            v
    property / mutation / fault witnesses
            v
    periodic independent human/model/forum review

A tool remains active while its observed runner cost and operational noise stay
below the point where it meaningfully delays or destabilizes primary QA.
Retirement remains an explicit later decision based on accumulated field
evidence, not a one-shot benchmark.

### R8 - CI advisory integration

Integrate only selected tools as non-blocking Heavy QA jobs.

Requirements:
- exact tool/model/profile pins;
- cold/warm cache receipts;
- no external inference secrets;
- named UNAVAILABLE/DEGRADED states;
- no auto-write or auto-remediation;
- exact candidate SHA in every receipt.

### R9 - Second-repository reuse

Run the same selected mechanics on one second Theseus repository, preferably a
consumer with different semantics such as `theseus-1f916-client`.

Repository-specific corpora, thresholds, path policies and invariants remain local.

### R10 - Shared runner extraction

Only after second-repository reuse, propose generic cache/orchestration/receipt
mechanics for `marcopolo-cookbook`.

Do not move domain semantics or acceptance authority into the shared layer.

### R11 - Promotion decision

Promotion is an explicit decision with evidence from:
- frozen-fixture comparison;
- advisory CI operation;
- second-repository reuse;
- shared-runner extraction/readback where applicable.

Generic embedding similarity alone cannot become a correctness gate.

Possible dispositions:
- keep advisory;
- promote one narrowly defined deterministic condition;
- retire a low-value tool;
- retain periodic/manual witness only.

## Graph verification

The machine-readable roadmap graph is derived coordination state. This document
and GitHub issue state remain the human-readable coordination record; neither
Wolfram nor the graph snapshot gains project authority.

The exact snapshot above is checked by:

1. a local stdlib-only graph verifier for vertex/edge validity, DAG structure,
   reachability, single source/sink and declared prerequisite paths;
2. an independent Wolfram Language witness using `AcyclicGraphQ`,
   `TopologicalSort`, weakly connected components and transitive reachability.

A disagreement is REVIEW_REQUIRED, not an automatic override.

## Immediate next action

Execute **R6**: compare the durable R3 semdup, R4 Semble and corrected R5/R5b
Needle receipts under the retention-by-cost policy. Record role, runner cost,
operational noise and trace value without forcing a single winner.
