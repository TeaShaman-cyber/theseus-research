# Transmission Ecology Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap `TeaShaman-cyber/theseus-transmission-ecology-lab`, its GitHub Project roadmap, dual QA endpoints, and a reproducible deterministic v0 comparing virus, meme, and agent transmission on one frozen graph.

**Architecture:** The lab uses one immutable directed weighted graph fixture and three substrate adapters that each build a linear next-generation operator `K_s`. A shared runner computes spectral, topology-control, diversity, convergence, and perturbation metrics into deterministic receipts. Repository QA (`tools/dev/check`) and research-contract QA (`tools/research/check`) remain separate, and automated checks have no scientific acceptance authority.

**Tech Stack:** Python 3.11+, stdlib `unittest`, NumPy for matrix/eigenvalue operations, JSON fixtures/receipts, POSIX shell entrypoints, GitHub Actions, GitHub Projects V2, independent Wolfram Language witness.

**Spec:** `docs/superpowers/specs/2026-09-22-transmission-ecology-lab-design.md`

## Global Constraints

- Repository name is exactly `TeaShaman-cyber/theseus-transmission-ecology-lab`.
- Deterministic v0 only; stochastic, nonlinear, reassortment/coinfection, complex-contagion, simplicial/hypergraph, graph-rewiring, learned-parameter, and dashboard work are out of scope.
- One frozen shared graph fixture must be used by all three substrate adapters.
- `tools/dev/check` is the canonical network-free repository QA endpoint.
- `tools/research/check` is the canonical deterministic research-contract QA endpoint.
- `research QA PASS != scientific truth`; automated QA authority is always `NONE`.
- `cycle_rank_beta1` is a topology control, not a success classifier.
- Negative results are first-class; deterministic v0 disposition is one of `FOUND_USEFUL_STRUCTURE`, `NO_SIGNAL`, `REFINE`, `REJECT`, `UNKNOWN_WITHIN_CURRENT_CONTRACT`.
- External witnesses may verify selected mathematical claims but must not be required for ordinary local repository QA.
- Git, issue acceptance criteria, CI receipts, and exact readback remain authority; the GitHub Project is coordination state only.
- Do not choose or add a repository license automatically. Current sibling Theseus repositories have no canonical license file; any future license selection requires explicit user authority.

## Review Focus

- A graph fixture with duplicate nodes, dangling edges, or nonpositive/NaN weights must fail closed instead of producing metrics; pin this in Task 3 graph validation tests.
- A transmission operator containing NaN/Inf/negative entries or shape inconsistent with `N * M` must be rejected before simulation; pin this in Task 4 state/operator tests.
- Entropy and dominant-share metrics must handle zero total mass without NaN/division-by-zero; pin this in Task 5 metric tests.
- Research QA must not return PASS when the run receipt, independent witness, exact commit binding, or required control result is absent/mismatched; pin this in Task 2 research-QA negative tests.
- Same graph plus two parameterizations on opposite sides of `rho(K)=1` must produce opposite control behavior, proving topology alone is insufficient; pin this in Task 7 control tests.

---

## File Structure

The new repository owns these files after v0:

```text
README.md
CHANGELOG.md
pyproject.toml
.gitignore
src/transmission_ecology/
  __init__.py
  graph.py              # graph schema, validation, adjacency, beta_1
  state.py              # operator validation and deterministic evolution
  metrics.py            # spectral/diversity/convergence/perturbation metrics
  receipt.py            # canonical JSON serialization, hashes, Git provenance
  research_qa.py        # research-contract validator and QA receipt
  cli.py                # run-v0 CLI only
  models/
    __init__.py
    base.py              # substrate protocol and shared operator builder
    virus.py
    meme.py
    agent.py
experiments/v0/
  contract.json
  shared-graph.json
  controls.json
  parameters/
    virus.json
    meme.json
    agent.json
receipts/reference/
  v0-virus.json
  v0-meme.json
  v0-agent.json
  v0-controls.json
receipts/independent/
  wolfram-v0.json
receipts/research-qa/
  v0.json
tests/
  test_graph.py
  test_state.py
  test_metrics.py
  test_receipt.py
  test_research_qa.py
  test_models.py
  test_runner.py
  test_controls.py
tools/dev/check
tools/research/check
tools/run-v0
.github/workflows/qa.yml
.github/workflows/v0-replay.yml
docs/methodology.md
docs/epistemic-boundary.md
docs/v0-disposition.md
```

---

### Task 1: Create the repository, Project, and traceable roadmap

**Files:**
- Create remotely: `TeaShaman-cyber/theseus-transmission-ecology-lab`
- Create remotely: GitHub Project `Theseus — Transmission Ecology Lab`
- Create remotely: eleven roadmap issues in the new repository
- Modify: `TeaShaman-cyber/theseus-research#72` with exact bootstrap receipt after readback

**Interfaces:**
- Consumes: approved design spec and existing `theseus-research#72`.
- Produces: repository URL, Project number/URL, roadmap issue URLs, field vocabulary, exact remote bootstrap receipt.

- [ ] **Step 1: Re-probe mutation capabilities and absence of the target repository/project**

Run:

```bash
GH=/workspace/.local/bin/gh
[ -x "$GH" ] || GH=/usr/local/bin/gh
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" auth status -h github.com
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" repo view TeaShaman-cyber/theseus-transmission-ecology-lab --json nameWithOwner,url 2>/dev/null && exit 20 || true
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project list --owner TeaShaman-cyber --format json > /tmp/transmission-projects.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/transmission-projects.json'))
matches=[p for p in d.get('projects',[]) if p.get('title')=='Theseus — Transmission Ecology Lab']
assert not matches, matches
PY
```

Expected: authenticated write profile; repository and named Project do not already exist. If either exists, stop and inspect rather than duplicate.

- [ ] **Step 2: Create an intentionally minimal public repository**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" repo create TeaShaman-cyber/theseus-transmission-ecology-lab \
  --public \
  --description "Reproducible cross-substrate transmission ecology experiments for virus, meme, and agent systems." \
  --disable-wiki
```

Do not pass `--license`; license selection is not delegated.

- [ ] **Step 3: Independently read back repository identity and visibility**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" repo view TeaShaman-cyber/theseus-transmission-ecology-lab \
  --json nameWithOwner,url,visibility,hasIssuesEnabled,hasWikiEnabled,description
```

Expected: exact repository identity, `PUBLIC`, issues enabled, wiki disabled, exact description.

- [ ] **Step 4: Create the public GitHub Project and metadata**

Run:

```bash
project_json=$(GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project create \
  --owner TeaShaman-cyber --title "Theseus — Transmission Ecology Lab" --format json)
printf '%s\n' "$project_json" > /tmp/transmission-project.json
project_number=$(python3 - <<'PY'
import json
print(json.load(open('/tmp/transmission-project.json'))['number'])
PY
)
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project edit "$project_number" --owner TeaShaman-cyber \
  --visibility PUBLIC \
  --description "Prioritized roadmap for deterministic cross-substrate transmission experiments, research QA, independent mathematical verification, and v0 disposition." \
  --readme "Coordination view for TeaShaman-cyber/theseus-transmission-ecology-lab. Git, issue acceptance criteria, CI receipts, independent verification, and explicit scientific disposition remain authority; this Project is not scientific acceptance authority."
```

- [ ] **Step 5: Add roadmap fields using established Theseus vocabulary**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project field-create "$project_number" --owner TeaShaman-cyber \
  --name Priority --data-type SINGLE_SELECT --single-select-options P0,P1,P2,P3
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project field-create "$project_number" --owner TeaShaman-cyber \
  --name Maturity --data-type SINGLE_SELECT --single-select-options Proposed,Active,Verified,Parked,Rejected
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project field-create "$project_number" --owner TeaShaman-cyber \
  --name Area --data-type SINGLE_SELECT \
  --single-select-options Program,Graph-Spectral,Virus,Meme,Agent,Hodge-HigherOrder,QA,Literature,Tooling
```

- [ ] **Step 6: Create the eleven roadmap issues with exact titles**

Create these issues in this order:

```text
1  Bootstrap repository and canonical tools/dev/check
2  Research QA: canonical tools/research/check contract and receipt
3  Freeze shared graph fixture and experiment contract
4  Implement shared spectral, topology, diversity, and perturbation metrics
5  Implement deterministic virus adapter
6  Implement deterministic meme adapter
7  Implement deterministic agent adapter
8  Add threshold and topology-only negative controls
9  Add independent spectral/Hodge cross-check
10 Record deterministic v0 disposition
11 Decide whether stochastic/nonlinear v1 earns promotion
```

Each issue body must include: motivation, intended invariant, acceptance criteria, explicit non-goals, and authority boundary. Issue 11 must state that it cannot become `Active` before issue 10 records a disposition.

- [ ] **Step 7: Add every issue to the Project and set initial fields**

Use `gh project item-add` for each issue URL. Set `Status=Todo` and `Maturity=Proposed` for all items. Set `Priority=P0` for issues 1-4 and 8-10, `P1` for issues 5-7, and `P2` for issue 11. Set areas respectively:

```text
1 Tooling
2 QA
3 Graph-Spectral
4 Graph-Spectral
5 Virus
6 Meme
7 Agent
8 QA
9 Hodge-HigherOrder
10 Program
11 Program
```

Use:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project item-add "$project_number" --owner TeaShaman-cyber --url "$issue_url"
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project item-edit "$project_number" --owner TeaShaman-cyber --url "$issue_url" --field Status --value Todo
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project item-edit "$project_number" --owner TeaShaman-cyber --url "$issue_url" --field Priority --value P0
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project item-edit "$project_number" --owner TeaShaman-cyber --url "$issue_url" --field Maturity --value Proposed
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project item-edit "$project_number" --owner TeaShaman-cyber --url "$issue_url" --field Area --value QA
```

Replace only the issue URL, priority, and area with the declared per-issue values.

- [ ] **Step 8: Read back the repository, Project fields, and all eleven items**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" repo view TeaShaman-cyber/theseus-transmission-ecology-lab --json nameWithOwner,url,visibility
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project view "$project_number" --owner TeaShaman-cyber --format json
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project field-list "$project_number" --owner TeaShaman-cyber --format json
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" project item-list "$project_number" --owner TeaShaman-cyber --format json --limit 100
```

Expected: exact repo, public Project, fields `Status/Priority/Maturity/Area`, exactly eleven new roadmap items.

- [ ] **Step 9: Comment on `theseus-research#72` with observed bootstrap identifiers**

Record only observed repository URL, Project URL/number, issue URLs, and readback status. Do not mark scientific acceptance.

---

### Task 2: Bootstrap package layout and canonical repository QA

**Files:**
- Create: `README.md`
- Create: `CHANGELOG.md`
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `src/transmission_ecology/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/test_dev_check.py`
- Create: `tools/dev/check`
- Create: `.github/workflows/qa.yml`

**Interfaces:**
- Consumes: repository from Task 1.
- Produces: installable Python package skeleton and network-free `tools/dev/check` ending in `DEV_CHECK_PASS`.

- [ ] **Step 1: Clone the empty repository and create an initial bootstrap branch**

Run:

```bash
cd /workspace
git clone https://github.com/TeaShaman-cyber/theseus-transmission-ecology-lab.git
cd theseus-transmission-ecology-lab
git switch -c research/deterministic-v0
```

- [ ] **Step 2: Write the failing QA endpoint test**

`tests/test_dev_check.py`:

```python
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DevCheckTests(unittest.TestCase):
    def test_dev_check_exists_is_executable_and_has_terminal_pass_marker(self):
        check = ROOT / "tools" / "dev" / "check"
        self.assertTrue(check.is_file())
        self.assertTrue(check.stat().st_mode & 0o111)
        text = check.read_text(encoding="utf-8")
        self.assertIn("DEV_CHECK_PASS", text)

    def test_dev_check_passes_on_clean_repo(self):
        result = subprocess.run(
            [str(ROOT / "tools" / "dev" / "check")],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DEV_CHECK_PASS", result.stdout)
```

- [ ] **Step 3: Run the test and verify RED**

Run: `python3 -m unittest tests.test_dev_check -v`

Expected: FAIL because `tools/dev/check` does not exist.

- [ ] **Step 4: Add minimal package metadata and QA script**

`pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "theseus-transmission-ecology"
version = "0.1.0"
description = "Deterministic cross-substrate transmission ecology experiments."
requires-python = ">=3.11"
dependencies = ["numpy>=1.26,<3"]

[project.scripts]
transmission-ecology = "transmission_ecology.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
```

`tools/dev/check`:

```sh
#!/bin/sh
set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  printf '%s\n' 'dev-check: not inside a Git worktree' >&2
  exit 2
}
cd "$ROOT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPYCACHEPREFIX="${THESEUS_TRANSMISSION_DEV_CACHE:-/tmp/theseus-transmission-dev}/pycache"
mkdir -p "$PYTHONPYCACHEPREFIX"

printf '%s\n' '== unit tests =='
python3 -m unittest discover -s tests -p 'test_*.py'

printf '%s\n' '== python syntax =='
python3 -m compileall -q src tests

printf '%s\n' '== json fixtures =='
find experiments receipts -type f -name '*.json' -print 2>/dev/null | sort | while IFS= read -r path; do
  python3 -m json.tool "$path" >/dev/null
done

printf '%s\n' '== whitespace =='
git diff --check
git diff --cached --check

printf '%s\n' 'DEV_CHECK_PASS'
```

Make executable: `chmod +x tools/dev/check`.

- [ ] **Step 5: Add README boundary text and baseline changelog**

`README.md` must state:

```text
This repository tests whether selected transmission-dynamics invariants survive a substrate change from virus to meme to AI-agent systems.

It does not claim biological, cultural, and agent systems are identical.
`tools/dev/check` verifies repository mechanics.
`tools/research/check` verifies the declared research contract.
Neither endpoint has scientific acceptance authority.
```

`CHANGELOG.md` starts with `## Unreleased` and records bootstrap only.

- [ ] **Step 6: Add canonical lightweight CI**

`.github/workflows/qa.yml`:

```yaml
name: qa
on:
  pull_request:
  push:
    branches: [main]
jobs:
  dev-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install -e .
      - run: tools/dev/check
```

- [ ] **Step 7: Run QA and commit**

Run:

```bash
python3 -m pip install -e .
tools/dev/check
git add README.md CHANGELOG.md .gitignore pyproject.toml src tests tools .github
git commit -m "chore: bootstrap transmission ecology lab"
```

Expected: `DEV_CHECK_PASS`.

---

### Task 3: Add the canonical research QA contract and endpoint

**Files:**
- Create: `experiments/v0/contract.json`
- Create: `src/transmission_ecology/research_qa.py`
- Create: `tests/test_research_qa.py`
- Create: `tools/research/check`
- Create: `docs/epistemic-boundary.md`

**Interfaces:**
- Consumes: experiment contract JSON and later run/witness receipts.
- Produces: `evaluate_research_contract(contract, run_receipts, witness) -> dict` and executable `tools/research/check`.

- [ ] **Step 1: Write negative-first research QA tests**

`tests/test_research_qa.py`:

```python
import unittest

from transmission_ecology.research_qa import evaluate_research_contract


BASE_CONTRACT = {
    "schema_version": 1,
    "experiment_id": "deterministic-v0",
    "question": "Which declared invariants survive substrate change?",
    "hypothesis": "Selected operator-level invariants remain comparable across substrates.",
    "falsifiers": ["shared metrics add no value beyond domain-specific baselines"],
    "declared_metrics": ["spectral_radius", "cycle_rank_beta1"],
    "required_controls": ["subcritical", "supercritical", "topology_only"],
    "limitations": ["linear deterministic model only"],
    "independent_witness": {"required": True, "kind": "spectral_or_hodge"},
}


class ResearchQATests(unittest.TestCase):
    def test_missing_run_receipts_is_unknown_not_pass(self):
        out = evaluate_research_contract(BASE_CONTRACT, {}, None, source_commit="a" * 40)
        self.assertEqual(out["contract_status"], "UNKNOWN")
        self.assertEqual(out["authority"], "NONE")

    def test_missing_required_witness_is_unknown_not_pass(self):
        runs = {
            "virus": {"source_commit": "a" * 40, "controls": {"all_passed": True}},
            "meme": {"source_commit": "a" * 40, "controls": {"all_passed": True}},
            "agent": {"source_commit": "a" * 40, "controls": {"all_passed": True}},
        }
        out = evaluate_research_contract(BASE_CONTRACT, runs, None, source_commit="a" * 40)
        self.assertEqual(out["contract_status"], "UNKNOWN")

    def test_commit_mismatch_fails_closed(self):
        runs = {
            name: {"source_commit": "b" * 40, "controls": {"all_passed": True}}
            for name in ("virus", "meme", "agent")
        }
        witness = {"source_commit": "a" * 40, "status": "VERIFIED"}
        out = evaluate_research_contract(BASE_CONTRACT, runs, witness, source_commit="a" * 40)
        self.assertEqual(out["contract_status"], "FAIL")

    def test_complete_contract_can_pass_without_claiming_truth(self):
        runs = {
            name: {"source_commit": "a" * 40, "controls": {"all_passed": True}}
            for name in ("virus", "meme", "agent")
        }
        witness = {"source_commit": "a" * 40, "status": "VERIFIED"}
        out = evaluate_research_contract(BASE_CONTRACT, runs, witness, source_commit="a" * 40)
        self.assertEqual(out["contract_status"], "PASS")
        self.assertEqual(out["authority"], "NONE")
        self.assertNotIn("scientific_truth", out)
```

- [ ] **Step 2: Run RED**

Run: `python3 -m unittest tests.test_research_qa -v`

Expected: import failure because `research_qa.py` does not exist.

- [ ] **Step 3: Implement the minimal research QA state machine**

`src/transmission_ecology/research_qa.py` must:

```python
REQUIRED_RUNS = ("virus", "meme", "agent")


def evaluate_research_contract(contract, run_receipts, witness, *, source_commit):
    required = ("question", "hypothesis", "falsifiers", "declared_metrics",
                "required_controls", "limitations", "independent_witness")
    missing = [key for key in required if not contract.get(key)]
    if missing:
        return {"contract_status": "FAIL", "authority": "NONE",
                "reason": "missing_contract_fields", "missing": missing}

    absent = [name for name in REQUIRED_RUNS if name not in run_receipts]
    if absent:
        return {"contract_status": "UNKNOWN", "authority": "NONE",
                "reason": "missing_run_receipts", "missing": absent}

    if any(r.get("source_commit") != source_commit for r in run_receipts.values()):
        return {"contract_status": "FAIL", "authority": "NONE",
                "reason": "source_commit_mismatch"}

    if any(not r.get("controls", {}).get("all_passed") for r in run_receipts.values()):
        return {"contract_status": "FAIL", "authority": "NONE",
                "reason": "required_control_failed"}

    if contract["independent_witness"].get("required"):
        if witness is None:
            return {"contract_status": "UNKNOWN", "authority": "NONE",
                    "reason": "independent_witness_missing"}
        if witness.get("source_commit") != source_commit:
            return {"contract_status": "FAIL", "authority": "NONE",
                    "reason": "witness_commit_mismatch"}
        if witness.get("status") != "VERIFIED":
            return {"contract_status": "DEGRADED", "authority": "NONE",
                    "reason": "witness_not_verified"}

    return {
        "contract_status": "PASS",
        "epistemic_state": "HYPOTHESIS",
        "scientific_disposition": "UNKNOWN_WITHIN_CURRENT_CONTRACT",
        "authority": "NONE",
        "source_commit": source_commit,
    }
```

- [ ] **Step 4: Freeze `experiments/v0/contract.json` before result generation**

The file must declare exactly the question, hypothesis, falsifiers, metrics, required controls, model limitations, and required independent `spectral_or_hodge` witness from the approved spec. Its Git blob hash becomes part of every run receipt.

- [ ] **Step 5: Add `tools/research/check` wrapper**

The wrapper reads `experiments/v0/contract.json`, the three reference run receipts, `receipts/independent/wolfram-v0.json`, obtains `git rev-parse HEAD`, writes `receipts/research-qa/v0.json`, prints its JSON, and exits:

```text
0  PASS
1  FAIL
2  UNKNOWN or DEGRADED
```

Before reference receipts exist, `tools/research/check` must exit 2 with `contract_status=UNKNOWN`; that is an expected incomplete state, not repository QA failure.

- [ ] **Step 6: Run focused tests and repository QA**

Run:

```bash
python3 -m unittest tests.test_research_qa -v
tools/dev/check
```

Expected: tests PASS; repository QA PASS; research endpoint may remain `UNKNOWN` until later tasks create receipts.

- [ ] **Step 7: Commit**

Run:

```bash
git add experiments/v0/contract.json src/transmission_ecology/research_qa.py tests/test_research_qa.py tools/research/check docs/epistemic-boundary.md
git commit -m "feat: add canonical research QA contract"
```

---

### Task 4: Freeze the graph contract and deterministic state evolution

**Files:**
- Create: `experiments/v0/shared-graph.json`
- Create: `src/transmission_ecology/graph.py`
- Create: `src/transmission_ecology/state.py`
- Create: `tests/test_graph.py`
- Create: `tests/test_state.py`

**Interfaces:**
- Produces: `load_graph(path) -> GraphFixture`, `adjacency_matrix(graph) -> np.ndarray`, `cycle_rank_beta1(graph) -> int`, `validate_operator(K, state_size)`, `simulate(K, x0, horizon) -> list[np.ndarray]`.

- [ ] **Step 1: Write graph validation and beta_1 tests**

Use the frozen graph:

```json
{
  "schema_version": 1,
  "graph_id": "shared-v0",
  "nodes": ["n1", "n2", "n3", "n4"],
  "edges": [
    {"source": "n1", "target": "n2", "weight": 1.0},
    {"source": "n2", "target": "n3", "weight": 1.0},
    {"source": "n3", "target": "n1", "weight": 1.0},
    {"source": "n3", "target": "n4", "weight": 1.0},
    {"source": "n4", "target": "n1", "weight": 1.0}
  ]
}
```

`tests/test_graph.py` must assert:

```python
self.assertEqual(cycle_rank_beta1(graph), 2)
self.assertEqual(adjacency_matrix(graph).shape, (4, 4))
```

and must reject duplicate node IDs, dangling edge endpoints, weight `0`, negative weight, `float('nan')`, and `float('inf')`.

- [ ] **Step 2: Run graph tests RED, then implement graph validation**

Run: `python3 -m unittest tests.test_graph -v`

Implement an immutable `GraphFixture` dataclass and weak-component count over the underlying undirected graph using stdlib sets/queues. Compute `beta_1 = E - N + P` only after successful validation.

- [ ] **Step 3: Write operator/state tests**

`tests/test_state.py` must include:

```python
def test_simulate_linear_operator(self):
    K = np.array([[0.0, 0.5], [0.5, 0.0]])
    x0 = np.array([1.0, 0.0])
    states = simulate(K, x0, horizon=2)
    np.testing.assert_allclose(states[-1], np.array([0.25, 0.0]))
```

and reject wrong shape, negative entries, NaN/Inf, negative initial state, and negative horizon.

- [ ] **Step 4: Implement state evolution minimally**

`simulate` returns `[x0, x1, ..., x_horizon]` using exactly `x_{t+1}=K @ x_t` with no hidden normalization.

- [ ] **Step 5: Run focused tests, full QA, commit**

Run:

```bash
python3 -m unittest tests.test_graph tests.test_state -v
tools/dev/check
git add experiments/v0/shared-graph.json src/transmission_ecology/graph.py src/transmission_ecology/state.py tests/test_graph.py tests/test_state.py
git commit -m "feat: add frozen graph and deterministic state evolution"
```

---

### Task 5: Implement shared metrics and deterministic perturbation

**Files:**
- Create: `src/transmission_ecology/metrics.py`
- Create: `tests/test_metrics.py`

**Interfaces:**
- Consumes: validated `K`, simulation states, `GraphFixture`, `variant_count`.
- Produces: `spectral_radius(K)`, `variant_shannon_entropy(state, node_count, variant_count)`, `dominant_variant_share(...)`, `surviving_variant_count(...)`, `perturbation_recovery_ratio(...)`, `summarize_run(...)`.

- [ ] **Step 1: Write RED metric tests**

Required tests:

```python
self.assertAlmostEqual(spectral_radius(np.diag([0.5, 1.25])), 1.25)
self.assertEqual(variant_shannon_entropy(np.zeros(4), node_count=2, variant_count=2), 0.0)
self.assertEqual(dominant_variant_share(np.zeros(4), node_count=2, variant_count=2), 0.0)
self.assertEqual(surviving_variant_count(np.array([1.0, 0.0, 0.5, 0.0]), 2, 2), 1)
```

Add a perturbation test where knocking out the dominant variant yields a finite ratio in `[0, 1]` for a nonnegative linear system.

- [ ] **Step 2: Implement metrics with explicit zero-mass behavior**

Entropy uses natural logarithms over positive normalized variant mass; zero total mass returns `0.0`. Dominant share and recovery ratio return `0.0` when their denominator is zero. Reject nonfinite inputs.

- [ ] **Step 3: Run focused tests, full QA, commit**

Run:

```bash
python3 -m unittest tests.test_metrics -v
tools/dev/check
git add src/transmission_ecology/metrics.py tests/test_metrics.py
git commit -m "feat: add shared transmission metrics"
```

---

### Task 6: Implement the three substrate adapters on one shared operator interface

**Files:**
- Create: `src/transmission_ecology/models/__init__.py`
- Create: `src/transmission_ecology/models/base.py`
- Create: `src/transmission_ecology/models/virus.py`
- Create: `src/transmission_ecology/models/meme.py`
- Create: `src/transmission_ecology/models/agent.py`
- Create: `experiments/v0/parameters/virus.json`
- Create: `experiments/v0/parameters/meme.json`
- Create: `experiments/v0/parameters/agent.json`
- Create: `tests/test_models.py`

**Interfaces:**
- Produces: `build_operator(graph, params) -> np.ndarray` for each substrate.
- Shared base function: `kron_operator(graph_adjacency, variant_transition, scale, variant_fitness=None) -> np.ndarray`.

- [ ] **Step 1: Write adapter contract tests before implementations**

Use two variants in all three adapters. Assert each operator has shape `(8, 8)`, is finite/nonnegative, and preserves the exact shared graph support at block level.

Parameter fixtures:

`virus.json`:

```json
{"schema_version":1,"variants":["v0","v1"],"transmission_scale":0.85,"variant_transition":[[0.99,0.02],[0.01,0.98]],"recovery_loss":0.0}
```

`meme.json`:

```json
{"schema_version":1,"variants":["m0","m1"],"transmission_scale":0.65,"variant_transition":[[0.90,0.15],[0.10,0.85]],"attention_retention":1.0}
```

`agent.json`:

```json
{"schema_version":1,"variants":["a0","a1"],"transmission_scale":0.90,"variant_transition":[[0.95,0.08],[0.05,0.92]],"evaluator_weights":[1.0,0.95]}
```

- [ ] **Step 2: Run model tests RED**

Run: `python3 -m unittest tests.test_models -v`

- [ ] **Step 3: Implement the shared Kronecker-product builder**

Use node-major state ordering and `K = kron(A, V) * scale`; if variant fitness is supplied, left-multiply each target-variant block by the declared nonnegative fitness weight. The base builder validates that every column of `V` sums to `1` within `1e-12`.

- [ ] **Step 4: Keep substrate semantics explicit and narrow**

`virus.py` interprets scale/transition as linearized transmission plus mutation and states in its module docstring that reassortment and coinfection are not modeled.

`meme.py` states that reconstruction is represented only by the linear transition matrix; repeated-exposure complex contagion is not modeled.

`agent.py` states that local adaptation is represented by the transition matrix and evaluator weights; multi-artifact composition is not modeled.

- [ ] **Step 5: Run tests, QA, commit**

Run:

```bash
python3 -m unittest tests.test_models -v
tools/dev/check
git add src/transmission_ecology/models experiments/v0/parameters tests/test_models.py
git commit -m "feat: add deterministic substrate adapters"
```

---

### Task 7: Add deterministic controls, runner, and canonical run receipts

**Files:**
- Create: `experiments/v0/controls.json`
- Create: `src/transmission_ecology/receipt.py`
- Create: `src/transmission_ecology/cli.py`
- Create: `tests/test_receipt.py`
- Create: `tests/test_runner.py`
- Create: `tests/test_controls.py`
- Create: `tools/run-v0`
- Generate and commit: `receipts/reference/v0-virus.json`
- Generate and commit: `receipts/reference/v0-meme.json`
- Generate and commit: `receipts/reference/v0-agent.json`
- Generate and commit: `receipts/reference/v0-controls.json`

**Interfaces:**
- Produces: `run_substrate(name, graph_path, params_path, horizon, source_commit) -> dict` and stable JSON receipt serialization.

- [ ] **Step 1: Write receipt determinism and provenance tests**

Assert two serializations of the same Python object are byte-identical using `json.dumps(..., sort_keys=True, separators=(",", ":")) + "\n"`.

Each substrate receipt must contain:

```text
schema_version
experiment_id
source_commit
contract_sha256
graph_sha256
parameters_sha256
substrate
horizon
metrics
controls
scientific_authority
```

and `scientific_authority` must equal `NONE`.

- [ ] **Step 2: Write threshold/topology negative-control tests**

Take one base operator on the frozen graph and scale it to target radii `0.8` and `1.2`:

```python
def scale_to_radius(K, target):
    rho = spectral_radius(K)
    if rho <= 0:
        raise ValueError("cannot scale zero-radius operator")
    return K * (target / rho)
```

Assertions:

```python
self.assertLess(spectral_radius(K_low), 1.0)
self.assertGreater(spectral_radius(K_high), 1.0)
self.assertLess(low_states[-1].sum(), low_states[0].sum())
self.assertGreater(high_states[-1].sum(), high_states[0].sum())
self.assertEqual(cycle_rank_beta1(graph), 2)
```

This is the required topology-only negative control: graph shape remains identical while dynamics change.

- [ ] **Step 3: Implement the runner**

`tools/run-v0` invokes:

```sh
#!/bin/sh
set -eu
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m transmission_ecology.cli run-v0 --horizon 8 --write-reference
```

`cli.py` loads the one graph, runs virus/meme/agent adapters from their parameter files, runs the three controls, computes metrics, and writes the four reference receipts atomically via temp-file + `os.replace`.

- [ ] **Step 4: Run runner twice and prove deterministic bytes**

Run:

```bash
tools/run-v0
sha256sum receipts/reference/*.json > /tmp/v0-a.sha
tools/run-v0
sha256sum receipts/reference/*.json > /tmp/v0-b.sha
diff -u /tmp/v0-a.sha /tmp/v0-b.sha
```

Expected: no diff.

- [ ] **Step 5: Run controls, full QA, commit**

Run:

```bash
python3 -m unittest tests.test_receipt tests.test_runner tests.test_controls -v
tools/dev/check
git add experiments/v0/controls.json src/transmission_ecology/receipt.py src/transmission_ecology/cli.py tests/test_receipt.py tests/test_runner.py tests/test_controls.py tools/run-v0 receipts/reference
git commit -m "feat: add deterministic v0 runner and controls"
```

---

### Task 8: Add independent Wolfram spectral/Hodge witness

**Files:**
- Create: `receipts/independent/wolfram-v0.json`
- Create: `docs/methodology.md`
- Test: `tests/test_research_qa.py`

**Interfaces:**
- Consumes: exact committed `shared-graph.json`, control operator values, and source commit from Task 7.
- Produces: independently observed spectral radius / beta_1 witness bound to the exact source commit.

- [ ] **Step 1: Freeze the exact witness question before invoking Wolfram**

Record in `docs/methodology.md`:

```text
For the committed shared-v0 graph and the committed subcritical/supercritical control matrices, independently compute:
1. E - N + P for the underlying undirected graph;
2. rank/nullity of the incidence matrix confirming beta_1;
3. spectral radius of both control matrices;
4. verify low radius < 1 and high radius > 1.
Do not interpret these computations as evidence that the three substrates are scientifically isomorphic.
```

- [ ] **Step 2: Obtain Wolfram context then evaluate the exact matrices**

Use the connected Wolfram route in this order:

```text
mcp__Wolfram__WolframContext
mcp__Wolfram__WolframLanguageEvaluator
```

The evaluator expression must construct the matrices from exact committed numeric values; do not paste precomputed expected outputs as the computation.

- [ ] **Step 3: Write a bounded witness receipt from observed Wolfram output**

`receipts/independent/wolfram-v0.json` contains:

```json
{
  "schema_version": 1,
  "source_commit": "<exact 40-hex commit observed at execution>",
  "status": "VERIFIED",
  "authority": "NONE",
  "backend": "WolframLanguageEvaluator",
  "checks": {
    "cycle_rank_beta1": 2,
    "subcritical_radius_lt_1": true,
    "supercritical_radius_gt_1": true
  }
}
```

The executor replaces the commit field only with the observed exact commit. If Wolfram is unavailable or disagrees, write `status=DEGRADED` or do not create a verified witness; never fabricate success.

- [ ] **Step 4: Extend research-QA tests for witness mismatch/degradation**

Add tests asserting `DEGRADED` witness cannot produce `contract_status=PASS` and a mismatched witness commit yields `FAIL`.

- [ ] **Step 5: Run repository QA and the research endpoint**

Run:

```bash
tools/dev/check
tools/research/check
```

Expected after a verified witness and matching reference receipts: `contract_status=PASS`, `authority=NONE`, `scientific_disposition=UNKNOWN_WITHIN_CURRENT_CONTRACT`.

- [ ] **Step 6: Commit**

Run:

```bash
git add receipts/independent/wolfram-v0.json docs/methodology.md tests/test_research_qa.py receipts/research-qa/v0.json
git commit -m "test: add independent v0 mathematical witness"
```

---

### Task 9: Add acceptance-slice CI without making semantic judgment a merge authority

**Files:**
- Create: `.github/workflows/v0-replay.yml`
- Modify: `README.md`
- Test: `tests/test_runner.py`

**Interfaces:**
- Consumes: committed reference receipts and verified independent witness.
- Produces: hosted replay proving clean-checkout reproducibility for exact head.

- [ ] **Step 1: Add a test that reference receipts bind the current contract/fixture hashes**

The test recalculates SHA-256 for `experiments/v0/contract.json`, `shared-graph.json`, and each parameter file and requires exact equality with every committed reference receipt.

- [ ] **Step 2: Add manual acceptance workflow**

`.github/workflows/v0-replay.yml`:

```yaml
name: deterministic-v0-replay
on:
  workflow_dispatch:
jobs:
  replay:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install -e .
      - run: tools/dev/check
      - run: |
          mkdir -p /tmp/v0-reference
          cp receipts/reference/*.json /tmp/v0-reference/
          tools/run-v0
          diff -ru /tmp/v0-reference receipts/reference
      - run: tools/research/check
      - uses: actions/upload-artifact@v4
        with:
          name: deterministic-v0-receipts
          path: |
            receipts/reference/*.json
            receipts/research-qa/v0.json
            receipts/independent/wolfram-v0.json
```

`tools/research/check` here is a contract gate only. README must explicitly say the workflow is not scientific acceptance authority.

- [ ] **Step 3: Run local QA and commit**

Run:

```bash
tools/dev/check
tools/research/check
git add .github/workflows/v0-replay.yml README.md tests/test_runner.py
git commit -m "ci: add deterministic v0 acceptance replay"
```

---

### Task 10: Push, review, run hosted acceptance, and record deterministic v0 disposition

**Files:**
- Create: `docs/v0-disposition.md`
- Modify remotely: issues 1-10 and Project fields based on observed completion
- Modify remotely: `theseus-research#72` with exact acceptance receipt

**Interfaces:**
- Consumes: complete deterministic-v0 branch, local QA receipts, independent witness.
- Produces: reviewed PR, exact hosted acceptance evidence, explicit v0 disposition, no automatic v1 promotion.

- [ ] **Step 1: Run final local gates on exact branch head**

Run:

```bash
tools/dev/check
tools/research/check
git status --short
git rev-parse HEAD
```

Expected: both QA endpoints satisfy their declared contract; clean worktree.

- [ ] **Step 2: Push and independently verify remote branch SHA**

Run:

```bash
/workspace/marcopolo-cookbook/github-git-auth.sh --check
git push -u origin research/deterministic-v0
local_sha=$(git rev-parse HEAD)
remote_sha=$(git ls-remote origin refs/heads/research/deterministic-v0 | awk '{print $1}')
test "$local_sha" = "$remote_sha"
```

- [ ] **Step 3: Open one implementation PR linked to the roadmap issues**

The PR body lists `Closes` only for issues whose acceptance criteria are actually complete. Issue 10 remains open until hosted acceptance and disposition are recorded. Issue 11 must not be closed or activated by this PR.

- [ ] **Step 4: Request independent whole-branch review**

Review focus:

```text
- operator orientation and node-major state convention;
- false PASS paths in tools/research/check;
- zero-mass and nonfinite metric behavior;
- receipt provenance/hash binding;
- topology-only control really uses identical graph;
- scientific language does not overclaim isomorphism.
```

Any material review fix changes branch HEAD and invalidates prior exact-head hosted acceptance.

- [ ] **Step 5: Dispatch `deterministic-v0-replay` on the final reviewed SHA**

Record workflow run ID, run attempt, exact repository SHA, and artifact digest/ID when exposed. Hosted SUCCESS proves reproducible execution for that head only.

- [ ] **Step 6: Choose disposition from the preregistered vocabulary using observed results**

`docs/v0-disposition.md` must contain:

```text
FACT: which controls and cross-checks passed or failed.
INFERENCE: what the shared metrics appear to capture.
HYPOTHESIS: what remains worth testing.
UNKNOWN: what deterministic v0 cannot establish.
DISPOSITION: exactly one of FOUND_USEFUL_STRUCTURE / NO_SIGNAL / REFINE / REJECT / UNKNOWN_WITHIN_CURRENT_CONTRACT.
AUTHORITY: human-reviewed scientific disposition; automated QA authority remains NONE.
```

Do not choose `FOUND_USEFUL_STRUCTURE` merely because CI is green.

- [ ] **Step 7: Commit disposition, rerun local QA, push, and rerun hosted acceptance because HEAD changed**

Run:

```bash
git add docs/v0-disposition.md
git commit -m "docs: record deterministic v0 disposition"
tools/dev/check
tools/research/check
git push
```

Then dispatch hosted replay again on this exact final head.

- [ ] **Step 8: Merge only after review and exact-head hosted evidence**

After merge, independently read back:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write "$GH" repo view TeaShaman-cyber/theseus-transmission-ecology-lab --json defaultBranchRef,url
git fetch origin main
git rev-parse origin/main
```

Verify the merge commit contains the final disposition and reference receipts.

- [ ] **Step 9: Update roadmap state from observed completion**

Issues 1-10 move to `Done`/`Verified` only where their exact acceptance criteria are satisfied. Issue 11 remains `Todo`/`Proposed` unless the recorded v0 disposition plus explicit user intent authorizes starting stochastic/nonlinear work.

- [ ] **Step 10: Record final readback in `theseus-research#72`**

Comment with repository main SHA, PR/merge identity, hosted run identity, Project URL, deterministic v0 disposition, and any remaining UNKNOWN/DEGRADED boundaries. Do not close #72 unless its bootstrap acceptance criteria are all observed complete.

---

### Task 11: Register the lab in the Theseus research-line registry after verified repository bootstrap

**Files:**
- Modify in `TeaShaman-cyber/theseus-research`: `registry/research-lines.json`
- Regenerate in `TeaShaman-cyber/theseus-research`: managed README projections using the repository's existing registry tooling
- Test: existing registry contract/projection tests

**Interfaces:**
- Consumes: verified public lab repository identity from Task 1 and accepted repository role.
- Produces: canonical Theseus research-line registry entry without changing scientific disposition.

- [ ] **Step 1: Create or reuse a narrow registry-sync worktree from current `origin/main`**

Do not modify the old design-spec worktree after its role is complete.

- [ ] **Step 2: Add exactly one public active line**

Use ID:

```text
theseus-transmission-ecology-lab
```

Repository:

```text
TeaShaman-cyber/theseus-transmission-ecology-lab
```

Role text must describe reproducible cross-substrate transmission dynamics, deterministic research QA, and bounded scientific comparison without claiming established isomorphism.

- [ ] **Step 3: Use existing registry projection tooling, not hand-edited README tables**

Run the repository-native render/check command discovered from current `origin/main`, then:

```bash
tools/dev/check
```

- [ ] **Step 4: Commit, push, review, merge, and exact-readback the registry change**

The registry change is coordination metadata only and must not alter the lab's scientific disposition.

---

## Final Verification Matrix

| Claim | Required evidence | Not sufficient |
| --- | --- | --- |
| repository mechanically healthy | exact-head `tools/dev/check` | one unit test |
| experiment contract satisfied | exact-head `tools/research/check` receipt | green repository QA |
| spectral/Hodge witness reproduced | independent Wolfram receipt bound to exact commit | local NumPy output alone |
| deterministic v0 reproducible | clean hosted replay + receipt diff | local run alone |
| hypothesis scientifically accepted | explicit human-reviewed disposition with stated limits | CI PASS, Project status, reviewer approval alone |
| roadmap state current | Project readback after mutations | successful write response |
| repository registered in Theseus | registry commit + projection QA + remote readback | repo existence alone |

## Explicit Stop Rules

- If the topology-only negative control does not produce opposite dynamics on the same graph, stop and fix the model/test before interpreting any substrate result.
- If `tools/research/check` can PASS with missing/mismatched commit, control, or required witness evidence, stop; the endpoint is not trustworthy.
- If common metrics add no explanatory value beyond substrate-specific behavior, allow `NO_SIGNAL` or `REJECT`; do not add more metrics post hoc to force separation.
- If deterministic v0 requires nonlinear/multi-parent mechanisms to make the comparison meaningful, record `REFINE` and design a new v1 spec; do not smuggle those mechanisms into v0.
- If an external witness is unavailable, report `DEGRADED`/`UNKNOWN`; do not substitute self-report as independent verification.
