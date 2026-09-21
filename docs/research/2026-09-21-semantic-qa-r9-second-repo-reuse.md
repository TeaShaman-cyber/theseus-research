# Semantic QA R9 second-repository reuse

Date: 2026-09-21

Tracking: TeaShaman-cyber/theseus-research#57

Disposition: COMPLETE / SECOND-REPOSITORY REUSE VERIFIED

R9 reused the package-based semantic QA mechanics in
TeaShaman-cyber/theseus-1f916-client while keeping that repository's corpus,
path interpretation and contract invariants local.

Machine receipt:
docs/research/2026-09-21-semantic-qa-r9-second-repo-reuse-receipt.json

## Verified consumer state

Consumer issue: theseus-1f916-client#41
Bootstrap merge: theseus-1f916-client#45
Merge commit: 36a66f8c83b86ed2e67ac4f45d6d0918ac81dc3e
Hosted Semble/Needle witness: GitHub Actions run 35563619680

The consumer uses eight exact excerpts from its own canonical
docs/v1-contract.md. Invariant ids are metadata only and are not injected
into retrieval text.

## Reused mechanics

- immutable package identity and inner tar digest checks;
- cross-repository package consumption;
- bounded PR input;
- explicit freshness state;
- durable receipts and artifacts;
- advisory-only semantic output;
- exact base/candidate/task identity.

The consumer also verified a repository-local semdup DB lifecycle with
trusted-main seeding and exact-base restore.

## Boundary

R9 does not establish a strong defect-finding yield claim.

The first Semble/Needle PR added the semantic corpus and infrastructure itself,
so part of the retrieval sample is self-referential. The hosted result proves
technical integration and contract-neighborhood routing, not predictive
accuracy.

Needle's pinned package remains reproducible while reporting STALE_AVAILABLE
because upstream Git moved. That warning is non-blocking.

## Next node

R10 may now evaluate extracting only generic cache/orchestration/receipt
mechanics into marcopolo-cookbook.

Do not move repository-specific corpora, thresholds, invariants, semantic
interpretation or acceptance authority into the shared layer.
