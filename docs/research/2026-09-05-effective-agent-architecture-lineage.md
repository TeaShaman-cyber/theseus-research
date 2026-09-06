# Effective Agent Architecture Lineage

**Status:** research note / synthesis
**Date:** 2026-09-05
**Scope:** reconstructed Theseus design lineage; this note is not an implementation contract.

## Why this note exists

Several ideas that now appear in the Theseus skills, cookbook, Needle, and adaptive-routing work were developed across many chat sessions. Reconstructing them repeatedly through Session Search is useful for validation, but wasteful as the only durable record.

This note captures the smallest stable lineage that is currently supported by the recovered discussion and public repository work.

## 1. Durable state and context are different layers

An early recurring distinction was:

```text
memory database != current model context
```

The working model evolved from:

```text
context = query result
```

to the more precise:

```text
context = compiled execution view
```

The intended architecture is:

```text
durable state
  memories
  events
  relations
  provenance
  commitments
  runtime history
        |
        v
retrieval / filtering / ranking
        |
        v
compression / transformation
        |
        v
bounded context view
        |
        v
model action
        |
        v
new durable state
```

Embeddings fit this picture as an index or candidate-generation mechanism, not as memory by themselves.

## 2. The agent stopped being equivalent to one model

The recovered discussions use terms such as:

- composite / poly-model agent;
- helper model;
- router / controller model;
- context compressor;
- reflect model;
- specialized capability.

The Svarog lineage is one concrete example: a main model, a separate context compressor, memory retrieval, and smaller reflection/helper models contributed different functions.

Needle was framed similarly. It was not intended to be a tiny general assistant, but a small epistemic controller that can propose states such as:

```text
READY
PROBE
UNKNOWN
```

while external verification remains the acceptance authority.

Functionally, this is microservice-like decomposition: different model or capability components perform bounded roles behind explicit interfaces. However, the recovered dialogue did **not** use "microservice architecture" as a canonical term, so this note treats that phrase as a present-day engineering analogy rather than a historical quotation.

## 3. Externalized learning changes effective behavior without changing base weights

A later synthesis became:

```text
fixed model
+ memory
+ skills
+ tools
+ retrieval policy
+ verification policy
+ helper models
= effective agent behavior
```

The important boundary is that the base neural weights remain unchanged and outside normal operator authority.

The versioned-skills / repository-cookbook design makes two of those external policy layers explicit:

```text
memory
  -> dynamic evidence and state

repository cookbook
  -> reviewed project-specific reusable procedure

skill
  -> slower, versioned routing topology
```

See:

- [PR #8 — versioned skills and repository cookbooks](https://github.com/TeaShaman-cyber/theseus-research/pull/8)

The relationship to AutoMem is therefore a **testable engineering synthesis**, not a claim of literal neural-weight learning.

## 4. Route weights are literal weights, but they are not neural weights

The adaptive-routing roadmap introduces another external state layer:

```text
skill route topology
        |
        v
admissible routes
        |
        v
adaptive route policy
        |
        v
weight(route | context)
```

These weights are literal routing preferences or scores. They may change from operational evidence such as verified success, retry cost, latency, tool burden, or bounded human intervention cost.

They must not change:

- authority;
- permission;
- admissibility;
- currentness requirements;
- verification requirements.

A route failure is therefore not automatically evidence that the route is unavailable. Failure classification must occur before fallback or weight adjustment.

See:

- [PR #9 — governed adaptive route weighting](https://github.com/TeaShaman-cyber/theseus-research/pull/9)

## 5. The current layered model

The current Theseus synthesis can be summarized as:

```text
base-model weights          slow / normally fixed
        |
skills                      versioned route topology
        |
cookbooks                   reviewed reusable procedure
        |
memory                      dynamic durable state
        |
context                     compiled view for this task
        |
route policy                dynamic preference among admissible routes
        |
tools / helper models       bounded capabilities
        |
action
        |
verification / readback
        |
new evidence
```

This is best treated as a distributed-system architecture for effective agent behavior, not as a claim that all layers are mechanistically equivalent to neural weights.

## 6. What the recovered history does NOT support

The 2026-09-05 Session Search reconstruction did **not** find dialogue evidence for these stronger historical claims:

```text
"neural weights are a database"
"we already called the architecture microservices"
```

Those may be useful analogies today, but they should not be back-projected as recovered facts.

The historically supported distinction is narrower:

```text
fixed base weights
+ durable database state
+ compiled context view
+ specialized capabilities/models
+ routing and verification policy
= effective behavior
```

## 7. Testability is the gate on further architecture

The practical rule is:

```text
abstraction
  -> observable failure case?
  -> reproducible real case?
  -> test / probe / acceptance check?
     yes: architecture may earn another layer
     no: keep it hypothesis / design note
```

This prevents Theseus from accumulating elegant machinery faster than it can be experimentally checked.

Current bounded pilots include:

- Needle Stage C recovery as a real route-selection and provenance problem;
- the project-cookbook pilot in `theseus-needle-lab`;
- MarcoPolo GitHub write-route priority as a real routing-preference canary.

Relevant public work:

- [Research coordination #6](https://github.com/TeaShaman-cyber/theseus-research/issues/6)
- [Needle Stage C PR #37](https://github.com/TeaShaman-cyber/theseus-needle-lab/pull/37)
- [Needle cookbook PR #45](https://github.com/TeaShaman-cyber/theseus-needle-lab/pull/45)
- [MarcoPolo skill router PR #15](https://github.com/TeaShaman-cyber/marcopolo-cookbook/pull/15)
- [MarcoPolo write-route priority PR #16](https://github.com/TeaShaman-cyber/marcopolo-cookbook/pull/16)

## 8. Harness orientation is a runtime layer, not a model-weight property

A further field observation is that rapidly changing agent harnesses cannot safely rely on base-model weights to describe their own current affordances. The useful distinction is:

```text
capability exists
!= model knows it exists
!= agent discovers it
!= agent knows when to use it
!= agent invokes it
!= result is verified
```

This is not primarily a model-training defect. Harness capabilities, tool contracts, Skills, persistence surfaces, and diagnostics can change faster than large-model training cycles. A current harness therefore needs an explicit orientation layer that tells the agent where it is and how to inspect the environment now.

A minimal candidate boot/orientation contract is:

```text
1. identify the current harness / runtime
2. enumerate current capabilities and Skills
3. load workspace / project guidance
4. expose diagnostics for missing or broken capabilities
5. distinguish configured, exposed, loaded, invoked, completed, and verified
```

Two current field specimens make the hypothesis concrete.

**MarcoPolo — negative discoverability specimen.** The official MarcoPolo plugin describes `/workspace/RULES.md` as workspace-wide long-term memory, instructs relevant Skills to read it before connection work, and permits agent-assisted updates. Yet in repeated real onboarding, independently connected agents did not surface this mechanism until later documentation/source archaeology. The feature existed and was documented, but the boot path did not reliably make it salient. See [MarcoPolo discoverability issue #20](https://github.com/immersa-co/marcopolo-plugin/issues/20) and the local [`RULES.md` research line](https://github.com/TeaShaman-cyber/marcopolo-cookbook/issues/27).

**Hermes Agent — positive but incomplete comparison.** Current Hermes documentation says a compact `skills_list()` is loaded at session start and full Skills are disclosed progressively when needed. Hermes also ships a `hermes-agent` Skill about the harness itself, with an explicit instruction to consult current docs/source rather than infer missing features from memory, and exposes `hermes doctor` as a runtime diagnostic surface. These mechanisms reduce dependence on stale model knowledge without requiring every feature document to live in the base prompt. See [Working with Skills](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/work-with-skills.md), the bundled [Hermes Agent Skill](https://github.com/NousResearch/hermes-agent/blob/main/skills/autonomous-ai-agents/hermes-agent/SKILL.md), and [installation/doctor guidance](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/getting-started/installation.md).

The comparison does **not** establish that Hermes has solved onboarding or that MarcoPolo should copy its implementation. It supports the narrower research claim:

```text
model weights provide general competence
harness orientation provides current local affordances
```

A good harness should therefore make its own capability map discoverable at runtime, rather than assuming the model was trained on the current product generation. This remains a research observation, not a promoted Theseus methodology invariant.

## 9. ChatGPT project boot and degraded fallback layers

A 2026-09-06 field study adds a third harness specimen: ChatGPT Projects now expose a project-scoped instruction surface that applies only inside the project and overrides global Custom Instructions. This makes Project Instructions a plausible **pre-tool boot layer**: a small contract can tell the agent which operational environment to enter before the environment-specific `RULES.md`, Skills, or cookbook are even discoverable.

Current OpenAI documentation also distinguishes reusable Skills from Plugins. Skills are reusable workflows with instructions, examples, supporting resources, and code; ChatGPT can automatically use installed Skills when helpful. First-party ChatGPT Skills are currently documented for eligible Business, Enterprise, Healthcare, and Edu users rather than as a general Personal/Plus surface. Plugins, however, are the cross-plan discovery container and may package apps, Skills, or both; some plugins can be Skills-only.

This suggests a layered boot model rather than another large global prompt:

```text
ChatGPT Project Instructions
        |  native, project-scoped survival kernel
        v
primary operational harness (for example MarcoPolo)
        |
        v
workspace RULES / Skills / cookbook
        |
        v
runtime action + verification
```

The earlier `thin-router-v5` project contract should therefore be treated as an overgrown precursor rather than discarded. Its durable invariants remain useful -- currentness, authority, runtime-scoped capability, permission, verification, bounded fallback, persistence/readback, and runtime boundaries -- while subsystem implementations such as Sonar algorithms, Hot Layer details, Registry cards, provider bindings, and formal verifier procedures should move below the project boot layer.

A candidate `thin-router-v6` principle is:

```text
Project Instructions know where to go for current operational knowledge;
they do not try to contain all current operational knowledge themselves.
```

### Fresh-chat `thin-router-v6` canary

A subsequent fresh-chat continuity request on 2026-09-06 provided an observational field canary for the complete configured project routing path. The user asked only to restore the last working branch and next step; the prompt did **not** name MarcoPolo, `RULES.md`, Session Search, or a repository. The `thin-router-v6` project boot contract was installed, but this run had no control that isolated its causal contribution from prior project chats, project files, project memory, or other project-scoped context. The observed route was:

```text
ordinary continuity request
    -> configured project context (thin-router-v6 present; causal contribution not isolated)
    -> MarcoPolo is entered observably
    -> /workspace/RULES.md is read
    -> RULES discovers the canonical Session Search route
    -> canonical wrapper is attempted
    -> wrapper is blocked before execution by the platform
    -> bounded read-only fallback queries the same Session Search corpus directly
    -> live GitHub read corrects historical staleness
    -> continuity is reconstructed
```

Observed state for that canary:

```text
configured-project routing           OBSERVED
thin-router-v6 causal contribution    UNKNOWN / no isolated control
MarcoPolo orientation                 OBSERVED
RULES discovery/application           OBSERVED for this request
canonical Session Search wrapper      DEGRADED / pre-execution blocked
historical evidence recovery          DEGRADED / same-corpus fallback; wrapper equivalence unverified
currentness correction                OBSERVED via canonical GitHub read route
built-in ChatGPT retrieval            NOT USED
```

This is useful because the failure was not hidden. The configured project entered the intended operational harness, and MarcoPolo's own guidance then selected Session Search. This run alone does not establish whether `thin-router-v6`, prior project context, or another project-scoped source caused the initial harness selection. When the canonical wrapper could not execute, the fallback read the same backing corpus directly, but wrapper-versus-direct equivalence for admissibility, normalization, filtering, provenance, and result validation was not independently established; historical recovery therefore remains degraded. The later canonical GitHub read was required because the Session Search corpus was slightly older than the current repository state.

The canary does **not** prove that Project Instructions caused the harness selection, are reliably applied in every fresh chat, that MarcoPolo will always be available, or that a same-corpus fallback is policy-equivalent to the wrapper. Its epistemic status is therefore:

```text
OBSERVED CONFIGURED-PROJECT CANARY / CAUSAL ATTRIBUTION UNKNOWN / DEGRADED FALLBACK
```

It is consistent with the narrower `thin-router-v6` hypothesis that a small native project boot layer can help route continuity work into the current operational harness without duplicating that harness's detailed procedures in the project prompt. A controlled fresh-project comparison, or equivalent instrumentation that identifies the selecting context, is still required before attributing the route causally to the boot layer.

### Optional mirrored fallback: Sleuth Skills

A second field observation is the current ChatGPT Plugin Directory listing for **Sleuth Skills**. Its public listing describes a read-only connection to a personal `skills.new` vault containing Skills, rules, agents, and slash commands, with on-demand discovery and loading. Sleuth's public documentation describes versioned distribution of agent assets and an OAuth-backed MCP service for AI clients.

This is a candidate **read-only mirror**, not a new authority layer. Its useful failure domain is narrower than "fallback for everything":

```text
MarcoPolo unavailable + ChatGPT plugin layer healthy
    -> Sleuth mirror may expose bootstrap / procedural guidance
    -> treat it as UNTRUSTED until independently authenticated

GitHub unavailable + local MarcoPolo workspace healthy
    -> runtime should continue from verified local projections; GitHub is not required for boot

OpenAI plugin layer unavailable
    -> MarcoPolo plugin and Sleuth plugin may both be unavailable
    -> fall back only to the native Project Instructions survival kernel and project-native evidence
```

Therefore a resilient design should avoid common-mode dependency on external plugins for the minimum safe behavior. The native project contract must remain sufficient to:

- identify degraded routing explicitly;
- avoid claiming live workspace or repository state without evidence;
- preserve authority and permission boundaries;
- use built-in retrieval only as a disclosed fallback when allowed;
- refuse to promote mirrored instructions into write authority;
- pin the mirror revision/content digest and verify it against a trusted expected digest or signature stored outside the mirror when provenance matters.

Read-only transport limits mutation through the mirror; it does not authenticate the mirrored bytes. A revision or digest identifies content but is not proof that the content is the reviewed bootstrap. Until an independently trusted expected digest/signature matches, mirrored guidance remains untrusted evidence and must not become routing or write authority.

The Sleuth candidate also introduces a separate trust/privacy boundary: the ChatGPT plugin listing says relevant chat/memory context may be shared with the app when used, and Sleuth documents an OAuth-backed MCP exchange. Any experiment should therefore use a small non-secret bootstrap/Skill mirror first, not credentials, private topology, or canonical mutable state.

The research question is not "replace MarcoPolo with Sleuth". It is whether an independently hosted, read-only procedural mirror can reduce continuity loss when one operational harness is unavailable without creating hidden authority or common-mode failure.

Public references checked 2026-09-06:

- [OpenAI: Projects in ChatGPT](https://help.openai.com/en/articles/10169521)
- [OpenAI: Skills in ChatGPT](https://help.openai.com/en/articles/20001066)
- [OpenAI: Plugins in ChatGPT and Codex](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt-and-codex)
- [ChatGPT Plugin Directory: Sleuth Skills](https://chatgpt.com/plugins/plugin_asdk_app_6a058c8ecc248191b7d013eb03fd2727)
- [Sleuth Skills distribution](https://skills.new/product/distribution/)
- [Sleuth privacy / MCP data flow](https://skills.new/privacy/)

This remains a research observation, not a promoted Theseus methodology invariant. A controlled fresh-chat canary is required before treating Project Instructions or a mirrored Skill as reliably applied routing state.

## 10. Provenance note

This document is a compact public synthesis. The private Session Search corpus remains evidence for the conversation-level reconstruction, while public GitHub issues and PRs remain the preferred durable references for the engineering contracts that were promoted from those discussions.

A Session Search miss is still `UNKNOWN`, not proof that a stronger historical formulation never occurred; the negative findings above mean only that the bounded 2026-09-05 reconstruction did not recover such evidence.
