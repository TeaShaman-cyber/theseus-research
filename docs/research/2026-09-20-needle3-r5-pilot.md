# Needle 3 R5 capability boundary pilot

**Date:** 2026-09-20

**Tracking:** `TeaShaman-cyber/theseus-research#57`

**Roadmap node:** `needle3-bounded-pilot`

**Disposition:** COMPLETE / STOP EARLY / LINEAGE + EMBEDDING PRIMITIVE ONLY / NO CUSTOM RANKER

Machine-readable receipt:
`docs/research/2026-09-20-needle3-r5-pilot-receipt.json`

## Question

Can the frozen Needle 3 release act as the third local semantic-QA comparison
without requiring account-bound inference or a project-owned embedding/search
implementation?

R5 is explicitly allowed to stop early if Needle adds infrastructure without a
measurable benefit for the frozen failure-class fixture.

## Execution route

The preferred MarcoPolo write route returned HTTP 403 before the temporary
probe file was created.

The bounded fallback used native GitHub for branch/file writes and
GitHub-hosted Actions for the witness. Repository authority, issue #57, frozen
fixture identity, and the predeclared R1 upstream identities did not change.

## Frozen identities and pin-gap closure

Needle source:

`fc5bae0f9b6138828fe7589f6b531fb9a26968de`

Reported package version:

`3.0.1`

Needle 3 model repository:

`Cactus-Compute/needle3`

Exact model revision:

`b274efcb211a9eef48c9a88da4b43bd569696a39`

R1 found that the pinned Python fetch path did not pass an explicit Hugging
Face `revision`, so a normal cold fetch remained mutable.

R5 closed that gap for the experiment by downloading the exact HF snapshot
first, extracting the Linux engine from that snapshot, pre-seeding the exact
`needle3.cact` cache entry, setting `NEEDLE3_LIB_PATH`, then enabling
`HF_HUB_OFFLINE=1` and broken HTTP/HTTPS/ALL proxy values before inference.

Exact artifacts:

- `needle3.cact`: 35,335,380 bytes,
  SHA-256 `c9d915eca282ed42d1a09b143b592adb4cc6744ffe2d294adf5cfc5548170c38`;
- Linux x86-64 engine wheel: 536,871 bytes,
  SHA-256 `05770ef9a85686583968ea15f62f9ad44217e078efdaa99559d3208bb8a369b0`;
- extracted `libneedle3.so`: 1,294,696 bytes,
  SHA-256 `978fce130aac08af506b5fe8bb2950da58e9479d0de69d972d9bd69db953568d`.

The exact local engine and weights completed the offline capability probe.

## The upstream documentation conflict

The pinned repository documentation and the current Needle Python docs describe
a built-in top-5 tool retriever for catalogues above five tools, persisted via
`tool_index_path`.

A newer Cactus porting note for the current Needle 3 release says the shipped
archive does not contain the contrastive embedding head. In that state the
engine can still return a deterministic probe vector through `needle_embed`,
but native tool retrieval is not present.

R5 resolved this conflict against the frozen artifact rather than selecting the
more convenient prose description.

## Exact archive manifest

The `.cact` format declares optional probe heads through a manifest:

- code 1 = embedding / contrastive head;
- code 2 = confidence head;
- code 3 = router head.

The exact frozen archive contained:

`head_codes = [2]`

Observed:

- confidence head: present;
- embedding head: absent;
- router head: absent.

The archive carried 581 tensors. The optional-head section contained seven
tensors: one manifest plus the six tensors belonging to the confidence head.

This matches the current Cactus porting note: this release does not ship the
contrastive retrieval head.

## Python/runtime surface

The exact source exposed:

- `Needle.embed()`: yes;
- `Needle.search()`: no;
- `Needle.retrieve_tools()`: no;
- module-level `search`: no;
- module-level `retrieve_tools`: no.

A catalogue of eight synthetic failure-class tools was initialized with an
explicit `tool_index_path`.

After initialization:

`tool_index_exists = false`

So the documented persistence path did not materialize an index on this frozen
archive, consistent with the missing embedding head.

## Local embedding primitive

Although the contrastive head is absent, `Needle.embed()` works using the
shipped release's fallback probe representation.

Observed on the hosted CPU runner:

- dimension: 3072 floats;
- first-vector norm: 0.9999998675;
- second unrelated-vector norm: 0.9999999259;
- same input twice: maximum absolute delta = 0.0;
- same-input float32 bytes: identical;
- same-input SHA-256:
  `80d37d970ff4eb1e58da95c768612d38c8042e6bd2ef68c24bfe417f05f1a1a3`;
- three same-process embed calls: about 100.3 ms total;
- peak process RSS: 117,372 KiB.

This proves a deterministic local embedding primitive exists on the tested
runner. It does not by itself provide a ranked retrieval contract.

## Why the frozen failure-class ranking was not run

The official porting note demonstrates that an application can build a
catalogue matrix from `embed()` and rank a query with a dot product.

Doing that in Theseus would nevertheless create exactly the layer this roadmap
was intended to avoid reinventing:

`embedding primitive -> project-owned similarity matrix -> ranking -> provenance adapter`

Semble R4 already supplies the full relevant surface natively:

`chunking -> local embedding -> lexical retrieval -> fusion -> ranked result -> path/line/score -> cache`

Needle 3 R5 supplies, on this frozen release:

`local embed() -> vector`

The difference is enough to trigger the predeclared R5 stop rule. Adding a
custom cosine/nearest-neighbor layer would increase infrastructure before any
measured operational advantage over the already-working Semble path.

Therefore no R5 failure-class ranking, top-k metric, or acceptance threshold was
manufactured.

## Needle 2 lineage

The current `theseus-needle-lab` lineage was read back at
`b5a7f02da0b2aa18f861bf243891c53cb7b9a270`.

Several things that required explicit laboratory work around Needle 2 are now
ordinary Needle 3 runtime capabilities:

- local CPU engine and local model archive;
- one-time local engine/weights cache;
- documented air-gapped/offline operation;
- a direct text embedding primitive;
- explicit engine override through `NEEDLE3_LIB_PATH`;
- published prebuilt engine artifacts for multiple platforms.

Several important requirements remain Theseus responsibilities, not model
features:

- immutable source/model identity binding;
- artifact hashes and provenance receipts;
- canonical deterministic QA;
- scientific acceptance and final disposition;
- keeping model evidence separate from authority/permission;
- stable ranked failure-class retrieval and its provenance contract.

`tool_index_path` sits between those categories: the API is exposed, but the
frozen archive cannot activate its documented contrastive retrieval path.

## Reproducibility boundary

The exact Needle source, HF model revision, weights, and engine binary were
pinned and hashed.

The Python package itself declares `huggingface_hub` without an exact version.
The hosted pilot observed `huggingface_hub==1.32.0`, but transitive Python
resolution was not frozen.

Because R5 stops before integration, no additional dependency-freezing
infrastructure is justified by this pilot. If a later Needle release with a
real retrieval head is evaluated, its runtime environment should be frozen as a
new witness version.

## Interpretation

### FACT

- exact local Needle 3 engine and weights ran successfully with HF offline mode,
  broken proxies, and telemetry disabled;
- the exact archive contains confidence head code 2 but no embedding head code
  1 and no router head code 3;
- `Needle.embed()` returns a deterministic 3072-dimensional near-unit vector;
- the exact Python source exposes no ranked search or retrieve-tools method;
- an eight-tool initialization with `tool_index_path` created no index file.

### INFERENCE

Needle 3 is a useful local embedding/runtime primitive and an important
continuation of the Needle 2 research lineage, but this frozen release does not
improve the known-failure retrieval role over Semble without adding a
project-owned ranking layer.

### UNKNOWN

- quality of a future Needle contrastive embedding head;
- retrieval quality of a custom dot-product adapter, intentionally not built;
- whether a later Needle archive will activate `tool_index_path`;
- repository-scale retrieval latency for a future native search surface.

## R5 disposition

R5 is COMPLETE by its stop rule.

Keep Needle 3 as lineage evidence and a local embedding primitive.

Do not promote it as the known-failure retriever for this roadmap.

Do not build a custom cosine or nearest-neighbor checker merely to force a
three-way benchmark.

The graph can proceed to R6 using:

- R3 semdup receipt;
- R4 Semble receipt;
- R5 Needle 3 capability-boundary receipt.
