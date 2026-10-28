# Complementary Defect Discovery in AI-Assisted Software Engineering: An Observational Study of LLM Review and Mutation-Guided CI

**Status:** WORKING DRAFT — unpublished, not peer reviewed. This is a source-bound paper skeleton, not a completed empirical paper.
**Coordination:** [#97](https://github.com/TeaShaman-cyber/theseus-research/issues/97)
**Basis:** [accepted observational comparison, September 2026](https://github.com/TeaShaman-cyber/theseus-research/blob/main/docs/research/2026-09-20-codex-review-vs-heavy-ci.md)
**Authorship/affiliation:** TBD by explicit decision; no institutional affiliation inferred.

## Abstract (working)

AI-assisted software engineering often combines model-based code review and
deterministic testing, yet their contributions to discovering new questions
and retaining checks on existing invariants can be conflated. This candidate
paper organizes retrospective, publicly preserved Theseus development traces:
two research-repository review/design PRs and four merged test-only client PRs
evaluated without completed Codex review. In the historical mutation witness,
seven behavioral tests accompany a shift from 391 killed and 206 surviving
mutants to 424 killed and 173 surviving mutants, without production-code
changes in the tested slice. This does **not** represent 33 distinct defects
or causally prove one verification strategy superior. We propose an evidence
coding protocol separating review questions, confirmed behavioral gaps,
regression tests and equivalent or diagnostic-only mutation survivors.
Repository, period, maturity and task differences preclude a controlled
comparison. The preliminary interpretation is complementary rather than
substitutive; a same-candidate follow-up would be needed to test causality.

**Keywords (provisional):** AI-assisted engineering; code review;
mutation testing; regression tests; provenance; empirical software engineering.

## 1. Introduction and questions

Green tests demonstrate compliance with encoded assertions, not that the
assertions are sufficient. LLM review can raise architecture, privacy,
lifecycle or authority concerns without supplying a reproducible failure.
The study asks what each historical instrument exposed and which findings
were converted into durable repeatable tests.

- **RQ1:** What classes of review questions and test gaps are observable?
- **RQ2:** Which discovered claims became independently checkable regressions?
- **H1, unproven:** review expands the space of questions; mutation-guided
  deterministic QA deepens coverage of already formalized invariants.

We do **not** claim that the cases represent a population, or that review and
CI were randomly assigned to comparable tasks.

## 2. Retrospective design

Cases were selected from completed
[Theseus issue #55](https://github.com/TeaShaman-cyber/theseus-research/issues/55)
and its accepted summary. The study unit is an evidence-backed
PR/claim/test event, not the mutant or the model response taken uncritically.
Use the source inventory to recover exact event identities and CI receipts
before converting preliminary observations into final results.

### 2.1 Review-oriented trace A

- [Research PR #5](https://github.com/TeaShaman-cyber/theseus-research/pull/5),
  historical head `40b572554b8711dc6fb06de6cdc7e02e99f6dfdb`:
  the accepted note reports 45/45 registry checks green, while preserved
  review requests and the migration map raised privacy, identity, pagination,
  fail-closed and readback questions. Latest repository check
  (2026-10-29): **CLOSED, not merged**. Review prompts cannot be counted
  as confirmed defects without tracing their disposition.
- [Research PR #8](https://github.com/TeaShaman-cyber/theseus-research/pull/8):
  iterative review/design discussions challenged provenance, canonical vs
  installed vs executed state, currentness/invalidation and promotion
  authority. Latest repository check (2026-10-29): **OPEN**. Historical
  batches of review remarks require exact finding-by-finding coding.

These are archival review traces, not accepted/merged study interventions.

A [source-level audit](data/2026-10-29-codex-review-audit.md) of
the GitHub inline REST comments found **36 distinct bot-authored review
remarks** (13 on #5 and 23 on #8), plus 29 author replies. These are
**not 36 unique defects**. Four PR #5 validation failures were
independently reproduced with the same synthetic invalid inputs on
original and later exact source commits: unrecognized status, malformed
repository identity, private-incubation repository identity and
visibility/status mismatch. In all four cases the older validator
accepted invalid input and the later validator rejected it; **this
does not establish a real-world data leak or an accepted production
deployment**. Another five comments had corresponding exact-head
regression tests (the full historical 45/45 suite passed) but no
independent pre-fix reproducer in this audit. Twenty #8 threads had
author replies and related revised design text only; no code behavior
was verified. Seven comments (four #5, three #8) had no inline
author reply, with correction status outside the thread UNKNOWN.

This stratification prevents conflating review suggestions, developer
fix claims, source tests, and independently reproduced behavior.
The exact [36-row comment inventory](data/review-comments.json) links
each comment and correction reply to its original SHA and evidence level.

### 2.2 Test-focused trace B

The [client mutation issue #22](https://github.com/TeaShaman-cyber/theseus-1f916-client/issues/22)
and research note record four merged PRs, with no completed Codex review
in those rounds. Historical mutation witness snapshots:

| Step | Exact source head of PR | Added behavioral tests | Killed | Survived |
| --- | --- | ---: | ---: | ---: |
| [pre-#36 baseline](https://github.com/TeaShaman-cyber/theseus-1f916-client/actions/runs/35518827962), `2a8cd41a194c00841e367919ce8449f9e0814119` | 0 | 391 | 206 |
| [#36](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/36), `8707bfb4cecaafbb337603bcafa5c586c92b92db` | 2 | 397 | 200 |
| [#37](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/37), `e0811d8e3667e9f0f98a82b67183e4294b4cb542` | 2 | 403 | 194 |
| [#39](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/39), `f4401c67ac75967118355d7b9039bf846f6eda2c` | 2 | 408 | 189 |
| [#40](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/40), `a669a1c8500c02c86bfb3aef6f77579e15c1c0b7` | 1 | 424 | 173 |

The five [original hosted mutation logs](data/2026-10-29-mutation-source-audit.md)
have now been read, and their exact source commits independently matched to
GitHub Actions. All five runs share the exact `forum_state.py` Git blob,
mutation configuration, pinned dependency lock, runner script and workflow;
each reports `597` total mutants, `mutmut 3.8.0`, and zero incomplete
categories. GitHub diffs confirm each PR adds **only tests**, specifically
2 + 2 + 2 + 1 named test functions. Canonical QA and property runs are
`success` at the same five exact heads. Mutation workflows deliberately
report `failure` for remaining mutants (`SURVIVORS_PRESENT`).

Thus the +33 killed-mutant change is a **source/profile-held-constant
historical observation**. It is not a count of independently confirmed
production defects, nor evidence that the methods were experimentally
matched. The `ackable_cursor` triage is a negative control: seven survivors,
zero classified `REAL_TEST_GAP`, and no score-chasing PR.

## 3. Claim coding and analysis plan (PARTIALLY EXECUTED)

For every candidate claim record: repository, PR/issue, exact source SHA,
timestamp, originating instrument, original claim, independently observed
reproducer, accepted regression, evidence URL, and disposition. The first retrospective claim classification is recorded in the review
comment inventory; independent red-before/green-after verification remains
partial. A prospective comparison still requires frozen coding rules
**before** execution.

- `QUESTION_ONLY`: plausible question, no confirmed failure.
- `CONFIRMED_GAP`: reproducible missing behavior or violated invariant.
- `REGRESSION_ADDED`: accepted test for a stated behavior.
- `EQUIVALENT` / `DIAGNOSTIC_ONLY`: mutation not a valid behavior gap.
- `UNKNOWN`: source, test, denominator or attribution unavailable.

**Cheap baseline:** independently confirmed gaps and regression tests, not
reviewer verbosity or raw mutation score. Quantitative defect rates,
statistical tests, reviewer costs and time-to-disposition are **NOT MEASURED**.
A source-index manifest now records the five historical mutation runs and
seven test names. A separate historical review-comment manifest records
36 Codex comments, response evidence, four independently probed validation
gaps, and explicit UNKNOWN dispositions. Both are **archival audits**,
not a matched cross-method dataset or a prospective experiment.

## 4. Preliminary observations (archival, non-causal)

The new review audit documents directly observed validation gaps and
a larger set of design-review questions spanning architecture, privacy,
currentness and authority boundaries. Only four specific validator
behaviors have independent red-before/green-after proof so far.
In the bounded client sequence, added regression tests correspond to 33
fewer surviving mutants across the archived snapshots. The counts may
include multiple mutants per invariant; neither method's general efficacy,
nor a difference in defect-discovery *rates*, follows from these data.

The `ackable_cursor` non-action is evidence that triage can reject
metric optimization when no actual test gap is identified.

## 5. Threats to validity

1. **Selection and confounding:** the two modes concern different repos,
   tasks, maturity and calendar times. No causal A/B inference is possible.
2. **Measurement units:** 36 Codex inline remarks include correlated
   design questions, 29 separate maintainer replies, and only four
   independently reproduced validator gaps. None of these quantities
   is interchangeable with 597 mutants, distinct defects or accepted tests.
3. **Mutation comparability:** exact baseline SHA, source Git blob, profile
   files and constant 597-mutant denominator are now source-verified; no new
   cross-host reproduction of the generated mutation set was performed.
   Mutants remain correlated and their kill-count is not a unique-bug count.
4. **Missingness:** archival review iterations, rate-limit events,
   negative findings and labor costs may be incompletely preserved.
5. **External validity:** a bounded single-ecosystem comparison cannot
   rank all human/model review or testing systems.
6. **Rights and disclosure:** use public artifacts only. Paper authorship,
   rights and eventual third-party publication require distinct review.

## 6. Discussion and possible prospective work

A falsifiable working pattern is:

`independent questions -> explicit invariant -> deterministic regression
-> repeatable heavy witness -> review of still-unasked questions`.

The retrospective record motivates the pattern but does not establish that
the pattern is optimal. A prospective follow-up would give independent
reviewers and CI **the same exact candidate and a common defect oracle**,
log false positives, finding cost, provider availability and all no-finding
outcomes. Such an experiment has **not been approved or run** under #97.

## 7. Provisional conclusion

The archived evidence now includes independently confirmed validation
errors, nine head regression-test witnesses, and a separate design-only
review set. These justify a transparent observational case study and a
hypothesis about complementary QA roles. It does not demonstrate
causal superiority, replacement of independent review, or one defect for
every killed mutation. The mutation-track source audit is complete
within its stated historical-log scope; review-claim coding and related
scholarly literature assessment remain incomplete.

## Availability and status

Evidence provenance and unresolved extraction requirements:
[data/README.md](data/README.md). No new cleaned dataset, rerun, external
submission, peer review, DOI publication or grant award is claimed.
