# Research DevOps principles — small-batch lifecycle — 2026-09-19

Status: CURRENT / WORKING CROSS-REPOSITORY GUIDANCE
Scope: Theseus research lines declared in `registry/research-lines.json`
Coordination anchor: #51 — Architecture: define a cross-repository Research DevOps lifecycle

This note captures the practical DevOps principles that converged during active repository work on 2026-09-18 and 2026-09-19. It is a working architecture snapshot, not a claim that every repository must implement identical machinery.

## Core loop

```text
small causal slice
  -> focused regression / negative fixture
  -> canonical repository QA
  -> domain witness when needed
  -> exact-head independent review / hosted acceptance
  -> explicit promotion
  -> promoted-state readback
  -> terminal disposition
  -> reusable learning
```

## Working principles

1. **One PR, one causal change.**
   Do not bundle unrelated QA, registry, lifecycle, review fixes, and opportunistic cleanup. Prefer a separate small slice when it can be used and verified independently.

2. **Issue-first for substantial durable work, but Issue is not authority.**
   A narrow Issue records motivation, current evidence, intended invariant, acceptance criteria, and disposition. It coordinates work; it does not grant unrelated implementation or promotion authority.

3. **Discover repository-native QA/lifecycle before inventing new verification.**
   Look for `tools/dev/check`, existing CI, acceptance runners, release rules, and repository-local conventions first.

4. **`tools/dev/check` is the canonical pre-review gate when present.**
   It should fail closed, work from a clean checkout, and cover the committed/worktree states relevant to the repository. A checker failure is not PASS.

5. **Keep lifecycle states separate.**
   `QA_PASS != domain truth != review approval != acceptance != merge permission != release permission`. Automation verifies repeatable properties; judgment and authority remain explicit.

6. **Bind important evidence to an exact revision.**
   Local QA, Codex review, hosted CI, domain witnesses, and receipts prove only the exact SHA/input they observed. A new commit makes earlier evidence historical until re-run where required.

7. **Merge is not the end of the lifecycle.**
   For meaningful changes, verify the promoted state on `main` or the actual release/publication target. Post-merge/readback establishes that the accepted state survived integration.

8. **Every completed slice needs terminal disposition.**
   Use explicit states such as merged, accepted, rejected, superseded, parked, or blocked. Avoid completed work remaining indefinitely in review/pending limbo.

9. **Receipts are first-class CI outputs.**
   Preserve machine-readable outcome, exact revision/input, provenance, and failure class. Distinguish assertion failure, provider outage, missing capability, `DEGRADED`, `UNKNOWN`, and `CORPUS_BOUNDARY` instead of collapsing them into generic failure.

10. **Regression guards must test the promised capability, not a proxy symptom.**
    A nonzero hit count is insufficient when the invariant is retrieval of a specific declaration/object. Guard exact IDs, hints, or invariants when that is the demonstrated capability.

11. **Research gets DevOps discipline without pretending CI proves science.**
    Reproducible checks can verify provenance, artifact identity, pipeline behavior, numerical or symbolic witnesses, and retrieval seams. They do not by themselves establish a theorem or scientific conclusion.

12. **Classify failures before retrying or changing routes.**
    A transport 403, request-filter rejection, shell-dialect error, provider outage, and target-operation failure are different classes. Verify whether execution happened before retry. Fallback only after observed insufficiency, and make route changes visible.

13. **Canonical source, runtime projection, coordination view, and memory are distinct.**
    Git/versioned contracts govern code and versioned policy; GitHub Projects and Issues coordinate; runtime files are projections; memory stores continuity/guidance. `merge != installed`, `installed != verified`.

14. **Shared invariant does not imply identical implementation everywhere.**
    Repositories may share lifecycle vocabulary while keeping domain-specific verifiers local. Promote shared wrappers only after repeated value in materially different repositories.

15. **Close the learning loop only for demonstrated recurring value.**

    ```text
    observed gap
      -> smallest responsible repair
      -> deterministic regression
      -> canonical QA
      -> bounded independent review
      -> promotion/readback
      -> reusable lesson
    ```

    Add process when it removes a recurring failure class or reduces recovery cost, not for ceremonial consistency.

## Fresh delta from 2026-09-18/19

The important shift is that **code + tests + review is no longer treated as a complete unit of work**.

The completed unit is now:

```text
exact change
  -> exact-head evidence
  -> accepted promotion
  -> promoted-state verification
  -> terminal disposition
```

Two rules became especially explicit during these sessions:

- keep slices small enough that independent review, diagnosis, rollback, and retry remain cheap;
- treat incomplete lifecycle itself as process debt when finished work remains indefinitely pending.

## Evidence and authority boundary

This repository document is the versioned, reviewable form of the working guidance under issue #51.

External projections intentionally have narrower roles:

- Basic Memory: durable semantic guidance and continuity evidence;
- ButlerBrain: compact DIFF/pointer;
- GitHub Issues/Projects: coordination and lifecycle state;
- promoted remote Git state: authority for current versioned repository state;
- CI: evidence bound to the exact revision/input executed by the workflow;
- runtime readback: evidence for current execution/runtime state and installed projections.

No memory projection overrides promoted remote Git state, current permissions, or explicit promotion authority. CI and runtime readback retain their bounded evidentiary roles and do not become promotion authority.
