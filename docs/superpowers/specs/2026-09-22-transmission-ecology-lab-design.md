# Transmission Ecology Lab — design

**Issue:** TeaShaman-cyber/theseus-research#72
**Planned repository:** TeaShaman-cyber/theseus-transmission-ecology-lab
**Planned Project:** Theseus — Transmission Ecology Lab
**Status:** design for review; no lab repository or Project created yet

## 1. Purpose

Build a small reproducible research lab that asks one bounded question:

> Which dynamical invariants survive when the substrate changes from viral transmission to cultural/memetic transmission to AI-agent transfer?

The lab is not intended to prove a universal biological/cultural/agent isomorphism. Its job is to make the comparison executable, falsifiable, and cheap enough to reject when it stops helping.

## 2. Design choice

Three approaches were considered.

### A. Keep experiments inside theseus-research

Lowest bootstrap cost, but it mixes research coordination with executable model code and would make the root repository another laboratory warehouse.

### B. Extend theseus-repo-search-lab

Reuses graph machinery directly, but conflates dependency-graph retrieval semantics with transmission dynamics. That would weaken both projects' boundaries.

### C. Dedicated transmission ecology lab — selected

Create `theseus-transmission-ecology-lab` and borrow proven patterns from repo-search and theseus-research without coupling their domain semantics.

This is selected because the work already needs independent fixtures, model adapters, metrics, receipts, CI, and a research roadmap.

## 3. Scope: deterministic v0 only

v0 uses one frozen directed weighted graph and one common linearized state-transition form:

`x(t+1) = K_s x(t) + u_s`

where `s` is the substrate: virus, meme, or agent.

The common interface is deliberately narrower than the real domains. It tests the operator-level analogy before adding stochastic or nonlinear mechanisms.

### Included

- one shared graph fixture used by all three substrates;
- explicit per-substrate transmission and variant-transition parameters;
- spectral radius and threshold behavior;
- cycle rank / beta_1 control measurement;
- lineage diversity and survival after a fixed number of steps;
- convergence / extinction behavior;
- one deterministic perturbation and recovery measurement;
- positive and negative controls;
- machine-readable receipts with epistemic labels.

### Explicitly deferred

- stochastic epidemic simulation;
- influenza reassortment requiring coinfection/nonlinear state;
- complex contagion / repeated-exposure thresholds;
- simplicial or hypergraph dynamics;
- endogenous graph rewiring;
- learned model parameters;
- real-world causal claims;
- visualization-heavy dashboards.

Deferred mechanisms are not treated as absent; v0 simply does not model them.

## 4. Mathematical object

### Graph

A fixture defines:

- stable node IDs;
- directed edges;
- optional edge weights;
- declared scope;
- provenance / fixture version.

Borrow from repo-search:

- bounded traversal patterns;
- deterministic ordering;
- explicit scope boundaries;
- ambiguity fails closed.

Do not import repo-search as a runtime dependency in v0. Reuse the contract ideas, not its dependency-graph semantics.

### State

For N graph nodes and M transmissible variants, each substrate owns a nonnegative state vector of size N*M.

Each substrate adapter produces a deterministic next-generation matrix `K_s` from:

- shared adjacency structure;
- substrate-specific transmissibility/loss parameters;
- a variant-transition matrix;
- optional substrate-specific fitness/evaluator weights.

### Variation boundary

v0 represents mutation/reconstruction/local adaptation as a linear variant-transition matrix.

Influenza reassortment, cultural recombination requiring multiple sources, and agent composition requiring multiple artifacts are nonlinear or multi-parent mechanisms and are intentionally deferred.

That boundary prevents a convenient linear model from being mislabeled as a full biological or cultural simulator.

## 5. Shared metrics

Every substrate run emits the same metric names when the measurement is meaningful:

- `spectral_radius`;
- `subcritical_or_supercritical` relative to 1;
- `cycle_rank_beta1` of the frozen graph;
- `total_mass_by_step`;
- `variant_shannon_entropy`;
- `surviving_variant_count`;
- `dominant_variant_share`;
- `time_to_extinction_or_horizon`;
- `perturbation_recovery_ratio`.

`cycle_rank_beta1` is a topology control, not a claimed predictor of success. Theseus #37 already established that topology-only structure can fail to discriminate useful research paths.

## 6. Controls

### Positive threshold control

Construct a matrix with `rho(K) > 1`. With zero innovation and nonzero seed state, total mass must grow over the declared short horizon.

### Negative threshold control

Construct a matrix with `rho(K) < 1`. With zero innovation, total mass must decay over the declared horizon.

### Topology-only negative control

Use the same graph with two different parameterizations on opposite sides of the spectral threshold.

This directly falsifies any implementation that accidentally treats graph shape alone as the outcome.

### Cycle-rank control

Use a frozen fixture with known `mu = E - N + P`. Cross-check the implementation against an independent incidence-matrix/Hodge calculation.

## 7. Proposed repository layout

```text
README.md
CHANGELOG.md
pyproject.toml
src/transmission_ecology/
  graph.py
  state.py
  metrics.py
  receipt.py
  models/
    base.py
    virus.py
    meme.py
    agent.py
experiments/
  v0/
    shared-graph.json
    controls.json
    parameters/
      virus.json
      meme.json
      agent.json
receipts/
  reference/
tests/
  test_graph.py
  test_metrics.py
  test_models.py
  test_controls.py
  test_receipt.py
tools/
  dev/check
  run-v0
  verify/
    independent-crosscheck.md
.github/workflows/
  qa.yml
  v0-replay.yml
docs/
  methodology.md
  epistemic-boundary.md
```

Keep files small and responsibilities explicit. No graph database, service, UI, or external persistence in v0.

## 8. Receipt contract

Each run writes one deterministic JSON receipt containing:

- schema version;
- source commit;
- fixture hash;
- substrate;
- parameter hash;
- horizon;
- metric values;
- controls passed/failed;
- implementation version;
- epistemic classification;
- scientific authority = NONE.

Allowed experiment dispositions:

`FOUND_USEFUL_STRUCTURE`, `NO_SIGNAL`, `REFINE`, `REJECT`, `UNKNOWN_WITHIN_CURRENT_CONTRACT`.

A receipt reports a computation; it does not promote a scientific interpretation.

## 9. QA

`tools/dev/check` is the first local pre-review gate.

v0 QA should include:

- format/schema checks for fixtures and receipts;
- unit tests for graph and metrics;
- deterministic replay of all three substrates;
- threshold positive/negative controls;
- topology-only negative control;
- receipt reproducibility from a clean checkout;
- mutation tests only after ordinary tests establish a stable baseline.

An independent mathematical cross-check must reproduce at least one spectral or Hodge measurement before deterministic v0 is called complete.

Preferred independent routes, in order of operational simplicity:

1. a second local exact/symbolic implementation;
2. Wolfram through an already available integration or mcporter route;
3. another external mathematics backend if independently reproducible.

External verifier availability must not make the basic local QA path unusable.


## 9.1. Two canonical QA endpoints

The lab must expose two distinct executable QA entrypoints with non-overlapping claims.

### Repository QA endpoint

`tools/dev/check` answers only:

> Is the repository-local deterministic state structurally and mechanically valid for the exact state under test?

It covers code/tests/schema/fixtures/formatting and remains network-free. `DEV_CHECK_PASS` does not establish scientific truth or acceptance.

### Research QA endpoint

`tools/research/check` answers only:

> Did this experiment satisfy the declared research contract for provenance, preregistration, controls, reproducibility, and claim boundaries?

It must be deterministic for the same committed experiment inputs and emit a machine-readable research-QA receipt.

The first version should validate at least:

1. exact source commit and experiment identity;
2. frozen fixture and parameter hashes;
3. declared hypothesis / question / falsifiers;
4. declared metrics before result interpretation;
5. positive, negative, and topology-only controls;
6. receipt schema and complete observed values;
7. explicit domain-model limitations;
8. independent witness status when the experiment requires one;
9. scientific disposition vocabulary;
10. separation between automated QA status and scientific judgment.

Recommended output dimensions:

- `contract_status`: PASS / FAIL / DEGRADED / UNKNOWN;
- `epistemic_state`: FACT / INFERENCE / HYPOTHESIS / UNVERIFIED / DEGRADED;
- `scientific_disposition`: FOUND_USEFUL_STRUCTURE / NO_SIGNAL / REFINE / REJECT / UNKNOWN_WITHIN_CURRENT_CONTRACT;
- `authority`: NONE for automated QA.

A `contract_status=PASS` means only that the experiment satisfied its declared research contract. It must never be rendered as `hypothesis=true`, `scientific_truth=PASS`, or an automatic promotion decision.

## 9.2. KnowledgeOps-derived research QA framework

The research-QA lifecycle reuses the existing Theseus KnowledgeOps shape:

```text
question / hypothesis
    -> preregistered experiment contract
    -> provenance + normalization
    -> schema / structural checks
    -> controls + domain-specific witness
    -> contradiction / falsifier handling
    -> independent verification when required
    -> explicit scientific disposition
    -> durable receipt
    -> drift / invalidation / learning loop
```

This deliberately mirrors informational CI/CD without pretending that automation can decide scientific truth.

Research-QA meta-lenses inherited from current Theseus practice:

- **BOUNDARY** — did representation or serialization weaken evidence/identity?
- **PHASE** — is a consumer evaluating only produced and verified state?
- **CLAIM** — did the verifier observe exactly the proposition being marked PASS/FOUND/VERIFIED?
- **AUTHORITY** — is a tool result being confused with permission or acceptance?
- **PROVENANCE** — are observations bound to exact source/input/model/profile identities?

Known-failure-class tracking should be local to the lab once repeated defects exist. Do not invent failure classes speculatively.

## 9.3. Advisory semantic QA

The existing Theseus semantic-QA research provides optional attention-routing witnesses:

- Semble-style known-failure retrieval;
- semdup-style semantic duplication witness;
- Needle-style alternative embedding/retrieval trace.

These are **not** required for bootstrap and are not correctness gates. They may be added only after the lab has a real failure-class corpus or repeated research-review scars worth retrieving.

Any semantic witness must preserve:

- exact tool/model/profile identity;
- candidate/source SHA;
- corpus digest;
- named UNAVAILABLE/DEGRADED states;
- authority = NONE.

Current Theseus precedent remains `KEEP_ADVISORY_NO_SEMANTIC_GATE`.

## 10. Scientific falsifiers

Park or reject the common-invariant hypothesis if:

- the same operator family does not reproduce even qualitative threshold behavior across substrates;
- useful discrimination comes entirely from substrate-specific mechanisms and the shared metrics add no value;
- `rho(K)` becomes a decorative statistic disconnected from observed deterministic behavior;
- diversity/monoculture conclusions depend on one arbitrary metric choice;
- the common model erases the mechanisms that matter enough to make the comparison misleading;
- a simpler domain-specific baseline explains the results more cheaply.

Negative results are first-class.

## 11. GitHub Project design

Create one public user Project named `Theseus — Transmission Ecology Lab` after repository creation.

Project description should state that Git, issue acceptance criteria, CI receipts, and independent verification remain authority; the Project is only a coordination view.

Reuse established Theseus roadmap conventions:

- `Status`: Todo / In Progress / Done;
- `Priority`: P0 / P1 / P2 / P3;
- `Maturity`: Proposed / Active / Verified / Parked / Rejected;
- `Area`: Program / Graph-Spectral / Virus / Meme / Agent / Hodge-HigherOrder / QA / Literature / Tooling.

Initial roadmap issues after bootstrap:

1. Bootstrap repository and canonical `tools/dev/check`;
2. Freeze shared graph fixture and receipt schema;
3. Implement shared spectral/diversity metrics;
4. Implement virus linearized adapter;
5. Implement meme linearized adapter;
6. Implement agent linearized adapter;
7. Add threshold and topology-only controls;
8. Run independent spectral/Hodge cross-check;
9. Record deterministic v0 disposition;
10. Decide whether stochastic/nonlinear v1 earns promotion.

Item 10 starts `Proposed` and must not become `Active` until item 9 records a disposition.


## 11.1. Roadmap amendment for research QA

Add an explicit roadmap item immediately after repository bootstrap:

**Research QA: implement canonical `tools/research/check` contract and machine-readable receipt schema.**

This item is P0 / Area=QA / Maturity=Proposed at Project creation and becomes Active before substrate-specific adapters are considered research-ready.

The existing `tools/dev/check` bootstrap item remains separate. Neither endpoint substitutes for the other.

## 12. Source relationships

- `theseus-research#72` remains the parent research-line coordination/evidence issue.
- `theseus-research#37` supplies the topology-only negative precedent and verified graph/Hodge identities.
- `theseus-repo-search-lab` supplies graph-contract patterns but is not a runtime dependency.
- the existing research notebook `From Viruses to Ideas to Agents` remains an editorial/research scratchpad, not code authority.

## 13. Bootstrap sequence after design approval

1. Create the public repository with only README/license/basic metadata.
2. Create the dedicated GitHub Project and fields.
3. Open the ten initial roadmap issues and add them to the Project.
4. Add the repository skeleton through the normal reviewed branch/PR path.
5. Run local QA and hosted CI.
6. Verify repository, Project, issue set, and merged bootstrap commit by remote readback.

Repository creation and Project creation are operational bootstrap, not scientific acceptance.

## 14. Success condition for deterministic v0

v0 is complete when the same frozen graph and receipt contract run all three substrate adapters, controls behave as preregistered, one independent mathematical route reproduces a selected metric, and a disposition is recorded without post-hoc changing the success criteria.