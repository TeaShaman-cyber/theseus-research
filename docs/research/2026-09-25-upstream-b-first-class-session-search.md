# Draft upstream B: first-class read-only Session Search for models

Status: review draft under `TeaShaman-cyber/theseus-research#81`. Not submitted upstream.

## Feature request

Expose historical conversation search to the model as a bounded read-only tool, separate from Memory synthesis.

OpenAI already documents human-facing sidebar search across chats and chat messages, including archived chats, and separately documents Reference chat history as a source of relevant context from past conversations.

What is missing from the public product contract is an inspectable model-facing historical-search interface with explicit query, scope, provenance, and uncertainty semantics.

A minimal conceptual tool could accept:

```text
query
optional time range
optional conversation / project scope
result limit
optional retrieval mode
```

and return:

```text
conversation identity
message / fragment locator
timestamp
role
matching excerpt
retrieval mode
coverage / uncertainty state when known
```

## Keep Session Search separate from Memory

```text
Memory:
what context is useful to carry forward?

Session Search:
what was actually said in prior conversation evidence?
```

A synthesized memory does not need to preserve every historical detail if the underlying history remains explicitly searchable when exact reconstruction matters.

## A simple staged retrieval contract

The first version does not need a vector database or a complicated semantic-memory architecture.

```text
strict lexical search
        ->
optional broader recall
        ->
model inspection / reranking
```

Broader recall should remain typed as a candidate, not silently promoted into historical fact.

Useful states could include:

```text
STRICT_MATCH
RECALL_CANDIDATE
AMBIGUOUS
NO_RESULT
UNKNOWN_WITHIN_SEARCHED_HISTORY
```

A zero-result search should not imply that the conversation never happened unless the searched history is known to be complete for that claim.

## Reproducible evidence

The public Theseus Session Search prototype has concrete tests for these cases:

- adjacent wording: strict search misses, bounded broader recall surfaces the intended session;
- evidence split across several messages: message-local strict search misses, session-level recall recovers the session;
- broad contextual query: useful context is returned but remains candidate-only;
- alias-only wording: both strict search and recall can miss, so the result remains unknown rather than fabricated absence.

The implementation keeps source artifacts as historical evidence and treats its search index as a regeneratable projection.

## Non-goals

- no replacement of ChatGPT Memory;
- no assertion that retrieved historical statements are still true or currently authoritative;
- no requirement to expose proprietary ranking internals;
- no write access to conversation history;
- no claim that a search miss proves absence.

## Current OpenAI documentation

Chat/search surface: https://help.openai.com/en/articles/10056348-finding-your-chats-projects-and-files-in-chatgpt

Memory / Reference chat history: https://help.openai.com/en/articles/8590148-memory-in-chatgpt

## Public evidence

Research container: https://github.com/TeaShaman-cyber/theseus-research/issues/81

Session Search Lab: https://github.com/TeaShaman-cyber/theseus-session-search-lab

Recall issue: https://github.com/TeaShaman-cyber/theseus-session-search-lab/issues/20
