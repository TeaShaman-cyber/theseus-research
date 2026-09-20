# Local semantic QA witness over known failure classes

**Date:** 2026-09-20

**Status:** research design / non-normative

**Tracking:** TeaShaman-cyber/theseus-research#57

## Purpose

Theseus already has strong deterministic QA and is beginning to use heavier
property and mutation witnesses. Independent LLM review remains useful, but it
introduces provider, quota, latency, and availability dependencies.

This pilot tests a narrower intermediate layer: use a small local embedding
model to retrieve known failure classes that are semantically close to a
candidate change, then emit an advisory receipt.

The witness does not review code in the general sense. It does not decide
correctness and cannot grant merge authority. Its purpose is to route attention
back to failure classes the project has already learned.

## Initial corpus

The first corpus is docs/qa/failure-classes.md.

The pilot treats each top-level failure-class row as one semantic record with a
stable class identifier, class title, representative reproductions, prevention
invariant, deterministic guard summary, source provenance, and corpus digest.

Initial class IDs:

- verification-target-mismatch
- authority-provenance-closure
- identity-preservation
- identity-grammar-mismatch
- claim-status-semantics
- phase-dag-closure
- boundary-transport-contract
- derived-state-heuristic-coverage

The existing meta-review lenses remain useful context but are not separate
retrieval records in v0.1.

## Initial model profile

Candidate model:

- repo: BAAI/bge-small-en-v1.5
- revision: 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a
- dimension: 384
- runtime: FastEmbed / ONNX / CPU
- network: model acquisition only when cache is cold
- auth: none required for the public model

The revision above was observed from the public Hugging Face Git repository on
2026-09-20 using git ls-remote. Hugging Face metadata identifies the model as a
public MIT-licensed sentence-transformers/ONNX feature-extraction model.

The exact revision is part of the witness profile. An unpinned main/latest
reference is insufficient evidence for reproducible CI.

## Prior project evidence

This design intentionally reuses project experience instead of inventing a new
embedding lifecycle.

Private TeaShaman-cyber/automem current main already contains local
FastEmbed/TextEmbedding inference, AUTOMEM_MODELS_DIR and explicit cache
directory support, first-use download followed by cached local operation,
runtime embedding-dimension probing, batch embedding, and tests that assert a
model cache directory is supplied.

The local FastEmbed provider originated at commit
7ca7a3894a3a39bd896c84b511be4b379d20468a, which explicitly introduced no-key
local embeddings and a persistent model cache.

The published AutoMem experiment in
docs/research/automem-resource-and-helper-evaluation-2026-08-22.md records an
important migration invariant: changing embedding spaces requires an isolated
re-embed/replay rather than assuming vectors are interchangeable. Matching
dimensions alone do not make two embedding spaces equivalent.

The semantic witness adopts the same principle: model revision, embedding
dimension, extraction/chunking contract, and normalization contract together
define the witness space. Changing any of them creates a new witness profile.

## Candidate input

v0.1 operates on a bounded Git diff, not the whole repository.

Candidate chunks are extracted deterministically from changed text-like files.
Each chunk retains path, source range, source SHA, base SHA, extractor version,
and chunk content digest. Generated, binary, vendor, and cache paths are
excluded by an explicit path policy.

Semantic inference starts only after provenance has been fixed.

## Retrieval

For each candidate chunk:

1. generate a local embedding;
2. compare it against the embedded failure-class corpus;
3. retain top-k matches;
4. emit similarity scores and provenance.

v0.1 does not claim that one universal threshold is correct. Thresholds are
profile data and must be calibrated against fixtures.

A high score means that a changed chunk resembles a previously recorded failure
class. It does not mean that the change violates that invariant.

## Status model

The witness emits one top-level status:

- MATCH: at least one candidate match meets the advisory threshold;
- NOVEL: eligible chunks were processed but none meet the threshold;
- NO_SIGNAL: no eligible semantic chunks were produced;
- UNAVAILABLE: pinned model/cache/runtime could not produce embeddings;
- INVALID: malformed profile, corpus, candidate input, or receipt precondition.

These states are separate from repository QA PASS/FAIL.

UNAVAILABLE must not silently fall back to OpenAI, Voyage, hosted Hugging Face
inference, Ollama, another embedding model, or hash/placeholder embeddings.

A missing semantic witness is evidence that the witness was unavailable, not
evidence that the candidate is safe.

## Receipt shape

The v0.1 JSON receipt should include:

- schema version and witness status;
- source repository, base SHA, source SHA, and diff digest;
- corpus path, content digest, and record count;
- profile ID, model repo, exact model revision, dimension, runtime,
  extractor version, and threshold profile;
- per-match candidate path/range/digest, failure-class ID, score, and rank;
- cache state and runtime duration.

The same source/profile should be reproducible on another runner.

## Cache contract

The CI cache is an optimization, not authority.

Conceptual flow:

pinned public model/revision
-> cache key derived from profile identity
-> verified local model material
-> local ONNX inference
-> receipt names exact profile/revision

A cache hit does not prove model identity by itself. The runner still verifies
that the loaded profile matches the pinned model/revision expectations.

The first implementation should measure cold download/start time, warm cache
start time, cache size, inference time, and total witness time.

## Evaluation fixture

The first fixture should contain historical candidate snippets representing at
least Authority/provenance closure, Claim/status semantics, Boundary/transport
contract, Identity grammar mismatch, and unrelated changes expected to produce
weak or no useful matches.

Evaluation records top-1/top-k class retrieval, misleading high-similarity
matches, useful low-ranked matches, cold/warm latency, repeat-run score
stability, and whether the match helped select an existing deterministic guard
or review lens.

The first pass has no arbitrary pass score.

## Promotion boundary

The semantic witness starts as advisory evidence.

It may become a blocking gate only if a later separately reviewed change can
state a deterministic proposition that the witness is actually capable of
proving. Generic embedding similarity is not such a proposition.

A successful pilot may justify extracting generic runner/cache/receipt
mechanics into marcopolo-cookbook, while repository-specific corpus semantics,
class IDs, thresholds, and path policies remain with the consuming repository.

Consumer proof comes before shared infrastructure.

## Relationship to other work

- theseus-research#55 compares independent review with heavy deterministic CI.
- theseus-research#30 studies multiple independent LLM reviewers.
- theseus-1f916-client#38 is a Heavy QA v2 pilot for reusable process mechanics.
- docs/qa/failure-classes.md is the initial semantic corpus.
- TeaShaman-cyber/automem provides prior no-key FastEmbed/cache/migration
  implementation evidence.

This design does not change Theseus methodology or contract authority.
