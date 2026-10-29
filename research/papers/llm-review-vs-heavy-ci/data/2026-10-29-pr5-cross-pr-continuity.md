# PR #5: resolution continued in a DIFFERENT merged PR

**Inspection date:** 2026-10-29.
**Research issue:** [#97](https://github.com/TeaShaman-cyber/theseus-research/issues/97).
**Original review:** [PR #5](https://github.com/TeaShaman-cyber/theseus-research/pull/5),
CLOSED without merge, exact head
`40b572554b8711dc6fb06de6cdc7e02e99f6dfdb`.
**Actual canonical promotion:** [PR #46](https://github.com/TeaShaman-cyber/theseus-research/pull/46),
MERGED 2026-09-19T06:20:26Z as
`94b012d04024131efd572ea4a5b7a96d56d2c255`.

Four Codex comments at the END of PR #5 contain **no inline author reply**.
Previous manuscript drafts correctly recorded absent thread replies but
had not followed the fixes across GitHub PR boundaries. That gap is now
partially closed by independent historical source-level reproductions.

| Bot comment (no inline reply) | Old PR #5 behavior | First verified fix commit (on PR #46's merged ancestry) | Latest verified main behavior |
| --- | --- | --- | --- |
| [Private candidate discovery](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3941398477) | Synthetic private candidate enters discovery output | [1fc4416](https://github.com/TeaShaman-cyber/theseus-research/commit/1fc4416da7754208f7e913f2ef584ddd269eef29) (earlier public-only query added by [13f7ac2](https://github.com/TeaShaman-cyber/theseus-research/commit/13f7ac232860f1c390c161f14201d62dca323ac4)) | Private candidate excluded, even if fake search API returns one |
| [Incomplete search](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3941398481) | `incomplete_results: true` accepted as empty candidate list | [1fc4416](https://github.com/TeaShaman-cyber/theseus-research/commit/1fc4416da7754208f7e913f2ef584ddd269eef29) | `GitHubUnavailable` raised, fail-closed for this search |
| [Lost doctor JSON report](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3941398485) | Simulated optional issue-publication failure escapes with no report | [12d158d](https://github.com/TeaShaman-cyber/theseus-research/commit/12d158d46fa4e2e22b1047563a4662a11ed4cf90) | JSON persisted, nested `drift_issue.status=UNREACHABLE`; **overall status remains DECLARED_DRIFT, exit code 2** |
| [Two-file write failure](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3941398487) | First README altered when second file write throws `OSError` | [64a01a4](https://github.com/TeaShaman-cyber/theseus-research/commit/64a01a45cccfe157c0a3ea3cdb49d0b3c1cf53d9); hardened by [df21288](https://github.com/TeaShaman-cyber/theseus-research/commit/df212882fd11f20683499b36d5fa966dca9b847e) | Both README files restored after recoverable second-write failure |

Source evidence: [read-only Python reproducer](https://github.com/TeaShaman-cyber/theseus-research/blob/main/research/papers/llm-review-vs-heavy-ci/analysis/reproduce_pr5_unanswered.py) and [exact three-state observations](pr5-unanswered-continuity-results.json).
Each case executes **original PR #5 source -> first verified repair commit -> current main snapshot** with temporary files and fake GitHub transport. All four strict behavioral assertions and first-fix/current-state equality checks passed.

## Interpretation, including a divergence from the reviewer request

**The JSON-report case is a PARTIAL semantic correction relative to the
Codex recommendation.** The reviewer requested a top-level `UNREACHABLE`
status and exit code 3. The accepted implementation preserves the
underlying observation `DECLARED_DRIFT` and exit 2, while recording the
optional publication failure as a separately inspectable nested
`drift_issue.status=UNREACHABLE` with its error. This satisfies the
narrow *report-preservation* invariant but not the proposed global
exit-code/status contract. The difference is observable at the earliest
repair commit and current main, and is not silently labeled a full match.

**The bilingual rollback is bounded.** A second-file `OSError` is handled
by restoring both original files. Later tests also cover partial invalid
UTF-8. This is a compensated two-file write for recoverable exceptions,
**not** an atomic transaction against power loss, process termination,
or failed rollback. We do not infer stronger durability guarantees.

**The private-repository scenario is synthetic.** It proves a historical
discovery/filtering defect on a fake private result, not a real leak or
actual public issue comment. No private repository identifiers are used
in this dataset. The incomplete-results scenario demonstrates one API
uncertainty path, not complete API availability proof.

## Evidence dimensions and wider study implications

- **Inline-thread axis:** four PR #5 bot comments have no author reply,
  a permanently correct historical observation.
- **Accepted-code axis:** three behavior classes received bounded
  corrections on PR #46's ancestry; the publication-failure case also
  received persistence protection but differs from reviewer-requested
  global status/exit semantics.
- **Independent evidence axis:** four original sources, four exact
  first-correction commits, current-main exact SHA
  `362ef9caebc775f09e75bccc408823849a493984`,
  and original 36-comment registry permit cross-version rechecking.

The full PR #5 review has **13 bot comments**: nine with author replies
and historical before/after reproducers at PR #5 candidate head, plus
these four without replies whose repair path was observed across PR #46.
This is **13 source-scoped review findings with reproduced behavior
transitions**, NOT 13 independent deployed defects or 13 production
incidents. PR #8 remains an architectural specification candidate with
20 design-text replies and three unanswered comments; it was not
validated as runtime code in this audit.

This distinction motivates a two-axis outcome classification:
`THREAD_REPLY_PRESENT` is independent of
`REMEDIATION_VERIFIED_IN_ACCEPTED_SOURCE`.
Cross-PR tracking changes the research interpretation; the comment
count alone does not.

**Verification limits:** a first-fix commit on the ancestry of a merged
PR is evidence of repository promotion; the fake-transport tests are
not proof of the actual online GitHub side effects or production usage.
No matched-candidate LLM-review-versus-heavy-CI experiment was performed.
