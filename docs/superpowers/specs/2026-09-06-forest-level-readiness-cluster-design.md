# Forest-Level Readiness for the Current Theseus Cluster — Design v0.1

Status: **DESIGN ONLY / NO IMPLEMENTATION AUTHORIZED**  
Research issue: `TeaShaman-cyber/theseus-research#12`  
Date: 2026-09-06

## 1. Problem

Several Theseus lines now interact:

- cookbook/query routing changes task context;
- memory-provider work changes recalled evidence/context;
- Needle can measure behavioral effects of those inputs;
- program governance decides what may become accepted authority.

Local tests and PR reviews answer whether one component is healthy in isolation. They do not necessarily answer whether the **next cross-project transition** is safe while several candidates are still moving.

Working hypothesis:

> `local green` does not necessarily imply `forest green`.

v0.1 tests whether a tiny forest-level readiness model makes those transitions safer and clearer without creating new infrastructure.

## 2. Feynman statement

```text
Projects are trees; the interacting cluster is a small forest.
Before crossing project or authority boundaries, ask:
- what depends on what?
- what is only evidence?
- what can influence behavior?
- who can actually change authority?
Then classify the next step as SAFE, HOLD, or BLOCKED.
```

If this requires a graph database, policy engine, large ontology, or mandatory ritual for ordinary local PRs, v0.1 has failed.

## 3. Scope

Only the currently interacting cluster is modeled:

- `G` — Theseus research governance and promotion/authority boundaries;
- `C` — cookbook/query-router candidate;
- `M` — memory-provider candidate;
- `N` — Needle integration canary;
- `A` — accepted baseline(s) used to interpret candidates.

`A` is a role, not one universal SHA.

Out of scope:

- the full Theseus portfolio;
- unrelated observatory/research lines;
- adaptive route weighting;
- a universal project registry replacement;
- automated promotion, merge blocking, or governance.

Expansion is allowed only after this bounded cluster demonstrates added decision value.

## 4. Relation vocabulary

Use exactly four semantic relation types.

### `DEPENDS_ON`

The source/state is required to interpret a proposed step.

```text
N DEPENDS_ON C
N DEPENDS_ON M
```

Dependency is not authority.

### `PROVIDES_EVIDENCE_FOR`

One line produces observations relevant to evaluating another.

```text
N PROVIDES_EVIDENCE_FOR C
N PROVIDES_EVIDENCE_FOR M
```

Evidence may support a promotion decision; it does not perform that decision.

### `CAN_INFLUENCE`

One line can alter another line's behavior or measurement.

```text
C CAN_INFLUENCE N
M CAN_INFLUENCE N
```

This relation exposes confounders and feedback loops.

### `GRANTS_AUTHORITY`

An explicit transition changes what is accepted as operational authority.

The intended path is:

```text
candidate / experiment evidence
        -> review
        -> governance evaluation
        -> explicit human acceptance
        -> accepted baseline
```

Candidate components and experiments do not grant authority to each other automatically.

Core invariant:

```text
evidence != authority
dependency != authority
observed influence != validation
```

## 5. Minimal system map

```text
                 G
          research governance
             /    |    \
            C     M     N
             \    |    /
                  A
           accepted baseline
```

Important directions:

```text
C --CAN_INFLUENCE------> N
M --CAN_INFLUENCE------> N
N --PROVIDES_EVIDENCE--> G
G + human acceptance --> A

N --X GRANTS_AUTHORITY-> A
C --X GRANTS_AUTHORITY-> M
M --X GRANTS_AUTHORITY-> C
```

The forbidden authority shortcuts are the central safety property.

## 6. Feedback-loop risk

A normal research loop is acceptable:

```text
candidate
  -> influences experiment
  -> experiment produces evidence
  -> evidence informs evaluation
```

It becomes unsafe when evidence silently becomes authority:

```text
candidate
  -> favorable experiment result
  -> automatic promotion
  -> changed authority
  -> next experiment
```

Therefore evidence-to-authority promotion remains a separate governance event with explicit human acceptance.

## 7. Readiness states

Readiness belongs to a **specific proposed cross-project step**, not to a repository forever.

### `SAFE`

A step is `SAFE` only when:

1. dependent executable inputs have immutable identities;
2. candidate state, evidence, and accepted authority are distinguishable;
3. the measurement boundary supports the intended claim;
4. no unresolved blocker can materially change result interpretation;
5. rollback preserves accepted baseline and evidence.

Feynman form: inputs known, authority clear, effect interpretable, blockers cleared, safe way back.

### `HOLD`

Local work may continue, but the cross-project transition waits for a concrete condition.

Typical reasons:

- moving dependency candidate;
- incomplete review;
- ambiguous baseline;
- unfrozen executable input;
- incomplete measurement contract;
- unsettled parent governance contract.

`HOLD` means **not yet**, not failure.

### `BLOCKED`

The route itself conflicts with the current safety/epistemic model.

Examples:

- experiment evidence directly changes accepted authority;
- a component changes the measurement and defines its own success without independent control;
- the experiment cannot separate causes required by the intended claim;
- rollback would destroy accepted baseline or audit evidence.

Waiting does not turn `BLOCKED` into `SAFE`; the route/design must change.

## 8. Forest-level stop conditions

1. **Evidence/authority collapse** — if they cannot be distinguished -> `BLOCKED`.
2. **Moving interpretive dependency** — if a changing candidate can alter experiment interpretation -> `HOLD`.
3. **Self-judging measurement** — if a component changes and judges its own measurement without independent control -> `BLOCKED`.
4. **Unreconstructable input** — if exact executable inputs cannot be reconstructed -> `HOLD`.
5. **Destructive rollback** — if rollback destroys evidence or accepted baseline -> `BLOCKED`.
6. **Local/system conflict** — if local PASS conflicts with a parent/system contract, the system contract governs the cross-project step.

Operational summary:

```text
local green != forest green
```

## 9. Trigger boundary

Ask one question:

> Does this proposed step cross a project, experiment, evidence, or authority boundary?

If **no** -> normal local workflow.

If **yes** -> evaluate the transition with this readiness model.

Examples:

```text
fix bool validation inside context_router.py
-> local workflow

run Needle using cookbook + memory candidates
-> forest-level check

promote a canary result into accepted guidance
-> forest-level check
```

## 10. Current-cluster snapshot

This dated snapshot validates the model. It is **not a registry or source of authority**.

Snapshot date: **2026-09-06**.

### G — governance candidate

`TeaShaman-cyber/theseus-research#8`  
Observed head: `4ebaae08fa15c4c7e77b1db7879186b7d3d78056`

State for treating this candidate as settled cross-project authority: **HOLD**.

Reason:

- design remains unmerged;
- fresh review still questions exact human-acceptance verification and invalidation/discovery behavior.

Only allowed next action:

```text
finish/review the governance contract itself;
do not treat candidate design as active authority.
```

### C — cookbook/query-router candidate

`TeaShaman-cyber/marcopolo-cookbook#25`  
Observed head: `bd3c6d70e8c7522a6d91c0ad1921624dfcd29c59`

State for using C as a frozen canary input: **HOLD**.

Reason:

- fresh review still has bounded correctness findings affecting exact compiled context/classification/budget behavior.

Only allowed next action:

```text
close bounded review findings;
run full gate;
request exact-head review;
then reassess.
```

### M — memory-provider candidate

`TeaShaman-cyber/marcopolo-cookbook#20`  
Observed head: `05bde60d5571b15103d3e0830073e0c4bd18b5d3`

State for using M as a frozen canary input: **HOLD**.

Reason:

- fresh review still has admission/persistence findings that can alter what canonical bytes are accepted, retained, or reconstructed.

Only allowed next action:

```text
close bounded adapter-contract findings;
verify exact-head behavior;
then reassess.
```

### N — Needle integration canary

`TeaShaman-cyber/theseus-needle-lab#46`

State for execution: **HOLD**.

Reason:

- C and M are not frozen inputs;
- the exact Needle runtime revision is not yet selected;
- exact context injection/rendered prompt identity is not yet frozen well enough to exclude representation confounding.

Only allowed next action:

```text
refine/freeze experiment inputs and measurement contract only;
do not execute A/B/C/D yet.
```

### N -> A automatic promotion

Proposed transition:

```text
Needle canary result
-> automatic accepted cookbook or memory authority
```

State: **BLOCKED**.

Reason:

```text
N PROVIDES_EVIDENCE_FOR C/M  = valid
N GRANTS_AUTHORITY TO C/M    = invalid
```

Only allowed next action:

```text
none under v0.1;
retain canary output as evidence;
use separate governance + explicit human acceptance for promotion.
```

## 11. Snapshot table

| Proposed transition | State | Immediate reason | Only allowed next action |
|---|---|---|---|
| Use G candidate as settled authority | HOLD | parent authority contract still under review | finish governance review |
| Use C as frozen canary input | HOLD | relevant router findings remain | bounded fixes + exact-head review |
| Use M as frozen canary input | HOLD | relevant adapter findings remain | bounded fixes + exact-head review |
| Execute N with C + M | HOLD | moving/unfrozen dependencies and input contract | freeze inputs/measurement only |
| Promote N directly into A | BLOCKED | evidence cannot grant authority | separate governance + human acceptance |

Linked issues, PRs, commits, reviews, and receipts remain source state. This table is a rebuildable view.

## 12. Decision protocol

For a proposed cross-project step:

1. name the exact transition;
2. identify `DEPENDS_ON`, `CAN_INFLUENCE`, and `PROVIDES_EVIDENCE_FOR` relations;
3. check for any implicit `GRANTS_AUTHORITY` shortcut;
4. apply STOP-1 through STOP-6;
5. return `SAFE`, `HOLD`, or `BLOCKED` with reasons;
6. for `HOLD`, name the condition that triggers reassessment;
7. for `BLOCKED`, change the route/design before reassessment.

v0.1 output stays prose or a small review table. No machine-readable schema is required.

## 13. Feynman self-review

**What problem is being solved?**  
A local component can be healthy while the next cross-project transition remains unsafe or uninterpretable.

**What changes?**  
Only the review lens for boundary-crossing steps: four relation meanings, six stop conditions, three readiness states.

**What stays fixed?**  
GitHub issues/PRs/commits/reviews remain source state; project-local tests and review gates remain unchanged.

**Can the mechanism be explained without a new subsystem?**  
Yes: identify dependency/evidence/influence/authority, apply stop conditions, classify the next step.

**What does SAFE not prove?**  
Scientific truth, model quality, long-term stability, or completeness of the dependency map. It only says the declared transition is ready under current scope/evidence.

## 14. Five Whys pressure test

**Why typed relation names?**  
Ordinary links do not distinguish dependency, evidence, influence, and authority; confusing those meanings is the failure under study.

**Why HOLD instead of only local blockers?**  
Because readiness belongs to a cross-project transition while blockers remain owned by their local lines.

**Why BLOCKED instead of another HOLD reason?**  
Some routes are structurally wrong; time alone cannot make automatic evidence-to-authority promotion valid.

**Why record a snapshot if GitHub already has the facts?**  
To test whether the model improves a real decision. The snapshot is explicitly non-authoritative and disposable.

**Why no automation?**  
Because decision value is the hypothesis. Automating before proving it would optimize an unproven abstraction.

## 15. Non-goals and falsifier

v0.1 does not create:

- graph DB or JSON/YAML graph state;
- readiness CLI/service/Action/dashboard;
- automated merge blocking;
- adaptive weighting;
- automatic promotion;
- mandatory forest review for local work;
- a model of every Theseus project.

Do not promote this design into implementation research unless at least one real cross-project decision shows that the model either:

1. exposes a risk local review did not make salient; or
2. makes an existing `SAFE`, `HOLD`, or `BLOCKED` decision materially clearer.

Otherwise record:

```text
NO_ADDED_VALUE
```

and stop.

## 16. Decision log

1. **Start with one cluster.** The goal is to test the lens, not build a Theseus ontology.
2. **Source state stays where it lives.** Readiness snapshots are rebuildable views, not authority.
3. **No automatic authority.** Evidence informs promotion; governance + explicit human acceptance changes baseline authority.
4. **No automation in v0.1.** First prove better cross-project reasoning.

## 17. Review questions

Reviewers should attack three things:

1. Does the design accidentally create a second source of authority?
2. Can it expose circular evidence or authority leakage in this bounded cluster?
3. Is anything here more complex than the problem it is meant to solve?

Removing concepts while preserving those properties is a successful review.
