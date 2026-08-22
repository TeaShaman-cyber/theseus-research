# AutoMem Resource and Helper-Model Evaluation

**Status:** research note · aggregate results published for public review
**Date:** 2026-08-22
**Languages:** English (international reference) · [Русский перевод](automem-resource-and-helper-evaluation-2026-08-22.ru.md)
**Scope:** local AutoMem resource reduction and bounded helper-model enrichment
**Related program:** [Theseus contract](../../README.md) · [Sadhana of Engineering](../methodology.md)

## Abstract

This note reports a bounded Theseus experiment with two goals:

1. reduce the local resource footprint of AutoMem's semantic memory;
2. make stored memories more useful to primary agents through a helper model,
   without giving that helper independent write or infrastructure authority.

The local result uses FastEmbed BGE-base at 768 dimensions instead of
BGE-large at 1024 dimensions. Retrieval quality did not regress in the tested
replay, while the API model footprint fell substantially. The helper experiment
selected Solar Pro4 as the first operational candidate because it was more
reliable on the actual AutoMem JSON protocol, even though Laguna S scored higher
on the small labelled semantic fixture.

These results are bounded evidence, not a universal model ranking or a claim
that AutoMem has replaced the active Hermes/Hindsight memory route.

## Research boundary

The experiment kept these routes separate:

```text
Hermes active memory route:    Hindsight
Local experimental profile:    AutoMem / Codex path
Cloud evaluation environment:  disposable Timeweb lab
```

No production Hindsight bank was used as a test corpus. No raw user memory,
credential, provider payload or backup archive is published here.

## Method

The work proceeded in stages:

1. record the local BGE-large baseline;
2. compare BGE-large and BGE-base on an isolated copy with fixed queries;
3. probe external embedding endpoints without changing the working collection;
4. compare helper candidates on protocol and labelled semantic fixtures;
5. implement an opt-in advisory enrichment layer for summary, tags and entities;
6. validate the layer in a disposable cloud worker and then in one local live
   canary;
7. preserve rollback and verify read-back/deletion postconditions.

The public aggregate fixture manifest is stored at
[`automem-resource-and-helper-evaluation-fixture-2026-08-22.json`](automem-resource-and-helper-evaluation-fixture-2026-08-22.json).
The original working fixture is not published because it contains
workflow-specific text; a neutral public rerun is a separate follow-up.

## Embedding results

The remote same-host comparison used the same graph and a fixed 100-query
replay:

| Variant | Recall@10 | MRR | NDCG@10 | API RAM | Mean latency | p95 |
|---|---:|---:|---:|---:|---:|---:|
| BGE-large / 1024d | 0.9100 | 0.7825 | 0.8130 | 2.57 GiB | 682.9 ms | 831.1 ms |
| BGE-base / 768d | 0.9200 | 0.7823 | 0.8152 | 979.6 MiB | 788.7 ms | 927.2 ms |

A second BGE-base replay reproduced the quality metrics. The result is a
resource/quality tradeoff: BGE-base saves roughly 62% of the API model
footprint and is somewhat slower in this test. It is not a proof that it wins
on every corpus.

The local cutover created a separate `memories_base` collection, re-embedded
the graph, and retained the original 1024d collection and volume backups. The
local health endpoint reports a filtered visible count; direct graph/vector ID
comparison found 401/401 IDs with no orphan IDs. The active local runtime now
uses 768d and remains healthy.

## Helper-model results

### Protocol and semantic quality are different questions

The early 14-case labelled fixture returned 100% for both Solar Pro4 and Laguna
S. It was intentionally easy and is superseded by the broader 21-case fixture:

| Model | Valid JSON | Correct labels | Accuracy | Mean latency | p95 |
|---|---:|---:|---:|---:|---:|
| Laguna S | 21/21 | 17/21 | **81.0%** | 3.00 s | 4.97 s |
| Solar Pro4 | 21/21 | 15/21 | 71.4% | 3.59 s | 5.69 s |
| Hy3 | 21/21 | 13/21 | 61.9% | 3.82 s | 5.85 s |

Every call returned valid JSON. Laguna S won this bounded semantic fixture.

The real AutoMem dry-run produced a different operational result:

```text
Solar Pro4, 128 tokens:  10/10, parser errors 0
Laguna S, 256 tokens:    10/10, parser errors 1
Laguna S, 512 tokens:    10/10, parser errors 1
```

Therefore Solar Pro4 was chosen as the first operational helper. This is not a
claim that Solar is semantically superior; it is a reliability-first decision
for a memory pipeline where malformed output must not silently become a normal
memory type.

### Advisory enrichment

The helper receives memory text and returns structured suggestions for:

```text
summary;
normalized tags;
grounded entities: tools, projects, people, concepts, organizations.
```

AutoMem validates the JSON, requires entity values to occur in the original
text, corrects conflicting categories, and applies the accepted result itself.
If the provider fails or returns invalid JSON, the existing rule-based path
remains usable. The helper cannot directly write FalkorDB/Qdrant, repositories
or infrastructure.

A cloud A/B using the same memory text showed that rules-only enrichment placed
`Laguna S` and `Timeweb Lab` in `people`. The helper-assisted path corrected them
to `tools` and `projects`, removed the incorrect `people` entries, preserved
`AutoMem` as an organization, and produced a shorter uncertainty-preserving
summary.

A ten-memory cloud canary then produced:

```text
processed:            10/10
helper metadata:      10/10
summary:              10/10
errors:                0
exact-ID cleanup:     10/10
```

The local profile explicitly enables the same advisory path with:

```text
ENRICHMENT_LLM_ENABLED=true
ENRICHMENT_LLM_MODEL=upstage/solar-pro4:free
ENRICHMENT_LLM_MAX_TOKENS=256
```

One local live canary completed enrichment, read-back and exact-ID deletion
(`HTTP 200`, followed by `HTTP 404`). The focused regression subset reported
`210 passed, 1 skipped, 0 failed`.

## External embedding routes

Several external routes were checked separately from the local cutover:

```text
Voyage-4 family:
  live 1024d route; first 200M tokens per account free, not free forever.

OpenRouter LFM embedding:
  live 1024d free route observed; account/model limits are variable.

BotHub bge-m3:
  live 1024d route; free status not confirmed.

Groq and Nous embeddings:
  no usable route with the tested credentials.

Ollama:
  native AutoMem path, but not installed/running in this workstation state.

Hugging Face / Cloudflare / Google / Jina:
  adapter or quota/region work remained unresolved.
```

Matching dimensions do not make embeddings interchangeable. Any external
switch requires a full isolated re-embed and a new recall comparison.

## Engineering lessons

- A hard-coded 50-token classification budget is too small for many
  reasoning/free models. Classification and enrichment now use separate
  configurable budgets.
- A VLESS HAPP subscription is not an HTTP proxy URL. The reversible cloud path
  is subscription → VLESS profile → temporary sing-box → private Docker network.
- Provider reachability, JSON protocol compatibility and semantic quality must be
  measured as separate layers.
- Backup, separate vector collection, direct ID comparison and read-back are
  more important than a successful container health check alone.
- The helper should advise and structure; the parent memory service retains
  authority to apply, reject or later correct the result.

## Related work and upstream credit

This work was informed by public AutoMem and Hindsight documentation, source and
maintainer discussions. These references are prior art, not endorsements of
Theseus or claims that maintainers participated in this experiment:

- AutoMem custom OpenAI-compatible base URL:
  [verygoodplugins/automem#96](https://github.com/verygoodplugins/automem/issues/96)
- AutoMem summary-first recall:
  [verygoodplugins/automem#180](https://github.com/verygoodplugins/automem/issues/180)
- AutoMem enrichment quota circuit breaker proposal:
  [verygoodplugins/automem#222](https://github.com/verygoodplugins/automem/issues/222)
- Hindsight model-specific token parameter handling:
  [vectorize-io/hindsight#978](https://github.com/vectorize-io/hindsight/issues/978)
- Hindsight structured-output and malformed-JSON discussions:
  [#1002](https://github.com/vectorize-io/hindsight/issues/1002),
  [#2668](https://github.com/vectorize-io/hindsight/issues/2668),
  [#3683](https://github.com/vectorize-io/hindsight/issues/3683)
- Hindsight native multi-LLM implementation:
  [`multi_llm.py`](https://github.com/vectorize-io/hindsight/blob/main/hindsight-api-slim/hindsight_api/engine/multi_llm.py)
- AutoMem upstream configuration and implementation:
  [`docs/ENVIRONMENT_VARIABLES.md`](https://github.com/verygoodplugins/automem/blob/main/docs/ENVIRONMENT_VARIABLES.md),
  [`automem/config.py`](https://github.com/verygoodplugins/automem/blob/main/automem/config.py)

## Limitations and next work

The study does not establish a universal best helper model, a permanent free
provider, or a production Hermes provider switch. Query rewriting and a
separate reranker were not implemented. The cloud VPS and HAPP route were
temporary research plumbing. A future public rerun should use a neutralized
fixture whose complete text can be published without exposing workflow-specific
or personal context.

## Data and review statement

Only aggregate metrics, synthetic examples, public upstream links and sanitized
method descriptions are published. No API keys, HAPP subscription, raw private
memory, backup archive or full session transcript is included. Review is
welcome on the method, evidence boundaries, reproducibility and limitations.
