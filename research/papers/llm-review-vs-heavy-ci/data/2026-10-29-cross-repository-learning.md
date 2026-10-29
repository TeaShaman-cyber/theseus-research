# Cross-repository learning is established Theseus practice

**Status:** first-party GitHub source audit / 2026-10-29.
**Question:** Does research issue #97's PR-level review evidence capture the
actual Theseus learning workflow, or omit transfer of defect classes and
verification invariants among distinct projects?

**Answer supported by earlier work:** it omits a documented existing
cross-repository layer. This note is a *scope and provenance correction*,
not a new five-project experiment or a claim of original discovery.
Existing coordinating studies are [Research #51](https://github.com/TeaShaman-cyber/theseus-research/issues/51),
[Research #53](https://github.com/TeaShaman-cyber/theseus-research/issues/53),
and [Repo Search #10](https://github.com/TeaShaman-cyber/theseus-repo-search-lab/issues/10).

## Existing independent cross-product evidence

- [Five-product synthesis, 2026-09-17](https://github.com/TeaShaman-cyber/theseus-repo-search-lab/issues/10#issuecomment-5709960845)
  compared Repository Search, Session Search, Needle, MarcoPolo Cookbook and
  Memory Provider Lab; documented 256 **top-level review remarks in aggregate**
  and three recurring classes: representation/boundary information loss,
  producer/consumer phase confusion, and overclaiming the verified postcondition.
  This is a historic *review count*, not 256 defects or independently
  rerun failures in this manuscript.
- [Needle independent class audit](https://github.com/TeaShaman-cyber/theseus-needle-lab/issues/50#issuecomment-5709759902)
  linked distinct artifact/seed/schema/receipt defects to the same lenses
  as the earlier Repo Search and Session Search audits. The Needle domain
  is not merely another commit in the same repository.
- [Public Observatory #23](https://github.com/TeaShaman-cyber/theseus-public-observatory/issues/23)
  explicitly reused Session Search and Transmission Ecology precedents to
  formulate a **source-admissibility** matrix: forecast != observation;
  partial != complete; received != admissible evidence.

## Actual cross-implementation / cross-repository transfer

- [Reciprocal QA experiment #67](https://github.com/TeaShaman-cyber/theseus-1f916-client/issues/67)
  compared independent Theseus and upstream 1F916 Python client
  implementations against a shared server contract. It deliberately rejects
  a winner/ranking framing and asks whether a failure class transfers.
- Independent GitHub readback confirms upstream
  [PR #361](https://github.com/1f916-ai/1f916/pull/361)
  MERGED to reject duplicate JSON object keys. In the other direction,
  Theseus client [PR #72](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/72)
  MERGED to preserve search truncation evidence (`has_more`), and
  [PR #73](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/73)
  MERGED to walk paginated comments. Later
  [PR #76](https://github.com/TeaShaman-cyber/theseus-1f916-client/pull/76)
  MERGED a fail-closed non-object JSON root check.
  The original issue #67 records the mutual evidence lineage.
- [Cookbook #64](https://github.com/TeaShaman-cyber/marcopolo-cookbook/issues/64)
  established *shared executable QA mechanics*, not just similar wording.
  [Canonical QA consumer](https://github.com/TeaShaman-cyber/marcopolo-cookbook/issues/64#issuecomment-5749355653)
  was accepted in the 1F916 client with hosted exact-source runs;
  [heavy-python profile](https://github.com/TeaShaman-cyber/marcopolo-cookbook/issues/64#issuecomment-5749658475)
  was consumed by Repo Search with a hosted receipt and separate advisory
  findings. The shared template does not impose one domain-specific
  acceptance rule on every repository.

## Correct unit of analysis

The natural ecosystem-level unit is **a falsifiable failure-class /
prevention-invariant pair**, not a code comment or PR in isolation.

Candidate trace:

`finding in A -> independently classify cause and observable counterexample
-> search comparable boundaries in B, C, ... -> record match/no-match/unknown
-> adapt domain-specific deterministic regression or shared CI mechanism
-> observe exact accepted-source postcondition -> monitor recurrence`.

Distinct evidence grades must be retained:

| Evidence grade | Meaning |
| --- | --- |
| `ANALOGY_ONLY` | Symptoms or terms resemble each other, no comparable reproduced causal boundary yet |
| `INDEPENDENT_RECURRENCE` | Same falsifiable invariant violated in at least two different systems; exact source and counterexamples recorded |
| `TRANSFER_CANDIDATE` | A reusable test/guard is proposed or copied, but source-specific acceptance not established |
| `TRANSFER_VERIFIED` | Adapted check is accepted and passes against the right version and a stated oracle; actual consumer/readback is recorded |
| `NO_MATCH` / `UNKNOWN` | Explicit negative or insufficient evidence, not silently omitted from the sample |

The five-product synthesis supports a retrospective class map, while the
reciprocal 1F916 experiment and shared Cookbook workflow consumers establish
concrete **verified transfer examples**. None alone gives a controlled
estimate of how much a reusable invariant reduces future defect recurrence,
or proves one universal cause across projects.

**Paper implication:** #97's present historical LLM-review vs mutation-CI
comparison is a *narrow slice*, not the entirety of Theseus QA learning.
Before making an originality claim, compare the existing cross-repository
study in #10/#51 and published transfer/defect-pattern literature.
A broader question may be: which independently detected defect classes
can be converted into portable checks without suppressing domain-specific
semantics, and which cannot? This is an **exploratory scope candidate**,
not a newly accepted empirical result or an automatically authorized
rewrite of the core observational question.

**Method preflight:** Feynman-style explicit explanation of a defect
mechanism and a bounded "five whys" causal probe are useful to formulate
the invariant; they do not independently establish that the same cause
recurs elsewhere. Require independent concrete counterexamples, negative
cases, and exact accepted revision before claiming transfer.
