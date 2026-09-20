# Semantic QA R1: upstream tool identity and capability freeze

**Date:** 2026-09-20

**Tracking:** `TeaShaman-cyber/theseus-research#57`

**Roadmap node:** `freeze-tool-identities`

**Disposition:** COMPLETE / READ-ONLY UPSTREAM FREEZE / NO TOOL SELECTED

## Purpose

Freeze exact upstream identities and capability surfaces before fixture runs.
R1 does not choose a winner and does not authorize CI integration.

## Summary

| Candidate | Frozen software identity | Local semantic primitive | CI/diff surface | Model identity | R1 disposition |
| --- | --- | --- | --- | --- | --- |
| semdup | `829f90ad94f453b73a24e46413202e9ece0b49e8`, Cargo `0.2.0` | ONNX Runtime + tree-sitter + SQLite/content-hash cache | built-in diff/check + GitHub Action + annotations | immutable model release tag + compiled blake3 pins | READY_FOR_FIXTURE |
| Semble | `8e40653de0d62526b62301dcc4d087ac19f86663`; release `v0.6.0@9bd776d7eaef0ee918ef39c546ea902399d7a5ba` | Model2Vec + BM25/RRF + tree-sitter | CLI/Python/MCP, JSON output; no built-in diff gate | default HF repo is mutable, local path override exists | READY_WITH_PIN_ADAPTER |
| Needle 3 | `fc5bae0f9b6138828fe7589f6b531fb9a26968de`, package/engine `3.0.1` | native local `embed()` + persistent tool embedding index | embedding primitive, not code-diff checker | normal HF fetch has no explicit revision | PIN_GAP_BEFORE_FIXTURE |

## semdup

Software pin:

`niklebedenko/semdup@829f90ad94f453b73a24e46413202e9ece0b49e8`

The pinned `Cargo.toml` declares version `0.2.0` and license
`MIT OR Apache-2.0`. No `v0.2.0` Git tag was observed, so the
pilot identity is the exact commit rather than a guessed software tag.

Relevant upstream mechanics already exist:

- tree-sitter function/block extraction;
- SQLite state keyed by content hashes;
- local ONNX Runtime CPU path;
- exact cosine scan plus optional approximate large-corpus path;
- `semdup diff --base origin/main --check`;
- reusable GitHub Action;
- base-branch handling through a temporary worktree;
- model/cache and SQLite cache restoration;
- incremental re-embedding;
- GitHub annotations.

A general JSON report surface was not confirmed during R1 and remains
`UNKNOWN` until the fixture phase.

Default model assets are not floating HF downloads. The pinned source names
release tag:

`model-coderankembed-1@b395e94fe94acdf5f3f7c21562a527c4306f66f8`

CPU default is the int4 `nomic-ai/CodeRankEmbed@fast` export. The
binary contains blake3 pins:

- ONNX:
  `34447cdd9e5b5f6c5606c611ef4d5872e4391ff9324e1cdee3197db9938a33a3`
- ONNX data:
  `f2b81387aee7a0db997f4a18948560f635396cb7796e1d4e34be018774da146c`
- tokenizer:
  `9323872b7f8abfe19f9bf09eb789d33378be39c951627bdde0aad0e9baeb839d`

A checksum mismatch is rejected before load.

**Disposition:** `READY_FOR_FIXTURE`.

## Semble

Observed current source:

`MinishLab/semble@8e40653de0d62526b62301dcc4d087ac19f86663`

Observed latest release:

`v0.6.0@9bd776d7eaef0ee918ef39c546ea902399d7a5ba`

License: MIT.

Semble already supplies the generic retrieval machinery proposed in #57:

- tree-sitter code-aware chunks;
- static Model2Vec embeddings;
- BM25 lexical retrieval;
- Reciprocal Rank Fusion;
- code-aware reranking;
- CPU execution;
- incremental repository indexes;
- `code`, `docs`, `config`, or combined corpora;
- CLI, Python and MCP surfaces;
- path/line/content/score provenance;
- JSON as the CLI default output.

It has no built-in Git-diff policy. That missing layer is repo-specific candidate
selection and receipt binding, not another search implementation.

Default model:

`minishlab/potion-code-16M-v2`

Observed HF HEAD:

`e9d2a44ca6a05ac6685f3b23709ea57eb7352d5b`

The default loader uses the repository name without an explicit revision, so a
cold default run is not an exact model pin.

Upstream supports:

`SEMBLE_MODEL_NAME=<local path>`

Therefore the pin gap is closable without a fork:

1. prefetch the exact HF revision;
2. verify/cache the snapshot;
3. set `SEMBLE_MODEL_NAME` to that local snapshot;
4. run upstream Semble unchanged.

**Disposition:** `READY_WITH_PIN_ADAPTER`.

## Needle 3

Observed current source:

`cactus-compute/needle@fc5bae0f9b6138828fe7589f6b531fb9a26968de`

`pyproject.toml`, `needle.__version__`, and the fetch layer
all declare `3.0.1` for the current package/engine. License:
Apache-2.0.

Relevant current surface:

- native local `Needle.embed(text) -> list[float]`;
- persistent `tool_index_path`;
- local engine/weights cache;
- documented `HF_HUB_OFFLINE=1` fail-fast operation;
- `NEEDLE3_LIB_PATH` engine override;
- no inference API requirement;
- CI environments excluded from telemetry according to upstream docs.

Needle 3 is not a drop-in code-search or Git-diff checker. It remains a bounded
semantic primitive / Needle-2 lineage comparison.

Engine/model repository:

`Cactus-Compute/needle3`

Observed HF HEAD:

`b274efcb211a9eef48c9a88da4b43bd569696a39`

Base archive:

`needle3.cact`

The pinned source calls Hugging Face download/list functions without an explicit
`revision` for the normal base engine/weights path. Thus a cold fetch
can still resolve mutable HF state even when the Python source commit is pinned.

Candidate closure for the fixture phase:

- preseed the expected cache from the exact HF revision;
- record artifact hashes;
- set `HF_HUB_OFFLINE=1`;
- use `NEEDLE3_LIB_PATH` where applicable;
- verify that no network path is taken.

**Disposition:** `PIN_GAP_BEFORE_FIXTURE`.

## Cross-tool conclusion

R1 materially narrows the implementation surface:

- semdup may own semantic near-duplicate/diff detection;
- Semble may own known-failure retrieval;
- Needle 3 remains a bounded alternative/lineage primitive until its artifact
  pin contract is proved.

Project-owned code should begin only where these upstream surfaces stop:

- historical fixture selection;
- exact source/profile provenance;
- status/receipt normalization;
- repo-specific failure-class IDs;
- minimal pin adapters where required.

A custom embedding checker is not justified by current evidence.

## R1 acceptance

- [x] exact upstream software revisions recorded;
- [x] package/release versions recorded where available;
- [x] licenses recorded;
- [x] local inference and account requirements recorded;
- [x] cache behavior recorded;
- [x] CI/diff surfaces recorded;
- [x] machine output recorded as FACT or UNKNOWN;
- [x] model/artifact identity recorded;
- [x] floating-model gaps named explicitly;
- [x] no tool selected by brand or benchmark alone.

R1 is complete. The next roadmap node is R2: freeze the historical fixture and
metrics before running any semantic tool.
