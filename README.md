# Theseus

Theseus is an independent, voluntary, ethical, non-commercial public-interest research program about how people and changing AI systems can collaborate over long periods while preserving memory, responsibility, verifiability, autonomy, and human wellbeing.

Its tools and experiments may change; the principles below are the stable part that should remain understandable and reviewable.

## Public Research Program Contract

**Version:** `1.0`

**Status:** `ACTIVE RESEARCH`

**Languages:** English (international reference) · [Русский перевод](README.ru.md)

**Scope:** voluntary, ethical, non-commercial public-interest research

**Operating model:** voluntary and maintainer-supported; compatible external help is welcome within the authority and ethics boundaries below

### Mission

We explore practical ways to make the technical components of long-term human–AI collaboration more continuous, transparent, interchangeable, and humane.

### Core invariants

1. Human intent and consent come before autonomous initiative.
2. Memory, retrieval, and model output are not truth by themselves.
3. Observations, inferences, hypotheses, and unknowns must be distinguishable.
4. Important results should be reproducible, portable, and verifiable.
5. Replacing a model, agent, service, or piece of infrastructure must not silently destroy meaning, provenance, or history.
6. External support must not control findings, conceal negative results, or turn the program into advertising.
7. Metaphors may guide inquiry, but they do not substitute for mechanisms and evidence.

### Non-goals

- building a commercial AI product;
- reselling donated API credits or compute;
- claiming that agents are people;
- creating one supposedly permanent artificial mind;
- replacing human responsibility or decision-making;
- preserving one particular model, provider, or platform forever.

### Knowledge as code

This contract is versioned, not timeless. Changes follow a reviewable path:

`proposal -> diff -> review -> explicit acceptance -> versioned commit`

- **PATCH** changes wording without changing meaning;
- **MINOR** adds compatible principles, areas, or clarifications. A MINOR change must preserve every existing invariant: it cannot remove, weaken, or silently narrow consent, least-privilege, provenance, reversibility, sponsor independence, or public-status commitments;
- **MAJOR** changes the mission, an invariant, a security, privacy, or authorization boundary, the autonomy boundary, sponsor independence, or public status. When compatibility is uncertain, use the higher version.
Every accepted change records its version, date, summary, reason, and review status.

### Revision record: `1.0` — 2026-09-06

- **Lifecycle:** Theseus moves from a public proposal awaiting review to an active research program.
- **Reason:** the repository and surrounding research program already contain multiple durable research lines, accepted methodology, public evidence, versioned review artifacts, and active GitHub coordination. Keeping proposal-phase wording had become materially misleading.
- **Compatibility:** this is a MAJOR revision because public program status changes. The existing mission and all consent, provenance, reversibility, sponsor-independence, non-commercial public-interest, and human-responsibility invariants remain in force.
- **Review model:** public and independent review remain welcome and informative. Ordinary research work does not wait for external review, while changes to this contract or accepted methodology still require a reviewable diff and explicit maintainer acceptance.
- **Repository model:** this repository is the public program coordination root for the contract, accepted methodology, durable research archive, and review/navigation artifacts. Live unfinished work remains in GitHub Issues and Pull Requests.
- **Registry boundary:** a machine-readable research-line registry is a separate infrastructure track and is not part of the accepted `1.0` baseline unless and until that track is explicitly merged into `main`.
- **Acceptance record:** `README.md`, `README.ru.md`, and the `1.0` entry in [CHANGELOG.md](CHANGELOG.md) are reviewed as one revision and become accepted atomically through maintainer merge.

### Historical revision: `0.3-draft` — 2026-08-13
- **Review source:** public review recorded in [issue #1](https://github.com/TeaShaman-cyber/theseus-research/issues/1) through a CISO / Zero-Trust / OWASP lens.
- **Review status:** accepted by the maintainer after public review; no second independent review was received before this revision.
- **Disposition:** adopt all six review directions: clarify technical interchangeability, bound external actions by explicit approval, distinguish contract rules from operational methodology, state the non-commercial public-interest status directly, tighten version-compatibility rules, and introduce Sonar only as an experimental example.
- **Version rationale:** this revision clarified and strengthened commitments already present in the `0.2-draft` scope, non-goals, and consent invariant; it did not remove or weaken an invariant.
- **Research context:** the human-centered direction was informed by [ComBodied Agents: a New Paradigm of Human-Centric Agentic AI](https://arxiv.org/abs/2608.10915) (Ding et al., arXiv:2608.10915v2, 2026-08-12). The paper is an external research reference, not a dependency, authority, or claim that Theseus implements a health, robotics, or personal-world-model system.

### Bilingual publication rule

Theseus maintains the public contract and methodology in English and Russian. English is the international reference text; Russian is the maintained reader-facing version for the maintainer's meaning verification. Both versions must be updated in the same revision and cross-linked. A wording divergence is a documentation defect to resolve before publication, not a silent choice of one language over the other.

### Operating and support model

Theseus is currently developed voluntarily and supported primarily by maintainer resources because the research is practically useful.

Compatible contributions, compute, infrastructure, grants, donations, sponsorship, and other outside help may be accepted when their conditions preserve the program's purpose and invariants. Support does not purchase research, publication, or governance authority. It must not control findings, conceal negative evidence, weaken consent or safety boundaries, compromise provenance or publication integrity, require advertising disguised as research, or override independent research judgment and ethical purpose.

Accepting this possibility does not imply a current funding arrangement, grant decision, hardware purchase, sponsor commitment, or institutional structure.

### Current repository boundary
This repository is the public coordination root of the Theseus research program. It contains the versioned program contract, accepted methodology, durable research notes and review artifacts, and navigation for current work.

Specific tools, laboratories, and implementations—including experimental tools such as [Sonar](https://github.com/TeaShaman-cyber/theseus-sonar)—may live in separate repositories and research lines. No single tool defines Theseus.

The durable research archive is indexed at [docs/research/README.md](docs/research/README.md). Current mutable research state, blockers, and candidate decisions live in [GitHub Issues](https://github.com/TeaShaman-cyber/theseus-research/issues) and [Pull Requests](https://github.com/TeaShaman-cyber/theseus-research/pulls).

The machine-readable research-line registry remains a separate pending infrastructure track. Its absence from the accepted `1.0` baseline does not block truthful active-program status, and this contract does not treat candidate registry content as accepted authority.

## Methodological foundation

Theseus follows a practice of human-agent engineering. An agent is neither a magical assistant nor an autonomous replacement for human responsibility, but a participant in a sociotechnical system. Our work reduces the distance between human intent and actual action through explicit contracts, bounded tools, provenance, observable postconditions, and read-back verification.

We distinguish historical memory from current operational truth, intention from permission, tool from wrapper, observation from inference, and MVP from production. When a route fails, we record the signal, identify the missing contract, repair the smallest responsible layer, verify the postcondition, and preserve the reusable lesson.

The longer explanation of this method is in [Methodology: Sadhana of Engineering](docs/methodology.md).

## Research archive

Durable public research evidence, syntheses, fixtures, and migration/review artifacts are indexed in [Theseus Research Archive](docs/research/README.md).

A merged research artifact is preserved evidence; it does not automatically become accepted methodology, contract authority, or research-line membership.

## Research context

Theseus is part of a wider conversation about human-centered agentic systems. [ComBodied Agents](https://arxiv.org/abs/2608.10915) describes a useful external research frame: event-based perception, longitudinal and correctable memory, personal-state modeling, and proportionate intervention constrained by consent, uncertainty, safety, reversibility, and user control.

Theseus uses that work as a research reference for sharpening its questions about continuity, memory, agency, and care. It does not adopt the paper's health, wearable, robotics, or personal-world-model scope as a product requirement. The Theseus contract remains the authority for this program, and any implementation must still be judged by its own evidence and reviewable boundaries.

## Continuous public review

Theseus is active research, not a proposal waiting for permission to begin. Public review, counterevidence, criticism, replication, and compatible contributions are welcome throughout the program.

External review informs the work but is not a standing execution gate for ordinary research. Concrete changes to the public contract or accepted methodology must still be proposed as a reviewable diff and explicitly accepted by the maintainer before they become authoritative.

## English summary

Theseus is an independent, voluntary, maintainer-supported, ethical, non-commercial public-interest research program for long-term human–AI collaboration. It prioritizes human consent, provenance, verifiability, portability, responsible memory, and human wellbeing. This repository is the versioned public coordination root for the program, not a product pitch or a promise that external support can buy authority over its findings.
