# Codex review vs heavy CI: an observational comparison

**Date:** 2026-09-20

**Status:** research note / observational comparison
**Tracking issue:** `TeaShaman-cyber/theseus-research#55`

## Question

Theseus has now exercised two materially different verification loops:

```text
A. exact-head LLM review -> findings -> fixes -> deterministic QA
B. formalized invariants -> canonical/property/mutation CI -> survivor classification -> regressions
```

This note asks what each loop appears to contribute to defect discovery and to the
project's learning process.

It is **not** a controlled A/B experiment. The compared repositories, code maturity,
and time periods differ. The evidence supports an observational process comparison,
not a causal ranking of reviewers or tools.

## Evidence set

### Trace A — Codex-centric review

Representative evidence comes from `TeaShaman-cyber/theseus-research`.

#### PR #5 — registry integration

At exact head `40b572554b8711dc6fb06de6cdc7e02e99f6dfdb`, the repository already reported
45/45 deterministic registry tests passing, plus `validate` and `render --check`.
The preserved exact-head review request still asked Codex to challenge:

- private-incubation repository-identity disclosure;
- visibility/status cross-field consistency;
- JSON fail-closed behavior on invalid/projection-mismatch exits;
- pagination before drift classification;
- repository identity validation;
- bilingual projection atomicity;
- issue-dedup pagination;
- remote write readback.

The later 1.0 migration map still recorded this candidate as `FIX BEFORE MERGE` with
four unresolved review findings. Green deterministic QA therefore did not exhaust the
review question space.

Evidence:

- `TeaShaman-cyber/theseus-research#5`
- `docs/research/2026-09-06-theseus-1.0-migration-map.md`

#### PR #8 — versioned skills / repository cookbooks

The design-review loop repeatedly changed the architecture after Codex challenges.
Preserved review requests explicitly record:

- a revision after prior findings;
- a later request after the "latest eight findings were addressed";
- another request after the "remaining four review findings were addressed".

The challenged concerns included:

- accepted provenance vs unmerged candidate state;
- currentness / invalidation / reprobe lifecycle;
- canonical vs installed vs selected vs executed skill state;
- runtime/project cookbook composition;
- immutable skill identity and release tags;
- human promotion vs runtime-update authority;
- externalized-learning claims vs implementation evidence.

The migration map later recorded three unresolved P2 findings on the design candidate.
This is characteristic of a reviewer expanding or restructuring the contract itself,
not merely checking whether existing tests cover every branch.

Evidence:

- `TeaShaman-cyber/theseus-research#8`
- `docs/research/2026-09-06-theseus-1.0-migration-map.md`

### Trace B — heavy CI without completed Codex review

Representative evidence comes from `TeaShaman-cyber/theseus-1f916-client` issue #22.

For PRs #36, #37, #39, and #40, GitHub records no completed Codex review. The only
Codex-side comments are quota-limit messages. These PRs were instead evaluated using:

- canonical exact-source QA;
- generated property tests;
- targeted mutation analysis during classification;
- full hosted mutation witnesses on GitHub runners;
- exact SHA and remote readback.

Observed mutation progression:

| Step | Exact PR head | Behavioral regressions added | Killed | Survived | Main gap classes |
| --- | --- | ---: | ---: | ---: | --- |
| accepted starting baseline | pre-#36 | — | 391 | 206 | established durable-state baseline |
| PR #36 | `8707bfb4cecaafbb337603bcafa5c586c92b92db` | 2 | 397 | 200 | recovery guard; caller clock / `updated_at_ms` |
| PR #37 | `e0811d8e3667e9f0f98a82b67183e4294b4cb542` | 2 | 403 | 194 | default clock; fresh recovery epoch; update timestamp |
| PR #39 | `f4401c67ac75967118355d7b9039bf846f6eda2c` | 2 | 408 | 189 | malformed canonical state; recovery validation boundary |
| PR #40 | `a669a1c8500c02c86bfb3aef6f77579e15c1c0b7` | 1 | 424 | 173 | canonical recovery positive path / recovery invariants |

Across those four PRs, **seven ordinary behavioral regression tests removed 33
surviving mutants**. This does **not** mean "33 bugs". Multiple mutants often represent
the same missing behavioral invariant.

The same classification process also produced a useful negative result:
`ackable_cursor` had seven surviving mutants but zero `REAL_TEST_GAP` survivors. They
were classified as diagnostic-only or equivalent, so no PR was created merely to
improve the mutation score.

Evidence:

- `TeaShaman-cyber/theseus-1f916-client#22`
- PRs `TeaShaman-cyber/theseus-1f916-client#36`, `#37`, `#39`, `#40`

## Observed difference

| Dimension | Codex-centric trace | Heavy-CI trace |
| --- | --- | --- |
| Typical discovery | New architectural or semantic question classes | Missing coverage inside an already formalized contract |
| Examples | authority, privacy, provenance, pagination, lifecycle, identity | wrong branch predicate, wrong field, missing positive path, clock/state invariant |
| Reproducibility | exact-head binding is possible, but output depends on model/provider availability | deterministic exact-SHA runner evidence once the invariant/profile exists |
| Provider dependency | quota / model / service availability matters | runner/toolchain availability matters, but no LLM quota is required |
| Triage burden | higher semantic interpretation; may reshape the design | survivor classification still needs judgment, but the failing witness is mechanically reproducible |
| Negative evidence | "no finding" is useful but model-dependent | equivalent/diagnostic survivor classification can explicitly prevent score chasing |
| Learning effect | can introduce a previously unknown failure class | can make an already known failure class difficult to regress silently |

## Epistemic interpretation

### FACT

- The older research traces contain deterministic-QA-green states followed by further
  Codex review questions and preserved unresolved findings.
- The four client PRs listed above have no completed Codex review and do have exact-SHA
  canonical/property/mutation evidence.
- The mutation witness moved from `391 killed / 206 survived` to
  `424 killed / 173 survived` across those bounded slices.
- Seven new behavioral regression tests account for that 33-mutant reduction.
- At least one survivor group (`ackable_cursor`) was explicitly classified with zero
  real test gaps rather than converted into tests for score improvement.

### INFERENCE

The traces suggest a division of labor:

- independent model/human/community review is comparatively strong at **expanding the
  space of questions**;
- heavy deterministic CI is comparatively strong at **deepening coverage inside a
  question space that has already been formalized into invariants**.

This inference is supported by the defect classes observed in these traces, but the
comparison is confounded by different repositories and maturity levels.

### HYPOTHESIS

A mature Theseus workflow can reduce dependence on LLM review for routine debugging by
turning previously discovered failure classes into reusable deterministic/heavy QA.
Independent review then becomes more valuable when used periodically for semantic,
authority, lifecycle, and architecture challenges that the current verifier cannot ask
on its own.

A concise target loop is:

```text
external review / field evidence discovers a new class
        -> formalize the invariant
        -> deterministic regression
        -> property / mutation / domain-specific heavy witness where useful
        -> reusable QA primitive after repeated proof
        -> later independent review probes for the next unknown class
```

Heavy QA therefore does not replace independent review. It can **externalize and retain
part of the reviewer's past learning**, reducing the need to rediscover the same defect
class through another expensive semantic review cycle.

## Why this matters for shared infrastructure

This supports the current Heavy QA direction:

1. project repositories remain the place where domain-specific invariants are defined;
2. a concrete repository first proves a useful verifier/profile;
3. stable generic runner mechanics move into shared infrastructure such as
   `marcopolo-cookbook`;
4. consumers pin exact promoted revisions;
5. reviewer/model availability is no longer a hidden prerequisite for routine
   deterministic acceptance;
6. independent review remains a separate evidence channel rather than merge authority.

This is consistent with the existing failure-class discipline in
`docs/qa/failure-classes.md`: recurring findings should become general invariants plus
representative deterministic guards rather than one test per historical bug.

## Candidate metrics for a stronger future comparison

A future controlled fixture should bind both modes to the **same exact candidate SHA**
and measure at least:

| Metric | Why it matters |
| --- | --- |
| new failure classes discovered | distinguishes semantic expansion from repetition |
| confirmed findings | avoids rewarding reviewer verbosity |
| false positives / diagnostic-only findings | measures triage cost |
| deterministic regressions produced | measures retained learning |
| mutation survivors killed | useful only for mutation-applicable scopes |
| reviewer iterations | attention / feedback-loop cost |
| exact-SHA reproducibility | whether another run can reproduce the evidence |
| provider/rate/quota failures | operational dependency |
| wall-clock runner time | compute cost |
| human/agent triage time | attention cost |
| contract-expanding vs contract-deepening findings | tests the main hypothesis directly |

One suitable future experiment is to preserve a bounded PR fixture with seeded but
undisclosed defect classes, run the heavy-QA profile and one or more independent
reviewers separately, then disposition all findings against the same oracle.

## Relationship to active work

- `theseus-research#30` studies diversity among independent LLM reviewers. This note
  instead compares semantic review with deterministic/heavy verification.
- `theseus-research#50` established recurring failure-class tracking and atomic
  contract regressions.
- `theseus-1f916-client#22` supplies the current mutation-classification trace.
- `theseus-1f916-client#38` treats the forum client as a Heavy QA v2 pilot/consumer,
  with reusable runner mechanics intended to migrate to shared infrastructure only
  after a concrete consumer proves their shape.

## Bounded conclusion

The evidence does not support "Codex is unnecessary" or "heavy CI is superior".
It supports a narrower process claim:

> Use deterministic and heavy CI to make known invariants cheap to re-check; use
> independent reviewers to challenge whether the current invariants are the right and
> sufficient ones.

That division better protects human attention and turns useful review findings into
persistent project capability instead of repeatedly paying to rediscover them.
