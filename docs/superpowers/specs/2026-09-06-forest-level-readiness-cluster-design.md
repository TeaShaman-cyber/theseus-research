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

`A` is a role, not one universal SHA. Every reviewed transition must bind the exact baseline identity it depends on; a moving or ambiguous baseline is a `HOLD`.

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
N DEPENDS_ON A
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

This relation exposes confounders and feedback loops. If the accepted baseline materially changes execution or evaluation, record `A CAN_INFLUENCE N`; otherwise `N DEPENDS_ON A` is sufficient to mark the baseline as an interpretive input.

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
N --DEPENDS_ON----------> A
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

### Measurement provenance check

The four relation types stay unchanged. For any experiment transition, the review input must also name three provenance fields:

```text
measurement_definition_source
evaluator_source
control_or_baseline_source
```

These are attributes of the reviewed transition, not new graph nodes or authority. If the measured candidate supplies its own success criterion or evaluator and no independent control makes the intended claim interpretable, the transition is `BLOCKED`. If any source is unknown, the transition is at least `HOLD`.

The exact accepted baseline identity must be pinned for the transition. If baseline content changes during evaluation, or incorporates prior candidate results in a way that affects interpretation, record that dependency/influence explicitly and reassess before drawing the intended claim.

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

## 10. Candidate-methodology and snapshot boundary

This spec is **candidate methodology/provenance**, not accepted Theseus methodology. Accepted lessons require a separate human promotion decision into both `docs/methodology.md` and `docs/methodology.ru.md`, preserving semantic parity. Reviewing or merging this spec alone grants no methodological authority.

The snapshot below is a dated derived view, not a registry or policy. Source Issues, PRs, exact review artifacts, commits, receipts, and accepted methodology remain authoritative in their own scopes.

Snapshot assembled at: **2026-09-06T09:32:43Z**.

## 11. Current-cluster snapshot

- **G — HOLD** for treating `theseus-research#8@4ebaae08fa15c4c7e77b1db7879186b7d3d78056` as settled cross-project authority. Evidence: <https://github.com/TeaShaman-cyber/theseus-research/pull/8#discussion_r3942132724>. The review still questions exact human-acceptance verification. Suggested next check: finish governance review, then rebuild this derived state.

- **C — HOLD** for using `marcopolo-cookbook#25@bd3c6d70e8c7522a6d91c0ad1921624dfcd29c59` as a frozen canary input. Exact-head evidence: <https://github.com/TeaShaman-cyber/marcopolo-cookbook/pull/25#discussion_r3943399561>, <https://github.com/TeaShaman-cyber/marcopolo-cookbook/pull/25#discussion_r3943399564>, <https://github.com/TeaShaman-cyber/marcopolo-cookbook/pull/25#discussion_r3943399568>, <https://github.com/TeaShaman-cyber/marcopolo-cookbook/pull/25#discussion_r3943399571>. These findings can change compiled context/classification/budget behavior. Suggested next check: bounded fixes + full gate + exact-head review.

- **M — HOLD** for using `marcopolo-cookbook#20@05bde60d5571b15103d3e0830073e0c4bd18b5d3` as a frozen canary input. Exact-head evidence: <https://github.com/TeaShaman-cyber/marcopolo-cookbook/pull/20#discussion_r3943264425>, <https://github.com/TeaShaman-cyber/marcopolo-cookbook/pull/20#discussion_r3943264427>. These findings affect credential admission and canonical persistence/readback. Suggested next check: resolve them, verify exact head, then rebuild this state.

- **N — HOLD** for executing `theseus-needle-lab#46`. Source: <https://github.com/TeaShaman-cyber/theseus-needle-lab/issues/46>, whose state remains `EXPERIMENT PROPOSED / DESIGN ONLY / IMPLEMENTATION NOT RUN`. `N DEPENDS_ON C`, `N DEPENDS_ON M`, and `N DEPENDS_ON` an exact accepted baseline `A`; the review must also pin `measurement_definition_source`, `evaluator_source`, and `control_or_baseline_source`. Suggested next check: freeze those inputs only after C and M become suitable immutable candidates.

- **N -> A automatic promotion — BLOCKED.** `N PROVIDES_EVIDENCE_FOR C/M` is valid; `N GRANTS_AUTHORITY TO C/M` is not valid without separate governance + explicit human acceptance. The existing authority boundary creates this block, not this snapshot. Suggested next check: retain the canary result as evidence and use the accepted promotion process.

These are derived claims tied to the cited evidence and observation time. They do not issue directives.

## 12. Decision protocol


For a proposed cross-project step:

1. name the exact transition and observation time;
2. pin exact candidate identities, exact accepted baseline `A`, and the source evidence used for the derived claim;
3. identify `DEPENDS_ON`, `CAN_INFLUENCE`, and `PROVIDES_EVIDENCE_FOR` relations;
4. record `measurement_definition_source`, `evaluator_source`, and `control_or_baseline_source`;
5. check for any implicit `GRANTS_AUTHORITY` shortcut;
6. apply STOP-1 through STOP-6;
7. return a derived `SAFE`, `HOLD`, or `BLOCKED` assessment with reasons;
8. for `HOLD`, name a non-binding reassessment condition; for `BLOCKED`, identify the existing authority/contract that makes the route invalid.

v0.1 output stays prose or a small review table. No machine-readable schema is required.

## 13. Feynman self-review

**What problem is being solved?**  
A local component can be healthy while the next cross-project transition remains unsafe or uninterpretable.

**What changes?**  
Only the review lens for boundary-crossing steps: four relation meanings, three measurement-provenance fields, six stop conditions, and three readiness states. No new authority source is introduced.

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
3. **Candidate methodology stays candidate.** Accepted lessons are promoted separately into both `docs/methodology.md` and `docs/methodology.ru.md`.
4. **No automatic authority.** Evidence informs promotion; governance + explicit human acceptance changes baseline authority.
5. **No automation in v0.1.** First prove better cross-project reasoning.

## 17. Review questions

Reviewers should attack three things:

1. Does the design accidentally create a second source of authority?
2. Can it expose circular evidence or authority leakage in this bounded cluster?
3. Is anything here more complex than the problem it is meant to solve?

Removing concepts while preserving those properties is a successful review.
