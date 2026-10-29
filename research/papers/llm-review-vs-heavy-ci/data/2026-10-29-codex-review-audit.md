# Codex review source audit — PR #5 and PR #8 (2026-10-29)

**Status:** historical GitHub review-thread inventory verified; nine PR #5 behaviors independently reproduced before/after (four validation guards and five additional cases).
**Scope:** two historical candidate PRs. This is neither a controlled comparison nor a claim of accepted runtime remediation.

Machine-readable evidence: [36 reviewed comments](review-comments.json), each linked to original GitHub comment ID, source commit, file, author reply where present, and source-level witness. The unit is the **review thread**, not an independently confirmed bug.

## Disjoint evidence categories

The GitHub review-comment REST collection has 65 entries: 36 Codex inline comments and 29 author replies.

| Category | PR #5 | PR #8 | Total | Evidence meaning |
| --- | ---: | ---: | ---: | --- |
| Independent historical red-before/green-after behavior and passed head tests | 9 | 0 | **9** | Four validator guards and five more documented behaviors differ at exact source heads |
| Test-only correction claims not independently reproduced | 0 | 0 | **0** | All nine replied-to PR #5 comments have isolated source-level behavior witnesses |
| Author reports design correction, relevant text found in final draft | 0 | 20 | **20** | Revised design text; NOT implemented or runtime-verified |
| No author reply in thread | 4 | 3 | **7** | No thread-level correction evidence; fix elsewhere UNKNOWN |
| **Distinct Codex comments** | **13** | **23** | **36** | Review observations, **not** defect counts |

[PR #5](https://github.com/TeaShaman-cyber/theseus-research/pull/5) is CLOSED without merge; [PR #8](https://github.com/TeaShaman-cyber/theseus-research/pull/8) remains OPEN. Neither candidate head is accepted Theseus `main`.

## Four independently reproduced validator gaps

An identical synthetic invalid in-memory registry entry was supplied to `tools/registry_contract.py` from the older reviewed SHA and the later PR #5 exact head `40b572554b8711dc6fb06de6cdc7e02e99f6dfdb`.

| Review comment | Invalid input | Older validator | Later validator |
| --- | --- | --- | --- |
| [3939739198](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939739198) | status `activ` | accepts | rejects: invalid status |
| [3939807477](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939807477) | repository `TeaShaman-cyber/` | accepts | rejects: invalid owner/repo |
| [3939993038](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939993038) | private-incubation entry contains repository | accepts | rejects: must omit repository |
| [3939993043](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939993043) | public visibility + private-incubation status | accepts | rejects: visibility/status mismatch |

[Reproduction script](https://github.com/TeaShaman-cyber/theseus-research/tree/main/research/papers/llm-review-vs-heavy-ci/analysis/reproduce_pr5_validation.py) and [exact output](pr5-validation-reproducers.json) preserve source identities and resulting errors. No GitHub write or external call was performed.

The third case demonstrates **a missing validation guard**, not an observed leak or an actual public disclosure event. Reproducing these defects in a historical candidate is not proof they ever reached production.

## Other PR #5 correction claims

Five further Codex comments have author replies, exact-head tests and now
independent historical before/after reproductions:

- [Bilingual prevalidation](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939739203):
  `test_render_write_validates_both_projections_before_writing_either`.
- [Drift issue pagination](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939739209):
  `test_existing_issue_on_second_page_is_reused_not_duplicated`.
- [Remote write readback](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939807479):
  `test_created_issue_requires_verified_remote_readback`.
- [Error JSON parent](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939993047):
  `test_doctor_creates_json_output_parent_before_invalid_early_return`.
- [Managed label pagination](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939993050):
  `test_managed_labels_are_collected_across_all_pages_before_drift`.

All nine relevant regression-test method names (including the four reproduced
cases) were absent at their reviewed source commits and present at PR #5's
later exact head. The full historical 45-test suite was independently executed
in a detached worktree at `40b572554b...`: **45/45 PASS**.
These now also have [five independent before/after source reproductions](2026-10-29-pr5-five-redgreen-audit.md)
and [machine-readable outcomes](pr5-remaining-validation-reproducers.json).
These source-level tests do not establish deployment or nine independent
real-world failure incidents.

Four final PR #5 comments have no inline author reply:
[private repository candidate discovery](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3941398477),
[incomplete GitHub search](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3941398481),
[error-report preservation](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3941398485),
and [bilingual write atomicity](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3941398487).
This does not establish their resolution or non-resolution elsewhere.

## PR #8: design-level evidence only

All 23 comments address a proposed architecture document. Twenty received
author replies claiming design corrections. Source verification established
that the design file changed after each originally reviewed commit and that
a thematically relevant text anchor appears at the final exact PR head.
Nineteen selected anchors were absent from their reviewed versions; one was
already present, which provides particularly weak correction evidence.
**No executable implementation was tested for PR #8**.

Three final PR #8 review threads have no author reply:
[existence versus target applicability](https://github.com/TeaShaman-cyber/theseus-research/pull/8#discussion_r3942132718),
[persistence of invalidation across sessions](https://github.com/TeaShaman-cyber/theseus-research/pull/8#discussion_r3942132722),
and [human acceptance at discovery](https://github.com/TeaShaman-cyber/theseus-research/pull/8#discussion_r3942132724).
These are **open questions in a historical design candidate**, not
demonstrated runtime defects.

## Epistemic limitations and next experiment

- Codex-authored comment = candidate finding; author reply = self-report;
  head text = design revision; executable regression = source-scoped test;
  before/after reproducer = confirmed behavior for the **specific probe**.
- A comment can overlap another root cause, so review counts cannot be
  compared directly with mutant counts or defect rates.
- This coding is **retrospective and not blinded or preregistered**.
- The two review PRs and the client mutation PRs cover different projects,
  tasks and maturity. No causal A/B conclusion is justified.
- All nine replied-to PR #5 comments have independent historical source
  reproductions; four unanswered PR #5 threads remain UNKNOWN. A future
  matched-sample study still needs a frozen, common cross-method oracle.
