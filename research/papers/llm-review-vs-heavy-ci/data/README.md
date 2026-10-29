# Evidence inventory — primary source audit

**Status:** historical evidence audited; manuscript editorial work complete. Nine candidate-head and four later accepted-source PR #5 behavior transitions reproduced; PR #8 implementation and prospective experimental questions remain outside this study.

- [Related-work primary-source evidence matrix](2026-10-29-related-work-evidence.md)
- [Cross-repository learning and verified QA transfer (existing Theseus evidence)](2026-10-29-cross-repository-learning.md)
- [Original CI log source audit](2026-10-29-mutation-source-audit.md)
- [Five-run machine-readable evidence manifest](mutation-runs.json)
- [Codex review source audit](2026-10-29-codex-review-audit.md)
- [Cross-PR disposition audit: four unanswered PR #5 threads](2026-10-29-pr5-cross-pr-continuity.md)
- [Four original / first-fix / main observations](pr5-unanswered-continuity-results.json) and [read-only reproducer](https://github.com/TeaShaman-cyber/theseus-research/blob/main/research/papers/llm-review-vs-heavy-ci/analysis/reproduce_pr5_unanswered.py)
- [All 36 bot-authored review comments with source links](review-comments.json)
- [Four historical before/after validator reproducers](pr5-validation-reproducers.json)
- [Five additional historical red-green reproductions](2026-10-29-pr5-five-redgreen-audit.md)
- [Five-result JSON](pr5-remaining-validation-reproducers.json) and [reproduction script](https://github.com/TeaShaman-cyber/theseus-research/blob/main/research/papers/llm-review-vs-heavy-ci/analysis/reproduce_pr5_remaining.py)
- [Read-only local reproduction script](https://github.com/TeaShaman-cyber/theseus-research/blob/main/research/papers/llm-review-vs-heavy-ci/analysis/reproduce_pr5_validation.py)
**Tracking:** [theseus-research #97](https://github.com/TeaShaman-cyber/theseus-research/issues/97)

| Source | Role | Observed identity/status (2026-10-29) | Evidence boundary |
| --- | --- | --- | --- |
| [Accepted comparison](https://github.com/TeaShaman-cyber/theseus-research/blob/main/docs/research/2026-09-20-codex-review-vs-heavy-ci.md) | Historical synthesis | accepted in main | Link each inference to raw event |
| [Research #55](https://github.com/TeaShaman-cyber/theseus-research/issues/55) | Original study coordination | closed | Not independent from its source note |
| [Research PR #5](https://github.com/TeaShaman-cyber/theseus-research/pull/5) | Review questions | historical head `40b572554b8711dc6fb06de6cdc7e02e99f6dfdb`, CLOSED | 9 fixed in candidate head; 4 no-reply threads independently traced to later accepted source (one partial contract divergence) |
| [Research PR #8](https://github.com/TeaShaman-cyber/theseus-research/pull/8) | Design review | head `4ebaae08fa15c4c7e77b1db7879186b7d3d78056`, OPEN | 20 revised-design claims with text anchors, 3 no thread reply; no runtime proof |
| [Client issue #22](https://github.com/TeaShaman-cyber/theseus-1f916-client/issues/22) | Mutation classification | historical witness | Verified in GitHub logs; reviewer coding still open |
| [Client PR #36](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/36) | Regression tests | `8707bfb4cecaafbb337603bcafa5c586c92b92db`, MERGED | Hosted log receipt verified; no new rerun |
| [Client PR #37](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/37) | Regression tests | `e0811d8e3667e9f0f98a82b67183e4294b4cb542`, MERGED | Hosted log receipt verified; no new rerun |
| [Client PR #39](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/39) | Regression tests | `f4401c67ac75967118355d7b9039bf846f6eda2c`, MERGED | Hosted log receipt verified; no new rerun |
| [Client PR #40](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/40) | Regression tests | `a669a1c8500c02c86bfb3aef6f77579e15c1c0b7`, MERGED | Hosted log receipt verified; no new rerun |

## Evidence completed and explicit limits

1. **DONE for archived GitHub CI logs:** source SHA, mutmut profile, exact Git
   blobs, five run receipts and stable 597-mutant denominator independently
   inspected; original logs are linked, not copied as huge files.
2. **DONE:** GitHub PR diffs independently verify only
   `tests/test_durable_state.py` changed across the four PRs; all seven named
   tests are recorded in `mutation-runs.json`.
3. **PARTIAL:** all 36 Codex comments classified by thread evidence. Nine
   PR #5 replied-to findings independently reproduced at its historical head,
   four no-reply PR #5 findings independently traced through merged PR #46
   to current code (one does not match the original global exit/status
   recommendation); twenty PR #8 design-text replies and three unanswered
   PR #8 questions still lack runtime verification. Seven comments across
   both PRs had no original inline reply: historical thread fact, not
   equivalent to absence of later correction. Underlying root-cause
   independence and production incidence remain UNKNOWN.
4. **LIMITATION, NOT A TASK:** absence-of-finding events, cost, provider
   availability and editorial selection are not fully observable. Avoid
   generalizing or inferring unrecorded outcomes.
5. **DONE for this manuscript:** source-verified Related Work and the
   retrospective classification are included. A prospective frozen
   coding protocol is outside the completed observational study.

A source URL alone is not an experimental result. Do not store project tokens,
non-public correspondence, private traces or unreviewed personal information.
