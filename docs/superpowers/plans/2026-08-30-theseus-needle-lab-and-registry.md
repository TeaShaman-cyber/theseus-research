# Theseus Needle Lab and Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a real public `TeaShaman-cyber/theseus-needle-lab` research line, integrate outstanding reviewer contributions into `theseus-research`, and establish an observable GitHub research-control-plane without inventing a Needle training pipeline.

**Architecture:** `theseus-research` remains the program contract and root map; `theseus-needle-lab` is a separate public execution/experiment repository. GitHub Issues carry research intent, Actions carry observable execution, receipts carry provenance, Project carries workflow state, Wiki carries human navigation, and Pages is reserved as a generated view. Every externally consequential write uses the verified MarcoPolo `gh-write` profile and is independently read back.

**Tech Stack:** Git, GitHub CLI 2.98.0+dirty, GitHub repositories, Issues, Projects v2, Wiki git repository, GitHub Actions, Markdown, YAML, Bash, SHA-256.

**Spec:** `docs/superpowers/specs/2026-08-30-theseus-needle-lab-and-registry-design.md`

## Global Constraints

- Owner is exactly `TeaShaman-cyber`.
- New repository name is exactly `theseus-needle-lab`.
- New repository visibility is `public`.
- Do not add an open-source license during bootstrap.
- Do not upload private conversation corpora, credentials, secrets, private datasets, or model artifacts.
- Do not implement or claim a real Needle training pipeline in this plan.
- `theseus-research` English and Russian maintained documents must remain meaning-equivalent when contract/methodology meaning changes.
- Preserve `master5d` authorship/provenance for PR #2 contributions.
- Public repository visibility does not itself grant open-source reuse rights.
- GitHub Wiki and Project creation are capability-gated; observed authorization failures are reported as `BLOCKED`, never bypassed with hidden credential routes.
- GitHub Actions bootstrap permissions start at `contents: read`.
- Workflow results are claims only about declared postconditions; green CI is not model-quality or scientific-proof evidence.
- Artifacts are integrity-verifiable by hash; GitHub storage is not described as immutable.
- Important writes require remote read-back before success is claimed.
- Stateful GitHub writes use `GH_CONFIG_DIR=/workspace/.config/gh-write`.

---

### Task 1: Create the empty public Needle Lab repository first

**Files:**
- No repository files created in this task.
- Remote object created: `TeaShaman-cyber/theseus-needle-lab`.

**Interfaces:**
- Consumes: verified `gh-write` profile.
- Produces: real repository URL `https://github.com/TeaShaman-cyber/theseus-needle-lab` for later registry links.

- [ ] **Step 1: Verify intended write profile and repository absence**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh auth status -h github.com
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo view TeaShaman-cyber/theseus-needle-lab --json nameWithOwner,url,visibility 2>/dev/null || true
```

Expected: authenticated account is `TeaShaman-cyber`; repository lookup returns not found before creation. If the repository already exists, stop creation and inspect whether it matches this plan instead of overwriting anything.

- [ ] **Step 2: Create only the remote repository object**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo create TeaShaman-cyber/theseus-needle-lab \
  --public \
  --description "Public Theseus research lab for observable, reproducible, and verifiable Needle learning experiments."
```

Do not pass `--add-readme`, `--license`, `--gitignore`, `--template`, or `--push` in this step.

- [ ] **Step 3: Read back repository properties**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo view TeaShaman-cyber/theseus-needle-lab \
  --json nameWithOwner,url,visibility,description,defaultBranchRef,hasIssuesEnabled,hasWikiEnabled
```

Expected:
- `nameWithOwner == TeaShaman-cyber/theseus-needle-lab`
- `visibility == PUBLIC`
- URL matches the real repository
- description matches the design
- `defaultBranchRef` may be null because the repository is intentionally empty.

- [ ] **Step 4: Record the observed URL for subsequent tasks**

The exact canonical URL used in later README edits is:

```text
https://github.com/TeaShaman-cyber/theseus-needle-lab
```

No other state is claimed in Task 1.

---

### Task 2: Prepare an isolated `theseus-research` integration workspace

**Files:**
- Existing repository: `TeaShaman-cyber/theseus-research`.
- Branch to create: `integration/needle-lab-registry-review`.

**Interfaces:**
- Consumes: current remote `main`, approved design branch, PR #2 refs.
- Produces: clean integration branch based on current `main` with approved design/plan documentation available.

- [ ] **Step 1: Fresh-clone the repository for execution**

Run from `/workspace`:

```bash
rm -rf /workspace/theseus-research-integration
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo clone TeaShaman-cyber/theseus-research /workspace/theseus-research-integration
cd /workspace/theseus-research-integration
git status --short
git branch --show-current
git rev-parse HEAD
```

Expected: clean `main` checkout.

- [ ] **Step 2: Fetch all required review/design refs**

Run:

```bash
cd /workspace/theseus-research-integration
git fetch origin main
git fetch origin design/theseus-needle-lab-and-registry:refs/remotes/origin/design/theseus-needle-lab-and-registry
git fetch origin pull/2/head:refs/remotes/origin/review-pr-2
```

Verify:

```bash
git log --oneline -3 origin/design/theseus-needle-lab-and-registry
git log --oneline -3 origin/review-pr-2
```

Expected to observe approved design commits including `8ff1e1c` and `cf76cf2`, and reviewer commits including `ac18a5c` and `22696ef`.

- [ ] **Step 3: Create integration branch from fresh `origin/main`**

Run:

```bash
cd /workspace/theseus-research-integration
git checkout -B integration/needle-lab-registry-review origin/main
git status --short
git merge-base --is-ancestor origin/main HEAD
```

Expected: clean branch, command exits 0.

- [ ] **Step 4: Bring approved design and plan documentation onto the integration branch**

Run:

```bash
git checkout origin/design/theseus-needle-lab-and-registry -- \
  docs/superpowers/specs/2026-08-30-theseus-needle-lab-and-registry-design.md \
  docs/superpowers/plans/2026-08-30-theseus-needle-lab-and-registry.md

git add docs/superpowers/
git commit -m "docs: add approved Needle Lab design and plan"
```

Verify:

```bash
git show --stat --oneline HEAD
git diff --check HEAD^
```

---

### Task 3: Integrate reviewer PR #2 while preserving provenance

**Files:**
- Create/modify: `CHANGELOG.md`
- Modify: `README.md`
- Modify: `README.ru.md`
- Modify: `docs/methodology.md`
- Modify: `docs/methodology.ru.md`

**Interfaces:**
- Consumes: reviewer commits `ac18a5cacf1588bedbfae51f02c18310866e6c81` and `22696ef6e96a076996ff13b0563e0edd44f7b778`.
- Produces: current-`0.3-draft` compatible contract-change machinery with reviewer authorship preserved.

- [ ] **Step 1: Cherry-pick the first reviewer commit and inspect conflicts before resolving**

Run:

```bash
cd /workspace/theseus-research-integration
git cherry-pick ac18a5cacf1588bedbfae51f02c18310866e6c81 || true
git status --short
git diff --name-only --diff-filter=U
```

Expected: conflicts are possible because current `main` is `0.3-draft`. Do not discard the reviewer commit.

- [ ] **Step 2: Resolve reviewer changes against current `0.3-draft`**

Resolution requirements:
- preserve named acceptance-authority concept;
- preserve `CHANGELOG.md` as the durable change ledger;
- preserve explanatory/not-normative distinction where applicable;
- preserve methodology anti-smuggling/checkability rule;
- retain current `0.3-draft` strengthened security/version language;
- do not regress current bilingual-publication rule.

After editing, run:

```bash
git add CHANGELOG.md README.md docs/methodology.md
git cherry-pick --continue
```

The resulting commit must retain original reviewer author metadata. Verify:

```bash
git show -s --format='author=%an <%ae>%ncommitter=%cn <%ce>%nsubject=%s' HEAD
```

Expected author includes `master5d`; committer may be the executing maintainer identity.

- [ ] **Step 3: Cherry-pick the reviewer state-model commit**

Run:

```bash
git cherry-pick 22696ef6e96a076996ff13b0563e0edd44f7b778
```

If `CHANGELOG.md` conflicts, preserve the three explicit states exactly in meaning:
- `draft / proposed`
- `accepted`
- `superseded`

Continue only after resolution and verify reviewer author metadata again.

- [ ] **Step 4: Adapt PR #2 meaning symmetrically into Russian maintained docs and current 0.3 state**

Update `README.ru.md` and `docs/methodology.ru.md` so acceptance authority, normative/explanatory relationship, and methodology change boundary match the English meaning.

Update `CHANGELOG.md` to include `0.3-draft — 2026-08-13` with:
- summary of accepted review-driven clarifications already present on `main`;
- reason: incorporation of issue #1 review directions;
- review state describing repository acceptance accurately;
- level consistent with the current `0.3-draft` rationale.

Commit separately:

```bash
git add README.ru.md docs/methodology.ru.md CHANGELOG.md README.md docs/methodology.md
git diff --cached --check
git commit -m "docs(contract): adapt reviewer process fixes to 0.3"
```

- [ ] **Step 5: Verify reviewer provenance remains observable in history**

Run:

```bash
git log --format='%h %an <%ae> %s' --max-count=8
```

Expected: history contains commits authored by `master5d` plus separate maintainer adaptation commit.

---

### Task 4: Add the bilingual Theseus research-line registry and remaining review dispositions

**Files:**
- Modify: `README.md`
- Modify: `README.ru.md`
- Modify when wording belongs there: `docs/methodology.md`
- Modify when wording belongs there: `docs/methodology.ru.md`

**Interfaces:**
- Consumes: real `theseus-needle-lab` URL from Task 1, Issue #3 findings.
- Produces: legible root map of Theseus research lines and low-risk wording repairs.

- [ ] **Step 1: Replace isolated Sonar context with a research-line registry in English**

Add a compact section that identifies exactly:
- `theseus-research` — public, active/root, program contract/methodology/research map;
- `theseus-public-observatory` — public, active, public-data observation and reproducible verification experiments;
- `theseus-needle-lab` — public, bootstrapping, observable/reproducible Needle learning experiments, linked to `https://github.com/TeaShaman-cyber/theseus-needle-lab`;
- Sonar — private incubation, experimental continuity/retrieval research line, no private repository URL exposed.

State explicitly that no research line individually defines Theseus.

- [ ] **Step 2: Mirror the registry meaning in Russian**

Update `README.ru.md` in the same commit. Names/statuses/visibility must match the English registry exactly in meaning.

- [ ] **Step 3: Apply the still-actionable Issue #3 wording repairs**

In both maintained languages:
- replace wording that implies donated API credits already exist or are expected with a neutral prohibition on reselling API credits or compute regardless of provenance;
- clarify that `Sadhana of Engineering` is a metaphorical name for disciplined engineering practice and does not create a religious commitment.

Do not invent a public incident ledger. The location/privacy model for engineering-defect records remains deferred to a dedicated follow-up issue.

- [ ] **Step 4: Verify EN/RU registry parity mechanically**

Run a small assertion script:

```bash
python3 - <<'PY'
from pathlib import Path
for f in ['README.md','README.ru.md']:
    s=Path(f).read_text()
    for token in ['theseus-research','theseus-public-observatory','theseus-needle-lab','Sonar']:
        assert token in s, (f, token)
print('registry parity tokens: PASS')
PY
```

Then run:

```bash
git diff --check
```

- [ ] **Step 5: Commit the registry/review wording as a separate change**

Run:

```bash
git add README.md README.ru.md docs/methodology.md docs/methodology.ru.md
git commit -m "docs: map Theseus research lines and close review gaps"
```

---

### Task 5: Create the deferred incident-record follow-up and open the `theseus-research` integration PR

**Files:**
- No additional repository files required.
- GitHub Issue created in `theseus-research`.
- GitHub PR created from `integration/needle-lab-registry-review` to `main`.

**Interfaces:**
- Consumes: completed integration branch from Tasks 2–4.
- Produces: reviewable successor PR and concrete deferred-work reference.

- [ ] **Step 1: Run documentation consistency checks before push**

Run:

```bash
cd /workspace/theseus-research-integration
git diff --check origin/main...HEAD
python3 - <<'PY'
from pathlib import Path
assert Path('CHANGELOG.md').exists()
for f in ['README.md','README.ru.md','docs/methodology.md','docs/methodology.ru.md']:
    assert Path(f).exists(), f
print('required docs: PASS')
PY
git status --short
```

Expected: no whitespace errors and no uncommitted changes.

- [ ] **Step 2: Push the integration branch and read back its SHA**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write git push -u origin integration/needle-lab-registry-review
local=$(git rev-parse HEAD)
remote=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh api repos/TeaShaman-cyber/theseus-research/git/ref/heads/integration/needle-lab-registry-review --jq '.object.sha')
printf 'LOCAL=%s\nREMOTE=%s\n' "$local" "$remote"
test "$local" = "$remote"
```

- [ ] **Step 3: Create the deferred incident-record/privacy-boundary issue**

Capture and read back the created issue URL:

```bash
incident_issue_url=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh issue create \
  --repo TeaShaman-cyber/theseus-research \
  --title "Define durable incident and engineering-defect record boundary" \
  --body $'Define where operational defects required by the methodology are recorded, including public/private/redacted boundaries, provenance links, privacy constraints, and what must never be published. This follow-up resolves the deferred finding from public review Issue #3 without inventing a public incident ledger prematurely.')
GH_CONFIG_DIR=/workspace/.config/gh-write gh issue view "$incident_issue_url" \
  --repo TeaShaman-cyber/theseus-research \
  --json number,title,state,url,body
```

Use this captured URL in the integration PR body/comment references.

- [ ] **Step 4: Open the integration PR without merging it**

Resolve the deferred issue URL from live GitHub state, then create the PR and capture its URL:

```bash
incident_issue_url=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh issue list \
  --repo TeaShaman-cyber/theseus-research --state open --limit 50 \
  --json title,url \
  --jq '.[] | select(.title == "Define durable incident and engineering-defect record boundary") | .url' | head -1)
test -n "$incident_issue_url"
body=$(printf '%s\n\nDeferred incident-record boundary: %s\n\nThis PR intentionally does not merge itself.' \
  'Integrates still-useful reviewer work from PR #2 with preserved authorship, adapts it to current 0.3-draft and bilingual publication, adds the Theseus research-line registry with the real public Needle Lab repository, and addresses remaining low-risk Issue #3 wording findings.' \
  "$incident_issue_url")
integration_pr_url=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh pr create \
  --repo TeaShaman-cyber/theseus-research \
  --base main \
  --head integration/needle-lab-registry-review \
  --title "docs: integrate review fixes and map Theseus research lines" \
  --body "$body")
printf 'integration_pr_url=%s\n' "$integration_pr_url"
```

- [ ] **Step 5: Read back PR state and changed files**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh pr view integration/needle-lab-registry-review \
  --repo TeaShaman-cyber/theseus-research \
  --json number,state,isDraft,mergeable,headRefName,baseRefName,url,files
```

Expected: `OPEN`, `baseRefName=main`, correct head branch, expected files. Do not merge.

---

### Task 6: Bootstrap the `theseus-needle-lab` repository on `main`

**Files:**
- Create: `README.md`
- Create: `docs/architecture.md`
- Create: `docs/experiment-lifecycle.md`
- Create: `experiments/README.md`
- Create: `receipts/README.md`
- Create: `.github/ISSUE_TEMPLATE/experiment.yml`
- Create: `.github/workflows/docs-check.yml`

**Interfaces:**
- Consumes: empty repository from Task 1, approved design.
- Produces: first versioned `main` commit and bootstrap validation workflow.

- [ ] **Step 1: Clone the empty repository and initialize `main` locally**

Run:

```bash
rm -rf /workspace/theseus-needle-lab
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo clone TeaShaman-cyber/theseus-needle-lab /workspace/theseus-needle-lab
cd /workspace/theseus-needle-lab
git checkout -b main
mkdir -p docs experiments receipts .github/ISSUE_TEMPLATE .github/workflows
```

- [ ] **Step 2: Write `README.md` with the bootstrap research contract**

Write exactly this bootstrap text (later reviewed PRs may refine wording):

```markdown
# Theseus Needle Lab

Theseus Needle Lab is a public research line under the [Theseus public-interest research program](https://github.com/TeaShaman-cyber/theseus-research). This repository does not define the Theseus program contract.

Its purpose is to make Needle learning experiments observable, reproducible, and verifiable: research intent is recorded before execution, execution is linked to versioned source, and important results carry provenance and verification receipts.

## Research boundary

- Negative and inconclusive results are first-class research outcomes.
- A green GitHub Action proves only the postcondition declared by that workflow; it does not prove model quality, scientific truth, or generalization.
- Training or learning outputs become accepted results only after explicit evaluation and verification.
- Secrets, credentials, private corpora, and user conversation data must not be committed to this public repository or emitted to public logs.
- Public visibility is for research transparency. In the absence of an explicit license, public visibility does not grant open-source reuse rights.
- Real Needle training CI is intentionally not implemented during bootstrap. The first research issue must establish the actual executable Needle interface and runtime requirements before a training workflow is proposed.

## Research flow

`Issue -> commit/PR -> Action -> artifact/hash -> evaluation -> receipt -> disposition`

See [architecture](docs/architecture.md) and [experiment lifecycle](docs/experiment-lifecycle.md).
```

- [ ] **Step 3: Write `docs/architecture.md`**

Use:

````markdown
# Architecture

Theseus Needle Lab separates research intent, execution evidence, provenance, and human-readable views.

```text
Issue
  -> commit / PR
  -> GitHub Action
  -> artifact + SHA-256
  -> evaluation
  -> verification receipt
  -> ACCEPTED | REJECTED | INCONCLUSIVE
```

## Authority boundaries

- Repository history is the versioned source for code, workflow definitions, schemas, and canonical documentation.
- Issues record research intent, questions, criteria, and dispositions.
- GitHub Actions provide execution evidence only for their declared jobs.
- Receipts provide machine-readable provenance and verification state.
- GitHub Wiki and Pages are navigation/presentation layers, not authority over versioned repository records.
- GitHub-hosted artifacts are retention-bound storage; integrity is established by recorded content hashes, not by assuming storage immutability.

The bootstrap intentionally contains no Needle training command. A later reviewed change may add one only after the real interface and runtime requirements are measured.
````

- [ ] **Step 4: Write `docs/experiment-lifecycle.md`**

Use:

````markdown
# Experiment lifecycle

```text
IDEA
  -> SPECIFIED
  -> RUNNING
  -> VERIFYING
  -> ACCEPTED | REJECTED | INCONCLUSIVE
```

An experiment starts as an Issue. Before execution it records the question or hypothesis, data/manifest identity, configuration identity, success/failure criteria, and privacy classification. Commits and PRs reference that Issue. Execution links back to the exact source revision. Evaluation and verification are recorded separately from execution success.

`REJECTED` and `INCONCLUSIVE` are preserved outcomes, not failures of record keeping.
````

- [ ] **Step 5: Write the experiment/receipt area READMEs and Issue Form**

`experiments/README.md`:

```markdown
# Experiments

Experiment directories are added only after a GitHub Issue specifies a real experiment. Bootstrap does not fabricate training commands, datasets, or results.
```

`receipts/README.md`:

```markdown
# Receipts

Receipts are machine-readable provenance records for executed experiments. The initial schema is intentionally not frozen until Issue `Define experiment receipt schema v0.1` is resolved.

Candidate fields include source commit SHA, workflow identity, data/config hashes, random seed, runner/image identity, tool versions, artifact hash and storage/retention class, evaluation metrics, and verification status.

GitHub Artifacts are retention-bound storage. A recorded SHA-256 identifies content for integrity verification; it does not make the storage immutable.
```

`.github/ISSUE_TEMPLATE/experiment.yml`:

```yaml
name: Experiment
description: Propose a reproducible Needle Lab experiment
title: "experiment: "
labels: []
body:
  - type: textarea
    id: question
    attributes:
      label: Hypothesis or research question
      description: State what is being tested without assuming the result.
    validations:
      required: true
  - type: input
    id: data_manifest
    attributes:
      label: Data or dataset manifest identity
      description: URL, version, digest, or explicit statement that no dataset is required.
    validations:
      required: true
  - type: input
    id: config_identity
    attributes:
      label: Configuration identity
      description: Version, path, digest, or explicit statement that configuration is not yet defined.
    validations:
      required: true
  - type: textarea
    id: criteria
    attributes:
      label: Success and failure criteria
      description: Define observable criteria before execution.
    validations:
      required: true
  - type: dropdown
    id: privacy
    attributes:
      label: Data classification
      options:
        - Public data
        - Synthetic data
        - Private data referenced by manifest only; no private content in GitHub
        - Undecided; must be resolved before execution
    validations:
      required: true
  - type: textarea
    id: runtime
    attributes:
      label: Expected runtime requirements
      description: CPU, GPU, memory, duration, external services, or unknowns. Hosted runners must not be assumed sufficient before measurement.
    validations:
      required: true
```

- [ ] **Step 6: Create least-privilege `docs-check.yml`**

Use:

```yaml
name: Docs check

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Record runner provenance
        shell: bash
        run: |
          set -eu
          printf 'runner_os=%s\n' "${RUNNER_OS:-unknown}"
          printf 'runner_arch=%s\n' "${RUNNER_ARCH:-unknown}"
          printf 'image_os=%s\n' "${ImageOS:-unknown}"
          printf 'image_version=%s\n' "${ImageVersion:-unknown}"
      - name: Validate bootstrap files
        shell: bash
        run: |
          set -eu
          for f in \
            README.md \
            docs/architecture.md \
            docs/experiment-lifecycle.md \
            experiments/README.md \
            receipts/README.md \
            .github/ISSUE_TEMPLATE/experiment.yml; do
            test -s "$f"
          done
```

Before final commit, resolve `actions/checkout` major tag `v4` to the exact observed commit and pin that SHA while retaining the human-readable major tag in a comment:

```bash
checkout_sha=$(git ls-remote https://github.com/actions/checkout.git refs/tags/v4 | awk '{print $1}')
test -n "$checkout_sha"
CHECKOUT_SHA="$checkout_sha" python3 - <<'PY2'
from pathlib import Path
import os
p=Path('.github/workflows/docs-check.yml')
s=p.read_text()
sha=os.environ['CHECKOUT_SHA']
s=s.replace('uses: actions/checkout@v4', f'uses: actions/checkout@{sha} # v4')
p.write_text(s)
PY2
grep 'uses: actions/checkout@' .github/workflows/docs-check.yml
```

The observed SHA becomes part of the reviewed workflow provenance.

- [ ] **Step 7: Locally validate required files and YAML presence**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
required=[
'README.md','docs/architecture.md','docs/experiment-lifecycle.md',
'experiments/README.md','receipts/README.md',
'.github/ISSUE_TEMPLATE/experiment.yml','.github/workflows/docs-check.yml'
]
for f in required:
    p=Path(f)
    assert p.exists() and p.stat().st_size > 0, f
print('bootstrap files: PASS', len(required))
PY
git diff --check
```

- [ ] **Step 8: Commit, push `main`, and read back remote identity**

Run:

```bash
git add .
git commit -m "chore: bootstrap Theseus Needle Lab"
GH_CONFIG_DIR=/workspace/.config/gh-write git push -u origin main
local=$(git rev-parse HEAD)
remote=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh api repos/TeaShaman-cyber/theseus-needle-lab/git/ref/heads/main --jq '.object.sha')
test "$local" = "$remote"
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo view TeaShaman-cyber/theseus-needle-lab \
  --json defaultBranchRef,url,visibility,hasIssuesEnabled,hasWikiEnabled
```

Expected: remote `main` matches local commit.

---

### Task 7: Enable repository features, probe Wiki, and create research issues

**Files:**
- Wiki repository pages only if capability is verified.
- GitHub Issues created in `theseus-needle-lab`.

**Interfaces:**
- Consumes: bootstrapped Needle Lab repository.
- Produces: enabled Issues/Wiki, capability-classified Wiki seed state, three bootstrap research issues.

- [ ] **Step 1: Explicitly enable Issues and Wiki and read settings back**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo edit TeaShaman-cyber/theseus-needle-lab \
  --enable-issues \
  --enable-wiki
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo view TeaShaman-cyber/theseus-needle-lab \
  --json hasIssuesEnabled,hasWikiEnabled,url
```

Expected: both booleans true.

- [ ] **Step 2: Probe Wiki git remote without claiming write success**

Run in a temporary directory:

```bash
rm -rf /workspace/theseus-needle-lab.wiki-probe
GIT_TERMINAL_PROMPT=0 git ls-remote https://github.com/TeaShaman-cyber/theseus-needle-lab.wiki.git || true
```

If `ls-remote` fails because the Wiki repository is not initialized, record `WIKI_SEEDING=BLOCKED` with that exact observation and do not fabricate pages.

If `ls-remote` succeeds, use the verified write profile and seed exact minimal pages:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh auth setup-git
rm -rf /workspace/theseus-needle-lab.wiki
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo clone TeaShaman-cyber/theseus-needle-lab.wiki /workspace/theseus-needle-lab.wiki
cd /workspace/theseus-needle-lab.wiki
cat > Home.md <<'MD'
# Theseus Needle Lab Wiki

Human-oriented navigation for the public Theseus Needle Lab. Canonical contracts, schemas, experiment records, and receipts remain in the main repository.

- [Terminology](Terminology)
- [Research lifecycle](Research-Lifecycle)
MD
cat > Terminology.md <<'MD'
# Terminology

- **Needle** — the learning system being investigated; its executable interface is not assumed during bootstrap.
- **Experiment** — an Issue-scoped research question with criteria and provenance.
- **Candidate** — an output awaiting evaluation/verification.
- **Receipt** — a machine-readable provenance and verification record.
- **Verification** — an explicit postcondition check separate from execution success.
MD
cat > Research-Lifecycle.md <<'MD'
# Research lifecycle

`IDEA -> SPECIFIED -> RUNNING -> VERIFYING -> ACCEPTED | REJECTED | INCONCLUSIVE`

The Issue is the unit of research intent. Versioned repository history and receipts remain authoritative over this Wiki view.
MD
git add Home.md Terminology.md Research-Lifecycle.md
git commit -m "docs: seed Needle Lab wiki"
git push origin HEAD:master
local_wiki=$(git rev-parse HEAD)
remote_wiki=$(git ls-remote origin refs/heads/master | awk '{print $1}')
printf 'LOCAL_WIKI=%s\nREMOTE_WIKI=%s\n' "$local_wiki" "$remote_wiki"
test "$local_wiki" = "$remote_wiki"
```

If GitHub initializes the Wiki default branch under a different observed branch name, use that observed branch instead of asserting `master`; verify with `git remote show origin` before the first push. No Wiki success is claimed until the pushed SHA is read back.

- [ ] **Step 3: Create Issue 1 — real Needle interface investigation**

Run:

```bash
needle_interface_issue_url=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh issue create \
  --repo TeaShaman-cyber/theseus-needle-lab \
  --title "Map the real Needle learning interface and runtime requirements" \
  --body $'Determine the real executable Needle learning interface before any training CI is written. Record entry points, dependency versions, accepted data formats, CPU/GPU requirements, expected duration, outputs/artifacts, random-seed and reproducibility controls, and measured suitability of GitHub-hosted runners. Do not assume hosted runners are sufficient before measurement.')
GH_CONFIG_DIR=/workspace/.config/gh-write gh issue view "$needle_interface_issue_url" \
  --repo TeaShaman-cyber/theseus-needle-lab --json number,title,state,url,body
```

- [ ] **Step 4: Create Issue 2 — receipt schema**

Run:

```bash
receipt_issue_url=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh issue create \
  --repo TeaShaman-cyber/theseus-needle-lab \
  --title "Define experiment receipt schema v0.1" \
  --body $'Define the smallest machine-readable experiment receipt covering source commit SHA, workflow identity, data/config hashes, random seed, runner/image identity, tool versions, artifact hash and storage/retention class, evaluation metrics, and verification status. Distinguish execution success from scientific/model-quality claims.')
GH_CONFIG_DIR=/workspace/.config/gh-write gh issue view "$receipt_issue_url" \
  --repo TeaShaman-cyber/theseus-needle-lab --json number,title,state,url,body
```

- [ ] **Step 5: Create Issue 3 — artifact/dataset boundaries**

Run:

```bash
storage_issue_url=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh issue create \
  --repo TeaShaman-cyber/theseus-needle-lab \
  --title "Decide artifact and dataset storage boundaries" \
  --body $'Define storage boundaries for datasets, learned artifacts, receipts, and evaluation outputs. Compare Git, GitHub Artifacts, Releases, external storage, and private-only storage across retention, SHA-256 integrity, licensing, privacy, size, reproducibility, and public-data constraints.')
GH_CONFIG_DIR=/workspace/.config/gh-write gh issue view "$storage_issue_url" \
  --repo TeaShaman-cyber/theseus-needle-lab --json number,title,state,url,body
```

---

### Task 8: Create the GitHub Project if authorized and link research issues

**Files:**
- GitHub Project v2 object owned by `TeaShaman-cyber` when authorized.

**Interfaces:**
- Consumes: three Needle Lab bootstrap issues.
- Produces: `Theseus — Needle Lab` Project or an exact `BLOCKED` permission receipt.

- [ ] **Step 1: Probe current Project authorization**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh auth status -h github.com
GH_CONFIG_DIR=/workspace/.config/gh-write gh project list --owner TeaShaman-cyber --format json
```

Current known scopes before execution are `gist`, `read:org`, `repo`, `workflow`; therefore Project access may be blocked. Treat the live command result as authority.

- [ ] **Step 2: If authorized, create the Project and read it back**

Run only if Step 1 succeeds:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh project create \
  --owner TeaShaman-cyber \
  --title "Theseus — Needle Lab" \
  --format json
GH_CONFIG_DIR=/workspace/.config/gh-write gh project list --owner TeaShaman-cyber --format json
```

Verify the returned project title and number.

- [ ] **Step 3: If authorization is blocked, stop Project writes only**

Report exact missing-scope/provider error as `PROJECT=BLOCKED`. Continue repository verification; do not switch credentials or hidden routes. Project linking remains pending explicit reauthorization.

- [ ] **Step 4: If Project exists, add the three issues**

Resolve the Project number and the three observed issue URLs, then add them without manually substituting identifiers:

```bash
project_number=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh project list \
  --owner TeaShaman-cyber --format json \
  --jq '.projects[] | select(.title == "Theseus — Needle Lab") | .number' | head -1)
test -n "$project_number"
GH_CONFIG_DIR=/workspace/.config/gh-write gh issue list \
  --repo TeaShaman-cyber/theseus-needle-lab --state open --limit 20 \
  --json title,url \
  --jq '.[] | select(.title == "Map the real Needle learning interface and runtime requirements" or .title == "Define experiment receipt schema v0.1" or .title == "Decide artifact and dataset storage boundaries") | .url' \
  > /tmp/needle-issue-urls.txt
test "$(wc -l < /tmp/needle-issue-urls.txt)" -eq 3
while IFS= read -r issue_url; do
  GH_CONFIG_DIR=/workspace/.config/gh-write gh project item-add "$project_number" \
    --owner TeaShaman-cyber --url "$issue_url"
done < /tmp/needle-issue-urls.txt
GH_CONFIG_DIR=/workspace/.config/gh-write gh project item-list "$project_number" \
  --owner TeaShaman-cyber --format json
```

Verify all three issue URLs are represented in the read-back.

Project custom workflow-state fields (`Idea`, `Specified`, `Running`, `Verifying`, `Accepted`, `Rejected`, `Inconclusive`) are a later Project-configuration action if the current `gh project field-create` capability and authorization are observed. Do not claim those fields exist until read back.

---

### Task 9: Verify the bootstrap Action as execution evidence

**Files:**
- Existing: `.github/workflows/docs-check.yml`.

**Interfaces:**
- Consumes: remote `main` bootstrap commit.
- Produces: observable GitHub Actions conclusion and logs containing runner provenance.

- [ ] **Step 1: Find workflow runs triggered by the bootstrap push**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh run list \
  --repo TeaShaman-cyber/theseus-needle-lab \
  --workflow "Docs check" \
  --limit 5 \
  --json databaseId,headSha,status,conclusion,event,url
```

Resolve the run ID by matching the observed remote `main` SHA:

```bash
head_sha=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh api \
  repos/TeaShaman-cyber/theseus-needle-lab/git/ref/heads/main --jq '.object.sha')
run_id=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh run list \
  --repo TeaShaman-cyber/theseus-needle-lab \
  --workflow "Docs check" --limit 10 \
  --json databaseId,headSha \
  --jq ".[] | select(.headSha == \"$head_sha\") | .databaseId" | head -1)
test -n "$run_id"
printf 'head_sha=%s run_id=%s\n' "$head_sha" "$run_id"
```

- [ ] **Step 2: Wait for the selected run to finish**

Run:

```bash
head_sha=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh api repos/TeaShaman-cyber/theseus-needle-lab/git/ref/heads/main --jq '.object.sha')
run_id=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh run list --repo TeaShaman-cyber/theseus-needle-lab --workflow "Docs check" --limit 10 --json databaseId,headSha --jq ".[] | select(.headSha == \"$head_sha\") | .databaseId" | head -1)
test -n "$run_id"
GH_CONFIG_DIR=/workspace/.config/gh-write gh run watch "$run_id" \
  --repo TeaShaman-cyber/theseus-needle-lab \
  --exit-status
```

Success means only the declared documentation/bootstrap checks passed.

- [ ] **Step 3: Read logs and verify provenance markers**

Run:

```bash
head_sha=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh api repos/TeaShaman-cyber/theseus-needle-lab/git/ref/heads/main --jq '.object.sha')
run_id=$(GH_CONFIG_DIR=/workspace/.config/gh-write gh run list --repo TeaShaman-cyber/theseus-needle-lab --workflow "Docs check" --limit 10 --json databaseId,headSha --jq ".[] | select(.headSha == \"$head_sha\") | .databaseId" | head -1)
test -n "$run_id"
GH_CONFIG_DIR=/workspace/.config/gh-write gh run view "$run_id" \
  --repo TeaShaman-cyber/theseus-needle-lab \
  --log | grep -E 'runner_os=|runner_arch=|image_os=|image_version='
```

Record observed values. Unknown values remain `unknown`; do not infer an image identity GitHub did not expose.

---

### Task 10: Close the reviewer provenance loop and report final bootstrap state

**Files:**
- GitHub comments/state only.

**Interfaces:**
- Consumes: successor integration PR URL, deferred-issue URL, Needle Lab repository URL, bootstrap issue URLs, Project/Wiki statuses, Actions run URL.
- Produces: explicit review dispositions and final verified status without merging the integration PR.

- [ ] **Step 1: Comment on `theseus-research` Issue #3 with explicit dispositions**

The comment must separate:
- already addressed by `0.3-draft`;
- adopted in successor integration PR;
- deferred incident-record boundary with its concrete issue URL.

Read the issue comments back and verify the new comment is visible before closing Issue #3.

- [ ] **Step 2: Close Issue #3 only after references are observable**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh issue close 3 \
  --repo TeaShaman-cyber/theseus-research
GH_CONFIG_DIR=/workspace/.config/gh-write gh issue view 3 \
  --repo TeaShaman-cyber/theseus-research \
  --json state,url,comments
```

Expected: `CLOSED` and disposition comment visible.

- [ ] **Step 3: Comment on PR #2 with successor provenance**

Comment must state that PR #2's reviewer-authored commits are preserved/adapted in the new integration branch/PR, link the successor PR, and explain that PR #2 is superseded because its old base conflicts with current `0.3-draft`.

Read the comment back.

- [ ] **Step 4: Close PR #2 as superseded/integrated, not rejected**

Run:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh pr close 2 \
  --repo TeaShaman-cyber/theseus-research
GH_CONFIG_DIR=/workspace/.config/gh-write gh pr view 2 \
  --repo TeaShaman-cyber/theseus-research \
  --json state,url,comments
```

Expected: `CLOSED`; successor-provenance comment observable.

- [ ] **Step 5: Perform final independent read-back checklist**

Read and classify:

```bash
GH_CONFIG_DIR=/workspace/.config/gh-write gh repo view TeaShaman-cyber/theseus-needle-lab \
  --json nameWithOwner,url,visibility,defaultBranchRef,hasIssuesEnabled,hasWikiEnabled
GH_CONFIG_DIR=/workspace/.config/gh-write gh issue list \
  --repo TeaShaman-cyber/theseus-needle-lab \
  --limit 20 \
  --json number,title,state,url
GH_CONFIG_DIR=/workspace/.config/gh-write gh pr view \
  --repo TeaShaman-cyber/theseus-research \
  integration/needle-lab-registry-review \
  --json number,state,url,headRefName,baseRefName
```

Final report must use only observed statuses:
- `REPO=VERIFIED` only if public repository and remote `main` are read back;
- `DOCS_CHECK=VERIFIED_PASS` only if the matching Action run concluded success;
- `WIKI=VERIFIED` only if enabled and seed pages were read back; otherwise separate `WIKI_ENABLED` and `WIKI_SEEDING=BLOCKED`;
- `PROJECT=VERIFIED` only if Project and issue items are read back; otherwise `PROJECT=BLOCKED` with exact reason;
- `THESEUS_INTEGRATION_PR=OPEN` unless the user later explicitly authorizes merge;
- `NEEDLE_TRAINING=NOT_IMPLEMENTED`.

Stop here. Do not merge the `theseus-research` integration PR and do not implement Needle training.
