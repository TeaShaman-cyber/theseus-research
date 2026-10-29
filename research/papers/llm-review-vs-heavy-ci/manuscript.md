# Tracing LLM Review Findings and Mutation-Guided CI Evidence: A Retrospective Theseus Case Study

**Manuscript status:** EDITORIALLY COMPLETE — unpublished, not peer reviewed. Evidence and manuscript scope frozen 2026-10-29.
**Study coordination:** [Theseus #97](https://github.com/TeaShaman-cyber/theseus-research/issues/97).
**Accepted source note:** [September 2026 observational comparison](https://github.com/TeaShaman-cyber/theseus-research/blob/main/docs/research/2026-09-20-codex-review-vs-heavy-ci.md).
**Authors and affiliations:** not assigned; explicit authorship decisions are outside this manuscript's evidence acceptance.

## Abstract

Model-assisted review and mutation-guided testing produce different forms
of software-quality evidence, but review suggestions, proven defects,
regression tests and killed mutants cannot be compared as interchangeable
counts. We retrospectively analyze two selected Theseus research-repository
review/design pull requests and a separate four-PR, test-only mutation
sequence in a client repository. Of 36 Codex-authored review comments,
13 concerned executable code in PR #5: nine have independently reproduced
historical before/after behavior differences within its candidate head,
while four received no inline reply but can be traced through later
accepted code in PR #46. One of those later changes preserves the report
without adopting the reviewer's requested global exit/status semantics.
The remaining 23 comments concern design PR #8: 20 have corresponding
revised text and three lack an inline reply, with no runtime implementation
verification established. In a separate fixed-source, fixed-profile
mutation sequence, seven added tests coincided with killed mutants increasing
from 391 to 424 out of 597, while surviving mutants fell from 206 to 173.
These are **33 more mutants killed**, not 33 independent real-world defects.
The cases are unmatched in repository, task, time and instrumentation, so
they cannot establish causal superiority or quantitative complementarity.
The contribution is an auditable **observational evidence classification**
that distinguishes reviewer assertions, source-reproduced behavior,
accepted-code provenance and test-strengthening signals.

**Keywords:** code review; LLM; mutation testing; regression testing;
evidence provenance; observational software engineering.

## 1. Introduction

A green CI result demonstrates only that the executed assertions passed on
the observed source. A model reviewer may ask a valuable question without
demonstrating a defect; conversely, a newly killed mutant is not itself
evidence of an independent production bug. Treating these outputs as
comparable defect counts would misstate the underlying measurements.

This study asks two bounded questions:

- **RQ1 — Review disposition:** Which historically observed review
  findings can be tied to a reproducible behavior change, a design-only
  revision, or an unresolved thread, including fixes accepted through
  another PR?
- **RQ2 — Mutation evidence:** What do archived CI logs establish about
  test-strengthening under a stable source and mutant profile, without
  assuming that mutant kills are real faults?

The working interpretation is that review can surface questions beyond
encoded test contracts, while deterministic mutation/regression checks
retain executable witnesses for selected invariants. **This is a
hypothesis about roles, not a causal comparison of their effectiveness.**

## 2. Related work

This is a targeted contextualization of the existing cases, not an
exhaustive or systematic literature review. A
[source-identification ledger](data/2026-10-29-related-work-evidence.md)
separately records primary-paper identities and the Notion technical
reviews that originally supplied some discovery leads.

**Review across iterations.**
[Zheng et al., MCR-Bench (2026)](https://doi.org/10.1145/3832219)
study annotated multi-round code-review tasks and defect-state changes.
Their unit is longitudinal review behavior. Our smaller historical case
distinguishes the original comment, an author reply, an actual source
change and independent reproduction; it does not reproduce MCR-Bench or
reuse its reported performance rates.

**Mutation adequacy and real faults.**
[Zhao, Zhou and Cohen (2026)](https://doi.org/10.1145/3832093)
examine when coverage and mutation scores of LLM-generated test suites
correlate with fault detection. Their evaluation setting differs from
our test-only client PRs, but it cautions against interpreting a mutation
score as a real-defect rate.
[Zhu, Panichella and Zaidman (2018)](https://doi.org/10.1002/stvr.1675)
survey mutation testing in quality assurance, including operator choice,
equivalent mutants, cost and subject availability. This motivates
disclosing our exact source commits, tool version, mutation profile and
survivor-classification boundaries.

**From concern to executable witness.**
[Harman et al., Meta ACH (2025)](https://doi.org/10.1145/3696630.3728544)
describe issue-targeted, mutation-guided LLM test generation. Their
industrial acceptance process is not a replication target here; the
methodological connection is the transition from an identified concern
to an executable regression oracle.

**Checking claims of completion.**
[Smyth et al., OverclaimBench (2026)](https://arxiv.org/abs/2609.20812)
investigate agents' completion claims relative to observed tool traces.
This is an **arXiv preprint**, not a confirmed peer-reviewed publication.
Our GitHub review archive does not establish which files the reviewing
agent read, so we do not infer review completeness from its final comments.

These works address different units: review-state transitions,
real-fault-detection proxies, mutation-guided test acceptance and
action coverage. None directly turns this selected, cross-repository
historical sample into a controlled head-to-head comparison.

## 3. Materials and methods

### 3.1 Selection and units of analysis

We use the public historical cases already coordinated under
[Theseus #55](https://github.com/TeaShaman-cyber/theseus-research/issues/55):
research-repository [PR #5](https://github.com/TeaShaman-cyber/theseus-research/pull/5)
and [PR #8](https://github.com/TeaShaman-cyber/theseus-research/pull/8)
for LLM review/design discussions, and the four test-only
[client PRs #36, #37, #39 and #40](data/2026-10-29-mutation-source-audit.md)
for mutation CI. Selection was retrospective and purposive, not random,
blinded or preregistered. The observations are **not paired by code change
or defect oracle**.

Review units are individual Codex-authored inline remarks, tracked by
GitHub comment ID and original source revision; author replies are
separate events. Source-level behavior is evaluated with synthetic
input and controlled before/after checks. Mutation units are
`mutmut` mutants within one fixed mutation profile, not production
failures. A repeated mutation of the same conceptual invariant may
yield multiple killed mutants.

### 3.2 Review evidence and disposition rules

We retrieved the complete available GitHub inline comment collections:
22 entries on PR #5 and 43 on PR #8. After separating maintainer
replies, there are **13 + 23 = 36 Codex comments** and **9 + 20 = 29
maintainer replies**. The
[36-comment inventory](data/review-comments.json) retains the original
comment URL, source SHA, content and separately verified follow-up.

Our retrospective evidence grades are:

- **Reproduced source behavior:** an explicit input demonstrates
  different behavior on pinned historical before/after revisions.
  This verifies the tested branch, not an actual deployed incident.
- **Textual design revision:** a reply points to changed specification
  text. This does not prove implemented or executed behavior.
- **No reply in original thread:** an archival thread fact, independent
  of whether later work in another PR supplies a fix.
- **Accepted-source follow-up:** an independently reproduced repair
  commit belongs to the ancestry of an actually merged PR; its contract
  semantics are compared with the original reviewer request.

The
[PR #5 reproducibility artifacts](data/2026-10-29-codex-review-audit.md)
include four isolated validation probes, five additional behavioral
probes, and a separate
[cross-PR source trace](data/2026-10-29-pr5-cross-pr-continuity.md)
for the final four no-reply remarks. The probes use local files and
fake GitHub transport: they do not make real GitHub writes. PR #8's
design revisions were inspected in source text only.

### 3.3 Mutation evidence and negative control

The
[archived mutation CI audit](data/2026-10-29-mutation-source-audit.md)
identifies five GitHub Actions runs and exact source SHAs. Each run
used `mutmut 3.8.0`, the same `forum_state.py` Git blob, the same
mutation configuration, dependency lock, runner and workflow, and
reported **597 mutants** with zero incomplete categories. The four
client PR diffs changed only `tests/test_durable_state.py`, adding
**2 + 2 + 2 + 1 = 7** deterministic tests. Canonical QA and property
workflows succeeded at the corresponding heads; mutation jobs reported
`SURVIVORS_PRESENT` as a failure because mutants remained.

The client [issue #22](https://github.com/TeaShaman-cyber/theseus-1f916-client/issues/22)
also provides a negative control for uncritical score optimization:
seven `ackable_cursor` surviving mutants were classified as
`DIAGNOSTIC_ONLY` or `EQUIVALENT`, with zero `REAL_TEST_GAP`;
no score-only change was made for them. That triage is a recorded
judgment, not proof that all 206 baseline survivors were equivalent.

## 4. Results

### 4.1 Review findings and their fate

| Review evidence | Number of Codex comments | Verified observation |
| --- | ---: | --- |
| PR #5: author replied; historical candidate-head behavior reproduced | **9** | Four validator guards and five further source-level behaviors differ before/after |
| PR #5: no original reply; later accepted-source correction traced | **4** | Four behavior transitions via merged PR #46; one differs from requested global status semantics |
| PR #8: author replied; design text changed | **20** | Textual specification evidence only, no code/runtime validation |
| PR #8: no original reply | **3** | No implementation or terminal disposition established |
| **Total** | **36** | **Not** 36 independent defects |

For PR #5, the nine replied-to source gaps include unsupported
registry statuses, malformed repository identity, visibility/status
constraints, bilingual projection prevalidation, issue and label
pagination, write readback and JSON error-report creation. The exact
historical candidate head
`40b572554b8711dc6fb06de6cdc7e02e99f6dfdb`
passed its **45/45** regression tests in an independent detached
replay; PR #5 was nonetheless **closed without merge**.

The other four PR #5 comments have **no reply in that original
thread**, yet a [three-version audit](data/pr5-unanswered-continuity-results.json)
verified their paths through accepted
[PR #46](https://github.com/TeaShaman-cyber/theseus-research/pull/46)
(merge `94b012d04024131efd572ea4a5b7a96d56d2c255`):
private-candidate filtering, rejection of incomplete search results,
preservation of a report after optional issue-publication failure,
and restoration of both README files after a recoverable failed write.
The report fix deliberately retains top-level
`status=DECLARED_DRIFT` and exit **2**, while recording nested
`drift_issue.status=UNREACHABLE`; the review requested top-level
`UNREACHABLE` and exit **3**. The compensated README rollback is
**not** crash-atomicity. No real private-data disclosure or production
write failure was demonstrated by these synthetic tests.

The remaining 23 comments belong to design
[PR #8](https://github.com/TeaShaman-cyber/theseus-research/pull/8),
which was **open at the 2026-10-29 observation cutoff**.
The 20 author replies correspond to changes in design text; the
three no-reply questions remain without implementation-level evidence.
They are not added to the count of reproduced code defects.

### 4.2 Fixed-profile mutation snapshots

| Historical step | Source SHA (prefix) | Newly added tests | Killed / 597 | Survived / 597 |
| --- | --- | ---: | ---: | ---: |
| [Baseline run](https://github.com/TeaShaman-cyber/theseus-1f916-client/actions/runs/35518827962) | `2a8cd41a194c` | 0 | 391 | 206 |
| [PR #36](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/36) | `8707bfb4ceca` | 2 | 397 | 200 |
| [PR #37](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/37) | `e0811d8e3667` | 2 | 403 | 194 |
| [PR #39](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/39) | `f4401c67ac75` | 2 | 408 | 189 |
| [PR #40](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/40) | `a669a1c8500c` | 1 | 424 | 173 |

The four PRs added seven tests in total. Across the archived runs,
**33 additional mutants were killed** while the tested production
source and mutation profile remained unchanged. This is evidence of
greater mutant sensitivity for the selected tests, **not 33 newly
found real defects**, a failure-rate estimate or an effect attributable
to the absence of model review. Exact full SHAs, run identifiers,
invariant Git blobs and test names are retained in
[the five-run manifest](data/mutation-runs.json).

## 5. Discussion

The case provides a concrete reason to distinguish **finding generation**,
**source-level falsification**, **accepted remediation**, and
**repeatable regression evidence**. A review remark may be answered
without a verified correction; it may also remain unanswered while its
substance is repaired in another PR. Conversely, a test can kill a
mutant without establishing an independent real fault. These are
different events that require different provenance and denominators.

The results are consistent with *possible* complementary roles:
review comments exposed candidate contract questions, while focused
tests strengthened enforcement of selected invariants. They do not
establish an incremental causal benefit of combining methods because
the observed tasks and repositories differ. A comparison of their
discovery rates, cost, latency or superiority is therefore **not a
result of this paper**.

Theseus already had a broader
[cross-repository learning audit](data/2026-10-29-cross-repository-learning.md)
before this manuscript: five projects were compared for recurring
evidence-loss, phase-ordering and verification-overclaim patterns.
A separate [reciprocal client QA experiment](https://github.com/TeaShaman-cyber/theseus-1f916-client/issues/67)
and [shared QA consumers](https://github.com/TeaShaman-cyber/marcopolo-cookbook/issues/64)
document actual transfer of checks across implementations and
repositories. This pre-existing work informs the interpretation,
**but is not a newly performed experiment or a third evaluated arm**
in this article. Similar symptoms alone are not proof of a shared
causal failure class.

The manuscript's bounded contribution is therefore methodological:
a reproducible example of classifying **what a piece of QA evidence
actually proves**, with explicit links from comments and commits to
behavioral witnesses, CI outputs and accepted-source status.

## 6. Threats to validity

1. **Selection:** The two development traces were selected from an
   existing case study. There is no representative or randomized sample.
2. **Confounding:** Review and mutation evidence come from different
   repositories, tasks, source states and calendar periods. The comparison
   cannot estimate relative or combined causal effectiveness.
3. **Counting:** Comments, replies, distinct failure mechanisms,
   regression assertions and mutants have different denominators.
   Correlated findings and mutants can exaggerate a naive count.
4. **Synthetic verification:** Historical before/after probes demonstrate
   specific source behavior using controlled inputs and fake API responses;
   they are not observations of actual private-data disclosures,
   production incidents, crash-consistent transactions or real external
   write success.
5. **Historical completeness:** GitHub comments and archived Actions
   logs do not guarantee complete model file-read transcripts, complete
   absence-of-finding data, personnel effort, provider availability, or
   retained mutation internals. The five original hosted logs were
   audited, not independently regenerated on another host.
6. **Retrospective coding:** Findings were classified after observing
   outcomes; independent blinded adjudication was not performed.
   PR #8 remains a design-specification trace rather than validated
   runtime changes.
7. **Literature scope:** Related work was selected as relevant context,
   not through a systematic search protocol. It cannot establish that
   the evidence-classification practice is unique in the field.

These limits are part of the present result, not an open-ended worklist.
A future paired experiment would require a frozen common source and
defect oracle, but is **outside this completed retrospective analysis**.

## 7. Conclusion

In the selected archival traces, 13 executable-review remarks from
PR #5 have source-level behavior transitions: nine in its historical
candidate and four traced through later accepted PR #46, with a
documented divergence from one reviewer-requested status contract.
Another 23 Codex remarks relate to design PR #8 and do not constitute
validated runtime faults. Independently, seven tests added in four
client PRs killed 33 additional mutants under a constant 597-mutant
profile and identical production-code blob. These observations support
**traceable differentiation** of review hypotheses, verified
source-level behavior and regression-test sensitivity; they **do not**
support treating the numbers as equivalent defects or ranking the
two QA methods.

The finite deliverable is an evidence-linked observational case study
and its reproducibility inventory, rather than a causal effectiveness
claim or a new ecosystem-wide research program.

## Evidence availability and editorial status

The [evidence inventory](data/README.md) links the original GitHub
review comments, code revisions, CI logs and scripted reproductions;
[references.bib](references.bib) distinguishes primary project
artifacts and scholarly publications. Reusable reproduction scripts
operate on pinned historical source snapshots and synthetic inputs.
The source ledger explicitly records which outcomes are **observed**,
which are **inferred**, and which remain **unknown**.

**Editorial disposition:** complete within the frozen observational
scope as of 2026-10-29. Authorship/affiliation, external peer review
and any distribution decision are separate from this internal
evidence-verification and editing milestone.
