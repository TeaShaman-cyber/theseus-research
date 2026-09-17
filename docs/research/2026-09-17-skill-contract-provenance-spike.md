# Skill/workflow contract verifier spike: exact provenance binding

**Date:** 2026-09-17  
**Coordination issue:** #42  
**Status:** `MECHANISM PROOF / NOT YET BLIND / NO METHODOLOGY PROMOTION`

## Question

Can one reusable machine-checkable invariant distinguish historical bad states from corrected controls across multiple Theseus product domains?

This slice tests only exact evidence/provenance binding. It does not attempt the full five-class verifier proposed in #42.

## Invariant

> Every evidence object used to establish a claim must preserve each exact identity/provenance binding required by that claim.

The local projection uses only:

```json
{
  "claim": {"required_bindings": {}},
  "evidence": {"bindings": {}}
}
```

For each required binding the checker returns either `MISSING_BINDING` or `BINDING_MISMATCH`. No scalar score is produced. Acceptance is `ACCEPT` only when all required exact bindings are preserved.

## Frozen matched pairs in this mechanism slice

Four domains are represented with a defective state and a corrected control:

1. Repository Search — replay DB and reported artifact can come from different builds.
2. Session Search — completeness evidence can include a page whose conversation membership is not established.
3. Needle — launcher `GITHUB_SHA` can be recorded as experiment identity after checkout switches to another commit.
4. Memory Provider — content-equal readback can come from a different persisted operation version.

Machine-readable fixtures:

- `experiments/skill-contract-verifier/corpus/provenance_cases.json`
- human verdicts kept separately in `experiments/skill-contract-verifier/corpus/verdicts.json`

The checker does not read the verdict file.

## TDD receipt

Observed RED before checker implementation:

```text
Ran 3 tests
FAILED (errors=2)
FileNotFoundError: .../verify.py
```

The corpus-structure test already passed, while both checker tests failed because the checker did not yet exist.

After adding the minimal checker:

```text
Ran 3 tests in 0.027s
OK
```

Observed classification:

```text
bad specimens:       4/4 REJECT
corrected controls:  4/4 ACCEPT
counterexample emitted for every REJECT
```

Domains: Repository Search, Session Search, Needle, Memory Provider.

## Evidence-source correction

The preregistration in #42 currently cites `theseus-repo-search-lab` review comment `r4024246755` for the DB/artifact identity defect. That URL returned 404 during this spike.

The live review evidence for the same defect is:

`https://github.com/TeaShaman-cyber/theseus-repo-search-lab/pull/7#discussion_r4025952964`

Its review text explicitly states that `--db` and `--artifact` from different builds can produce a PASS receipt attributed to the wrong artifact and recommends comparing the projection `artifact_identity` with the manifest identity. The fixture uses this live source. This correction must be recorded rather than silently replacing the frozen evidence pointer.

## Critical limitation: this is not yet a blind result

The mechanism separates machine fixtures from human verdicts, and the checker itself contains no case IDs or historical verdicts. However, the fixtures in this first slice were manually projected after the historical review findings were already known.

Therefore:

```text
FACT:
  one compact invariant can discriminate these four modeled bad/fixed pairs.

NOT ESTABLISHED:
  that the same invariant would have been selected and the required bindings
  encoded from the pre-verdict skill/plan/workflow alone.
```

This is a mechanism/discriminability proof, not yet evidence that the formal method catches the defects prospectively.

## Next falsifiable step

Use at least two historical cases whose reviewer verdict is withheld from the projection step:

1. take the pre-review plan/workflow state;
2. derive `required_bindings` only from declared contracts, `Consumes`/`Produces`, workflow semantics, and authoritative source state;
3. freeze the projection hash;
4. run the unchanged checker;
5. reveal the historical review verdict only afterward;
6. compare with the matched corrected state.

If the projection cannot be derived without defect-aware annotations, this provenance invariant should be classified as `PARK` for predictive use even though the mechanism test passes.

## Upstream relevance

If a later blind run succeeds, the result would materially strengthen existing Superpowers discussions:

- `obra/superpowers#2186`: instrument success vs exact claim/evidence binding;
- `obra/superpowers#2309`: task/state closure and explicit producer-consumer coordinates;
- potentially `#895`: detailed executable plans as defect-bearing artifacts, but only if the blind projection demonstrates useful plan-time detection rather than merely post-hoc formalization.

No upstream mutation is justified by this mechanism-only result.
