# Theseus Needle Lab and Research-Line Registry — Design

**Date:** 2026-08-30
**Status:** approved design, incorporating five-optic review
**Parent program:** Theseus
**Scope:** public research infrastructure, documentation, provenance, and GitHub workflow boundaries

## 1. Purpose

Create a new public Theseus research line, `TeaShaman-cyber/theseus-needle-lab`, for observable and reproducible Needle learning experiments without making ChatGPT local compute or MarcoPolo the required execution environment.

At the same time, make `TeaShaman-cyber/theseus-research` the legible root map of the Theseus family so external readers can see how public projects and private incubation lines relate to the program.

This first stage builds the research control plane and documentation. It does **not** invent a Needle training workflow before the actual Needle training interface, data requirements, and runtime constraints are inspected.

## 2. Program boundary

Theseus remains the program-level contract and methodology. No implementation repository defines Theseus.

The public map will distinguish:

| Research line | Visibility | Role | Initial status |
| --- | --- | --- | --- |
| `theseus-research` | public | Program contract, methodology, research map | active / root |
| `theseus-public-observatory` | public | Public-data observation and reproducible verification experiments | active |
| `theseus-needle-lab` | public | Observable, reproducible Needle learning experiments | bootstrapping |
| Sonar | private incubation | Experimental continuity/retrieval research line | private incubation |

The registry lists only research lines explicitly declared part of Theseus. It is not an inventory of every repository owned by `TeaShaman-cyber`.

Sonar is named so readers can understand its relationship to Theseus, but the public README will not expose a private repository link while the implementation remains private.

## 3. Changes to `theseus-research`

### 3.1 Research-line registry

Add a small `Theseus research lines` section to both `README.md` and `README.ru.md`.

Each entry must expose:

- line name;
- public/private-incubation status;
- concise purpose;
- repository link only when public;
- explicit statement that the line supports Theseus but does not define it.

This replaces the current isolated Sonar mention with a durable family map.

### 3.2 Preserve reviewer provenance

Open PR #2 (`master5d`, commits `ac18a5c...` and `22696ef...`) contains still-useful process repairs but now conflicts with the current `0.3-draft` main branch.

Implementation will preserve authorship by integrating the reviewer commits rather than silently copying the text. Conflicts will be resolved against current `main`; maintainer adaptations will be separate commits. Any PR #2 wording that affects contract or methodology meaning must be applied symmetrically to the maintained English and Russian documents in the same revision.

The useful PR #2 changes are:

- named acceptance authority;
- a real `CHANGELOG.md` for the change record promised by the contract;
- explicit `draft / proposed`, `accepted`, and `superseded` states;
- explicit marking of explanatory text;
- a checkable rule preventing methodology changes from silently altering core invariants.

The changelog state describes repository acceptance of a revision, not whether its version label contains `-draft`; an accepted current draft can remain explicitly open to further public revision. The changelog must include the current `0.3-draft` state rather than stopping at historical `0.1/0.2` entries. After successful integration, PR #2 receives a maintainer comment linking the successor integration PR/commits and is closed as `superseded / integrated`, not rejected.

### 3.3 Remaining Issue #3 findings

Issue #3 is not treated as already resolved merely because `0.3-draft` exists. Findings will receive explicit dispositions.

Already substantially addressed by `0.3-draft`:

- ambiguity around replacing humans versus technical components;
- capabilities versus permission;
- stronger MINOR/MAJOR compatibility rules;
- Sonar being experimental rather than normative.

Still actionable in this integration:

1. Replace the narrow wording `reselling donated API credits or compute` with wording that does not imply donated credits already exist or are expected.
2. Add a short clarification that `Sadhana of Engineering` is a metaphorical name for disciplined engineering practice and does not create a religious commitment.
3. Adopt the acceptance-authority and changelog repairs from PR #2.
4. Replace the isolated Sonar reference with the research-line registry.

Deferred rather than invented in this patch:

- define the durable location and privacy boundary for incident / engineering-defect records. The methodology says defects must be recorded, but a public incident ledger may expose operational or personal information. A dedicated follow-up issue will define what is public, private, redacted, or merely linked by receipt before a storage location is made normative.

After implementation, Issue #3 receives a maintainer comment recording `adopted / already addressed / deferred with issue` dispositions. It is closed only after the referenced changes and follow-up issue are observable.

## 4. New repository: `theseus-needle-lab`

### 4.1 Repository properties

- owner: `TeaShaman-cyber`;
- visibility: public;
- default branch: `main`;
- Issues: enabled;
- Wiki: enabled;
- Actions: enabled;
- Pages: reserved for generated experiment documentation;
- license: do not invent one during bootstrap; choose explicitly in a later governance issue if no existing Theseus license decision applies.

Repository description:

> Public Theseus research lab for observable, reproducible, and verifiable Needle learning experiments.

### 4.2 Initial tree

```text
theseus-needle-lab/
├── README.md
├── docs/
│   ├── architecture.md
│   └── experiment-lifecycle.md
├── experiments/
│   └── README.md
├── receipts/
│   └── README.md
└── .github/
    ├── ISSUE_TEMPLATE/
    │   └── experiment.yml
    └── workflows/
        └── docs-check.yml
```

No `src/`, model artifacts, datasets, or fabricated training command are added until the first Needle interface investigation establishes what is actually required.

### 4.3 README contract

The README must state:

- this repository is a research line under Theseus;
- it is not the Theseus program contract;
- experiments are hypothesis-driven and negative results are first-class;
- a green GitHub Action proves only the declared job postcondition, not model quality or scientific truth;
- training outputs become accepted results only after evaluation and verification;
- secrets, private corpora, and user conversation data must not enter the public repository or logs;
- repository visibility is public for research transparency, but public visibility does not itself grant open-source reuse rights; licensing is governed only by an explicit license decision.

## 5. Experiment lifecycle

An Issue is the unit of research intent.

```text
IDEA
  -> SPECIFIED
  -> RUNNING
  -> VERIFYING
  -> ACCEPTED | REJECTED | INCONCLUSIVE
```

The experiment issue records at minimum:

- hypothesis/question;
- data or dataset manifest identity;
- configuration identity;
- success/failure criteria;
- privacy/public-data classification;
- execution run link;
- artifact/receipt hashes when available;
- final disposition.

Commits and PRs reference the issue number. Accepted implementation changes use normal reviewable Git history rather than editing experiment history in place.

## 6. GitHub Project

Create a GitHub Project owned by `TeaShaman-cyber` named:

`Theseus — Needle Lab`

The repository and initial research issues are linked to it.

Preferred research states:

- Idea
- Specified
- Running
- Verifying
- Accepted
- Rejected
- Inconclusive

If the current GitHub OAuth profile lacks the Project scope, repository creation proceeds but Project creation is reported `BLOCKED` until the smallest additional authorization is explicitly completed. No alternative hidden credential route is used.

## 7. Wiki

The Wiki is the human-oriented map, not the machine source of truth. Wiki seeding is capability-gated: enable Wiki first, probe the separate Wiki git remote, and only seed pages after a writable path is observed. If the remote cannot be initialized or written through the verified GitHub route, report `WIKI_SEEDING=BLOCKED` rather than claiming success.

Bootstrap pages:

- `Home` — purpose, relation to Theseus, navigation;
- `Terminology` — Needle, experiment, candidate, receipt, verification;
- `Research-Lifecycle` — human-readable version of the issue lifecycle.

Canonical machine-relevant contracts, schemas, and experiment records stay in the main repository because the Wiki is a separate Git repository and should not silently become authority.

## 8. Actions and auto-documentation

### 8.1 Stage 1: bootstrap validation only

The initial workflow is intentionally small. `docs-check.yml` verifies that required repository documentation and experiment template files exist and are internally linkable. It must not pretend to train Needle. It starts with least-privilege workflow permissions (`contents: read`) and records the observable GitHub runner/environment identity available to the job. Third-party Actions are pinned to reviewed versions, preferably commit SHAs where practical, so dependency identity is part of provenance.

### 8.2 Stage 2: real Needle experiment pipeline

Only after the first investigation issue establishes the executable Needle interface, a later reviewed change may add:

```text
prepare
  -> train / learn
  -> evaluate
  -> verify on clean job/runtime
  -> emit receipt.json
  -> publish content-addressed / integrity-verifiable artifact
```

A receipt should eventually include, where available:

- source commit SHA;
- workflow identity;
- data manifest hash;
- config hash;
- random seed;
- runtime/tool versions and available runner/image identity;
- execution status;
- artifact hash and storage location/retention class;
- evaluation metrics;
- verification status.

### 8.3 Pages

Pages is generated from repository documentation and machine-readable receipts. The generated site is a view, not authority.

A run does not directly rewrite canonical documentation. When a result deserves permanent narrative documentation, automation may open a documentation PR for human review rather than silently committing to `main`.

## 9. First issues

Create at least these bootstrap issues in `theseus-needle-lab`:

1. **Map the real Needle learning interface and runtime requirements**
   Determine executable entry points, dependencies, data format, CPU/GPU needs, duration, outputs, and reproducibility controls before writing training CI.

2. **Define experiment receipt schema v0.1**
   Specify the smallest machine-readable provenance and verification record needed for reproducibility.

3. **Decide artifact and dataset storage boundaries**
   Determine what belongs in Git, GitHub Artifacts/Releases, external storage, or must remain private.

No issue may claim that GitHub-hosted runners are sufficient until measured.

## 10. Verification and success criteria

The bootstrap is successful only after observable read-back confirms:

### `theseus-research`

- integration branch is based on current `main`;
- reviewer authorship/provenance is preserved where PR #2 content is reused;
- EN/RU registry sections agree in meaning;
- new changelog/authority text does not weaken current `0.3-draft` invariants;
- Issue #3 dispositions point to actual commits/issues rather than promises.

### `theseus-needle-lab`

- repository exists and is public;
- default branch and repository settings match the design;
- README and initial docs are readable from remote `main`;
- Issues and Wiki are enabled; Wiki seed pages are readable back, or seeding is explicitly reported `BLOCKED` with the observed capability limitation;
- bootstrap issues exist and link to the Project when capability permits;
- workflow YAML is present with least-privilege permissions and at least one bootstrap validation run has an observable conclusion;
- workflow provenance records available runner/environment identity and reviewed dependency versions;
- no training success is claimed before a real Needle pipeline exists.

### GitHub Project

- Project exists and is readable back through `gh`, or the exact missing authorization is reported as `BLOCKED`.

## 11. Change sequencing

Implementation order:

1. create the empty public `theseus-needle-lab` repository first and read it back, so later documentation links point to a real object;
2. create an integration branch in `theseus-research`;
3. integrate reviewer PR #2 with preserved provenance and resolve against `0.3-draft`;
4. add bilingual research-line registry and remaining low-risk review fixes, including symmetric EN/RU contract/methodology wording where meaning changes;
5. add/update `CHANGELOG.md` through current `0.3-draft`, then open a reviewable integration PR; do not silently merge it;
6. bootstrap `theseus-needle-lab` repository structure on `main`;
7. create Project, enable Wiki, probe Wiki seeding capability, and create bootstrap issues, subject to verified GitHub capability;
8. run bootstrap validation and read back remote state;
9. comment on Issue #3 with explicit dispositions and references; comment on PR #2 with successor provenance and close it as superseded/integrated only after that provenance is observable;
10. stop before implementing the real Needle training pipeline.

## 12. Non-goals for this stage

- proving that Needle training works on GitHub-hosted runners;
- uploading private conversation corpora or credentials;
- defining a universal model-evaluation framework;
- choosing GPU infrastructure before measurement;
- auto-promoting a candidate model/artifact to `current`;
- silently merging the `theseus-research` integration PR;
- making Wiki or Pages authoritative over versioned repository records.
