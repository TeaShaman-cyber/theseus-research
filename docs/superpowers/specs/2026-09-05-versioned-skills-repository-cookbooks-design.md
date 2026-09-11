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

Cookbook discovery tracks **accepted cookbook existence, accepted rule state, candidate overlay, and durable invalidation receipts independently**. A single cookbook-wide `ACTIVE/UNKNOWN` bit is insufficient because one rule may be invalidated while neighboring rules remain current.

```text
ACCEPTED_COOKBOOK_REVISION
  immutable revision/content identity
  | ABSENT

ACCEPTED_RULES
  rule_id -> ACTIVE | REPROBE_REQUIRED | UNKNOWN | DEPRECATED
             + rule/content digest
             + target-revision/applicability boundary

CANDIDATE_OVERLAY
  rule/cookbook ADD | MODIFY | DELETE_TOMBSTONE | ABSENT

DURABLE_INVALIDATIONS
  rule_id + accepted-rule digest + evidence digest
          + effective status + acceptance identity
```

Cookbook **existence or absence is derived only from the accepted canonical revision applicable to the target code revision**, never from the current worktree filesystem alone. If an accepted target revision contains `docs/cookbook/README.md` and a dirty worktree deletes it, discovery still sees the accepted cookbook plus a candidate deletion tombstone. Ordinary work may continue using unaffected accepted rules; the unmerged deletion is not authority to bootstrap a replacement or erase accepted guidance.

For ordinary operational work, an `ACTIVE` rule must come from an accepted canonical revision whose provenance is verified against the repository's authoritative remote state and whose applicability is bound to the **target code revision being operated on**. The default branch is not automatically authoritative for work on a release branch or historical SHA. Rule state and applicability are evaluated per `rule_id`; lack of currentness for one rule must not withdraw unrelated verified rules, and a target-revision mismatch affects only the rules whose applicability cannot be established.

Dirty-worktree, contributor-branch, and unmerged PR cookbook changes are candidate overlays, not silently active instructions. A candidate add/modify/delete may coexist with accepted guidance; ordinary work uses only the accepted rule bytes that remain effective, unless the user explicitly authorizes candidate evaluation.

A transient observation or candidate-file assertion is **not** sufficient to durably revoke accepted guidance. Immediate invalidation has two layers:

1. a current execution encountering directly verified contradictory evidence must fail closed for the affected rule in that execution/session;
2. cross-session withdrawal requires a **trusted, durable, rule-scoped invalidation receipt** bound to the exact accepted-rule digest and applicability boundary.

Trusted invalidation evidence must be current, provenance-bound, and independently observable through the operation's required verification/read-back path; dirty candidate text, unverified memory, or an agent inference alone cannot satisfy that predicate. A durable invalidation receipt must identify the affected `rule_id`, accepted rule/content digest, evidence reference/digest, reason, effective status (`REPROBE_REQUIRED` or `UNKNOWN`), acceptance identity, and durable read-back location. The authority allowed to accept such a durable revocation must be explicitly declared; under this design it is an authorized human acceptance event, not an autonomous agent decision.

The invalidation receipt is distinct from any candidate replacement. Until it is durably persisted and read back, the system may report `INVALIDATION_PENDING_PERSISTENCE` and must not claim that cross-session revocation is established. Once accepted and durable, discovery overlays that receipt on the accepted baseline and excludes only the affected rule. Review latency must not reactivate a durably invalidated rule merely because the accepted cookbook bytes themselves have not yet changed.

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

If the **accepted canonical revision applicable to the target code revision** has no `docs/cookbook/README.md`:

```text
ACCEPTED_COOKBOOK_REVISION = ABSENT
    ↓
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

A missing file in a dirty worktree, contributor branch, or unmerged PR is not `NO_COOKBOOK` when the accepted baseline still contains one; it is a candidate deletion/tombstone. The agent must not silently create the directory or files merely because the convention exists.

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
        ↓ tests/review + explicit authorized human acceptance + accepted repository change
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

Each promoted rule requires a stable `rule_id`, immutable rule/content digest, and enough applicability context to know when revalidation is required, including the relevant target repository revision or explicitly demonstrated compatible revision range plus any workflow/provider/runtime dependency boundary. Rule status is evaluated independently: a changed dependency, target-revision mismatch, contradictory current evidence, or failed reproduction affects only the rule(s) whose applicability/evidence is invalidated.

A current execution with verified contradictory evidence stops using the affected rule immediately. Durable cross-session state changes only through the trusted invalidation-receipt path defined in §6.1; the candidate replacement is a separate object and cannot itself revoke the baseline. There is no requirement for arbitrary time-based expiry when the dependency is stable; invalidation is evidence-, revision-, or contract-triggered.

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
classify accepted revision + per-rule trust/applicability + candidate overlay
   ├─ accepted cookbook ABSENT -> propose cookbook creation to user
   │                                ↓
   │                          no creation without approval
   └─ accepted cookbook PRESENT
          ↓
      load only accepted rules with effective state ACTIVE
          + apply durable rule-scoped invalidation receipts
          + exclude REPROBE_REQUIRED / UNKNOWN / DEPRECATED rules
          + keep candidate ADD/MODIFY/DELETE tombstones separate for review/evaluation only
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

The semi-automatic registry/projection work in `theseus-research` remains the discovery authority for public Theseus repositories. However, the current `research-lines` schema is intentionally narrower than the full project set: `theseus-skills` is shared operational infrastructure, not a research line.

The registry contract must therefore distinguish **project kind** from visibility and lifecycle status before `theseus-skills` is registered as active. At minimum the semantic classes must be able to represent:

```text
program-root          -> theseus-research
research-line         -> theseus-needle-lab and other labs/experiments
shared-infrastructure -> theseus-skills and similar cross-project operational repositories
```

Visibility (`public` / `private-incubation`) and lifecycle status (`active`, etc.) remain separate concerns from project kind.

A semantically compatible entry for `theseus-skills` should be equivalent to:

```json
{
  "id": "theseus-skills",
  "kind": "shared-infrastructure",
  "visibility": "public",
  "repository": "TeaShaman-cyber/theseus-skills",
  "role": {
    "en": "Versioned shared agent skills and routing contracts for Theseus projects",
    "ru": "Версионируемые общие навыки агентов и контракты маршрутизации для проектов Theseus"
  },
  "status": "active",
  "topics": ["theseus", "agent-skills", "cross-project-operations"],
  "release_policy": "checkpoint"
}
```

The exact field names and schema version belong to the registry review. The invariant is semantic: tooling and public projections must distinguish research lines from shared infrastructure without inferring kind from repository names or topics.

The project-level registry `release_policy` remains `checkpoint`; individual skill packages inside `theseus-skills` use the SemVer policy defined below. These are different versioning scopes and must not be conflated.

Expected publication flow:

```text
generalize + accept project-kind registry contract
        ↓
create theseus-skills repository boundary
        ↓
populate canonical skill files + skill registry
        ↓
validate exact canonical artifacts and immutable identities
        ↓
only then register theseus-skills as shared-infrastructure / active
        ↓
registry validate
        ↓
registry doctor / remote metadata verification
        ↓
render README.md + README.ru.md from registry
        ↓
review + merge
        ↓
exact remote readback
```

README project-map projections must come from registry state, not hand-maintained rows. The renderer may use grouped sections such as `Research lines` and `Shared infrastructure`, or an explicit project-kind column; either representation must preserve the semantic distinction and must not publish `theseus-skills` as a research line.

This design depends on the registry/projection contract currently being developed in `theseus-research` PR #5 or a reviewed successor. That contract must be generalized before `theseus-skills` can be registered as active shared infrastructure.

### 9.2 Canonical skill identity and metadata

Each canonical `SKILL.md` carries human-readable metadata:

```yaml
metadata:
  version: "1.0.0"
  update_mode: "manual_user"
```

A version string alone is not artifact identity. The canonical skill registry must bind each release to immutable source and exact bytes, for example:

```json
{
  "using-theseus-projects": {
    "current_version": "1.0.0",
    "path": "skills/using-theseus-projects/SKILL.md",
    "source_commit": "<immutable git commit SHA>",
    "sha256": "<SHA-256 of exact SKILL.md bytes>",
    "release_tag": "skill/using-theseus-projects/v1.0.0",
    "update_mode": "manual_user"
  }
}
```

Required release/acceptance validation:

```text
registry.current_version == SKILL.md metadata.version
registry.update_mode      == SKILL.md metadata.update_mode
sha256(SKILL.md bytes)    == registry.sha256
source_commit contains the same path + bytes
release_tag points to source_commit
```

The immutable canonical artifact identity is:

```text
path + source_commit + sha256
```

SemVer and the release tag are navigation labels over that identity. Moving or reusing a release tag to point at different bytes is a contract defect and must not silently redefine a released skill.

A manually installed copy may be claimed byte-identical to canonical only when its bytes or digest are directly observable and match the canonical digest. If a runtime exposes only a version string, installed artifact identity remains `UNKNOWN` even when that string matches the canonical version.

### 9.3 SemVer policy

- **PATCH** — wording, typo, or compatible routing clarification;
- **MINOR** — compatible new routing behavior or project-discovery capability;
- **MAJOR** — incompatible behavior or a changed approval/authority/update boundary.

Canonical skill releases require immutable namespaced Git tags so the required `release_tag -> source_commit` acceptance check has one meaning. Candidate/unreleased work has no release tag.

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

State must remain explicit and independently observable:

```text
CANONICAL_ARTIFACT = version + path + source_commit + sha256 from GitHub
INSTALLED_ARTIFACT = installed version/digest only if runtime or installation acceptance exposes them; else UNKNOWN
SELECTION_MODE      = AUTO_SELECTED | MANUAL_SELECTED | NOT_SELECTED | UNKNOWN
ACTIVE_ARTIFACT     = loaded/active version + digest/identity only if runtime exposes it; else UNKNOWN
LOAD_EVIDENCE       = observed successful load/activation | NOT_OBSERVED | UNKNOWN
EXECUTION_EVIDENCE  = observed invocation/execution | NOT_OBSERVED | UNKNOWN
```

These dimensions must not be collapsed. A skill may be manually selected without being auto-selected. A runtime may report an auto-selection decision even if loading later fails. A successful load does **not** count as execution evidence; invocation remains `NOT_OBSERVED` or `UNKNOWN` until execution is actually observed. A newer installed copy does not prove a cached older body stopped being active. After manual update, acceptance verifies only the dimensions the runtime actually exposes; the rest remain `UNKNOWN`.

## 11. Mutation and publication boundaries

Cookbook and skill changes use normal repository governance, but automation is evidence rather than promotion authority:

```text
proposal
  → diff
  → tests/checks
  → bot/peer review
  → derive immutable promoted-artifact identity
  → explicit authorized human acceptance OF THAT IDENTITY
  → accepted merge/release only if published identity matches acceptance
  → remote readback
```

The human acceptance record must bind the exact artifact being promoted, not merely the PR number or an earlier chronological approval event. For cookbook promotion this may be an immutable tree/content-set digest (or exact commit when appropriate); for a canonical skill release it includes the required source commit, content SHA-256, and release-tag identity. If candidate bytes, tree identity, or release identity change after acceptance, the acceptance is stale and explicit re-acceptance is required before promotion.

The human promotion gate is distinct from the later manual runtime-update gate. Automated checks, bot review, automated merge, conflict resolution, or release machinery alone must not promote materially different bytes under an older acceptance event.

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

## 13. Relationship to externalized learning / AutoMem

This architecture is a **proposed, testable synthesis** of an older Theseus research hypothesis: useful long-horizon adaptation may be externalized into memory policy and experience-to-skill distillation even when the base model weights cannot be updated. The current design is not implementation evidence or proof of long-horizon adaptation.

The useful boundary is:

```text
base model weights
        -> fixed from the operator's point of view

dynamic harness state
        -> memory, retrieval, cookbooks, skills, routing, task state,
           verification, tools, and helper models

effective agent policy
        -> behavior produced by the composition of both
```

A compact working formulation is:

```text
fixed model weights + dynamic harness state = effective agent policy
```

This is **functional weighting, not literal neural-weight mutation**. The terms `external weights` or `dynamic weights` may be used as engineering metaphors only when that distinction is explicit.

The adaptation layers operate at different speeds:

```text
context / session state     -> fastest, ephemeral
memory                      -> fast, plastic experience state
repository cookbook         -> slower, verified operational lessons
shared skill                -> slower still, generalized procedural routing
base model weights          -> outside this architecture's update authority
```

The intended learning loop is therefore:

```text
experience
   ↓
OBSERVED memory / evidence
   ↓ currentness + reproduction + review
VERIFIED reusable lesson
   ↓
repository cookbook
   ↓ repeated cross-task or cross-project evidence
routing-contract change actually required?
   ├─ no  -> keep the generalized procedure in cookbooks or higher-level methodology
   └─ yes -> candidate thin-skill routing change
                 ↓ PR + review + explicit human promotion + immutable release identity
              canonical skill version
   ↓ explicit manual user update
future inference behavior changes
```

If implemented and evaluated, this design would test one governed path adjacent to the earlier `collect trajectories -> score decisions -> propose scaffold/policy diff -> bounded A/B -> readback` AutoMem direction. A single bad episode must not become a durable procedure merely because it was memorable. Broader experience-to-procedure distillation that does not change routing remains outside the thin-skill contract and belongs in cookbook/methodology or a separate future design.

The layers remain distinct:

- **memory** preserves experience and task-relevant semantic state;
- **cookbooks** preserve reviewed repository/runtime-specific operational lessons;
- **skills** preserve slower-changing generalized **routing** policy, not arbitrary procedural encyclopedias;
- **tests, reviewers, currentness checks, and readback** provide evidence about what experience may be promotable;
- **an explicit authorized human promotion gate** decides whether candidate guidance becomes active cookbook authority or a canonical skill release;
- **a separate manual user update gate** controls installation of a canonical skill release into a managed runtime.

This relationship is an architectural synthesis, not evidence that AutoMem, internal model learning, J-space/global-workspace mechanisms, and skill routing are the same mechanism. Mechanistic equivalence remains `UNKNOWN` unless separately demonstrated.

## 14. Example: Needle

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

## 15. Failure handling

If cookbook discovery, currentness, skill-version state, or runtime selection cannot be established, fail honestly:

- `UNKNOWN` — evidence missing;
- `DEGRADED` — usable route exists with weaker authority/coverage;
- `BLOCKED` — required permission, contract, or current state missing;
- `REPROBE_REQUIRED` — cached/remembered state is insufficiently current.

A search miss is not evidence that no guidance exists outside the searched scope.

## 16. Acceptance criteria for implementation phase

Implementation should not begin until this architecture is reviewed and accepted.

When implementation is later approved, minimum acceptance should cover:

1. dedicated canonical `TeaShaman-cyber/theseus-skills` repository with `skills/registry.json` and canonical source for each managed skill;
2. the `theseus-research` project registry distinguishes project kind so shared infrastructure is not mislabeled as a research line;
3. README and README.ru project-map projections render `theseus-skills` from registry state according to its explicit infrastructure kind rather than hand-maintained rows;
4. `theseus-skills` is not registered as `active` until canonical skill files and their validation receipts exist;
5. canonical skill identity requires exact path + immutable source commit + SHA-256, with registry/SKILL metadata consistency validation;
6. cookbook discovery tracks accepted baseline and candidate overlay independently; candidate bytes never silently replace accepted bytes;
7. active cookbook guidance is bound to the target code revision or an explicitly demonstrated compatible revision range;
8. unresolved currentness or invalidating evidence removes the affected baseline rule from active guidance immediately and enters `REPROBE_REQUIRED`/`UNKNOWN`;
9. promoted rules have an explicit invalidation/reprobe path;
10. composed runtime/project cookbook conflicts on the same concern return `BLOCKED` unless authoritative evidence resolves them;
11. canonical skill releases require immutable namespaced release tags bound to the exact source commit;
12. explicit `manual_user` update mode and no automatic runtime skill mutation;
13. repository cookbook discovery at `docs/cookbook/README.md`;
14. missing-cookbook path proposes creation and requires explicit user approval;
15. bootstrap guidance treats history as evidence, not authority;
16. promotion requires verification/review **and explicit authorized human acceptance** before becoming active cookbook authority or a canonical skill release;
17. canonical artifact, installed artifact, selection mode, active artifact, load evidence, and execution evidence are tracked independently and remain `UNKNOWN` where not directly observable;
18. successful load never counts as execution evidence without observed invocation;
19. repeated procedural lessons do not enter a thin skill unless they require an actual routing-contract change;
20. GitHub mutation targets and important postconditions receive exact readback.

## 17. Review questions for Codex and human reviewers

Please review this document specifically for:

1. **Architecture:** does the split `thin skill router / repository-local cookbook` create hidden duplication or authority ambiguity?
2. **Contracts:** are cookbook discovery, bootstrap, promotion, invalidation, and manual-update states deterministic enough to implement and test?
3. **Authority:** can any path accidentally promote historical or unmerged text into current operational authority?
4. **Human approval:** is cookbook creation clearly blocked until explicit user approval?
5. **Skill lifecycle:** is there any hidden path that could be interpreted as automatic installation or self-update?
6. **Artifact identity:** are version, immutable source commit, digest, installed artifact, selection mode, active artifact, and execution evidence sufficiently separated?
7. **Composability:** is runtime guidance plus repository guidance sufficiently partitioned by concern, with `BLOCKED` for unresolved overlap?
8. **Registry integration:** does the generalized project-kind contract cleanly distinguish research lines from shared infrastructure without weakening the existing validation/projection workflow?
9. **Publication order:** can the registry ever advertise an active project before its promised canonical artifacts are present and verified?
10. **Failure modes:** what important edge cases are missing before implementation begins?

## 18. Proposed implementation sequence after review

Only after accepted review:

1. generalize and review the `theseus-research` project-registry/projection contract so `kind: shared-infrastructure` is representable without pretending infrastructure is a research line;
2. create the dedicated `TeaShaman-cyber/theseus-skills` repository boundary, but do not yet register it as active;
3. add `skills/registry.json`, canonical `SKILL.md` sources, CHANGELOGs/READMEs, immutable source-commit/digest identity fields, and validation checks inside `theseus-skills`;
4. adapt the existing MarcoPolo router source and add the generic Theseus project-router skill under review, then validate the initial canonical release artifacts;
5. only after step 4 passes, register `theseus-skills` as public `shared-infrastructure` / `active` through the accepted Theseus project registry;
6. render and verify README.md + README.ru.md project-map projections from that registry entry, then review/merge/read back the exact remote state;
7. ask the user to manually install/update the approved runtime skill version and record only directly observable installed/selection/active/execution state;
8. separately propose the first repository-local cookbook (Needle is a candidate);
9. reconstruct that cookbook from project history under a reviewed bootstrap PR with accepted-baseline trust and currentness gates.

No item in this sequence is authorized by the architecture document alone.
