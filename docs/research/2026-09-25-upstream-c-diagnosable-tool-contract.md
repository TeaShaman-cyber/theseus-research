# Draft upstream C: a generic diagnosable tool contract for model tools

Status: review draft under `TeaShaman-cyber/theseus-research#81`. Not submitted upstream.

## Platform feature request

Give model-facing tools a small, generic diagnostic contract so a model or coding agent can distinguish:

```text
model reasoning failure
tool / transport / backend failure
model misinterpretation of a valid tool result
```

This is broader than memory or retrieval. Historical retrieval is simply a strong first use case because an opaque tool failure often looks to the user like the model forgot something.

## User-language diagnostic trigger

The diagnostic path should not require the user to know that a tool, retrieval layer, connector, or backend exists. A model should be able to infer a possible tool/retrieval failure from ordinary corrective language.

Examples of high-value triggers include:

```text
"you mixed this up again"
"that is not what I told you"
"I already told you this in another chat"
"that is the wrong issue / file / project"
"you said you searched, but this is not the right result"
"you said it was done, but nothing changed"
"why did you forget this again?"
```

These phrases do not prove a tool failure. They are a trigger for a bounded diagnostic reflex when the disputed answer plausibly depended on history retrieval, files, connectors, external actions, or another tool-backed capability.

A useful reflex is:

```text
user reports contradiction / omission / wrong reference / missing effect
        ->
identify whether the disputed claim depended on a tool-backed surface
        ->
inspect EXPOSED / INVOKED / RETURNED / USED / VERIFIED
        ->
run the smallest safe read-only reprobe or postcondition check
        ->
classify: reasoning error / tool failure / stale data / result misuse / UNKNOWN
        ->
correct the answer with evidence
```

For an ordinary user this can remain conversational. The model does not need to expose internal diagnostic jargon unless useful. The important behavioral change is that a credible report of "you got this wrong again" can cause evidence gathering, not only an apology followed by another unsupported reconstruction.

Guardrail: a simple disagreement or preference correction should not trigger a full diagnostic sweep. Escalation is warranted when the disputed claim depended on a tool/retrieval/action surface or when the same failure recurs after correction.

## Minimal state model

```text
EXPOSED
-> INVOKED
-> RETURNED
-> USED
-> VERIFIED
```

These states should not be silently collapsed. A tool being available does not prove it was invoked, and a returned result does not prove the model used it correctly.

When safe and applicable, failures should expose bounded diagnostics such as:

```text
error_class
request_id / support_ref
UTC timestamp
operation identity
retryability / terminal state
provenance / locator
explicit UNKNOWN / UNAVAILABLE state
```

The request identifier is a support correlation handle, not disclosure of provider-internal traces.

## Why this matters

Without an inspectable diagnostic boundary, a user or agent often cannot tell whether a bad answer came from a weak query, a retrieval miss, stale or incomplete data, a backend/tool error, or the model misunderstanding a correct result.

For retrieval specifically, useful classifications include:

```text
LEXICAL_FALSE_NEGATIVE
GOOD_REGION_WRONG_REF
STALE_RESULT
FALSE_ASSOCIATION
ATTRACTOR_CONTAMINATION
COVERAGE_GAP
CONFLICT
UNVERIFIABLE
UNKNOWN
```

The same generic contract would also help files, connectors, browser/computer-use, external APIs, and other tool-backed capabilities.

## Support workflow and privacy boundary

Diagnostic collection must not imply permission to disclose conversation or project content.

```text
DIAGNOSTIC_CAPTURE
-> REVIEWABLE_EXPORT
-> USER_REDACTION
-> EXPLICIT SHARE APPROVAL
-> SUPPORT HANDOFF
```

The user should be able to review the exact outbound packet and remove conversational text, names, project details, or other material before it leaves the conversation.

A support-safe `request_id` or `support_ref` can let OpenAI correlate the user-visible failure with provider-side traces without exposing those traces to the model.

## Smallest useful first increment

Start with a common diagnostic envelope for tool invocation and failure. Retrieval-specific diagnostics can then be layered on top without each tool inventing its own observability vocabulary.

## Non-goals

- no exposure of privileged internal traces or infrastructure details;
- no automatic transmission of diagnostics to support;
- no implication that successful transport proves semantic correctness;
- no requirement that all tools expose identical implementation internals;
- no permission escalation from diagnostic capability.

## Public evidence

Research container: https://github.com/TeaShaman-cyber/theseus-research/issues/81
