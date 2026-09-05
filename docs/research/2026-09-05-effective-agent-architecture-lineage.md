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

## 8. Provenance note

This document is a compact public synthesis. The private Session Search corpus remains evidence for the conversation-level reconstruction, while public GitHub issues and PRs remain the preferred durable references for the engineering contracts that were promoted from those discussions.

A Session Search miss is still `UNKNOWN`, not proof that a stronger historical formulation never occurred; the negative findings above mean only that the bounded 2026-09-05 reconstruction did not recover such evidence.
