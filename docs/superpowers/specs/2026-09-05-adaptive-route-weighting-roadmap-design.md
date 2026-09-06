# Governed Adaptive Route Weighting Roadmap

**Status:** architecture roadmap / research design

**Scope:** adaptive selection among already-authorized routes

**Implementation status:** not implemented

**Related design:** [PR #8 — versioned skills and repository cookbooks](https://github.com/TeaShaman-cyber/theseus-research/pull/8)

## 1. Why this exists

A thin skill can act as a router without being a large procedural encyclopedia.

For one task class, the router may know several legitimate routes. GitHub work already provides a concrete example:

```text
GitHub task
    |
    +-> native connector
    +-> governed GitHub API / app route
    +-> governed gh route
    +-> git transport where appropriate
    +-> bounded fallback
```

Today those choices are mostly static: preferred route first, then a documented fallback sequence.

A second layer is possible. If route outcomes are monitored, the system can estimate which admissible route currently performs better for a given context using signals such as:

- verified success rate;
- first-pass success;
- token and tool-call cost;
- latency;
- retry and recovery cost;
- postcondition/read-back success;
- human intervention or correction count;
- route-specific control-plane or provider failure rate;
- provenance quality.

This suggests a governed adaptive router: **the skill defines the allowed route graph; monitoring supplies evidence; an adaptive policy changes route preference weights inside that graph.**

The design must not turn performance statistics into authority.

## 2. Core invariant

```text
AUTHORITY / CAPABILITY / PERMISSION / CURRENTNESS
                    |
                    v
          admissible route set
                    |
                    v
          adaptive route scoring
                    |
                    v
                 choice
                    |
                    v
          action + postcondition
                    |
                    v
          telemetry / policy update
```

The adaptive layer may choose only among routes that already passed hard gates.

It may not:

- grant new authority;
- widen permission;
- invent a new route;
- bypass a required human approval;
- bypass required read-back;
- change a skill or cookbook;
- reinterpret an unsafe route as safe because it is cheap or successful;
- treat missing evidence as zero cost;
- silently convert `UNKNOWN` into a favorable score.

A route excluded by the hard contract has effective weight zero regardless of historical performance.

## 3. Terminology

### Route topology

The versioned, relatively slow-changing graph of routes that a skill knows may exist.

Example:

```text
github.read
github.mutate.connector
github.mutate.governed_api
github.mutate.gh
github.git_transport
```

Topology answers:

> What routes are allowed to be considered at all?

Topology belongs to reviewed/versioned procedural knowledge, not to online telemetry.

### Route policy

The dynamic preference state used to rank or sample among admissible routes.

Policy answers:

> Of the routes allowed here, which one is currently preferred?

### Route evidence

Observed attempts and their outcomes.

Evidence answers:

> What actually happened when a route was tried under a specific context and policy snapshot?

### Route weight

A derived preference value, probability, score, or ranking for one admissible route under a context.

This is a literal routing weight. It is **not** a neural-model weight.

### Policy snapshot

An immutable **executable-policy manifest** used for one decision. It binds not only the derived scores but also the scorer/build identity, feature and receipt semantics, evidence set, route-stack epoch, activation/expiry, approval state, and compatible static fallback so later replay does not reinterpret old policy state through new code.

## 4. Relationship to the externalized-learning architecture

PR #8 separates:

```text
memory
    -> plastic experience state

cookbook
    -> reviewed local operational lessons

skill
    -> slower-changing generalized procedural routing
```

Adaptive route weighting adds another state layer without changing that separation:

```text
session/context state       fastest
memory
route observations/statistics
adaptive route policy
repository/runtime cookbook
skill route topology        slow
base-model weights          outside operator update authority
```

The topology remains slow and reviewed. Route preference can adapt faster.

A useful formulation is:

```text
fixed model weights
+ versioned route topology
+ dynamic memory
+ dynamic route policy
+ current runtime state
= effective agent behavior
```

The adaptive policy therefore becomes one concrete form of externalized learning without base-weight updates.

## 5. Why this is not merely round-robin

Plain round-robin ignores evidence:

```text
A -> B -> C -> A -> B -> C
```

Weighted round-robin can encode preference:

```text
A -> A -> A -> B -> B -> C
```

but still assumes that one global weight is sufficient.

Theseus tasks are contextual. The preferred route can depend on:

- read versus mutation;
- risk class;
- payload size and shape;
- current provider/control-plane health;
- current authentication state;
- runtime profile;
- required provenance/read-back strength;
- latency or token budget;
- route version and recent drift.

The useful object is therefore closer to:

```text
weight(route | task_class, runtime_state, risk, payload_class, route_version)
```

A contextual bandit is a possible later algorithm family, but it is not the starting assumption.

## 6. Three candidate policy approaches

### Approach A — deterministic evidence-weighted ranking

For each admissible route, compute a risk-adjusted utility from recent evidence and choose the highest-ranked route.

Conceptually:

```text
utility =
    verified_success_value
  - token_cost
  - latency_cost
  - retry_cost
  - expected_failure_recovery_cost
  - bounded_human_intervention_cost
```

Safety, authority, permission, and provenance requirements remain hard constraints, not utility terms.

**Advantages**

- easy to reason about;
- deterministic replay is possible;
- no deliberate exploration;
- easiest first production candidate.

**Weaknesses**

- can get stuck on historically good routes;
- sensitive to metric and coefficient choices;
- does not naturally quantify uncertainty.

### Approach B — weighted randomized selection

Convert utilities/confidence into selection probabilities among admissible routes.

**Advantages**

- gathers comparative evidence;
- avoids permanently locking onto one route;
- simpler than a full contextual bandit.

**Weaknesses**

- deliberate exploration can be inappropriate for mutation/high-risk tasks;
- randomization complicates incident reproduction;
- probability calibration can hide poor metric design.

### Approach C — contextual bandit

Use context features and uncertainty to choose between routes, with candidate families such as Thompson sampling or upper-confidence-bound methods.

**Advantages**

- explicitly models uncertainty and context;
- can balance exploitation and exploration;
- potentially adapts to changing route quality.

**Weaknesses**

- highest Goodhart and feedback-loop risk;
- credit assignment is harder when several fallback routes form one successful sequence;
- requires careful non-stationarity handling;
- easy to overfit sparse route/context combinations;
- difficult to justify for high-risk mutations.

### Recommendation

Use a staged architecture:

```text
Stage 0: observation only
Stage 1: shadow deterministic scorer
CAUSAL-COMPARABILITY GATE: comparable assignments for each promotable route/task stratum
Stage 2: bounded exploit-only adaptive ranking, only for strata that passed that gate
Stage 3: low-risk read-only weighted exploration
Stage 4: contextual-bandit experiment, only if earlier stages justify it
```

The architecture should permit later bandit experiments without making them necessary for the first useful system.

## 7. The selection pipeline

One decision should follow this order:

```text
1. classify task
2. resolve route topology version
3. discover currently exposed routes
4. verify capability/currentness
5. apply authority + permission + risk gates
6. apply health/circuit-breaker gates
7. obtain admissible route set
8. load applicable policy snapshot
9. score/rank admissible routes
10. choose route
11. executor revalidates a short-lived authorization decision bound to the exact principal, target, operation, route, route topology version, approval, and current circuit-breaker state
12. execute only if that decision is still current; otherwise return `BLOCKED`
13. verify exact postcondition
14. classify action, verification, and task outcomes separately
15. append linked telemetry receipt(s)
16. derive future policy state
```

If steps 1–7 produce no admissible route, the result is `BLOCKED` or `UNKNOWN`.

Step 11 is owned by the executor/authorization boundary, not by the adaptive scorer. A previously admissible route is not authority to execute later. The same immediate reauthorization is required when the system falls back to the reviewed static route order. A stale or mismatched decision returns `BLOCKED` with a reason such as `authorization_stale`; it is never silently refreshed by the scorer.

The adaptive scorer must never expand the candidate set to make progress.

## 8. Route identity and statistics scope

Statistics are meaningful only if the route identity is stable enough to compare.

A route observation should bind at minimum:

```text
route_id
route_topology_version
route_stack_epoch
runtime_profile
task_class
risk_class
route/provider version when observable
skill identity when applicable
policy_snapshot_id
```

Context dimensions that materially affect performance should be explicit, but the system should avoid exploding into an unlearnable Cartesian product.

`route_stack_epoch` is mandatory even when a provider or connector exposes no useful version. It is an immutable fingerprint or administratively bumped epoch covering all behaviorally relevant dependencies of the route: connector/wrapper build, auth mode, endpoint/provider behavior boundary, model/harness/runtime class, and other dependencies declared by that route contract. Optional provider/version fields are descriptive evidence; they are not a substitute for the epoch.

A connector upgrade, auth-mode change, wrapper rewrite, model/runtime switch, endpoint/provider behavior change, or major policy-contract change invalidates the prior epoch. If the runtime cannot establish which route-stack epoch an observation or policy belongs to, prior statistics are not reused and the adaptive policy becomes `POLICY_STALE` for that route/stratum.

Old evidence must not silently retain full weight after a route changes meaning.

## 9. Telemetry receipt

The telemetry layer should store structured receipts, not raw conversational transcripts by default.

A candidate task receipt should preserve linked attempts rather than collapse action and verification into one Boolean:

```json
{
  "task_id": "immutable-id",
  "decision_id": "immutable-id",
  "observed_at": "timestamp",
  "task_class": "github.mutation",
  "risk_class": "bounded_mutation",
  "runtime_profile": "M0-MARCOPOLO",
  "route_topology_version": "immutable-ref",
  "route_stack_epoch": "immutable-ref",
  "policy_snapshot_id": "immutable-ref",
  "eligible_routes": ["route-a", "route-b"],
  "excluded_routes": [
    {"route_id": "route-c", "reason": "capability_unverified"}
  ],
  "selected_route": "route-a",
  "selection_mode": "static|shadow|adaptive|explore",
  "attempts": [
    {
      "attempt_id": "immutable-attempt-id",
      "sequence": 1,
      "parent_attempt_id": null,
      "route_id": "route-a",
      "route_role": "action",
      "fallback_trigger": null,
      "action_outcome": "CONTROL_PLANE_FAILURE",
      "verification_outcome": null,
      "evidence_digest": "sha256:minimized-evidence"
    },
    {
      "attempt_id": "immutable-attempt-id-2",
      "sequence": 2,
      "parent_attempt_id": "immutable-attempt-id",
      "route_id": "route-b",
      "route_role": "action",
      "fallback_trigger": "CONTROL_PLANE_FAILURE",
      "action_outcome": "ACTION_REPORTED_SUCCESS",
      "verification_outcome": null,
      "evidence_digest": "sha256:minimized-evidence"
    },
    {
      "attempt_id": "immutable-attempt-id-3",
      "sequence": 3,
      "parent_attempt_id": "immutable-attempt-id-2",
      "route_id": "route-c",
      "route_role": "verification",
      "fallback_trigger": null,
      "verifies_attempt_id": "immutable-attempt-id-2",
      "action_outcome": null,
      "verification_outcome": "VERIFIED_SUCCESS",
      "evidence_digest": "sha256:minimized-evidence"
    }
  ],
  "task_outcome": "VERIFIED_SUCCESS",
  "metrics": {
    "elapsed_ms": 0,
    "tool_calls": 0,
    "token_cost": "number-or-UNKNOWN",
    "retry_count": 1,
    "human_interventions": 0
  }
}
```

The exact storage schema belongs to a later implementation spec, but the separation of task identity, attempt identity/order, route role, fallback trigger, action outcome, verification outcome, and minimized evidence binding is a contract requirement. A successful mutation with unavailable verification must remain distinguishable from both a failed mutation and a verified success; it must not trigger a blind duplicate retry.

### Privacy / minimization boundary

The default telemetry receipt should not contain:

- secrets;
- credential values;
- full prompts;
- private document bodies;
- raw conversation history.

Prefer task classes, bounded context features, hashes, opaque identifiers, and quantitative outcome data.

## 10. Outcome classes

A route should not receive a success reward merely because a tool call returned 2xx or exit code zero.

Useful outcome classes include:

```text
VERIFIED_SUCCESS
UNVERIFIED_RESULT
TARGET_REJECTED
CONTROL_PLANE_FAILURE
AUTH_FAILURE
PERMISSION_BLOCK
CAPABILITY_MISMATCH
TIMEOUT
POSTCONDITION_MISMATCH
USER_ABORT
INCONCLUSIVE
```

Only `VERIFIED_SUCCESS` counts as verified success.

`UNVERIFIED_RESULT` is not equivalent to failure, but it must not improve the route as if the requested outcome had been confirmed.

## 11. Metrics and objective function

The router should remain multi-objective internally even if a scalar utility is used for final ranking.

Candidate dimensions:

### Reliability

- verified success rate;
- first-pass verified success;
- fallback frequency;
- retry count;
- rollback/recovery frequency.

### Cost

- input/output tokens where observable;
- tool calls;
- API monetary cost where observable;
- compute/runtime duration;
- expected recovery cost after failure.

Unknown cost is `UNKNOWN`, not zero.

### Ergonomics

Use observable operational proxies rather than guessing user sentiment:

- required manual confirmations beyond the contract minimum;
- user corrections;
- route-switch interventions;
- repeated requests caused by route failure;
- avoidable interaction steps.

Do not infer emotional state or satisfaction as a routing metric.

### Verification/provenance

- postcondition read-back success;
- exact target identity preserved;
- receipt completeness;
- provenance quality required by the operation.

Verification/provenance floors are preferably constraints before optimization, not rewards that can be traded away for cheapness.

## 12. Policy update lifecycle

Dynamic does not mean untraceable.

Each adaptive decision should bind an immutable policy manifest containing at minimum:

```text
policy_contract_version
+ scorer / algorithm build identity
+ feature_schema_version
+ receipt_schema_version
+ route_topology_version
+ route_stack_epoch
+ exact evidence cutoff and/or evidence-set digest
+ policy configuration
+ derived policy snapshot id
+ activation time
+ expiry / revalidation boundary
+ approval state / acceptance identity
+ compatible static_fallback_version
```

Policy snapshots should be reproducible from the bound evidence and executable contract where practical. An old snapshot must not be loaded by a scorer/runtime that cannot prove compatibility with those schema/build identities; incompatibility yields `POLICY_STALE` and the compatible reviewed static fallback.

A route-policy update should be rollbackable independently from skill topology.

The design should distinguish:

```text
canonical route topology
current telemetry
derived policy candidate
active policy snapshot
previous policy snapshot
```

A malformed or insufficient policy state should fall back to the last accepted static route policy.

## 13. Non-stationarity and evidence ageing

Route quality changes over time.

Examples:

- provider outage;
- connector update;
- authentication change;
- API behavior change;
- model/harness change;
- wrapper fix;
- rate-limit policy change.

The router therefore needs an ageing policy.

Candidates include:

- version-bounded evidence windows;
- recency decay;
- explicit invalidation on route-version changes;
- health events that temporarily suspend a route.

The first implementation should prefer understandable invalidation and recency windows over clever long-memory statistics.

Historical evidence remains useful for diagnosis, but stale evidence must not dominate current routing.

## 14. Circuit breaking is not route learning

Fast health protection and slower preference learning are different mechanisms.

```text
recent hard failure / outage
        -> health gate / circuit breaker

repeated comparative outcomes
        -> route preference evidence
```

A circuit breaker may temporarily make a route inadmissible.

The learning policy should not encode outages only by slowly lowering a score while continuing to send work into a known-broken route.

## 15. Exploration boundary

Exploration is the dangerous part.

The default roadmap rule is:

```text
read-only low-risk work
    -> exploration may eventually be allowed within an explicit budget

mutation / expensive / irreversible / externally visible work
    -> NO exploration by default; exploit/static choice only
```

A later design may authorize narrowly bounded mutation or externally visible exploration only through a **separately versioned mutation-experiment contract** with explicit human acceptance, its own authority/rollback/receipt rules, and immediate executor reauthorization. Nominal reversibility is not sufficient: notifications, billing, audit trails, third-party observations, and external side effects may be irreversible even when local state can be rolled back.

Exploration budget, minimum evidence, and confidence thresholds must be explicit preregistered experiment parameters before any experimental activation. This roadmap intentionally does not invent universal numeric thresholds.

## 16. Static fallback remains a first-class route

Adaptive routing must fail closed.

If policy evidence is missing, corrupt, stale, conflicting, or unavailable:

```text
adaptive policy
      |
      X
      |
      v
reviewed static route order
```

The static route order is not an embarrassing legacy path. It is the deterministic recovery baseline.

This also gives every adaptive experiment a natural control.

## 17. Credit assignment problem

A task often succeeds through a sequence:

```text
route A fails control plane
    -> route B succeeds
    -> read-back route C verifies
```

It would be misleading to label only the final route as `success`.

Telemetry must preserve:

1. **action-attempt outcomes** — what each action route actually did or failed to do;
2. **verification-attempt outcomes** — what independent read-back established, including unavailable/inconclusive verification;
3. **task-level outcome** — whether the full requested postcondition was reached.

These are linked by stable task/attempt identities and ordering. Later scoring must decide how to attribute recovery cost without erasing the evidence that the first route failed or treating missing verification as failed action. Verification routes may be scored independently while still contributing cost/provenance to the parent task.

This is a major review question for Codex.

## 18. Goodhart and feedback-loop risks

The system can optimize the wrong thing even when every metric is measured correctly.

Examples:

- choose a cheap route that produces more unverified outputs;
- avoid a strong verification route because it adds tool calls;
- prefer easy task classes and underexplore difficult ones;
- reward routes that fail fast because latency looks low;
- overvalue a route whose failures are silently rescued by an expensive fallback;
- learn from biased data because static routing sent most tasks to the incumbent route;
- keep obsolete preferences after a runtime/provider change.

Mitigations:

- hard constraints before utility;
- task-level and attempt-level receipts;
- explicit missing-data state;
- shadow evaluation before activation;
- static baseline comparison;
- route-version scoping;
- holdout/replay evaluation;
- human-readable reason codes;
- periodic cold review;
- rollbackable policy snapshots.

## 19. Decision observability

Every adaptive choice should be explainable at an engineering level without exposing hidden model reasoning.

A compact decision receipt should answer:

```text
What task class was recognized?
Which routes were considered?
Which routes were excluded, and why?
What policy snapshot and route-stack epoch were used?
What measurable and causally comparable evidence favored the selected route?
Was selection exploit or exploration?
Was executor authorization revalidated immediately before dispatch?
What action outcome and verification outcome were observed afterward?
```

This is operational provenance, not chain-of-thought.

## 20. GitHub as the first pilot

GitHub is a useful pilot because several route families already exist and their failures are observable.

Candidate task classes:

```text
github.read
github.issue_comment
github.issue_update
github.pr_review
github.file_write
github.branch_or_ref_update
github.git_transport
```

The pilot should begin with read-only and low-risk operations.

The known mutation lesson remains a hard invariant:

```text
intent
-> target_type
-> target_id
-> operation
-> expected_postcondition
-> matching mutation primitive
-> exact read-back
```

Adaptive scoring happens only after that target/operation contract is resolved.

The pilot must not learn that a semantically wrong mutation primitive is good merely because the API request succeeded.

## 21. Proposed staged roadmap

### Phase 0 — instrumentation baseline

Goal: learn without changing behavior.

- define route IDs;
- classify current static choices;
- record attempt/task receipts;
- measure missing telemetry;
- establish static baseline metrics;
- no adaptive selection.

Exit gate:

> Telemetry can reconstruct why a route was attempted and whether the requested postcondition was verified.

### Phase 1 — shadow scorer

Goal: compute recommendations without acting on them.

- define deterministic risk-adjusted utility;
- generate shadow route ranking;
- compare shadow recommendation with actual static route;
- replay historical receipts;
- test route-version invalidation and missing-data handling.

Exit gate:

> Shadow policy is reproducible and does not recommend inadmissible routes.

Shadow agreement, offline replay, and historical fallback receipts are **not sufficient causal evidence** that an alternative route is better. Fallback observations are conditional on incumbent failure and therefore come from a systematically different population.

Before any route/task stratum may enter Phase 2, a causal-comparability gate must identify contemporaneous comparable assignments, for example:

- naturally overlapping assignments within a fixed preregistered stratum;
- a separately approved safe randomized **read-only** evidence-collection trial;
- another explicitly justified assignment mechanism that supports comparison without relying on fallback-only selection bias.

The assignment mechanism, strata, evidence window, and exclusion rules must be preregistered. If comparable evidence does not exist, the ranking remains `SHADOW_ONLY` regardless of its historical score.

### Phase 2 — bounded exploit-only adaptive routing

Goal: let evidence alter route priority without deliberate exploration.

- activate only in approved low-risk task classes and route/task strata that passed the causal-comparability gate;
- choose best admissible route using deterministic ranking;
- preserve reviewed static fallback;
- immutable policy snapshot per decision;
- canary rollout with rollback.

Exit gate:

> Adaptive policy improves preregistered operational metrics without degrading verified-success or provenance floors.

### Phase 3 — bounded exploration

Goal: collect evidence on alternatives that static exploitation would rarely try.

- read-only low-risk tasks only by default;
- explicit exploration budget;
- weighted randomized selection or equivalent;
- independent monitoring for regressions;
- no mutation or externally visible exploration unless a separately versioned mutation-experiment contract is active and explicitly accepted.

Exit gate:

> Exploration produces useful comparative evidence without unacceptable failure or human-friction cost.

### Phase 4 — contextual-bandit research

Goal: test whether context-aware uncertainty modeling beats simpler policies.

- compare contextual bandit against deterministic scorer and weighted baseline;
- isolate model/runtime/provider changes;
- evaluate non-stationarity and sparse-context failure modes;
- keep bandit policy experimental until independent review.

This phase is optional. A successful Phase 2 system may already provide most practical value.

## 22. Evaluation design

Each stage should be evaluated against the static baseline.

Candidate primary metrics:

```text
verified task success
first-pass verified success
total tool calls per verified task
tokens per verified task
elapsed time per verified task
fallback/retry count
human correction/intervention count
postcondition mismatch rate
expected recovery cost
```

Evaluation should include:

- offline replay where possible;
- a time-separated holdout window;
- route-topology and mandatory route-stack-epoch-aware grouping;
- fixed-stratum causal/comparability analysis for any ranking proposed for activation;
- explicit treatment of fallback-only historical data as biased diagnostic evidence rather than counterfactual proof;
- failure-class breakdown;
- cold-start behavior;
- degraded-provider scenarios;
- deliberately missing telemetry;
- policy rollback tests.

Before an online adaptive pilot, acceptance thresholds should be preregistered rather than chosen after observing results.

## 23. Implementation boundaries

This roadmap does not choose the production storage engine or scheduler.

A first MarcoPolo experiment could naturally use local DuckDB for structured telemetry and derived policy snapshots, because that runtime already uses DuckDB for machine operational truth. That would be an experiment-specific implementation decision, not a program-wide requirement.

Likewise, this PR does not decide:

- the final telemetry database;
- the final bandit library;
- a universal utility coefficient set;
- universal exploration percentages;
- a universal observation-window length.

Those choices should be made by later implementation/research specs with measurable acceptance tests.

## 24. Security and authority boundary

Adaptive routing is an optimization subsystem, not an authorization subsystem.

The policy may consume:

```text
capability state
permission state
risk classification
health state
cost/quality telemetry
```

but may not write back authority or permission.

Authority state is an input boundary.

If telemetry and authority disagree, authority wins.

If currentness is unknown for a critical route, the route is not made eligible merely because historical telemetry is excellent.

## 25. Failure handling

The adaptive subsystem should expose honest states:

- `STATIC_BASELINE` — adaptive policy intentionally disabled;
- `SHADOW_ONLY` — scores computed but not used;
- `ADAPTIVE_ACTIVE` — bounded adaptive choice allowed;
- `POLICY_STALE` — evidence/policy invalidated;
- `POLICY_DEGRADED` — partial telemetry available, static fallback preserved;
- `BLOCKED` — no admissible route;
- `UNKNOWN` — evidence insufficient to classify.

A failure of the adaptive subsystem should not become a failure of the underlying safe static route unless that static route is itself unavailable.

## 26. Questions for Codex architecture review

Please attack this blueprint rather than merely checking prose.

### Contracts and authority

1. Is the hard-gate/adaptive-score separation strong enough to prevent optimization from creating authority?
2. Which state transitions could accidentally let stale policy override current capability or permission?
3. Is route topology sufficiently separated from dynamic policy state?

### Statistical design

4. Which metrics are likely to Goodhart first?
5. Is deterministic risk-adjusted ranking a sound first adaptive stage, or is another baseline better?
6. How should uncertainty be represented before any bandit stage?
7. What minimum evidence concepts are needed without hard-coding arbitrary global sample counts?
8. What non-stationarity strategy best prevents old route evidence surviving a route/provider/runtime change?

### Credit assignment

9. How should a multi-route fallback sequence attribute success, failure, and recovery cost?
10. Should read-back/verification routes be scored as part of the action route, independently, or both?

### Safety and rollout

11. Which route classes should remain permanently exploit-only?
12. What conditions should immediately invalidate or circuit-break a route?
13. What is the smallest safe canary for Phase 2?
14. What rollback evidence must be retained?

### Telemetry and privacy

15. Is the proposed receipt sufficient for replay without retaining raw private task content?
16. Which context features are necessary for a useful contextual policy without creating a privacy or cardinality problem?

### Architecture

17. Should adaptive route policy live beside skills, in runtime operational state, or behind a separate policy service?
18. Which pieces are generic Theseus contracts versus MarcoPolo-specific implementation details?
19. Does the roadmap need an explicit policy-schema/version registry before implementation?
20. What obvious failure mode or feedback loop is missing from this draft?

## 27. Review / implementation gate

This PR is a roadmap only.

It should not authorize implementation by itself.

The next transition is:

```text
roadmap PR
    -> Codex + human architecture review
    -> accepted corrections
    -> decomposition into bounded implementation/research specs
    -> explicit approval
    -> implementation plan
    -> TDD implementation
```

The first implementation spec should cover **Phase 0 instrumentation only** unless review establishes a smaller responsible slice.

## 28. Working summary

```text
SKILL
  defines permitted route topology
        |
        v
HARD GATES
  authority / permission / capability / currentness / risk
        |
        v
ADMISSIBLE ROUTES
        |
        v
ADAPTIVE POLICY
  measured reliability / cost / ergonomics / uncertainty
        |
        v
SELECTED ROUTE
        |
        v
ACTION + READ-BACK
        |
        v
STRUCTURED RECEIPT
        |
        v
UPDATED ROUTE EVIDENCE
        |
        +------> future preference changes
```

The key discipline is:

> **Learn preference, never learn permission.**

Dynamic route weights may change how the system chooses among approved roads. They must never decide which roads are legal to drive.
