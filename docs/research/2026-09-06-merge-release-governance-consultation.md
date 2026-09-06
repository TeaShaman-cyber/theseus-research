# Merge and release governance consultation

Status: `ADVISORY DRAFT / NOT AUTHORITY`
Date: 2026-09-06
Scope: Theseus program repositories

## Why this exists

Theseus has moved from a small public-review proposal into an actively maintained research program. The repositories now contain a growing forest of research branches, draft PRs, executable tooling, adapters, methodology candidates, and program-level contract work.

The current failure mode is not lack of work. It is accumulated unfinished integration state: useful work can remain on reviewed but unmerged branches while new work continues around it.

This document is a consultation surface, not a governance decision. It asks for a minimal merge/release discipline that reduces branch debt without turning an independently maintained research program into a process-heavy project.

## Existing authority boundary

The following constraints are already intentional:

- maintainer acceptance remains the final merge/promotion authority;
- automated review is advisory evidence, not authority;
- public review is welcome but does not gate ordinary research work;
- research evidence does not automatically become methodology or program contract;
- executable tooling requires stronger verification than a research note;
- important state-changing operations require observable postconditions;
- process is justified only when it removes a recurring failure or lowers recovery cost;
- support or funding may accelerate the work but must not buy authority over conclusions, ethical purpose, publication integrity, or safety boundaries.

## Current repository classes

```text
theseus-research
  program contract + methodology + research integration

theseus-session-search-lab
  executable research tooling + adapters + forensic evidence retrieval

marcopolo-cookbook
  operational procedures + workspace tools + candidate infrastructure
```

These repositories should not necessarily share identical release rules.

## Current integration snapshot

This is observational state from 2026-09-06, not durable authority.

### theseus-research

| PR | Kind | Current state |
|---|---|---|
| #14 | harness-orientation research | merged to `main` after exact-head clean review |
| #16 | Theseus 1.0 migration map | open; 1 unresolved P2 |
| #13 | forest-level readiness candidate | draft; exact-head clean review; not promoted |
| #9 | adaptive route weighting | open; 6 unresolved findings |
| #8 | skill/cookbook contract | open; 3 unresolved findings |
| #5 | research-line registry integration | open; 4 unresolved findings |

### theseus-session-search-lab

| PR | Kind | Current state |
|---|---|---|
| #21 | opt-in continuity recall | open; CI green; 0 unresolved threads; exact-head Codex review pending |
| #19 | Speed Booster export adapter | open; CI green; 2 unresolved P2 findings |

### marcopolo-cookbook

| PR | Kind | Current state |
|---|---|---|
| #29 | Git-backed workspace RULES projection | open; unresolved review findings remain on current head |
| #23 | lightweight Dev Kit / quality gate | draft; 6 unresolved findings |
| #20 | memory-provider loop research | draft; substantial unresolved review set |
| #25 | query-routed cookbook research | draft; unresolved review work remains |
| #26 | Feynman / Five Whys docs | draft |
| #16 | governed GitHub write route | open; 2 unresolved P1 findings |

## Observed repository conventions

- `theseus-research` currently permits merge commits, squash merges, and rebase merges.
- The recent program research merge used a merge commit, preserving branch provenance.
- Merged remote branches are not deleted automatically by repository settings.
- The three repositories currently have mostly GitHub's default label vocabulary rather than a custom governance taxonomy.
- No established public release/tag cadence is currently visible for these repositories.

## Questions for consultation

Please evaluate the following as an engineering/governance problem, not as a request to maximize process.

### 1. What is the smallest useful merge-readiness model?

Should Theseus use different readiness gates for at least these classes?

```text
A. research note / observational evidence
B. executable research tooling
C. operational infrastructure / cookbook procedure
D. methodology promotion
E. program contract / public status change
```

For each class, what evidence should be required before merge, and what should explicitly *not* be required?

### 2. What should `draft` mean?

Recommend a simple rule for when a PR should remain draft versus become ready-for-merge.

Avoid treating draft as a permanent archive for unfinished ideas if a better disposition exists.

### 3. Which merge method should be the default?

Compare merge commit, squash, and rebase for this research program.

Consider:

- provenance and branch history;
- ease of reconstructing why a research conclusion changed;
- revertability;
- noise from iterative review-fix commits;
- cross-repository evidence references that may point to exact commits.

Recommend one default plus clearly bounded exceptions if needed.

### 4. When should a repository get a release/tag?

Propose the smallest useful release semantics for:

- `theseus-research` as a program contract/research integration repository;
- `theseus-session-search-lab` as executable research tooling;
- `marcopolo-cookbook` as operational infrastructure/procedures.

In particular, evaluate whether:

- Session Search is mature enough for a first `v0.1.0` after the current continuity-recall work lands;
- Theseus `1.0` should mean an accepted active-program contract rather than finished research;
- cookbook should use releases at all, or rely primarily on reviewed main + exact commit provenance.

### 5. What is the minimal useful label vocabulary?

The repositories mostly contain default GitHub labels today.

Recommend labels only if they reduce recurring ambiguity or cleanup cost. Prefer a very small orthogonal set over a taxonomy project.

Potential dimensions to assess:

```text
kind: research / tooling / methodology / contract
state: blocked / ready / needs-decision
cross-repo dependency / release-impact
```

Are any of these worth encoding as labels, or should PR draft state, review threads, Projects, and ordinary text carry the information instead?

### 6. How should stale or long-running branches be disposed?

Recommend a bounded policy for branches/PRs that are:

- useful but blocked on real findings;
- superseded by later work;
- clean research artifacts that were simply never merged;
- experimental spikes whose result is already recorded elsewhere;
- large draft PRs that have accumulated too many unrelated concerns.

The goal is to reduce branch debt without deleting historical evidence.

### 7. How should automated review be used?

Codex currently provides useful exact-head review, but the program does not want automated review to become an implicit external authority or a permanent gate.

Recommend when Codex review is:

- strongly useful;
- optional;
- insufficient by itself;
- unnecessary overhead.

Also recommend how unresolved automated findings should affect merge readiness by artifact class.

### 8. What should happen immediately after this consultation?

Given the snapshot above, propose a **small release train of at most 3–5 integration actions** that removes the most branch debt while preserving current authority and verification boundaries.

Do not recommend fixing every open PR before shipping anything.

## Desired output from review

Please respond with:

1. a minimal merge-readiness matrix by artifact class;
2. a recommended default merge method and exceptions;
3. a minimal release/tag policy by repository;
4. no more than 3–5 labels unless more are demonstrably necessary;
5. a branch-disposition rule;
6. a concrete next 3–5 action release train for the current snapshot;
7. any places where the proposed governance would create more process than value.

Treat all recommendations as advisory. Maintainer acceptance remains separate from this review.
