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
