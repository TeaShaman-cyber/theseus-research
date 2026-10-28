# First-party GitHub mutation source audit — 2026-10-29

**Status:** VERIFIED historical source/reporter identity and hosted log readback.
**Not:** a new experimental execution, independent reproduction on a new host,
or proof that each killed mutant is an independent real defect.

See [machine-readable snapshots](mutation-runs.json) for exact source SHAs, all
five hosted run URLs, QA/property run links, and individual test names.

## Exact baseline

- Source commit: [`2a8cd41a194c00841e367919ce8449f9e0814119`](https://github.com/TeaShaman-cyber/theseus-1f916-client/commit/2a8cd41a194c00841e367919ce8449f9e0814119).
- First-party [GitHub Actions mutation log](https://github.com/TeaShaman-cyber/theseus-1f916-client/actions/runs/35518827962) prints the receipt:
  `total=597 killed=391 survived=206 no_tests=0 suspicious=0 timeout=0 segfault=0`.
- `mutmut 3.8.0`; only `forum_state.py` is mutated, selected tests
  `tests/test_durable_state.py`; the receipt source_sha matches the run head.
- GitHub workflow conclusion `failure` is expected for
  `SURVIVORS_PRESENT`, not proof that canonical or property tests failed.
  Both independent baseline QA and property runs completed successfully.

## Comparison integrity

All five exact commits share identical Git blobs for:
`forum_state.py`, `setup.cfg`, the hashed mutation dependency lock,
`tools/ci/mutation-test`, and the mutation workflow file. These are
versioned source identities, not assumptions of equivalent behavior.

The four PRs [#36](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/36),
[#37](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/37),
[#39](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/39) and
[#40](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/40)
each modify **only** `tests/test_durable_state.py`. GitHub PR diffs
contain 2, 2, 2, and 1 added test function(s), respectively.

## Confirmed hosted log sequence

| Exact run | Killed | Survived | Additional killed from prior |
| --- | ---: | ---: | ---: |
| [baseline 35518827962](https://github.com/TeaShaman-cyber/theseus-1f916-client/actions/runs/35518827962) | 391 | 206 | — |
| [PR #36 35525307620](https://github.com/TeaShaman-cyber/theseus-1f916-client/actions/runs/35525307620) | 397 | 200 | 6 |
| [PR #37 35525986665](https://github.com/TeaShaman-cyber/theseus-1f916-client/actions/runs/35525986665) | 403 | 194 | 6 |
| [PR #39 35526782335](https://github.com/TeaShaman-cyber/theseus-1f916-client/actions/runs/35526782335) | 408 | 189 | 5 |
| [PR #40 35527004335](https://github.com/TeaShaman-cyber/theseus-1f916-client/actions/runs/35527004335) | 424 | 173 | 16 |

Every hosted receipt reports `597` mutants, `SURVIVORS_PRESENT`,
zero incomplete categories, a matching exact source SHA and the same mutmut
version. Corresponding canonical QA and property workflow runs report
success at the same PR heads; links are recorded in the JSON manifest.

**Bounded inference:** these snapshots support +33 mutants killed / -33
survivors for a held-constant mutation source/profile, coincident with seven
new deterministic test functions. This is an observational test-coverage
measurement, not a causal generalization about competing QA methods.

## Negative classification / remaining boundaries

The [issue #22 survivor triage](https://github.com/TeaShaman-cyber/theseus-1f916-client/issues/22)
records `ackable_cursor` with seven surviving mutants, all classified as
`DIAGNOSTIC_ONLY` or `EQUIVALENT`, and **zero `REAL_TEST_GAP`**.
No score-only fix was made. Such classifications are human research decisions
rather than mechanically proven equivalence the logs themselves establish.

GitHub Actions exposes log-embedded receipts; the artifact listing for these
runs contained no separate downloadable artifact in the inspected API result.
This audit validates their historical log values and exact identities,
**not** a fresh mutmut replay or an independently recreated mutants database.

Review PR #5 has 22 inline review comments and is CLOSED without merge.
Review PR #8 has 43 inline comments and remains OPEN. These are gross
conversation counts, **not** confirmed bug counts, independent findings, or
a comparable denominator. Claim-by-claim review dispositions remain to audit.
