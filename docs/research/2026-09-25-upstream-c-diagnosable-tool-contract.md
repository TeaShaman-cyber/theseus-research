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
