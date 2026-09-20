# Theseus Research Archive

This directory is the durable public research archive for `theseus-research`.
It helps readers find merged evidence, syntheses, fixtures, and review artifacts
without turning the root contract into a live task tracker.

## What this index means

`Durable` means the artifact is preserved in the accepted Git history of this
repository. It does **not** mean that every claim in the artifact has been
promoted into the Theseus contract or methodology.

```text
merged research artifact
!= accepted methodology
!= contract revision
!= research-line membership
```

This file is a navigation aid, not a registry or source of live project state.
Current work, blockers, review findings, and candidate decisions live in
[GitHub Issues](https://github.com/TeaShaman-cyber/theseus-research/issues) and
[Pull Requests](https://github.com/TeaShaman-cyber/theseus-research/pulls).

## Research notes and syntheses

### AutoMem resource and helper-model evaluation — 2026-08-22

- [English reference](automem-resource-and-helper-evaluation-2026-08-22.md)
- [Русский перевод](automem-resource-and-helper-evaluation-2026-08-22.ru.md)
- [Public fixture](automem-resource-and-helper-evaluation-fixture-2026-08-22.json)

Type: bounded evaluation note + public fixture.

The note records a local AutoMem resource-reduction and helper-model experiment.
Its conclusions are bounded to the tested setup and do not define the active
memory architecture or a universal model ranking.

### Semantic QA R6/R7 role comparison — 2026-09-20

- [Role comparison](2026-09-20-semantic-qa-r6-r7-role-comparison.md)
- [Machine-readable receipt](2026-09-20-semantic-qa-r6-r7-role-comparison.json)

Type: cross-pilot role assignment / runner-cost retention decision.

The comparison keeps semdup, Semble and Needle as non-exclusive advisory
signals while observed runner cost remains acceptable, and advances the
roadmap to reusable non-blocking CI integration.

### Needle 3 R5b ready-made ranker correction — 2026-09-20

- [Correction result](2026-09-20-needle3-r5b-ranking.md)
- [Machine-readable receipt](2026-09-20-needle3-r5b-ranking-receipt.json)

Type: frozen-fixture retrieval correction / off-the-shelf exact cosine ranking.

R5b corrects the earlier inference that testing Needle's exported vectors would
require project-owned similarity code. Needle still provides the embeddings,
while scikit-learn NearestNeighbors performs exact cosine top-k ranking. The
ready-made ranker works cleanly, but the current Needle fallback embedding
geometry reaches only 1/4 top-1 and 3/4 top-3 on the frozen failure-class
positives, below the observed Semble retrieval result.

### Needle 3 R5 capability boundary pilot — 2026-09-20

- [Pilot result](2026-09-20-needle3-r5-pilot.md)
- [Machine-readable receipt](2026-09-20-needle3-r5-pilot-receipt.json)

Type: exact-archive local capability probe / Needle-2 lineage comparison.

The pilot closes the mutable Hugging Face fetch gap with an exact snapshot,
runs the exact Needle 3 engine and weights offline, and verifies the shipped
archive's optional-head manifest and public Python surface. The frozen release
provides deterministic local embeddings but no native ranked retrieval surface,
so the pilot stops before adding project-owned cosine/search infrastructure.

### Semble R4 failure-class retrieval pilot — 2026-09-20

- [Pilot result](2026-09-20-semble-r4-pilot.md)
- [Machine-readable receipt](2026-09-20-semble-r4-pilot-receipt.json)

Type: frozen-fixture local retrieval pilot / hosted CPU witness.

The pilot runs exact-source Semble with an exact local model snapshot against
the pre-merged R2 retrieval cases. It compares the canonical failure-class
document with a minimal one-record-per-class projection. The result remains
advisory: ranked retrieval is evidence for attention routing, not a correctness
or confidence verdict.

### semdup R3 advisory pilot — 2026-09-20

- [Pilot result](2026-09-20-semdup-r3-pilot.md)
- [Machine-readable receipt](2026-09-20-semdup-r3-pilot-receipt.json)

Type: frozen-fixture semantic-duplication pilot / hosted CPU witness.

The pilot exercises exact-source semdup against the pre-merged R2 controls,
records cold/warm/cache and PR-style diff evidence, and keeps the result
advisory. No production threshold is promoted.

### Semantic QA R1 tool freeze — 2026-09-20

- [Upstream identity and capability freeze](2026-09-20-semantic-qa-r1-tool-freeze.md)

Type: roadmap evidence / exact upstream capability snapshot.

The note freezes semdup, Semble and Needle 3 software/model identities and
records reproducibility gaps before fixture execution. No tool is selected or
promoted by this artifact.

### Local semantic QA witness — 2026-09-20

- [Pilot design](2026-09-20-local-semantic-qa-witness-design.md)

Type: research design / advisory semantic-QA pilot.

The design pins a small local FastEmbed/ONNX model and defines a non-blocking
receipt that maps changed chunks to known failure classes without an LLM API.
Similarity remains evidence for review routing, not correctness or authority.

### Codex review vs heavy CI — 2026-09-20

- [Observational comparison](2026-09-20-codex-review-vs-heavy-ci.md)

Type: comparative methodology note / observed process traces.

The note compares earlier exact-head Codex review loops with a later no-completed-Codex
heavy-CI mutation/property trace. It records observed differences and confounders; it
does not rank reviewers or promote a new methodology contract by itself.

### Effective Agent Architecture Lineage — 2026-09-05

- [Research synthesis](2026-09-05-effective-agent-architecture-lineage.md)

Type: reconstructed architecture lineage / synthesis.

The note preserves a supported design lineage across Theseus work. It is not an
implementation contract and does not promote candidate architecture into
methodology by itself.

## Migration and review artifacts

### Theseus 1.0 Migration Map — 2026-09-06

- [Migration map](2026-09-06-theseus-1.0-migration-map.md)

Type: non-normative migration and reconciliation artifact.

The map explains the transition from a public proposal to an active research
program and separates repository cleanup, research merge, methodology
promotion, registry acceptance, and contract revision. The map itself is not
contract authority.

## Navigation boundaries

- The [root contract](../../README.md) defines the public program contract.
- The [methodology](../methodology.md) is the accepted explanatory and operational companion to that contract.
- This directory preserves durable research evidence and review artifacts.
- GitHub Issues and Pull Requests carry live mutable research state.
- A machine-readable research-line registry is a separate infrastructure track. It is not part of the accepted Theseus 1.0 baseline unless and until that track is explicitly merged and read back from `main`.

When an artifact is later used to change methodology or the contract, that promotion requires its own reviewable diff and explicit maintainer acceptance.
