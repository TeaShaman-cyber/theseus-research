# Recurring failure classes and regression coverage

This file tracks causal defect classes that have repeated in `theseus-research`.
It is intentionally small: historical review findings remain in Issues/PRs; this
matrix records only the reusable invariant and the deterministic guard that
prevents recurrence.

Methodology reference: `TeaShaman-cyber/theseus-repo-search-lab#10`.

| Failure class | Representative reproductions in this repository | Prevention invariant | Current deterministic guard | Coverage |
| --- | --- | --- | --- | --- |
| Verification-target mismatch | `git diff --check` missed staged/committed state; first QA endpoint missed untracked whitespace | A PASS must observe the exact state it claims to verify | `tools/dev/check` checks committed range, index, tracked worktree, and untracked files; negative untracked fixture was exercised during PR #48 | PARTIAL |
| Authority / provenance closure | drift writes require exact remote readback; candidate discovery must not publish private repository identity | Evidence and writes stay bound to the exact authority surface and are independently read back where available | `test_registry_issue.py`; private-candidate regressions in `test_registry_doctor.py` | GUARDED |
| Identity preservation | stale role topics from another declared line were treated as unrelated; identity-bearing fields could be normalized or projected without preserving their meaning | Strong typed identity/vocabulary must not be weakened before the final consumer | managed-topic vocabulary regression; identity-specific contract validation | GUARDED |
| Identity grammar mismatch | Unicode/multiline/degenerate slugs; truncated `1.1.1 -> 1.1`; repository values such as `../..`, `./repo`, or `owner/..`; enum containers reaching set membership | Validate against the authoritative downstream identity grammar, not a convenient local approximation; type-check before vocabulary membership; reject normalization/path ambiguities | current head: line-ID and contract-version token regressions; repository-path and enum type guards are pending lower-stack incorporation/rebase | PARTIAL |
| Claim / status semantics | incomplete GitHub search could otherwise report PASS; API failure must not mean absence | `PASS`, `DECLARED_DRIFT`, `CANDIDATE_UNDECLARED`, and `UNREACHABLE` describe distinct observed states | doctor incomplete-result and API-failure regressions | GUARDED |
| Phase / DAG closure | contract changelog moved to 1.1 while bilingual contract headers/revision records could remain at 1.0 | A contract revision is promoted atomically across all authoritative version surfaces | `test_contract_atomicity.py` | GUARDED |
| Boundary / transport contract | multiline role text and IDs could inject malformed Markdown; projection marker ambiguity must fail closed | Every serialization/projection boundary has an explicit input grammar and rejects ambiguous structure | contract single-line/slug validation; projection marker regressions | GUARDED |
| Derived-state / heuristic coverage | generated EN/RU tables can drift from the registry source | Derived projections must be reproducible from the declared authority and checked as derived state | projection render/check and bilingual projection tests | GUARDED |

## Meta-review lenses

Before adding a local exception, ask three questions:

1. **BOUNDARY** — what stronger identity/state/evidence is being weakened here?
2. **PHASE** — is a consumer reading only already-produced and already-verified state, while state N remains valid until N+1 is ready?
3. **CLAIM** — what exact postcondition did the instrument observe, and is that exactly the proposition being marked PASS/FOUND/COMPLETE/VERIFIED?

Use the more specific authority/provenance and transport lenses only where they
are causally relevant. Do not create one test per historical bug when one general
invariant plus representative negative fixtures covers the recurring class.

## Identity grammar mismatch

This class is narrower than generic input validation. It applies when a field is
accepted as an identity by one layer but interpreted under a stricter or different
grammar by a downstream authority surface such as GitHub paths, Markdown links,
version parsers, registry keys, or closed vocabularies.

Invariant:

> Validate the exact authoritative downstream identity grammar before crossing the
> boundary. Type-check before vocabulary membership, preserve the complete token,
> and reject values whose normalization can change the addressed object.

Representative subtypes and target negative fixtures:

- **lexical under-validation** — reject Unicode or malformed component slugs where
  the contract requires lowercase ASCII components (`é`, `研究`, `foo--bar`, trailing
  or leading separators);
- **type under-validation** — reject arrays/objects before closed-vocabulary checks
  such as `visibility` or `release_policy`; validation must return machine-readable
  `INVALID`, not raise a `TypeError`;
- **path-segment ambiguity** — reject repository identities containing dot segments,
  empty segments, traversal-like forms, or other values that can normalize to a
  different API path (`../..`, `./repo`, `owner/..`);
- **parser truncation** — preserve the complete authoritative token (`1.1.1` must not
  become `1.1`);
- **serialization ambiguity** — reject embedded newlines or delimiters that can turn
  one identity into multiple rendered structures.

On this exact head, repository-path and enum-container cases are documented reproductions, not yet current deterministic guards; they remain PARTIAL until the lower registry slice is incorporated and QA is rerun.

Do not treat adding a stricter regex as sufficient evidence by itself. The guard is
the combination of the authoritative grammar, representative negative fixtures, and
a fail-closed observable result at the consumer boundary.
