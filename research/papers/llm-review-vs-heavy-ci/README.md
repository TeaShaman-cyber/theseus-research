# LLM review and mutation-guided CI — paper workspace

**Status:** EDITORIALLY COMPLETE WORKING MANUSCRIPT (2026-10-29); not peer reviewed.
**Coordination:** [theseus-research #97](https://github.com/TeaShaman-cyber/theseus-research/issues/97)
**Evidence origin:** [accepted #55 comparison](https://github.com/TeaShaman-cyber/theseus-research/blob/main/docs/research/2026-09-20-codex-review-vs-heavy-ci.md)

## Purpose

Completed a bounded, source-linked retrospective manuscript based on the
accepted observational comparison. The evidence corpus and research questions
are frozen; closing the manuscript task does not promote scientific acceptance.

- [manuscript](manuscript.md): editorially complete retrospective case study,
  results, limitations and evidence availability.
- [references](references.bib): first-party artifacts plus five independently checked research sources.
- [related-work evidence ledger](data/2026-10-29-related-work-evidence.md): primary source links, Notion discovery lineage, DOI correction and limits.
- [source inventory](data/README.md): primary GitHub receipts, reviewer comment evidence, and remaining gaps.

## Research contract

**RQ:** In public Theseus development traces, which defect/contract questions
occur under exact-head LLM review versus exact-source property/mutation CI, and
what remains reproducible afterward?

**HYPOTHESIS, not a causal result:** independent reviewers can expand the
question space beyond encoded invariants; deterministic QA can deepen and retain
already-defined behavioral checks.

**Cheap baseline:** count confirmed behavioral gaps and regression tests, not
reviewer questions or mutation score alone. A surviving mutant is not
automatically a defect; 33 extra killed mutants are not 33 bugs.

**Falsifiers / stop rules:**
- No confirmed reviewer-origin finding: do not claim reviewer discovery.
- Missing mutant denominator, baseline source SHA or profile comparability:
  report snapshots only, not an improvement rate.
- Non-matched repositories, tasks or maturity: no causal rank of methods.
- No additional decision value beyond cheap checks: retain negative outcome.

## Completion and boundary

- **DONE:** historical source and hosted mutation-log audits, reviewer
  comments, reproducible source-level probes, accepted-source lineage.
- **DONE:** versioned evidence classifications, invariant mutation profile,
  formal results tables, related work, validity threats and conclusions.
- **DONE:** bounded editorial review; no new study arm or population claim.
- **NOT A BLOCKER:** authorship assignment, peer-review submission, further
  matched-candidate experiments and broad ecosystem causal evaluation.

Closure of coordination issue #97 means the **manuscript editing task**
is terminal, not that the scientific hypothesis has been proven.
Subsequent genuinely new investigations belong to their existing
research issues, not a reopened manuscript scope.
