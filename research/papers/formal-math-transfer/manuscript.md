# From frontier formal mathematics to software engineering: an open, agent-assisted knowledge-transfer case study

**Working manuscript v0.1 — 27 November 2026. Unpublished; not peer reviewed.**
**Research program:** Theseus, independent public-interest research.
**Proposed creator:** TeaShaman-cyber (manuscript-specific confirmation pending; no institutional affiliation claimed).
**Study registration:** [Theseus Research #141](https://github.com/TeaShaman-cyber/theseus-research/issues/141).
**Status:** author review, rights audit, related-work expansion and final candidate acceptance pending.

## Abstract

Contemporary formalization projects make mathematical statements and their dependencies accessible to software agents, but retrieving a proof is not the same as discovering a valid engineering application. This case study investigates the transfer of mathematical structures from research-level Lean corpora to an append-only proposal ledger in an AI research system. The open Theseus RepoSearch infrastructure federates source retrieval and bounded declaration-graph traversal over a provenance-bound catalog of 27 formalization artifacts. We document a chronological case combining literature review, formal source retrieval, graph expansion, independent Lean lemmas, synthetic experiments and regression-tested implementation. A first accepted optimization removes repeated prefix validation; a second candidate uses monotonicity of historical edge insertion and a single topological traversal to remove repeated reachability checks. For 2,500 vertices, seven uninstrumented repetitions per implementation and graph shape yield median materialization times of 942.7 versus 170.4 ms for a reverse-insertion chain and 1,516.6 versus 190.7 ms for reverse-insertion diamonds; simple forward chains and fan-out workloads do not show comparable gains. Exhaustive four-vertex differential experiments cover 8,192 ordered histories and 13,032 candidate appends. We also retain a negative result: exact rejection of arbitrary corruption cannot be achieved by inspecting only a fixed proper subset of independently untrusted rows. The Kahn algorithm is established mathematics; this study does not claim its invention or causal superiority of graph retrieval. Its contribution is an inspectable example of research-level mathematical knowledge transfer, together with executable evidence and explicit failure boundaries. A separate prospective extension addresses invariant-based analysis of agent observability metrics.

**Keywords:** formal mathematics; Lean; knowledge transfer; dependency graphs; agent-assisted research; software engineering; append-only ledgers; reproducibility; observability.

## 1. Motivation and research questions

Formal mathematical artifacts increasingly accompany contemporary research, including work in fluid dynamics, combinatorics, number theory and computational complexity. Such artifacts encode structure beyond keyword similarity: exact definitions, statements, proof dependencies, and the context in which an argument is used. Theseus collects selected research-level formalizations with the goal of exploiting this structure for problems outside the original mathematical domain, including problems for which an engineering solution has not yet been identified.

We study three questions:

- RQ1: Can an agent locate and transfer a mathematical invariant or proof pattern from a contemporary formal corpus to a concrete software task, while preserving the conditions under which the pattern is valid?
- RQ2: Can the transfer be traced through original sources, independent proofs, implementation changes, negative controls and repeatable measurements?
- RQ3 (prospective): Does the same approach help define robust observability metrics and detect operational changes that raw scalar indicators do not capture?

RQ1–RQ2 are addressed by a retrospective single case, not a controlled study of retrieval effectiveness. RQ3 is a separate open line, not a result of the ledger experiment.

## 2. Research infrastructure

RepoSearch is an open retrieval and artifact-production system. The frozen consumer revision is [059cde32e3e63e17d4ad3917d9fe85c6490d62df](https://github.com/TeaShaman-cyber/theseus-repo-search-lab/tree/059cde32e3e63e17d4ad3917d9fe85c6490d62df); its accepted catalog contains 27 entries, including formalizations named openai-navier-stokes, openai-euler, openai-cdc-lean, openai-matrix-exponent, anthropic-fermats-last-theorem and several Ten Proofs projects. The catalog is a curated selection, not a comprehensive library or a certification of every mathematical claim. Acceptance denotes verified artifact intake and indexed scope. Each occurrence retains its source, artifact identity and declaration provenance.

The unified CLI searches selected accepted artifacts through Turso and expands bounded dependency neighborhoods through Kusto (Azure Data Explorer). The dependency graph is derived from indexed declarations, not from speculative inter-corpus edges. Equal declaration names in different sources do not establish identity. The lexical rank and graph coverage are distinct; unavailable projections, truncated neighborhoods and roots outside indexed scope are reported separately. Open producer, consumer, source descriptors and accepted release packages permit inspection independently of the hosted databases. See [RepoSearch #183](https://github.com/TeaShaman-cyber/theseus-repo-search-lab/issues/183), [#185](https://github.com/TeaShaman-cyber/theseus-repo-search-lab/issues/185), and the [frozen catalog](data/accepted-corpora.json). Hosted services are not themselves open-source implementations of every backend; independent replay can use the repository's local artifact consumer.

The engineering case is Dreaming Worker, an agent-assisted research system with a derived-only, append-only ledger. Its contract preserves exact content identities, evidence provenance, event order, distinct record references and acyclic supersession. A proposal is not canonical truth. A PostgreSQL transaction-scoped advisory lock protects validated writes. The study uses synthetic records and disposable PostgreSQL only; it does not access real conversation history, invoke model inference through the worker or deploy production changes.

## 3. Related work

Topological ordering is classical [1]. Prior work provides verified incremental cycle-detection algorithms with stronger implementation-level proof claims than the abstract lemmas used here [2]. Incremental view maintenance and incremental integrity checking offer relevant algebraic techniques [3,4], but presuppositions about prior validity and mediated changes matter when stored history itself may be corrupt. Cryptographic append-only commitments [5] and proofs of retrievability [6] address different trust and storage guarantees.

Formal-premise retrieval already exploits graph structure. LeanGraphSearch [7] uses semantic seeds and dependency propagation for theorem proving; TheoremGraph [8] links informal mathematical statements and typed formal dependencies, with public extractors and retrieval infrastructure; DAPS [9] targets underrepresented research-level premises using dependency-aware selection. These works demonstrate that structural retrieval is not new. Our narrower question is transfer to an engineering system outside the original proof task, with source-to-code evidence rather than a theorem-proving recall score. This targeted survey is preliminary, not a systematic review or a priority claim.

## 4. Case chronology and transfer mechanism

The original bottleneck was observed in [Dreaming Worker #108](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/issues/108): repeated validation and cloning of every prefix while holding the ledger write lock. The initial remedy used a transaction-local index and single-pass ordered replay, retaining full persisted-row validation. It was accepted through [PR #109](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/pull/109), exact head 681ec80f1d5428b13a2ae13404af1e0af4f945e4, merge 9957f0e5fcd91bed4bbdb012cdb9639468a8a43f.

The second investigation began with mathematical reasoning and literature on incremental checks, then searched the formal corpora. The lexical queries acyclic, Reachable and Merkle searched 27/27 catalog entries; TransGen had degraded coverage (26/27, one HTTP 502). Absence of a hit was not treated as absence of a theorem. We recovered DCR.cone and DCR.Star from Decreasing Diagrams [10] and CDCLean.FiniteGraph.reachable_of_adj_reachable from the CDC corpus [11]. The latter proves path transfer by replacing adjacency steps with reachable paths in an undirected graph.

The key historical-cycle optimization was derived during this initial phase, before the later Kusto graph expansion; it must not be retrospectively attributed to Kusto. The maintainer subsequently requested use of the full graph-search capability. Reverse traversal from the CDC lemma revealed dependent statements, including reachability preservation under edge deletion/replacement and quotient connectivity. Six selected CDC seeds yielded complete bounded neighborhoods in the indexed internal scope, with no graph backend failures. A second query recovered DCR.Escape and its dependencies Star and stepOff. The direct source context and graph occurrences are pinned in the [evidence manifest](evidence.md). These results inspired explicit directed-path transfer lemmas, rank-based pruning and possible graph simplification.

The retrieved undirected results are not directed-DAG theorems. Arbitrary contraction can even create cycles in a DAG. We therefore reconstructed the relevant claims independently for directed relations and checked them in Lean 4.28.0. We did not reuse the undirected statements as proof of the software implementation. Graph search produced additional mathematical directions; no controlled comparison yet establishes how often it outperforms lexical or literature search.

## 5. Mathematical formulation and verified boundaries

Let E_i be the set of distinct directed edges after processing history prefix i. Supersession only adds edges: E_i is a subset of E_{i+1}. A directed path in E_i remains a path in every later graph. Consequently, if the final graph has no directed cycle, no prefix has a cycle; conversely, acyclicity of every prefix includes acyclicity of the final graph. This equivalence permits one historical acyclicity check instead of checking each edge prefix individually.

All non-graph invariants still require original event order: schema, recomputed fingerprints, unique event IDs, distinct existing endpoint records and reference-before-event. Parallel supersession events with different reasons are preserved in the event history but contribute one adjacency pair to the derived graph. Kahn's algorithm checks the graph in O(V+E) time with O(V+E) storage. This is graph work, not a bound on arbitrary payload serialization or hashing cost.

For a valid topological rank r, every edge u to v satisfies r(u)<r(v); induction along a directed path gives the same strict inequality for its endpoints. A new forward edge in that order cannot create a cycle. For a backward candidate u to v, a path from v to u can only visit vertices whose ranks are at most r(u), allowing safe pruning. An accepted backward edge can invalidate the order, so the candidate implementation discards the ranks and uses exact DFS thereafter. It does not use stale order certificates.

A separate formal result establishes reachability preservation when adding an edge already represented by a directed path. Component labels constant along edges also give a sound negative reachability filter. These are additional candidate optimizations, not claimed as implemented. Full transitive closure can require quadratic space and update work; arbitrary graph contraction is not used.

The implementation must preserve error precedence. If a later row or non-graph check fails, it checks the successfully indexed prefix for an earlier cycle before returning the later error. On success it exposes the validated index only after the final topological check. Tests exercise first-error precedence, malformed SQL rows, branching graphs, parallel events, rank invalidation, reference-before-event and rollback. The standalone append contract remains independently validated. See candidate [PR #110](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/pull/110), exact 5af5588567c009d7b7ce0b71ce048145c748726b.

**Storage-integrity negative result.** Consider n independently untrusted row-validity bits. A deterministic checker reading only a fixed proper subset cannot distinguish the all-valid state from the state in which an unobserved bit is invalid. An adaptive checker has the same obstruction on its all-valid execution path if any row is never observed. The fixed-subset version is machine-checked in Lean; the adaptive argument is given here informally. Under this adversarial model, exact validation without trusted aggregate evidence requires observing all rows in the worst case. This is not a general lower bound for every database architecture. The disposable PostgreSQL experiment changed an unrelated historical fingerprint while leaving SQL shape constraints satisfied. Candidate ID lookup returned absent, but full validation rejected the candidate and no insert occurred. Thus simply replacing full validation with local indexed lookups would weaken the current contract. We preserve the physical full-history read.

The abstract proofs in [proofs/](proofs/) establish mathematical lemmas, not a machine-checked refinement of TypeScript, SQL or the complete algorithm's complexity. This distinction is essential.

## 6. Experimental method and results

All data are synthetic. The initial accepted #109 change was measured with a disposable PostgreSQL 17 instance, runtime-role writes and identical proposal-only history. At 100, 500 and 1,000 prior rows, the observed lock-held intervals were respectively 147/14, 3,059/34 and 9,257/47 ms (baseline/candidate). Both implementations read every row. These were single loopback observations, not throughput or percentile estimates. A same-team rerun using the packaged disposable wrapper yielded lock intervals 162/77, 2,291/44 and 9,990/58 ms and reproduced the corruption witness. Raw observations: [initial benchmark](data/initial-postgres-benchmark.jsonl), [rerun](data/postgres-reproduction.txt).

The graph-replay candidate #110 was compared against #109's exact accepted tree. An initial reverse-chain experiment with instrumented SHA-key Map.get counts yielded 12,512,498 versus 34,996 accesses for 9,999 events, with 4,404 versus 311 ms elapsed under instrumentation. These are single observations and counts of one operation class, not total CPU work.

To address that limitation, a separate repeated benchmark measured six synthetic shapes (proposal-only, reverse/forward chains, fan-out, disconnected chains, and reverse-insertion diamonds), three vertex counts (160, 1,000, 2,500), two warmup runs per version and seven elapsed measurements per version, with alternating order within each case. Fixture generation, output equality assertions and Map.get instrumentation are outside timed intervals. Both versions use Node 22.23.5 on the same x86-64 VM (2 available CPUs, approximately 3.8 GiB RAM). Samples, median, minimum/maximum and separate deterministic operation counts are available in [raw data](data/repeated-benchmark.jsonl), [summary CSV](data/repeated-benchmark-summary.csv) and the accompanying scripts.

| Graph shape (2,500 vertices) | Baseline median ms | Candidate median ms | Baseline SHA-key lookups | Candidate SHA-key lookups |
|---|---:|---:|---:|---:|
| Proposals only | 101.0 | 105.2 | 2,500 | 7,500 |
| Reverse chain | 942.7 | 170.4 | 3,131,248 | 17,496 |
| Forward chain | 219.8 | 244.4 | 9,997 | 17,496 |
| Fan-out | 160.5 | 169.6 | 9,997 | 17,496 |
| Disconnected chains | 217.8 | 193.6 | 46,036 | 17,184 |
| Diamonds | 1,516.6 | 190.7 | 4,172,498 | 20,828 |

The adverse-order chain and diamond cases exhibit the predicted large decrease in repeated traversal. The simpler graphs incur additional topological bookkeeping; in this run some were slower. We do not claim a universal speedup or a known production workload distribution. VM timing variability, execution order and sample size limit inference; deterministic counts give complementary evidence. No latency results are extrapolated to a remote database.

An independent comparison of actual implementations over every directed four-vertex edge set in both insertion orders matched 8,192 materialization outcomes (including failure messages) and 13,032 candidate appends to valid histories. An additional abstract experiment checked 6,516 reachability queries across 543 labeled DAGs, 3,588 resolved without visiting vertices by rank/component filters; all 468 redundant-edge insertion witnesses preserved reachability. These are exhaustive finite-domain checks, not a proof for arbitrary implementation sizes.

Candidate #110 passed local canonical QA (448 JavaScript tests, 51 Python tests, native specification coverage and reverse trace), 73 targeted tests and isolated PostgreSQL 17 canonical integration. Final hosted mutation/review status must be refreshed before publication; local passes do not establish acceptance. Exact evidence and current disposition are recorded in #108.

## 7. Threats to validity

The case is retrospective, selected after successful progress. The first improvement originated in code inspection and the major historical DAG idea before graph expansion. The additional Kusto-guided ideas have mixed implementation status; weak-component filtering and graph reduction are unimplemented candidates. Therefore neither the acceleration nor the whole algorithm can be attributed causally to graph retrieval. For a comparative study, freeze tasks, retrieval conditions (literature alone, lexical formal retrieval, lexical plus graph expansion), model/version/tool budgets and judging criteria before collecting results; evaluate source-supported transferable invariants, proof success, implementation parity, measurement and negative results. A non-improvement is a valid result. This is a proposed prospective protocol, not completed evidence.

Indexed dependencies are bounded to accepted artifact scopes and may omit external Mathlib declarations. Source acceptance and graph reachability do not certify truth or cross-domain applicability. Some corpora are previews or formalizations of conjectural targets; no resolution of their underlying scientific questions is inferred. Abstract proofs and finite differential checks cover different failure modes and neither alone establishes complete implementation verification. Timing observations are hardware- and workload-specific.

## 8. Prospective transfer to observability

The broader Theseus question includes agent-control and telemetry systems. Related work in [Theseus #133](https://github.com/TeaShaman-cyber/theseus-research/issues/133) studies positive-affine-invariant standardized skewness and its first variation in the context of distribution-shape drift. The accepted Navier–Stokes formal corpus supplies a research-level example of similarity geometry. This motivates separating changes of observation scale and offset from changes of normalized shape, not claiming that fluid equations govern agent behavior. A scalar skewness value is not a complete invariant of distribution shape.

Prior preliminary telemetry analysis retained a negative result: upper-tail latency expansion was not a universal signature of semantic/goal degradation across two labeled episodes; technically healthy indicators may coexist with incorrect behavior. The observability extension should test relationships between observables, against independently labeled outcomes and known capture gaps. Model Usage Lab [#22](https://github.com/TeaShaman-cyber/theseus-model-usage-lab/issues/22) investigates Langfuse Topics and Tempo with a separately registered protocol; native Topics execution and transfer benefit are not established. Langfuse and Grafana/Tempo are measurement surfaces, not truth authorities. No private trace contents, credentials, session identifiers or unpublished correspondence are included in this package.

An initial prospective experiment should freeze synthetic or explicitly permitted cohorts; distinguish sample size, model/workload mix, incomplete capture and duplicate instrumentation; derive candidate invariants from sourced mathematics; test known affine transformations as negative controls and known shape changes as positive controls; compare simple baselines and record uncertainty. Only then evaluate real telemetry within authorized privacy and cost boundaries. The database case supplies a workflow for the experiment, not evidence of observability efficacy.

## 9. Open-science and accountability statement

The primary research artifacts are the versioned public repositories, issue receipts, exact candidate commits, machine-checkable abstract proofs and runnable experiments. The proposed Zenodo deposit will archive an immutable version of the manuscript and replication materials; a DOI is not peer review. The author is responsible for checking the claims, evidence, citations and final text. AI agents assisted with retrieval, hypothesis generation, drafting, formalization, synthetic fixture generation, implementation and verification. This substantial methodological role must be disclosed; AI output is not evidence without independent checks. Human research direction, scope choices, authorization and interpretation are to be confirmed in author review. No AI system is proposed as an accountable author.

The study is independently valuable without vendor support. The relationship to Langfuse research support is recorded in [Theseus #95](https://github.com/TeaShaman-cyber/theseus-research/issues/95), including a sanitized historical clarification for independent researchers. No grant, eligibility determination, sponsorship or peer-reviewed publication is claimed. The proposed preprint may later be submitted to an appropriate peer-review venue after further evaluation. No funding or conflict-of-interest statement should be finalized without author confirmation.

## References

1. A. B. Kahn (1962). Topological sorting of large networks. https://doi.org/10.1145/368996.369025
2. A. Guéneau, J.-H. Jourdan, A. Charguéraud, F. Pottier (2019). Formal Proof and Analysis of an Incremental Cycle Detection Algorithm. ITP 2019. https://doi.org/10.4230/LIPIcs.ITP.2019.18
3. Budiu et al. (2025). DBSP: automatic incremental view maintenance for rich query languages. VLDB Journal 34, 39. https://doi.org/10.1007/s00778-025-00922-y
4. Oriol and Teniente (2025). Incremental checking of SQL assertions in an RDBMS. Information Systems. https://doi.org/10.1016/j.is.2025.102550 (abstract/institutional record consulted; publisher full text unavailable in initial investigation).
5. RFC 9162 (2021). Certificate Transparency Version 2.0. https://www.rfc-editor.org/rfc/rfc9162
6. H. Shacham, B. Waters (2008). Compact Proofs of Retrievability. https://eprint.iacr.org/2008/073
7. Xu et al. (2026). Lean Graph Search for Formal Theorem Proving. Preprint. https://arxiv.org/abs/2610.22339
8. Kurgan et al. (2026). TheoremGraph: Bridging Formal and Informal Mathematics. Preprint. https://arxiv.org/abs/2606.25363
9. Chen et al. Dependency-Aware Premise Selection for LLM Theorem Proving (2026). Preprint. https://arxiv.org/abs/2610.41536
10. Decreasing Diagrams formalization, archived source. https://zenodo.org/records/23160921 (exact source archive and declaration identifiers in evidence.md; full bibliographic creator metadata pending audit).
11. CDC Lean formalization, exact indexed source revision 577e9d9ea326d520f80672ee69b830bf1d513df5, CDCLean/NashWilliams.lean. See the frozen source descriptor and accepted artifact in evidence.md.

Publication checklist, rights decisions and reproduction instructions accompany this draft. This is not an accepted final manuscript.
