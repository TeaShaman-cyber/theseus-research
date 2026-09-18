# Theseus Contract Changelog

This changelog records revisions to the public Theseus program contract.
Ordinary research merges, fixtures, plans, and implementation changes do not
create a contract version by themselves.

## 1.1 — 2026-09-18

**Lifecycle:** accept the versioned research-line registry as program infrastructure without changing scientific or execution authority.

**Summary:**

- adds `registry/research-lines.json` as the Git-visible authority for explicitly declared Theseus research-line membership;
- keeps GitHub Projects, repository metadata, and bilingual README tables as derived coordination/projection surfaces;
- adds read-only registry validation/doctor tooling and deterministic bilingual projection checks;
- records `theseus-repo-search-lab` and `theseus-math-research-lab` as active public research lines;
- leaves undeclared repository candidates advisory rather than inferring membership from naming or ownership;
- does not promote research conclusions, grant cross-repository mutation authority, or make metadata drift equivalent to research failure.

**Version rationale:** MINOR. This adds compatible program infrastructure and an explicit membership authority while preserving the existing mission, consent, provenance, reversibility, sponsor-independence, public-interest, and human-responsibility invariants.

**Acceptance rule:** this changelog entry, the registry/tooling, and the EN/RU registry projections become accepted together only through explicit maintainer merge and exact remote readback. Green QA or an open PR is not acceptance.

## 1.0 — 2026-09-06

**Lifecycle:** transition from public proposal to active research program.

**Summary:**

- changes the public status from `proposed for public review` to
  `ACTIVE RESEARCH`;
- describes Theseus as a voluntary, maintainer-supported, non-commercial
  public-interest research program that is already operating;
- preserves continuous public review while making clear that external review is
  not a gate for ordinary research work;
- expands the repository boundary from contract-only wording to a public
  coordination root containing the contract, accepted methodology, durable
  research archive, and review/navigation artifacts;
- adds a durable research navigation index without creating a second registry;
- states that the machine-readable research-line registry remains a separate
  pending infrastructure track unless explicitly merged into the accepted
  baseline;
- allows compatible external help, compute, grants, donations, or sponsorship
  only when their conditions do not control findings, conceal negative results,
  weaken consent/safety boundaries, compromise provenance/publication
  integrity, or override the program's ethical purpose;
- synchronizes methodology metadata to reference the `1.0` contract without
  promoting new methodology content.

**Version rationale:** this is a MAJOR revision because the public lifecycle and
status boundary changes from a proposal awaiting review to an active research
program. Existing mission, consent, provenance, reversibility, sponsor
independence, non-commercial public-interest status, and human-responsibility
invariants are preserved rather than weakened.

**Acceptance rule:** this changelog entry, `README.md`, and `README.ru.md` are
reviewed as one contract revision. They become accepted together only through
explicit maintainer merge. The merged PR and commit history are the review and
acceptance record; this file does not self-certify them.

## 0.3-draft — 2026-08-13

Security/public-contract clarification accepted after the public review recorded
in issue #1. The revision strengthened technical interchangeability, bounded
external actions by explicit approval, separated contract from operational
methodology, stated non-commercial public-interest status directly, tightened
version-compatibility rules, and kept Sonar as an experimental example rather
than a defining implementation.

Earlier revision details remain available in Git history and the historical
revision record preserved in the root contract.
