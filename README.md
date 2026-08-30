# Theseus

Theseus is an independent, voluntary, ethical, non-commercial public-interest research program about how people and changing AI systems can collaborate over long periods while preserving memory, responsibility, verifiability, autonomy, and human wellbeing.

Its tools and experiments may change; the principles below are the stable part that should remain understandable and reviewable.

## Public Research Program Contract

**Version:** `0.3-draft`

**Status:** proposed for public review

**Languages:** English (international reference) · [Русский перевод](README.ru.md)

**Scope:** voluntary, ethical, non-commercial research

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
- reselling API credits or compute, donated or otherwise;
- claiming that agents are people;
- creating one supposedly permanent artificial mind;
- replacing human responsibility or decision-making;
- preserving one particular model, provider, or platform forever.

### Knowledge as code

This manifesto is a versioned contract, not a timeless declaration. Changes follow a reviewable path:

`proposal -> diff -> review -> explicit acceptance -> versioned commit`

- **PATCH** changes wording without changing meaning;
- **MINOR** adds compatible principles, areas, or clarifications. A MINOR change
  must preserve every existing invariant: it cannot remove, weaken, or silently
  narrow consent, least-privilege, provenance, reversibility, sponsor
  independence, or public-status commitments;
- **MAJOR** changes the mission, an invariant, a security, privacy, or
  authorization boundary, the autonomy boundary, sponsor independence, or
  public status. When compatibility is uncertain, use the higher version.

Every accepted change records its version, date, summary, reason, and review status in [CHANGELOG.md](CHANGELOG.md).

**Acceptance authority:** public review informs; the named program maintainer (currently [@TeaShaman-cyber](https://github.com/TeaShaman-cyber)) accepts. A change is "explicitly accepted" only when the maintainer merges it and records it in the changelog.

### Revision record: `0.3-draft` — 2026-08-13

- **Review source:** public review recorded in [issue #1](https://github.com/TeaShaman-cyber/theseus-research/issues/1) through a CISO / Zero-Trust / OWASP lens.
- **Review status:** accepted by the maintainer after public review; no second independent review was received before this revision.
- **Disposition:** adopt all six review directions: clarify technical interchangeability, bound external actions by explicit approval, distinguish contract rules from operational methodology, state the non-commercial public-interest status directly, tighten version-compatibility rules, and introduce Sonar only as an experimental example.
- **Version rationale:** this revision clarifies and strengthens commitments already present in the `0.2-draft` scope, non-goals, and consent invariant; it does not remove or weaken an invariant. A future change to a security, privacy, authorization, autonomy, sponsor-independence, or public-status boundary remains MAJOR.
- **Research context:** the human-centered direction is informed by [ComBodied Agents: a New Paradigm of Human-Centric Agentic AI](https://arxiv.org/abs/2608.10915) (Ding et al., arXiv:2608.10915v2, 2026-08-12). The paper is an external research reference, not a dependency, authority, or claim that Theseus implements a health, robotics, or personal-world-model system.

### Bilingual publication rule

Theseus maintains the public contract and methodology in English and Russian.
English is the international reference text; Russian is the maintained
reader-facing version for the maintainer's meaning verification. Both versions
must be updated in the same revision and cross-linked. A wording divergence is
a documentation defect to resolve before publication, not a silent choice of
one language over the other.

### Current boundary

This repository contains the program-level contract, methodology, and public map of Theseus research lines. Specific tools and implementations may support the program, but no single tool or repository defines Theseus.

### Theseus research lines

| Research line | Visibility / status | Role |
| --- | --- | --- |
| [`theseus-research`](https://github.com/TeaShaman-cyber/theseus-research) | public · active / root | Program contract, methodology, and research map |
| [`theseus-public-observatory`](https://github.com/TeaShaman-cyber/theseus-public-observatory) | public · active | Public-data observation and reproducible verification experiments |
| [`theseus-needle-lab`](https://github.com/TeaShaman-cyber/theseus-needle-lab) | public · bootstrapping | Observable and reproducible Needle learning experiments |
| [`theseus-memory-provider-lab`](https://github.com/TeaShaman-cyber/theseus-memory-provider-lab) | public · bootstrapping | Automatic memory-provider lifecycle, recall/retain semantics, and verifiable provider-contract experiments |
| Sonar | private incubation | Experimental continuity and retrieval research line; implementation remains private |

This registry lists only research lines explicitly declared part of Theseus; it is not an inventory of every repository owned by the maintainer. Private-incubation lines are named for context without exposing private repository links.

No decision about grants, sponsorship, hardware purchases, or institutional structure is implied by this draft.

## Methodological foundation

*This section is explanatory, not normative. Normative commitments are limited to Mission, Core invariants, Non-goals, and Knowledge as code above.*

Theseus follows a practice of human-agent engineering. An agent is neither a magical assistant nor an autonomous replacement for human responsibility, but a participant in a sociotechnical system. Our work reduces the distance between human intent and actual action through explicit contracts, bounded tools, provenance, observable postconditions, and read-back verification.

We distinguish historical memory from current operational truth, intention from permission, tool from wrapper, observation from inference, and MVP from production. When a route fails, we record the signal, identify the missing contract, repair the smallest responsible layer, verify the postcondition, and preserve the reusable lesson.

The longer explanation of this method is in [Methodology: Sadhana of Engineering](docs/methodology.md).

## Research notes

- [AutoMem resource and helper-model evaluation — 2026-08-22](docs/research/automem-resource-and-helper-evaluation-2026-08-22.md) · [Русский перевод](docs/research/automem-resource-and-helper-evaluation-2026-08-22.ru.md)

## Research context

Theseus is part of a wider conversation about human-centered agentic systems.
[ComBodied Agents](https://arxiv.org/abs/2608.10915) describes a useful external
research frame: event-based perception, longitudinal and correctable memory,
personal-state modeling, and proportionate intervention constrained by consent,
uncertainty, safety, reversibility, and user control.

Theseus uses that work as a research reference for sharpening its questions
about continuity, memory, agency, and care. It does not adopt the paper's health,
wearable, robotics, or personal-world-model scope as a product requirement. The
Theseus contract remains the authority for this program, and any implementation
must still be judged by its own evidence and reviewable boundaries.

## Public review

This is an intentionally small first version. Feedback should address the text, its boundaries, clarity, and consequences. Concrete changes should be proposed as a reviewable diff or issue and accepted explicitly before changing the contract.

## English summary

Theseus is an independent, voluntary, ethical, non-commercial public-interest research program for long-term human–AI collaboration. It prioritizes human consent, provenance, verifiability, portability, responsible memory, and human wellbeing. This repository is a versioned program contract, not a product pitch or funding promise.
