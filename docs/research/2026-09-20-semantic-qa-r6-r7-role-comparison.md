# Semantic QA R6/R7 role comparison

**Date:** 2026-09-20

**Tracking:** `TeaShaman-cyber/theseus-research#57`

**Disposition:** COMPLETE / NON-EXCLUSIVE ROLES / RETAIN BY OBSERVED COST

This closes the comparison and role-selection nodes without choosing a single
winner.

## Roles

| tool | advisory role | observed reason |
| --- | --- | --- |
| semdup | semantic duplicate witness | clean separation of planted rewrite from distinct control; upstream DUP/REVIEW semantics |
| Semble | known-failure attention router | projected frozen fixture 4/4 strict top-1, 4/4 top-3, MRR 1.0 |
| Needle 3 + sklearn | alternative embedding/retrieval trace | deterministic independent geometry; 1/4 top-1, 3/4 top-3, useful field trace for future Needle lab work |

These roles overlap by design only at the evidence layer. None becomes
correctness authority.

## Runner-cost interpretation

semdup's semantic work itself was cheap, but exact cold Cargo installation
dominated the hosted pilot. Routine CI should therefore cache or prebuild the
exact semdup binary/toolchain path before treating it as low-cost.

Semble and Needle both completed their hosted pilots in roughly tens of seconds.
That cost is currently acceptable for advisory parallel runners, subject to
field observation.

No permanent runner-cost threshold is declared yet. R8 receipts must make the
actual cost observable so retirement or throttling can be based on field data.

## Retention

All three tools remain active candidates while they do not materially delay or
destabilize primary QA.

A stronger result on one tiny fixture is not sufficient reason to retire an
otherwise cheap, independent signal source.

Needle receipts are additionally valuable as a longitudinal analytics trace:
future `theseus-needle-lab` work can compare model/profile revisions against
real repository changes instead of reconstructing synthetic history.

Required trace provenance remains:

`source SHA + model/profile + candidate SHA + task/fixture identity`

Trace evidence does not become acceptance authority.

## Next node

R8 may now integrate reusable non-blocking CI templates with:

- exact pins;
- no external inference secrets;
- named `UNAVAILABLE` / `DEGRADED` states;
- exact candidate SHA;
- bounded runner/input budgets;
- trace artifacts;
- no auto-write or remediation.
