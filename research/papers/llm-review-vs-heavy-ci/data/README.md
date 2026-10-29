# Evidence inventory — primary source audit

**Status:** historical mutation CI audit VERIFIED; Codex review comment census and four validation reproducers VERIFIED. Broader review dispositions, runtime implementation, and prospective matched study remain OPEN.

- [Related-work primary-source evidence matrix](2026-10-29-related-work-evidence.md)
- [Original CI log source audit](2026-10-29-mutation-source-audit.md)
- [Five-run machine-readable evidence manifest](mutation-runs.json)
- [Codex review source audit](2026-10-29-codex-review-audit.md)
- [All 36 bot-authored review comments with source links](review-comments.json)
- [Four historical before/after validator reproducers](pr5-validation-reproducers.json)
- [Read-only local reproduction script](https://github.com/TeaShaman-cyber/theseus-research/blob/main/research/papers/llm-review-vs-heavy-ci/analysis/reproduce_pr5_validation.py)
**Tracking:** [theseus-research #97](https://github.com/TeaShaman-cyber/theseus-research/issues/97)

| Source | Role | Observed identity/status (2026-10-29) | Needed before publication |
| --- | --- | --- | --- |
| [Accepted comparison](https://github.com/TeaShaman-cyber/theseus-research/blob/main/docs/research/2026-09-20-codex-review-vs-heavy-ci.md) | Historical synthesis | accepted in main | Link each inference to raw event |
| [Research #55](https://github.com/TeaShaman-cyber/theseus-research/issues/55) | Original study coordination | closed | Not independent from its source note |
| [Research PR #5](https://github.com/TeaShaman-cyber/theseus-research/pull/5) | Review questions | historical head `40b572554b8711dc6fb06de6cdc7e02e99f6dfdb`, CLOSED | 4 validators independently reproduced; 5 further source-tested; 4 no thread reply |
| [Research PR #8](https://github.com/TeaShaman-cyber/theseus-research/pull/8) | Design review | head `4ebaae08fa15c4c7e77b1db7879186b7d3d78056`, OPEN | 20 revised-design claims with text anchors, 3 no thread reply; no runtime proof |
| [Client issue #22](https://github.com/TeaShaman-cyber/theseus-1f916-client/issues/22) | Mutation classification | historical witness | Verified in GitHub logs; reviewer coding still open |
| [Client PR #36](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/36) | Regression tests | `8707bfb4cecaafbb337603bcafa5c586c92b92db`, MERGED | Hosted log receipt verified; no new rerun |
| [Client PR #37](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/37) | Regression tests | `e0811d8e3667e9f0f98a82b67183e4294b4cb542`, MERGED | Hosted log receipt verified; no new rerun |
| [Client PR #39](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/39) | Regression tests | `f4401c67ac75967118355d7b9039bf846f6eda2c`, MERGED | Hosted log receipt verified; no new rerun |
| [Client PR #40](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/40) | Regression tests | `a669a1c8500c02c86bfb3aef6f77579e15c1c0b7`, MERGED | Hosted log receipt verified; no new rerun |

## Missing, not assumed

1. **DONE for archived GitHub CI logs:** source SHA, mutmut profile, exact Git
   blobs, five run receipts and stable 597-mutant denominator independently
   inspected; original logs are linked, not copied as huge files.
2. **DONE:** GitHub PR diffs independently verify only
   `tests/test_durable_state.py` changed across the four PRs; all seven named
   tests are recorded in `mutation-runs.json`.
3. **PARTIAL:** all 36 Codex comments classified by source evidence; four
   narrow validation gaps independently reproduced, five more passing head
   regressions, twenty design-text claims, seven without inline author reply.
   Remaining claim-level root-cause analysis is OPEN.
4. **OPEN:** defensible treatment of absent review events, quota failures,
   equivalent mutants and editorial selection effects.
5. **OPEN:** freeze cross-method coding rules and create a scholarly related-
   work section before quantitative or generalized scientific claims.

A source URL alone is not an experimental result. Do not store project tokens,
non-public correspondence, private traces or unreviewed personal information.
