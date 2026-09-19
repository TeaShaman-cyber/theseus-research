# Recurring failure classes and regression coverage

This file tracks causal defect classes that have repeated in `theseus-research`.
It is intentionally small: historical review findings remain in Issues/PRs; this
matrix records only the reusable invariant and the deterministic guard that
prevents recurrence.

Methodology reference: `TeaShaman-cyber/theseus-repo-search-lab#10`.

| Failure class | Representative reproductions in this repository | Prevention invariant | Current deterministic guard | Coverage |
| --- | --- | --- | --- | --- |
| Verification-target mismatch | `git diff --check` missed staged/committed state; first QA endpoint missed untracked whitespace; embedded Git directories could be accepted without inspecting member files | A PASS must observe the exact state it claims to verify | `tools/dev/check` checks committed range, index, tracked worktree, ordinary untracked files, and nested files inside untracked embedded Git directories; executable negative fixture in `test_dev_check.py` | GUARDED |
| Authority / provenance closure | drift writes require exact remote readback; candidate discovery must not publish private repository identity; a declared-public repository becoming private must stop further metadata observation | Evidence and writes stay bound to the exact authority surface and are independently read back where available | `test_registry_issue.py`; private-candidate and private-boundary regressions in `test_registry_doctor.py` | GUARDED |
| Identity preservation | stale role topics from another declared line were treated as unrelated; public registry lines could omit common baseline topics; identity-bearing fields could be normalized or projected without preserving their meaning | Strong typed identity/vocabulary must not be weakened before the final consumer, and required baseline identity metadata must remain explicit | managed-topic vocabulary regression; public baseline-topic regression; identity-specific contract validation | GUARDED |
| Identity grammar mismatch | Unicode/multiline/degenerate slugs; truncated `1.1.1 -> 1.1`; repository values such as `../..`, `./repo`, or `owner/..`; enum containers reaching set membership | Validate against the authoritative downstream identity grammar, not a convenient local approximation; type-check before vocabulary membership; reject normalization/path ambiguities | line-ID, contract-version token, repository-path, GitHub-topic, and enum type regressions on the current stacked head | GUARDED |
| Claim / status semantics | incomplete GitHub search, first-page-only candidate search, or API failure could otherwise report PASS/absence | `PASS`, `DECLARED_DRIFT`, `CANDIDATE_UNDECLARED`, and `UNREACHABLE` describe distinct observed states; completeness must be proved before absence | doctor incomplete-result, pagination/search-cap, and API-failure regressions | GUARDED |
| Phase / DAG closure | contract changelog moved to 1.1 while bilingual contract headers/revision records could remain at 1.0; malformed new revision/changelog candidates could be skipped in favor of valid historical state | A contract revision is promoted atomically across all authoritative version surfaces; the first current-state candidate is selected before validating its grammar, never by searching for the first valid historical match | `test_contract_atomicity.py` covers bilingual disagreement, complete version tokens, malformed first revision records, and malformed first changelog candidates | GUARDED |
| Boundary / transport contract | multiline role text and IDs could inject malformed Markdown; projection marker ambiguity must fail closed; missing/unreadable projection inputs must not escape as tracebacks | Every serialization/projection boundary has an explicit input grammar and converts unreadable or ambiguous structure into a named fail-closed state | contract single-line/slug validation; projection marker and projection read-failure regressions | GUARDED |
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

On this exact stacked head, the lower registry slice is incorporated: repository-path, GitHub-topic, and enum-container cases have deterministic negative fixtures alongside the line-ID and contract-version guards. Canonical QA was rerun after the rebase.

Do not treat adding a stricter regex as sufficient evidence by itself. The guard is
the combination of the authoritative grammar, representative negative fixtures, and
a fail-closed observable result at the consumer boundary.
