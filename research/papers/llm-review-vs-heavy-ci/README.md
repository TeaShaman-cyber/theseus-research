# LLM review and mutation-guided CI — paper workspace

**Status:** UNPUBLISHED WORKING DRAFT / not peer-reviewed / no external submission.
**Coordination:** [theseus-research #97](https://github.com/TeaShaman-cyber/theseus-research/issues/97)
**Evidence origin:** [accepted #55 comparison](https://github.com/TeaShaman-cyber/theseus-research/blob/main/docs/research/2026-09-20-codex-review-vs-heavy-ci.md)

## Purpose

Turn the accepted observational comparison into a bounded manuscript without
silently changing the source report or promoting new research conclusions.

- [manuscript](manuscript.md): paper skeleton, empirical claims and unknowns.
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

## Stages and boundaries

1. Audit exact primary PR heads, dispositions and CI artifacts.
2. Freeze claim classifications, denominators and omitted-data handling.
3. Draft related work, methods, results, threats and source-based citations.
4. Evaluate a separate same-candidate prospective experiment only if justified.

Git remains canonical. Notion is optional editorial scratch space; Zenodo
archival, DOI publication and grant applications require separate decisions.
No new browser setup, sandbox token or service is needed for this workspace.
