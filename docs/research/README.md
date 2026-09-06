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
