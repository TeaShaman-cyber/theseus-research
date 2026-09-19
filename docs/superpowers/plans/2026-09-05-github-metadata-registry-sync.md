# GitHub Metadata and Registry Synchronization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Theseus research-line registry machine-readable, keep EN/RU README projections deterministic, and detect GitHub metadata drift without allowing automation to declare new research lines or mutate repository metadata.

**Architecture:** `registry/research-lines.json` is the Git-visible authority. Stdlib-only Python modules validate the contract, render bilingual README tables, observe GitHub metadata through an injected transport, classify drift, and expose one explicit optional drift-issue writer. A weekly/manual Action runs the doctor read-only; existing PR #5 remains the integration surface.

**Tech Stack:** JSON, Python 3 stdlib, `unittest`, GitHub REST API, GitHub Actions, Markdown.

**Spec:** `docs/superpowers/specs/2026-09-05-github-metadata-registry-sync-design.md`

## Global Constraints

- `registry/research-lines.json` is authority; README and GitHub metadata are projections.
- Candidate discovery never mutates membership.
- Managed labels are exactly: `kind:research`, `kind:engineering`, `kind:operations`, `scope:cross-project`, `evidence:required`.
- Release policies are exactly: `none`, `checkpoint`, `product`.
- Initial workflow is read-only for Topics, labels, Releases, tags, Discussions, Projects, and `.github`.
- Public lines require `OWNER/REPO`; private-incubation lines may omit it.
- GitHub API failure is `UNREACHABLE`, never absence or `PASS`.
- No third-party Python dependency in this slice.
- Target existing branch `integration/needle-lab-registry-review` / PR #5.
- Every GitHub write requires remote readback before success is claimed.

## File Map

```text
registry/research-lines.json            authority
tools/registry_contract.py             load + validate
tools/registry_projection.py           EN/RU table rendering
tools/registry_doctor.py               GitHub observation + drift
tools/check_registry.py                stable CLI
tests/test_registry_contract.py        contract tests
tests/test_registry_projection.py      projection tests
tests/test_registry_doctor.py          read-only doctor tests
tests/test_registry_issue.py           optional issue-write tests
.github/workflows/registry-doctor.yml  weekly/manual doctor
README.md / README.ru.md                generated table blocks
```

---

### Task 1: Machine-readable registry contract

**Files:** create `registry/research-lines.json`, `tools/__init__.py`, `tools/registry_contract.py`, `tests/__init__.py`, `tests/test_registry_contract.py`.

**Interfaces:**

```python
VALID_VISIBILITIES = frozenset({"public", "private-incubation"})
VALID_RELEASE_POLICIES = frozenset({"none", "checkpoint", "product"})
MANAGED_LABELS = (
    "kind:research", "kind:engineering", "kind:operations",
    "scope:cross-project", "evidence:required",
)

def load_registry(path: Path) -> dict[str, object]: ...
def validate_registry(document: Mapping[str, object]) -> list[str]: ...
def public_lines(document: Mapping[str, object]) -> list[Mapping[str, object]]: ...
```

Root JSON:

```json
{"schema_version":"theseus-research-lines-v1","managed_labels":["kind:research","kind:engineering","kind:operations","scope:cross-project","evidence:required"],"lines":[]}
```

Initial IDs, stable order: `theseus-research`, `theseus-public-observatory`, `theseus-needle-lab`, `theseus-memory-provider-lab`, `theseus-model-usage-lab`, `theseus-session-search-lab`, `theseus-tech-review-graph`, `sonar`.

Public topic sets:

```text
theseus-research            [theseus, theseus-research-line, research-program]
theseus-public-observatory  [theseus, theseus-research-line, observability]
theseus-needle-lab          [theseus, theseus-research-line, needle]
theseus-memory-provider-lab [theseus, theseus-research-line, memory]
theseus-model-usage-lab     [theseus, theseus-research-line, model-routing]
theseus-session-search-lab  [theseus, theseus-research-line, session-search]
theseus-tech-review-graph   [theseus, theseus-research-line, knowledgeops]
```

Use localized `role: {"en": ..., "ru": ...}`. Set seven public lines to `release_policy: checkpoint`; Sonar is `visibility/status: private-incubation`, `topics: []`, `release_policy: none`, no repository.

- [ ] Write RED tests for valid registry, duplicate IDs, missing public repository, private line without repository, invalid release policy, and extra managed label.

```python
def test_ids_must_be_unique(self):
    doc = load_registry(REGISTRY)
    doc["lines"].append(copy.deepcopy(doc["lines"][0]))
    self.assertIn("duplicate line id: theseus-research", validate_registry(doc))

def test_public_line_requires_repository(self):
    doc = load_registry(REGISTRY)
    line = next(x for x in doc["lines"] if x["id"] == "theseus-needle-lab")
    line.pop("repository")
    self.assertIn("public line theseus-needle-lab requires repository", validate_registry(doc))
```

- [ ] Run RED: `python3 -m unittest tests.test_registry_contract -v`; expect import/file failure.
- [ ] Implement minimal validator with deterministic error strings and exact closed vocabularies.
- [ ] Run GREEN: `python3 -m unittest tests.test_registry_contract -v`.
- [ ] Commit: `git commit -m "feat: add Theseus research-line registry contract"`.

---

### Task 2: Deterministic bilingual README projections

**Files:** create `tools/registry_projection.py`, `tests/test_registry_projection.py`; modify `README.md`, `README.ru.md`, and registry statuses.

**Interfaces:**

```python
BEGIN_MARKER = "<!-- BEGIN THESEUS_RESEARCH_LINES -->"
END_MARKER = "<!-- END THESEUS_RESEARCH_LINES -->"
def render_table(document, language: Literal["en", "ru"]) -> str: ...
def replace_projection(markdown: str, rendered: str) -> str: ...
def projection_matches(path: Path, rendered: str) -> bool: ...
```

Statuses are: root=`active-root`; six other public lines=`active`; Sonar=`private-incubation`. EN/RU status words are fixed dictionaries in code. Markers surround only the table, not explanatory paragraphs.

- [ ] Write RED tests: every declared ID exactly once in EN and RU; Sonar has no GitHub link; replacement idempotent; duplicate/missing markers fail closed; committed READMEs contain exact generated tables.

```python
def test_replacement_is_idempotent(self):
    source = "before\n<!-- BEGIN THESEUS_RESEARCH_LINES -->\nold\n<!-- END THESEUS_RESEARCH_LINES -->\nafter\n"
    once = replace_projection(source, "| table |\n")
    self.assertEqual(once, replace_projection(once, "| table |\n"))
```

- [ ] Run RED: `python3 -m unittest tests.test_registry_projection -v`.
- [ ] Implement renderer and strict marker replacement; require exactly one begin/end marker in correct order.
- [ ] Insert markers around both existing registry tables and render exact output from JSON.
- [ ] Run GREEN: `python3 -m unittest tests.test_registry_contract tests.test_registry_projection -v && git diff --check`.
- [ ] Commit: `git commit -m "feat: derive bilingual registry views from contract"`.

---

### Task 3: Read-only GitHub observation and drift classification

**Files:** create `tools/registry_doctor.py`, `tests/test_registry_doctor.py`.

**Interfaces:**

```python
class GitHubUnavailable(RuntimeError): ...
class GitHubTransport:
    def request(self, method: str, path: str, body: object | None = None) -> object: ...

def observe_declared_line(line, transport) -> dict[str, object]: ...
def discover_candidates(owner: str, declared: set[str], transport) -> list[dict[str, object]]: ...
def run_doctor(document, owner: str, transport) -> dict[str, object]: ...
```

Top-level precedence: any API uncertainty => `UNREACHABLE`; else declared mismatch => `DECLARED_DRIFT`; else advisory candidate => `CANDIDATE_UNDECLARED`; else `PASS`.

Per public repo use only GET:

```text
/repos/{owner}/{repo}
/repos/{owner}/{repo}/topics
/repos/{owner}/{repo}/labels?per_page=100
/repos/{owner}/{repo}/releases?per_page=100
```

Candidate search is bounded to:

```text
/search/repositories?q=user%3ATeaShaman-cyber+theseus+in%3Aname%2Cdescription&per_page=100
```

Managed-topic mismatch reports drift; unrelated local topics are informational. Missing managed labels report drift. Repository description is captured as observed metadata, while declared identity is enforced by exact repository full-name and visibility; v1 does not treat prose description differences as membership changes. `none` with existing releases reports drift; `checkpoint/product` with zero releases is allowed. Never create a Release.

- [ ] Build `FakeTransport` recording calls and returning fixture dicts/exceptions.
- [ ] Write RED tests: missing topic; unrelated topic ignored; missing managed label; missing repo => drift not deletion; API failure => unreachable; advisory undeclared candidate leaves the registry document byte-for-byte unchanged; checkpoint with zero releases allowed; none with release flagged; read-only path contains only GET calls and never creates a Release.

```python
report = run_doctor(document, "TeaShaman-cyber", transport)
self.assertTrue(all(method == "GET" for method, _, _ in transport.calls))
```

- [ ] Run RED: `python3 -m unittest tests.test_registry_doctor -v`.
- [ ] Implement `UrllibGitHubTransport` with GitHub JSON headers, optional `$GITHUB_TOKEN`, 15-second timeout, JSON-only decoding, and `GitHubUnavailable` conversion.
- [ ] Run GREEN: `python3 -m unittest tests.test_registry_doctor -v`.
- [ ] Commit: `git commit -m "feat: detect Theseus GitHub metadata drift"`.

---

### Task 4: Explicit optional canonical drift-issue writer

**Files:** modify `tools/registry_doctor.py`; create `tests/test_registry_issue.py`.

**Interfaces:**

```python
DRIFT_ISSUE_TITLE = "Registry drift: Theseus research-line metadata"
def render_drift_issue_body(report: Mapping[str, object]) -> str: ...
def ensure_drift_issue(repository: str, report, transport) -> dict[str, object]: ...
```

This path is never default. Guard it with:

```python
if report["status"] in {"PASS", "UNREACHABLE"}:
    raise ValueError(f"drift issue write not allowed for {report['status']}")
```

Dedup contract: GET open issues; exact title match => one comment; no match => one issue; ignore PR objects; never create one issue per drifting repository. Body must state: `This issue is a drift report. It does not declare any repository part of Theseus.`

- [ ] Write RED tests for create-once, comment-existing, multiple drifts=>one action, PASS refusal, UNREACHABLE refusal.
- [ ] Run RED: `python3 -m unittest tests.test_registry_issue -v`.
- [ ] Implement exact-title dedupe via `/repos/TeaShaman-cyber/theseus-research/issues?state=open&per_page=100` and one POST path.
- [ ] Run GREEN: `python3 -m unittest tests.test_registry_doctor tests.test_registry_issue -v`.
- [ ] Commit: `git commit -m "feat: add explicit deduplicated registry drift issue mode"`.

---

### Task 5: Stable local/CI CLI

**Files:** create `tools/check_registry.py`; extend tests.

**Interfaces:**

```text
python3 tools/check_registry.py validate
python3 tools/check_registry.py render --check
python3 tools/check_registry.py render --write
python3 tools/check_registry.py doctor --owner TeaShaman-cyber --json-output PATH
python3 tools/check_registry.py doctor --owner TeaShaman-cyber --json-output PATH --drift-issue write
```

Exit codes: `0 PASS`; `2 DECLARED_DRIFT/CANDIDATE_UNDECLARED`; `3 UNREACHABLE`; `4 contract/projection failure`. `--drift-issue` defaults to `off`; no environment variable may silently enable writes.

- [ ] Add RED subprocess tests for `validate`, `render --check`, and unknown subcommand.
- [ ] Run RED: `python3 -m unittest discover -s tests -v`.
- [ ] Implement `argparse` CLI. `validate` prints `{"status":"PASS","errors":[]}`; `render --check` names exact mismatched files; `doctor` validates contract/projections before network, writes stable pretty JSON, and only calls issue writer for explicit mode.
- [ ] Run full gate:

```bash
python3 -m unittest discover -s tests -v
python3 tools/check_registry.py validate
python3 tools/check_registry.py render --check
python3 -m compileall -q tools tests
git diff --check
```

- [ ] Commit: `git commit -m "feat: add registry validation and doctor CLI"`.

---

### Task 6: Weekly/manual read-only GitHub Action

**Files:** create `.github/workflows/registry-doctor.yml`; extend `tests/test_registry_doctor.py`.

Workflow contract:

```yaml
name: Registry Doctor
on:
  schedule:
    - cron: "17 6 * * 1"
  workflow_dispatch:
permissions:
  contents: read
```

One job, `ubuntu-latest`, timeout 10 minutes. Use immutable full-SHA `actions/checkout` already verified in Theseus evidence; no floating major tag. Steps: checkout; unit tests; validate/render check; doctor with `GITHUB_TOKEN=${{ github.token }}`; append JSON report to `$GITHUB_STEP_SUMMARY`; exit with doctor code.

- [ ] Add RED static test asserting workflow contains `contents: read`, `schedule`, `workflow_dispatch`; excludes `issues: write` and excludes `--drift-issue write`.
- [ ] Run RED: `python3 -m unittest tests.test_registry_doctor -v`.
- [ ] Create workflow. Resolve and insert the full immutable checkout SHA before commit.
- [ ] Run full local gate from Task 5.
- [ ] Commit: `git commit -m "ci: add read-only Theseus registry doctor"`.

Expected first live doctor result may be `DECLARED_DRIFT` because live repositories currently lack managed Topics/labels. That is a detector postcondition, not a test failure; distinguish it in the run log.

---

### Task 7: Create and connect the implementation issue

**Files:** no code file required.

Create one issue in `TeaShaman-cyber/theseus-research` titled `Implement GitHub metadata and research-line registry synchronization`. Body must link the approved spec and PR #5; state JSON authority; state read-only metadata scope; list out-of-scope surfaces; include verification checklist.

- [ ] Write exact issue body to `/tmp/theseus-registry-implementation-issue.md`.
- [ ] Create through `GH_CONFIG_DIR=/workspace/.config/gh-write gh issue create ... --body-file ...`.
- [ ] Read back title/body/state/url through the read profile and require invariants.
- [ ] Attempt native cross-repo/sub-issue linkage under `theseus-research#6` using currently executable GitHub capability.
- [ ] If native sub-issue mutation is unavailable, report `SUB_ISSUE_LINK=DEGRADED`, add reciprocal URL comments to #6 and the new issue, then read both comments back. Do not claim native linkage.

---

### Task 8: Publish exact branch and live verification gate

**Files:** only approved implementation files; do not commit live report JSON.

- [ ] Final local verification:

```bash
python3 -m unittest discover -s tests -v
python3 tools/check_registry.py validate
python3 tools/check_registry.py render --check
python3 -m compileall -q tools tests
git diff --check
git status --short
```

- [ ] Push existing branch without force:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write git push origin integration/needle-lab-registry-review
```

- [ ] Require remote branch SHA == local `HEAD` with `git ls-remote`.
- [ ] Fetch remote `registry/research-lines.json` from exact branch via GitHub API; decode and run `validate_registry` against remote bytes.
- [ ] Dispatch `registry-doctor.yml` explicitly on `integration/needle-lab-registry-review`; resolve the run by branch/head SHA.
- [ ] Inspect steps: unit tests and projection validation must pass; doctor must return `PASS`, expected drift/candidate, or `UNREACHABLE` with correct semantics; confirm no metadata writes occurred.
- [ ] Read PR #5 and require `headRefOid == local HEAD`.
- [ ] Request one fresh `@codex review` on exact head only after readback/CI observation.
- [ ] Stop before merge.

Terminal state:

```text
IMPLEMENTATION_COMMITTED
REMOTE_HEAD_VERIFIED
REGISTRY_READBACK_VERIFIED
LIVE_DOCTOR_OBSERVED
IMPLEMENTATION_ISSUE_VERIFIED
PR5_EXACT_HEAD_REVIEW_REQUESTED
MERGE_PENDING_REVIEW
```

## Self-Review

- Spec coverage: contract/4 missing lines=Task 1; EN/RU parity=Task 2; Topics/labels/releases/candidates/unreachable=Task 3; dedup issue=Task 4; stable CLI=Task 5; read-only schedule/manual automation=Task 6; #6 coordination=Task 7; remote/live verification=Task 8.
- No automatic membership mutation, Topic/label mutation, Release/tag creation, Discussions, Projects, `.github`, reusable-workflow repo, attestation, GHCR, or private-repo discovery is included.
- Interfaces are consistent: Task 2 consumes Task 1 document; Task 3 consumes Task 1 public lines; Task 4 consumes Task 3 report; Task 5 exposes Tasks 1–4; Task 6 calls Task 5 read-only mode.
- Runtime-captured issue number and immutable action SHA are execution values resolved from provider evidence, not design gaps.
