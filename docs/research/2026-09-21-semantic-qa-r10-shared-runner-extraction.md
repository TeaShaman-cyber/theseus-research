# Semantic QA R10 shared runner extraction

Date: 2026-09-21

Tracking: TeaShaman-cyber/theseus-research#57

Disposition: COMPLETE / SHARED MECHANICS VERIFIED

R10 extracted only mechanics that had already duplicated across two verified consumers.

The shared action now lives in marcopolo-cookbook at exact main
01af605cd35e60cb55724e1abfcff7331bbfda3e and is consumed by
theseus-1f916-client at exact merged main
9886e90ca3eba7a59f9397273dbe57b44186384c.

## Shared boundary

The cookbook owns bounded diff input preparation, package freshness/currentness,
exact artifact identity, outer and inner digest verification, safe extraction
and a non-authoritative mechanics receipt.

The consumer still owns tool-specific build-receipt validation, offline
installation, corpus, retrieval, semantic interpretation and acceptance
authority.

No corpus, threshold, semantic verdict, semdup DB policy or promotion authority
moved into the shared layer.

## Field witness

Client PR #46 consumed the merged cookbook action pinned by exact commit.

Hosted run 35583526179 passed both Semble and Needle lanes after migration.
Semble remained CURRENT and Needle remained STALE_AVAILABLE. Exact artifact and
tar digests were preserved. Both domain traces remained advisory.

The consumer migration removed more local generic code than it added.

## Security boundary

Cookbook workflow-security passed.

Dependency-security reproduced the already tracked issue #79 Undici 5.29.0
baseline with the same 12 advisories. R10 did not modify that dependency graph,
and the advisory was not suppressed.

## Next node

R11 is the promotion decision.

The promotion decision must use accumulated field evidence. Similarity scores
alone cannot become a correctness gate.
