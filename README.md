# Theseus

Theseus is a voluntary, ethical research program about how people and changing AI systems can collaborate over long periods while preserving memory, responsibility, verifiability, autonomy, and human wellbeing.

Theseus is an independent public-interest direction, not a commercial product by default. Its tools and experiments may change; the principles below are the stable part that should remain understandable and reviewable.

## Public Research Program Contract

**Version:** `0.2-draft`

**Status:** proposed for public review

**Scope:** voluntary, ethical, non-commercial research

### Mission

We explore practical ways to make long-term human–AI collaboration more continuous, transparent, replaceable, and humane.

### Core invariants

1. Human intent and consent come before autonomous initiative.
2. Memory, retrieval, and model output are not truth by themselves.
3. Observations, inferences, hypotheses, and unknowns must be distinguishable.
4. Important results should be reproducible, portable, and verifiable.
5. Replacing a model, agent, service, or piece of infrastructure must not silently destroy meaning, provenance, or history.
6. External support must not control findings, conceal negative results, or turn the program into advertising.
7. Metaphors may guide inquiry, but they do not substitute for mechanisms and evidence.

### Non-goals

- building a commercial AI product by default;
- reselling donated API credits or compute;
- claiming that agents are people;
- creating one supposedly permanent artificial mind;
- replacing human responsibility or decision-making;
- preserving one particular model, provider, or platform forever.

### Knowledge as code

This manifesto is a versioned contract, not a timeless declaration. Changes follow a reviewable path:

`proposal -> diff -> review -> explicit acceptance -> versioned commit`

- **PATCH** changes wording without changing meaning;
- **MINOR** adds compatible principles, areas, or clarifications;
- **MAJOR** changes the mission, invariants, autonomy boundary, sponsor independence, or public status.

Every accepted change records its version, date, summary, reason, and review status in [CHANGELOG.md](CHANGELOG.md).

**Acceptance authority:** public review informs; the named program maintainer (currently [@TeaShaman-cyber](https://github.com/TeaShaman-cyber)) accepts. A change is "explicitly accepted" only when the maintainer merges it and records it in the changelog.

### Current boundary

This repository contains the program-level contract only. Sonar and other tools are research lines that may support the program, but no single tool defines Theseus.

No decision about grants, sponsorship, hardware purchases, or institutional structure is implied by this draft.

## Methodological foundation

*This section is explanatory, not normative. Normative commitments are limited to Mission, Core invariants, Non-goals, and Knowledge as code above.*

Theseus follows a practice of human-agent engineering. An agent is neither a magical assistant nor an autonomous replacement for human responsibility, but a participant in a sociotechnical system. Our work reduces the distance between human intent and actual action through explicit contracts, bounded tools, provenance, observable postconditions, and read-back verification.

We distinguish historical memory from current operational truth, intention from permission, tool from wrapper, observation from inference, and MVP from production. When a route fails, we record the signal, identify the missing contract, repair the smallest responsible layer, verify the postcondition, and preserve the reusable lesson.

The longer explanation of this method is in [Methodology: Sadhana of Engineering](docs/methodology.md).

## Public review

This is an intentionally small first version. Feedback should address the text, its boundaries, clarity, and consequences. Concrete changes should be proposed as a reviewable diff or issue and accepted explicitly before changing the contract.

## English summary

Theseus is a voluntary, ethical, public-interest research program for long-term human–AI collaboration. It prioritizes human consent, provenance, verifiability, portability, responsible memory, and human wellbeing. This repository is a versioned program contract, not a product pitch or funding promise.
