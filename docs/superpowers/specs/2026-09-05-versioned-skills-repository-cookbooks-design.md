# Versioned Skills and Repository Cookbooks — Design

**Date:** 2026-09-05  
**Status:** proposed architecture for review  
**Scope:** Theseus GitHub projects and manually installed managed skills  
**Implementation status:** design only; no runtime skill, repository cookbook, updater, or automation is created by this document

## 1. Problem

Theseus projects accumulate operational knowledge through real work: issue discussions, pull-request reviews, CI incidents, failed routes, accepted fixes, and repeated engineering patterns.

Today that knowledge can remain scattered across history or be remembered only in the current session. A managed skill can help an agent recall known routes, but copying detailed project procedures into the skill creates a second knowledge base that drifts away from the repository.

The architecture therefore needs two different things:

1. a **thin, versioned routing skill** that tells the agent where to look;
2. a **repository-local cookbook** that stores verified operational lessons next to the project they govern.

The design must also preserve a hard human-control boundary: a newer canonical skill in GitHub must never silently replace the version installed in a runtime. Runtime skill updates are manual user actions.

## 2. Feynman model

```text
Skill       = librarian / map
Cookbook    = local map of known rakes
Repository  = durable project memory and review history
GitHub      = canonical source and version history
Runtime UI  = manually installed copy of a skill version
```

The short rule is:

> **Skills route. Repositories remember. History seeds the memory. Humans approve promotion and runtime updates.**

## 3. Goals

- keep operational knowledge close to the repository it applies to;
- make project-specific lessons reviewable and versioned through normal Git history;
- keep shared skills thin and slow-changing;
- allow a skill to discover a repository cookbook without duplicating its contents;
- require user approval before creating a cookbook in a repository that does not have one;
- use issue/PR/CI history as evidence when bootstrapping a cookbook;
- prevent historical advice from becoming current authority without re-verification;
- version canonical skill source in GitHub;
- require manual user installation/update of runtime skills;
- preserve explicit separation between canonical, installed, and observed-active skill state;
- compose runtime-specific guidance, such as MarcoPolo operational rules, with project-specific cookbook guidance.

## 4. Non-goals

This design does **not** introduce:

- automatic skill installation or update;
- self-modifying skills;
- a daemon that scans and rewrites every repository;
- automatic promotion of issue comments into operational rules;
- a second memory database for cookbook content;
- a requirement that every repository immediately have a cookbook;
- an agent permission to create a cookbook without explicit user approval;
- a replacement for README, architecture docs, experiment contracts, or scientific preregistration;
- a guarantee that a skill present in one runtime is installed or auto-selected in another.

## 5. Authority model

The architecture separates five kinds of state.

```text
program contract / methodology
        ↓ constrains
shared skill source in GitHub
        ↓ routes to
repository-local cookbook
        ↓ guides
runtime action
        ↓ produces
live postcondition / evidence
```

Authority rules:

1. The Theseus program contract remains above methodology, skills, and cookbooks.
2. A shared skill is routing guidance, not authority over current runtime state.
3. A repository cookbook is operational guidance for that repository, not proof that the live provider/runtime still behaves the same way.
4. Live runtime/provider state remains current operational authority where freshness matters.
5. Issue, PR, CI, and commit history are evidence sources, not automatically current instructions.
6. A runtime-specific cookbook and a repository-specific cookbook may both apply; neither silently overrides a higher-level project contract.

## 6. Repository-local cookbook contract

### 6.1 Discovery and trust state

The canonical discovery path is:

```text
docs/cookbook/README.md
```

Filesystem presence alone does **not** make a cookbook operational authority. Discovery must distinguish accepted repository guidance from candidate branch/worktree content.

```text
accepted canonical revision contains cookbook
        -> COOKBOOK_ACTIVE

cookbook exists only in an unmerged branch,
or differs from the accepted canonical revision
        -> COOKBOOK_CANDIDATE

accepted baseline/currentness cannot be established
        -> COOKBOOK_REPROBE_REQUIRED

accepted canonical revision has no cookbook
        -> NO_COOKBOOK
```

For ordinary operational work, `COOKBOOK_ACTIVE` guidance must come from an accepted canonical revision verified against the repository's authoritative remote state (normally the default branch or another explicitly accepted ref). Dirty-worktree, contributor-branch, and unmerged PR cookbook changes are review candidates, not silently active instructions.

When an active cookbook is being modified in a branch, the accepted baseline remains operational guidance until the candidate change is reviewed and accepted. A user may explicitly authorize evaluating candidate guidance, but that does not promote it into repository authority.

The root file should be a small index that identifies relevant sections rather than forcing the agent to load the entire cookbook.

Example only:

```text
docs/cookbook/
├── README.md
├── github-actions.md
├── scientific-runs.md
└── review-and-provenance.md
```

The exact section files are repository-specific and should be created only when the project history justifies them.

### 6.2 Missing cookbook

If `docs/cookbook/README.md` is absent:

```text
NO_COOKBOOK
    ↓
agent tells the user
    ↓
agent proposes creating a repository cookbook
    ↓
explicit user approval required
    ↓
BOOTSTRAPPING_COOKBOOK
```

The agent must not silently create the directory or files merely because the convention exists.

### 6.3 Bootstrap evidence

After user approval, candidate lessons may be reconstructed from:

- closed and open issues;
- pull-request reviews and review resolutions;
- accepted fix commits;
- CI/job failures and receipts;
- postmortems and evidence documents;
- current README/contracts/runbooks;
- repeated operational failures observed across sessions.

History is a discovery corpus, not authority. Before promotion into active guidance, each lesson must have its current applicability checked against the repository/runtime state relevant to the rule. If currentness cannot be established, the lesson is `UNKNOWN` and is **not promotable** as an active cookbook rule. It may remain linked as historical evidence or an incident note.

### 6.4 Promotion, invalidation, and revalidation lifecycle

```text
historical observation
        ↓
CANDIDATE LESSON
        ↓ currentness / reproduction / evidence check
VERIFIED LESSON
        ↓ review and accepted repository change
PROMOTED COOKBOOK RULE
        ↓ dependency/contract change, failed reprobe,
          contradictory current evidence, or applicability drift
REPROBE_REQUIRED / UNKNOWN
        ↓ confirmed obsolete
DEPRECATED
```

A lesson should not be promoted solely because an old issue says it once worked, and promotion is not permanent authority.

Recommended evidence vocabulary:

- `OBSERVED` — directly seen, mechanism not yet established;
- `VERIFIED` — mechanism or workaround reproduced or independently checked against a stated applicability boundary;
- `UNKNOWN` — insufficient evidence or currentness unresolved; not active guidance;
- `REPROBE_REQUIRED` — a previously verified rule has a concrete reason to require current verification before use;
- `DEPRECATED` — previously valid, now confirmed obsolete or no longer recommended/current.

A promoted rule should identify enough applicability context to know when revalidation is required, for example the relevant workflow/provider/runtime contract or repository behavior. A changed dependency or failed reproduction removes the rule from active guidance until it is reverified. There is no requirement for arbitrary time-based expiry when the dependency is stable; invalidation is evidence- or contract-triggered.

The cookbook should remain concise. Detailed raw logs stay in issues, artifacts, or evidence files and are linked when useful.

## 7. Feedback loop during ordinary work

When a project has an active cookbook:

```text
project task
   ↓
discover cookbook
   ↓
load smallest relevant section
   ↓
act + verify
   ↓
new repeatable failure?
   ↓
diagnose smallest responsible layer
   ↓
fix / test / reviewer evidence
   ↓
if reusable: propose or update cookbook
```

The important boundary is that **failure does not equal cookbook truth**. Promotion follows diagnosis and verification.

This turns failures into reusable operational knowledge without training model weights.

## 8. Shared skill contract

### 8.1 Purpose

A shared Theseus project skill is a thin recall router. It should not duplicate project cookbooks.

Its conceptual route is:

```text
identify repository
        ↓
look for docs/cookbook/README.md
        ↓
classify provenance/trust state
   ├─ COOKBOOK_ACTIVE -> load minimal relevant accepted section
   ├─ COOKBOOK_CANDIDATE -> review/evaluate only; do not treat as authority
   ├─ COOKBOOK_REPROBE_REQUIRED -> verify accepted/current source first
   └─ NO_COOKBOOK -> propose cookbook creation to user
                         ↓
                   no creation without approval
```

If the work runs through a runtime with its own operational cookbook, the two layers compose **by concern**, not by textual precedence:

```text
program/project contract
        ↓
repository cookbook -> project-specific procedure, scientific/CI invariants
runtime cookbook    -> runtime-specific transport, shell, auth, tool routing
live runtime state  -> current capability/availability evidence
```

Example:

```text
MarcoPolo operational rules: how to invoke GitHub/shell safely
        +
Needle rules: exact SHA, heldout, replica, scientific interpretation
        ↓
actual Needle work through MarcoPolo
```

If runtime and repository guidance make incompatible claims about the **same concern**, and current authoritative evidence does not resolve the conflict, the route is `BLOCKED`. The agent must not silently choose one cookbook, merge the instructions heuristically, or infer precedence from file location. Resolve the conflict through the higher-level contract, current authoritative state, or explicit human decision before mutation.

### 8.2 Skill stability

Skills should change less frequently than cookbooks.

A new project-specific failure normally updates that repository's cookbook, **not** the shared skill.

The shared skill changes when the routing contract itself changes, for example:

- adding the repository-cookbook discovery convention;
- changing approval behavior when a cookbook is absent;
- changing the skill-source/version contract;
- adding a new cross-project routing class.

## 9. Canonical skill source, project registration, and versioning

Canonical shared skill source lives in a dedicated public repository:

```text
TeaShaman-cyber/theseus-skills/
├── README.md
└── skills/
    ├── registry.json
    ├── using-theseus-projects/
    │   ├── SKILL.md
    │   ├── CHANGELOG.md
    │   └── README.md
    └── using-theseus-marcopolo/
        ├── SKILL.md
        ├── CHANGELOG.md
        └── README.md
```

The separation is intentional:

```text
theseus-research
  -> program contract, methodology, public project/research map

theseus-skills
  -> canonical versioned shared skill source

<project>/docs/cookbook/
  -> repository-specific operational memory

marcopolo-cookbook
  -> MarcoPolo runtime-specific operational memory
```

`theseus-research` therefore remains the program-level contract and registry authority rather than also becoming the executable skill-source repository.

### 9.1 Integration with the Theseus project registry and README projections

The existing semi-automatic project registry work in `theseus-research` is the discovery authority for public Theseus repositories. When `theseus-skills` is created, it must be registered there instead of being added to README tables manually.

Proposed registry entry under `registry/research-lines.json`:

```json
{
  "id": "theseus-skills",
  "visibility": "public",
  "repository": "TeaShaman-cyber/theseus-skills",
  "role": {
    "en": "Versioned shared agent skills and routing contracts for Theseus projects",
    "ru": "Версионируемые общие навыки агентов и контракты маршрутизации для проектов Theseus"
  },
  "status": "active",
  "topics": ["theseus", "theseus-research-line", "agent-skills"],
  "release_policy": "checkpoint"
}
```

The project-level registry `release_policy` remains `checkpoint`; individual skill packages inside `theseus-skills` use the SemVer policy defined below. These are different versioning scopes and must not be conflated.

Expected publication flow:

```text
create / accept theseus-skills repository
        ↓
add exact registry entry in theseus-research
        ↓
registry validate
        ↓
registry doctor / remote metadata verification
        ↓
render README.md + README.ru.md from registry
        ↓
review
        ↓
merge
        ↓
exact remote readback
```

The generated `Theseus research lines` tables in `README.md` and `README.ru.md` are projections of the registry. The `theseus-skills` row must therefore appear through the existing projection mechanism, not by hand-editing the generated table.

This design depends on the registry/projection contract currently being developed in `theseus-research` PR #5. If that contract changes before merge, the implementation must adapt to the accepted registry schema rather than freezing assumptions from this design document.

### 9.2 Skill metadata

Each canonical `SKILL.md` should carry at least:

```yaml
metadata:
  version: "1.0.0"
  update_mode: "manual_user"
```

The registry records canonical source state, for example:

```json
{
  "using-theseus-projects": {
    "current_version": "1.0.0",
    "path": "skills/using-theseus-projects/SKILL.md",
    "update_mode": "manual_user"
  }
}
```

A content SHA-256 may be added for exact-byte verification.

### 9.2 SemVer policy

- **PATCH** — wording, typo, or compatible routing clarification;
- **MINOR** — compatible new routing behavior or project-discovery capability;
- **MAJOR** — incompatible behavior or a changed approval/authority/update boundary.

Optional namespaced Git tags may preserve release points without coupling unrelated skill versions:

```text
skill/using-theseus-projects/v1.0.0
skill/using-theseus-marcopolo/v1.0.2
```

## 10. Manual runtime update boundary

This is a hard invariant:

```text
GitHub canonical skill changed
        !=
runtime skill changed
```

Allowed lifecycle:

```text
proposal
  → PR
  → review
  → merge
  → canonical version/tag
  → user is told a newer version exists
  → user manually updates runtime skill
  → runtime acceptance / observation
```

Forbidden by this design:

- a skill replacing its own installed body;
- an agent updating a managed runtime skill merely because GitHub has a newer version;
- treating canonical GitHub version as proof of installed version;
- claiming auto-selection from repository presence alone.

State must remain explicit:

```text
CANONICAL_VERSION = observed from GitHub
INSTALLED_VERSION = observed only if runtime exposes it, else UNKNOWN
ACTIVE/AUTO_SELECTED = observed only if runtime exposes evidence, else UNKNOWN
```

## 11. Mutation and publication boundaries

Cookbook and skill changes use normal repository governance:

```text
proposal → diff → tests/checks → review → accepted merge → remote readback
```

For GitHub writes, the intended target and operation should be bound before selecting a mutation primitive:

```text
target_type + target_id + operation + expected_postcondition
```

A successful write response is not sufficient; important remote postconditions require readback.

## 12. Relationship to existing MarcoPolo guidance

`using-theseus-marcopolo` already acts as a thin operational recall router into `marcopolo-cookbook`.

This design does not require rewriting that skill when a new MarcoPolo-specific failure is learned. The normal path remains:

```text
verified MarcoPolo lesson
        ↓
marcopolo-cookbook update
        ↓
existing skill routes to updated guidance
```

Only a change to the routing contract itself requires a skill version change.

## 13. Example: Needle

Needle motivates the design but does not receive special implementation in this architecture PR.

A future approved Needle cookbook could record repository-specific lessons such as:

- scientific failure versus infrastructure failure;
- exact experiment SHA versus launcher SHA;
- heldout/preregistration boundaries;
- independent replica requirements;
- CI timeout interpretation and safety margins;
- durable receipts and partial-run classification.

The bootstrap should be reconstructed from actual Needle issues, PR reviews, workflow runs, and accepted fixes, then reviewed before merge.

This design does **not** create those files yet.

## 14. Failure handling

If cookbook discovery, currentness, skill-version state, or runtime selection cannot be established, fail honestly:

- `UNKNOWN` — evidence missing;
- `DEGRADED` — usable route exists with weaker authority/coverage;
- `BLOCKED` — required permission, contract, or current state missing;
- `REPROBE_REQUIRED` — cached/remembered state is insufficiently current.

A search miss is not evidence that no guidance exists outside the searched scope.

## 15. Acceptance criteria for implementation phase

Implementation should not begin until this architecture is reviewed and accepted.

When implementation is later approved, minimum acceptance should cover:

1. dedicated canonical `TeaShaman-cyber/theseus-skills` repository with `skills/registry.json` and canonical source for each managed skill;
2. `theseus-skills` is registered through the accepted `theseus-research` project registry contract;
3. README and README.ru project-map rows are rendered from the registry rather than hand-maintained;
4. cookbook discovery distinguishes accepted canonical guidance from dirty/unmerged candidate content;
5. unresolved currentness prevents promotion into active guidance;
6. promoted rules have an explicit invalidation/reprobe path;
7. composed runtime/project cookbook conflicts on the same concern return `BLOCKED` unless authoritative evidence resolves them;
8. explicit `manual_user` update mode;
9. no automatic runtime skill mutation;
10. repository cookbook discovery at `docs/cookbook/README.md`;
11. missing-cookbook path proposes creation and requires explicit user approval;
12. bootstrap guidance treats history as evidence, not authority;
13. promotion requires verification/review before becoming an operational rule;
14. runtime-specific and project-specific cookbooks compose without silent precedence inversion;
15. installed/active skill state remains `UNKNOWN` unless directly observable;
16. GitHub mutation targets and important postconditions receive exact readback.

## 16. Review questions for Codex and human reviewers

Please review this document specifically for:

1. **Architecture:** does the split `thin skill router / repository-local cookbook` create hidden duplication or authority ambiguity?
2. **Contracts:** are cookbook discovery, bootstrap, promotion, and manual-update states deterministic enough to implement and test?
3. **Authority:** can any path accidentally promote historical text into current operational authority?
4. **Human approval:** is cookbook creation clearly blocked until explicit user approval?
5. **Skill lifecycle:** is there any hidden path that could be interpreted as automatic installation or self-update?
6. **Runtime boundaries:** are canonical, installed, and active skill states kept separate?
7. **Composability:** is runtime guidance plus repository guidance sufficiently ordered without creating conflicting sources of truth?
8. **Registry integration:** should `theseus-skills` fit the existing `research-lines` registry schema as an active cross-project operational line, or does that reveal a schema naming/scope mismatch that should be resolved first?
9. **Failure modes:** what important edge cases are missing before implementation begins?

## 17. Proposed implementation sequence after review

Only after accepted review:

1. create and review the dedicated `TeaShaman-cyber/theseus-skills` repository boundary;
2. register `theseus-skills` through the accepted `theseus-research` registry/projection workflow and verify README + README.ru projections;
3. add the shared skill-source registry and canonical skill files inside `theseus-skills`;
4. adapt the existing MarcoPolo skill source into the canonical GitHub layout without changing runtime installation automatically;
5. add the generic Theseus project-router skill;
6. add tests/validation for skill registry and metadata contracts;
7. separately propose the first repository-local cookbook (Needle is a candidate);
8. reconstruct that cookbook from project history under a reviewed bootstrap PR;
9. ask the user to manually install/update any runtime skill version after canonical release.

No item in this sequence is authorized by the architecture document alone.
