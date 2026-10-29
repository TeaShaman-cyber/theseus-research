# Related-work evidence ledger — 2026-10-29

**Status:** five source identities checked against original paper texts;
publisher metadata for peer-reviewed works checked using Crossref.
**Scope:** initial targeted selection, **not** an exhaustive review.
[Research issue #97](https://github.com/TeaShaman-cyber/theseus-research/issues/97).

## Research-to-evidence matrix

| Citation | Verified source / research unit | Theseus relevance | Non-transferable inference |
| --- | --- | --- | --- |
| [`zheng2026mcrbench`](https://doi.org/10.1145/3832219) | ACM ISSTA 2026, 2,269 multi-round code-review tasks | Track comment → response → verification | 36 comments are not 36 independent defects |
| [`zhao2026mutationscore`](https://doi.org/10.1145/3832093) | ACM ISSTA 2026, LLM-generated tests, mutation-vs-real-fault adequacy | Interpret fixed-profile mutant kills as proxy signal | Our seven tests are not a matched LLM test-generation sample |
| [`harman2025ach`](https://doi.org/10.1145/3696630.3728544) | FSE Companion 2025, Meta mutation-guided regression tests | Concern → invariant/test → witness; equivalent-mutant triage | Theseus did not run Meta ACH or reproduce its acceptance rates |
| [`smyth2026overclaim`](https://arxiv.org/abs/2609.20812) | arXiv preprint v3, transcript-tracked review scenarios | Separate reported review coverage from observed actions | No full file-read transcript verified for Theseus PR #5/#8 |
| [`zhu2018mutationreview`](https://doi.org/10.1002/stvr.1675) | Wiley STVR 2018 review of 191 mutation studies | Report input profile, mutants, equivalence, subject availability | Reporting completeness does not prove causality |

## Historical Notion leads (not scientific validation)

- [Techno-review 29 Aug 2026](https://app.notion.com/p/3cbb65ac4191816590cafe23466dd6a2):
  MCR-Bench, arXiv:2608.27442; DOI now independently verified.
- [Techno-review 20 Sep 2026](https://app.notion.com/p/3e1b65ac419181799a3de68f2ac4aa3a):
  OverclaimBench, arXiv:2609.20812v3, still a preprint.
- [Techno-review 22 Oct 2026](https://app.notion.com/p/401b65ac41918192841cf156c0d01c93):
  VERDICT, formal proof, adjacent but excluded from core five.
- [Techno-review 25 Oct 2026](https://app.notion.com/p/404b65ac41918150866feba5ceecdd53):
  Verified optimization, adjacent but excluded from core five.

Zhao and Meta ACH were discovered independently via academic search; Zhu
via Wiley Scholar Gateway. Their primary research texts were inspected.
Notion is a curated discovery record, not independent replication.

## Meta ACH DOI correction (important provenance discrepancy)

A previous [literature checkpoint in #97](https://github.com/TeaShaman-cyber/theseus-research/issues/97#issuecomment-6490843257)
associated Meta ACH with DOI `10.1145/3663529.3663839`.
That DOI is **not** the current publisher-registered identifier for ACH.

Crossref records, checked on 2026-10-29, distinguish:
- [`10.1145/3696630.3728544`](https://doi.org/10.1145/3696630.3728544):
  *Mutation-Guided LLM-based Test Generation at Meta*, Harman et al.,
  FSE Companion 2025, pages 180–191. **Use this DOI for ACH.**
- [`10.1145/3663529.3663839`](https://doi.org/10.1145/3663529.3663839):
  *Automated Unit Test Improvement using Large Language Models at Meta*,
  Alshahwan et al., FSE Companion 2024, pages 185–196. Different paper.

An earlier archived ACH author PDF carries conflicting conference/DOI
header text. The live Crossref record, FSE 2025 programme and UCL
publication catalogue agree on `10.1145/3696630.3728544`.
The previous checkpoint is historical and is **superseded only for this
citation identifier**, not silently rewritten.

## Method and remaining boundaries

- MCR-Bench, Zhao, Meta ACH, and Zhu have peer-reviewed conference/journal
  publication records; OverclaimBench is a preprint, regardless of whether
  it was mentioned in a technical digest.
- Observations from the original papers are **other researchers' results**,
  not Theseus findings. Source descriptions were checked with alphaXiv,
  Wiley Scholar Gateway, Exa and Parallel Search; Crossref supplied
  bibliographic metadata for four published works.
- Theseus has not independently reproduced those studies or established a
  common defect oracle between its review and mutation traces.
- The related-work selection is incomplete by design; future research
  should include foundational mutant-to-real-fault work and studies that
  compare review with CI on **matched source candidates**.
