# Semantic QA R8 package-based CI integration

**Date:** 2026-09-20

**Tracking:** `TeaShaman-cyber/theseus-research#57`

**Disposition:** COMPLETE / PACKAGE-BASED / NON-BLOCKING FIELD TRACES

Machine receipt:
`docs/research/2026-09-20-semantic-qa-r8-ci-integration-receipt.json`

## Operational shape

Routine semantic QA no longer recompiles or resolves the tools on every PR.

The lifecycle is split into two phases:

    rare explicit build
      -> exact immutable toolchain artifact
      -> pinned artifact/run/tar digests
      -> routine PR download + verify
      -> non-blocking freshness probe
      -> semantic field trace

semdup packages its Linux binary plus warmed ONNX model cache. Semble and
Needle package offline Python wheelhouses plus exact model artifacts.

Reproducibility and freshness are intentionally separate:

- a package must match its pinned artifact and inner tar digests to run;
- upstream movement or package age produces `STALE_AVAILABLE`, not failure;
- inability to verify currentness produces `CURRENTNESS_UNKNOWN`;
- an expired/missing/mismatched package produces `UNAVAILABLE`;
- none of these semantic jobs becomes merge authority.

## One-time build cost

| tool | package build | artifact size | scope |
| --- | ---: | ---: | --- |
| semdup | ~149 s | 156.7 MB | Ubuntu 24 / x86-64 / glibc 2.39 |
| Semble | ~41 s | 67.2 MB | Ubuntu 22 / x86-64 / Python 3.12 |
| Needle 3 | ~61 s | 102.5 MB | Ubuntu 22 / x86-64 / Python 3.12 |

Those costs are maintenance/build costs, not routine PR costs.

## First package-based field witness

GitHub Actions run: `35538583349`

Candidate: `90b3500ca4d0815cf9aadf06fdd2f22eb56578f4`

All three jobs concluded SUCCESS. All three packages were `READY` and all
freshness probes were `CURRENT`.

The R8 PR itself changed 22 paths. The frozen input budget is 20 files /
256 KiB total / 64 KiB per file, so the manifest intentionally became
`DEGRADED`: 20 paths and 92,995 bytes were selected; two paths were
skipped by the file-count budget.

That state propagated instead of being hidden:

- semdup package setup: ~6.65 s; orchestration: ~7.04 s. Because semdup's
  native diff is repository-wide, the runner skipped the semantic full diff
  rather than bypass the bounded-input contract.
- Semble package setup: ~10.71 s; cold retrieval ~13.14 s; warm retrieval
  ~11.73 s. The selected 20 changes were analyzed and the receipt stayed
  `DEGRADED`.
- Needle package setup: ~19.61 s; cold retrieval ~15.28 s; warm retrieval
  ~15.32 s. Cold/warm ranked outputs were identical and the receipt stayed
  `DEGRADED`.

The key result is operational: expensive compilation/model preparation is no
longer charged to routine semantic work.

## Freshness lifecycle

Each profile records its package identity, source/model identity, build time,
expiry time and a small currentness policy.

Currentness is checked on each advisory run. Staleness produces a visible
warning while the pinned reproducible package continues to run. Package refresh
is an explicit maintenance action via the separate build workflows.

This gives field analytics a stable identity while avoiding a forced rebuild
just because upstream moved.

## Verification

- actionlint: PASS;
- semantic input/freshness/package tests: 9/9 PASS;
- canonical repository suite: 93/93 PASS;
- `tools/dev/check`: `DEV_CHECK_PASS`;
- `git diff --check`: PASS;
- field run package readiness/currentness: VERIFIED.

## Boundary

R8 does not promote semantic scores, thresholds or auto-remediation.

The first normal PR below the file budget will provide the first packaged
semdup full-diff field trace; this self-hosting PR intentionally exercised the
DEGRADED budget path instead.

## Next node

R9 reuses the same mechanics in a second Theseus repository, preferably
`theseus-1f916-client`, while keeping repository-specific corpora and
invariants local.
