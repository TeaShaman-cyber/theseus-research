# Draft upstream A: model retrieval skill for existing historical retrieval

Status: review draft under `TeaShaman-cyber/theseus-research#81`. Not submitted upstream.

## Feature request

When ChatGPT has access to relevant context from past conversations, give the model a small reusable retrieval skill for querying that surface deliberately instead of relying on one opaque retrieval attempt.

The request is not for access to private retrieval internals and not for a new memory backend. It is a query and verification discipline that can work with an opaque retrieval service.

A useful bounded first pass is:

```text
1. literal/name probe
2. functional rephrase that omits the headline term
3. distinctive relation or phrase probe
```

Escalate only when those are insufficient. A larger bounded pass can add temporal, correction, falsifier, source, and epistemic-boundary probes.

The model should preserve distinctions such as:

```text
search miss != historical absence
semantic-region hit != exact entity/reference identification
repeated retrieval of one fragment != independent corroboration
retrieved historical context != current authority
recovering the attractor != recovering its later corrections and limits
```

If materially different formulations keep returning the same fragment without new provenance, stop probing rather than treating repetition as stronger evidence.

## Method lineage

This proposal is not an ad-hoc prompt recipe. It is a condensed form of an existing Sonar research line preserved in `theseus-research#11`.

The lineage is:

```text
historical Theseus Sonar / semantic-echolocation discipline
  -> controlled multi-probe retrieval
  -> calibrated against independently inspectable Session Search targets
  -> extended with literal / semantic / functional / relational / negative-control probes
  -> extended again with correction / falsifier / epistemic-boundary probes
```

The older Sonar protocol already required multiple controlled formulations, at least one functional/semantic probe that did not repeat the planted canary name, explicit source/conflict/gap recording, and `UNKNOWN` on retrieval failure rather than absence.

Issue #11 then calibrated that method against known historical episodes from Session Search. A Library-of-Congress fixture showed that functional and relational probes could recover the same target without repeating its headline entity. A later historical calibration corpus with strong semantic attractors and later corrections supplied the next refinement: recovering a vivid attractor is weaker than recovering the surrounding corrections, counterexamples, epistemic limits, and temporal drift.

So the proposed skill is a productized retrieval discipline derived from observed experiments, not a claim that this is the hidden OpenAI retrieval algorithm.

## Why

In a live reconstruction exercise, broad/default retrieval found the correct semantic area for an older heartbeat/liveness discussion but attached one concrete repository/issue reference incorrectly. Independent repository readback found the exact historical source elsewhere.

```text
SEMANTIC_REGION = GOOD
ENTITY_LOCALIZATION = WRONG
```

The retrieval was neither fully correct nor simply a miss. A model-facing retrieval skill should recognize partial success and verify exact locators before using them as facts.

A separate calibrated case showed that functional and relational probes could recover a known historical target even when the functional query omitted its headline entity name. Controlled reformulation can therefore improve recall without requiring knowledge of the hidden backend.

## Smallest useful implementation

This could initially be system guidance or a reusable built-in skill rather than a new API. Important behaviors:

- use several bounded, materially different probes when historical continuity matters;
- preserve provenance, conflicts, temporal drift, and uncertainty;
- distinguish recurrence from corroboration;
- treat misses conservatively;
- verify exact external references when the final claim depends on them.

## Non-goals

- no reverse engineering of private retrieval infrastructure;
- no claim that one retrieval backend is stable across all ChatGPT runtimes;
- no requirement to run multiple probes for ordinary low-stakes queries;
- no replacement for Memory;
- no promotion of retrieved historical material into current authority.

## Public evidence

Research container: https://github.com/TeaShaman-cyber/theseus-research/issues/81

Calibrated retrieval research: https://github.com/TeaShaman-cyber/theseus-research/issues/11
