# PR #5: Five additional historical before/after reproductions

**Scope:** historical project-owned code, local temporary files and fake
GitHub transport only. No production deployment, external API requests,
real GitHub writes, or matched review-versus-CI experiment.

The [read-only reproducer](https://github.com/TeaShaman-cyber/theseus-research/blob/main/research/papers/llm-review-vs-heavy-ci/analysis/reproduce_pr5_remaining.py)
loads the original reviewed Git commit and corrected PR #5 head into
isolated temporary Python processes. Exact results, commit IDs, and original
comment links are in [five-result JSON](pr5-remaining-validation-reproducers.json).

| Codex comment | Before correction | At corrected historical head |
| --- | --- | --- |
| [3939739203](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939739203) | Invalid RU markers leave English README overwritten | Both files unchanged, exit 4 `INVALID` |
| [3939739209](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939739209) | Issue hidden on page 2 triggers duplicate fake POST | Finds page 2, comments on existing #212 |
| [3939807479](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939807479) | False success after fake POST issue/comment with inconsistent persisted state | Both paths GET fake stored value, reject mismatch |
| [3939993047](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939993047) | Invalid registry + absent report parent gives `FileNotFoundError` | Structured `INVALID` report, exit 4 |
| [3939993050](https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r3939993050) | Labels on page 2 falsely treated as missing, `DECLARED_DRIFT` | Fetches page 2, returns `PASS` |

**Correction head:** `40b572554b8711dc6fb06de6cdc7e02e99f6dfdb`.
The individual original SHAs are preserved in the JSON and
[review-comments.json](review-comments.json), rather than substituting
one synthetic common baseline. Five complete hard assertions passed.
The readback case checks both issue creation and commenting: six
behavioral branches for five review comments, **not six separate bugs**.

Together with the [earlier four validator reproductions](pr5-validation-reproducers.json),
all **nine replied-to PR #5 Codex comments** now have independent
source-scoped red-before/green-after witnesses. Four final PR #5
comments have no inline author reply and remain `UNKNOWN`.
PR #8 still contains design-text revision evidence, not runtime proof.

**Limit:** confirmed historical behavior changes do not demonstrate
nine independent real-world failures, actual disclosure of private
data, or acceptance of PR #5 into canonical `main`.
