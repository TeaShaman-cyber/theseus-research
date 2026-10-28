# Evidence inventory — source pointers only

**Status:** INDEX ONLY; no independent re-extraction or dataset re-run.
**Tracking:** [theseus-research #97](https://github.com/TeaShaman-cyber/theseus-research/issues/97)

| Source | Role | Observed identity/status (2026-10-29) | Needed before publication |
| --- | --- | --- | --- |
| [Accepted comparison](https://github.com/TeaShaman-cyber/theseus-research/blob/main/docs/research/2026-09-20-codex-review-vs-heavy-ci.md) | Historical synthesis | accepted in main | Link each inference to raw event |
| [Research #55](https://github.com/TeaShaman-cyber/theseus-research/issues/55) | Original study coordination | closed | Not independent from its source note |
| [Research PR #5](https://github.com/TeaShaman-cyber/theseus-research/pull/5) | Review questions | historical head `40b572554b8711dc6fb06de6cdc7e02e99f6dfdb`, CLOSED | Confirm each actual defect disposition |
| [Research PR #8](https://github.com/TeaShaman-cyber/theseus-research/pull/8) | Design review | head `4ebaae08fa15c4c7e77b1db7879186b7d3d78056`, OPEN | Separate discussion from confirmed findings |
| [Client issue #22](https://github.com/TeaShaman-cyber/theseus-1f916-client/issues/22) | Mutation classification | historical witness | Exact baseline SHA/config and denominators |
| [Client PR #36](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/36) | Regression tests | `8707bfb4cecaafbb337603bcafa5c586c92b92db`, MERGED | Obtain matching hosted mutation receipt |
| [Client PR #37](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/37) | Regression tests | `e0811d8e3667e9f0f98a82b67183e4294b4cb542`, MERGED | Obtain matching hosted mutation receipt |
| [Client PR #39](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/39) | Regression tests | `f4401c67ac75967118355d7b9039bf846f6eda2c`, MERGED | Obtain matching hosted mutation receipt |
| [Client PR #40](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/40) | Regression tests | `a669a1c8500c02c86bfb3aef6f77579e15c1c0b7`, MERGED | Obtain matching hosted mutation receipt |

## Missing, not assumed

1. Raw CI artifacts for each reported mutation snapshot, config/profile
   identity, source SHA, and population comparability.
2. Diff-backed verification of test additions and unchanged production code.
3. Claim-level review attribution: question vs confirmed gap vs fixed finding.
4. Honest accounting for quota failures, missing events and equivalent mutants.
5. Frozen extraction/coding rules before a reproducible numerical analysis.

A source URL alone is not an experimental result. Do not store project tokens,
non-public correspondence, private traces or unreviewed personal information.
