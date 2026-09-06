# GitHub Metadata and Registry Synchronization — Design

**Date:** 2026-09-05  
**Status:** approved design, pending implementation plan  
**Parent program:** Theseus  
**Canonical research issue:** `TeaShaman-cyber/theseus-research#6`  
**Primary integration branch:** `integration/needle-lab-registry-review`

## 1. Purpose

Turn the Theseus research-line registry from a manually maintained README table into a small Git-visible contract with GitHub-native projections and drift detection.

The design has two goals:

1. keep the public Theseus research-line map current as new laboratories appear;
2. use GitHub metadata and coordination primitives more systematically without making GitHub UI state the authority for program membership or research truth.

The system must preserve the existing Theseus boundary:

> The registry lists only research lines explicitly declared part of Theseus. It is not an inventory of every repository owned by the maintainer.

Automation may detect likely drift. It must not autonomously declare a repository part of Theseus.

## 2. Current observed state

Live GitHub inventory on 2026-09-05 showed:

- the registry in PR #5 still lists only `theseus-research`, `theseus-public-observatory`, `theseus-needle-lab`, and private-incubation `Sonar`;
- four additional public repositories explicitly describe themselves as Theseus research lines or implementations: `theseus-memory-provider-lab`, `theseus-model-usage-lab`, `theseus-session-search-lab`, and `theseus-tech-review-graph`;
- checked repositories have no repository Topics, Releases, Git tags, or Milestones;
- Discussions are disabled;
- labels exist, but are almost entirely GitHub defaults such as `bug`, `enhancement`, `question`, and `documentation`;
- `theseus-needle-lab` is the only checked repository with a project-specific Issue Form (`experiment.yml`);
- account-level `TeaShaman-cyber/.github` does not yet exist.

These observations prove registry and metadata drift. They do not by themselves define the desired metadata.

## 3. Authority model

### 3.1 Registry authority

Create a machine-readable registry in `theseus-research`:

```text
registry/research-lines.json
```

This file is the Git-visible authority for declared Theseus research-line membership and its project-level metadata contract.

README EN/RU tables, GitHub Topics, shared labels, cross-repository issue links, release-policy checks, and future Project views are projections of that contract.

### 3.2 GitHub is a projection and execution substrate

GitHub metadata is useful for discovery and coordination, but does not become independent authority.

```text
research-lines.json
        ↓
   projections
        ├─ README EN/RU
        ├─ repository Topics
        ├─ common label profile
        ├─ release-policy checks
        ├─ cross-repository issue graph
        └─ optional Project view
```

If a GitHub projection disagrees with the registry, the system reports drift. It does not silently rewrite the registry from GitHub.

### 3.3 Research versus engineering state

Do not collapse research and engineering state.

```text
research graph
hypothesis → experiment → observation → conclusion

engineering graph
issue → plan → commit → PR → CI → verification
```

Cross-repository issue relationships and Projects may connect the graphs, but a merged PR or closed engineering issue must not automatically imply a research claim is accepted.

## 4. Registry contract

The initial `registry/research-lines.json` should remain intentionally small.

Each research line records at least:

```json
{
  "id": "theseus-session-search-lab",
  "visibility": "public",
  "repository": "TeaShaman-cyber/theseus-session-search-lab",
  "role": "Public Theseus research lab for verifiable session capture, portable historical search artifacts, and browser-independent session_search.",
  "status": "active",
  "topics": [
    "theseus",
    "theseus-research-line",
    "session-search"
  ],
  "release_policy": "checkpoint"
}
```

Private-incubation lines may omit a repository identifier.

The initial schema should support only fields required for current automation. Do not add owners, budgets, runtime bindings, credentials, deployment topology, or other unrelated infrastructure state.

## 5. Repository Topics

Topics provide repository-level classification and discovery.

The common baseline is:

```text
theseus
theseus-research-line
```

A repository may add one role/topic marker such as:

```text
research-lab
knowledgeops
observability
memory
model-routing
session-search
needle
```

Use few topics with stable semantics. Topics are not a substitute for the registry and must not be used to infer membership automatically.

`registry-doctor` compares declared topics with observed GitHub topics and reports missing or unexpected Theseus-managed topics.

## 6. Labels

Existing GitHub default labels remain valid local labels.

Add only a small cross-project Theseus profile:

```text
kind:research
kind:engineering
kind:operations
scope:cross-project
evidence:required
```

The profile classifies issue purpose and evidence requirements. It must not duplicate the complete status state machine.

In particular, avoid a second status vocabulary such as:

```text
status:accepted
status:verifying
status:done
```

unless a later design explicitly chooses labels as the status authority. Current lifecycle state remains in Issues/Projects/research dispositions.

Repositories may keep project-specific labels such as accessibility or experiment-oriented labels.

## 7. Releases and tags

Do not require every Theseus repository to publish Releases.

The registry declares a release policy:

```text
none
checkpoint
product
```

Meaning:

- `none` — no current durable release surface is required;
- `checkpoint` — publish only a promoted, reproducible research or architecture checkpoint worth naming;
- `product` — semantically versioned consumable software or runtime artifacts may be released.

A Release is a curated checkpoint, not raw CI storage.

For research checkpoints:

```text
Git tag
  ↓
GitHub Release
  ↓
assets / manifests
  ↓
hashes / Theseus verification receipt
  ↓
optional GitHub artifact attestation
```

Artifact attestations prove build provenance/integrity. Theseus receipts remain responsible for research meaning and acceptance semantics.

The first implementation of registry synchronization only validates policy. It must not automatically create tags or Releases.

## 8. Cross-repository issue graph

Use GitHub-native issue relationships where they improve legibility:

```text
program research issue
        ↓
cross-repository sub-issues
        ↓
project implementation / experiment issues
```

Dependencies may represent operational blocking relationships.

This provides a native navigation graph between the central research question and work in individual labs.

Relationships are coordination edges, not proof edges. Scientific evidence remains linked explicitly through receipts, artifacts, comments, or KnowledgeOps records.

The implementation issue for this design should be linked as a child/sub-issue of `theseus-research#6` when the available GitHub capability permits it.

## 9. Discussions and Projects

### Discussions

Do not enable Discussions across every laboratory.

If piloted, enable them first only in `theseus-research` as a program-level idea surface:

```text
Discussion
   ↓ mature question
Research Issue
   ↓
lab sub-issue / experiment
```

This keeps speculative conversation out of engineering Issues without fragmenting the social surface across many repositories.

### Projects

A cross-project GitHub Project may later provide a view over research and engineering work, but it is explicitly non-authoritative.

Useful fields could include:

```text
Research line
Graph: research | engineering
Research disposition
Engineering status
Evidence link
Parent research issue
```

No registry or research conclusion should exist only in Project fields.

Projects are deferred from the first implementation slice.

## 10. Registry Doctor

Add a deterministic GitHub-native checker in `theseus-research`.

Responsibilities:

```text
registry/research-lines.json
        ↓
validate registry schema
        ↓
query declared public repositories
        ↓
compare:
  existence
  visibility
  description / declared identity
  Theseus-managed topics
  Theseus-managed label profile
  release-policy observations
  selected issue-form/default expectations
  declared cross-project references
        ↓
detect likely undeclared Theseus repositories
        ↓
report drift
```

Candidate discovery may use bounded heuristics such as repository names/descriptions containing `theseus`, but candidate detection must remain advisory.

The doctor must distinguish:

```text
DECLARED_DRIFT
CANDIDATE_UNDECLARED
UNREACHABLE / UNKNOWN
PASS
```

An unreachable GitHub API or ambiguous repository is not absence.

## 11. Automation behavior

Initial automation runs:

- weekly `schedule`;
- manual `workflow_dispatch`.

The first version is read-only with respect to repository metadata.

On PASS:
- workflow succeeds and emits a compact report.

On drift:
- workflow fails or reports a drift status;
- create or update one canonical drift issue in `theseus-research`, if write permission for the issue path is explicitly configured and verified.

Avoid one issue per repository per run.

A future manual-only `metadata-sync --dry-run` may propose exact changes such as missing Topics or labels. Automatic metadata mutation is outside the first implementation slice.

## 12. Account-level `.github`

Keep the earlier Checkpoint C decision:

```text
TeaShaman-cyber/.github
= inherited human-facing defaults only
```

The first pilot remains a README-only public skeleton, creating no inherited behavior.

Later pilots may add exactly one low-risk research Issue Form and verify inheritance in a repository without a local override.

Do not mix reusable workflows, release assets, packages, or project evidence into the `.github` repository.

The `.github` pilot remains a separate bounded implementation under the canonical GitHub substrate research issue.

## 13. First implementation slice

The first implementation should update PR #5 rather than create a parallel registry architecture.

Scope:

1. add the four currently missing public Theseus research lines to the registry;
2. add `registry/research-lines.json`;
3. generate or validate EN/RU registry projections against the JSON contract;
4. add the minimal cross-project label/topic/release-policy declarations;
5. add deterministic `registry-doctor` validation;
6. add a weekly/manual GitHub Action in read-only metadata mode;
7. create a dedicated implementation issue linked to `theseus-research#6`;
8. independently read back branch SHA, CI result, issue content, and registry projection.

Out of scope:

- enabling Discussions;
- creating a cross-project Project;
- creating Releases/tags;
- creating `.github`;
- auto-mutating repository Topics/labels;
- reusable workflow repository;
- artifact-attestation pilot;
- GHCR;
- private-repository scanning beyond explicitly declared metadata.

## 14. Testing and verification

Tests must cover at least:

- registry schema and unique research-line IDs;
- public repository entries require repository identity;
- private-incubation entries may omit repository identity;
- EN/RU projection semantic parity;
- undeclared candidate does not become declared automatically;
- missing repository produces drift, not deletion;
- missing managed Topic is reported;
- unrelated local Topic is not deleted or treated as fatal unless policy says so;
- missing managed label is reported;
- release policy `none/checkpoint/product` validates;
- no Release is automatically created;
- GitHub API failure returns `UNKNOWN/UNREACHABLE`, not PASS or absence;
- scheduled doctor cannot mutate repository metadata;
- drift issue deduplicates to one canonical issue when issue-write mode is enabled.

Verification before success:

```text
local tests
→ schema/projection validation
→ GitHub Action
→ remote branch SHA readback
→ exact registry file readback
→ drift report readback
→ implementation issue readback
```

A green workflow proves only the declared metadata/registry postcondition.

## 15. Rollback and portability

The registry is ordinary Git data. Removing the GitHub Action returns the system to manual maintenance without losing the declared research-line map.

GitHub Topics, labels, sub-issues, Discussions, and Project fields are convenience projections. The core program map remains reconstructable from Git.

No GitHub-only UI object is required to understand which research lines are declared part of Theseus.

## 16. Success criteria

The slice succeeds when:

- PR #5 contains all currently declared public Theseus lines plus private-incubation Sonar;
- `research-lines.json` and EN/RU registry views agree;
- drift against current public GitHub metadata is machine-detectable;
- automation cannot autonomously add a research line;
- common metadata vocabulary remains small;
- Releases are governed by policy rather than generated for activity;
- the implementation issue is connected to the canonical GitHub substrate research line;
- all writes have independent remote readback;
- no new central GitHub UI surface becomes authority.
