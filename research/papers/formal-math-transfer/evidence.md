# Evidence manifest (working draft)

Frozen on 2026-11-27. Repository links below are public coordination or exact source identities, not proof by citation. The manuscript is not an accepted publication.

| Claim / evidence | Exact source | Status |
|---|---|---|
| Corpus catalog and retrieval mechanics | [RepoSearch consumer](https://github.com/TeaShaman-cyber/theseus-repo-search-lab/tree/059cde32e3e63e17d4ad3917d9fe85c6490d62df), [catalog](data/accepted-corpora.json), catalog digest 80290ac5b04b39ed1fb0c81f2dcdeb0a869a20a0f9f928b6f71d274fae8f2dca | 27 accepted entries; query-specific coverage only |
| Historical graph and proof discovery | [#108 initial research receipt](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/issues/108#issuecomment-7226130905) | abstract proofs, lexical retrieval, algorithm derived before Kusto |
| Kusto follow-up | [#108 graph receipt](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/issues/108#issuecomment-7226246794), [CDC graph metadata](data/graph-search-cdc-reverse.json), [DCR graph metadata](data/graph-search-dcr-escape.json) | bounded graph expansion, not retrieval efficacy experiment |
| First implementation | [#109 exact head](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/tree/681ec80f1d5428b13a2ae13404af1e0af4f945e4), [accepted merge receipt](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/issues/108#issuecomment-7226136172) | accepted, not deployed |
| PostgreSQL negative result and first timing | [#108 storage receipt](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/issues/108#issuecomment-7225662801), [initial data](data/initial-postgres-benchmark.jsonl) | disposable PG17, synthetic, one sample/size |
| Second implementation | [#110 exact head](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/tree/5af5588567c009d7b7ce0b71ce048145c748726b), [implementation receipt](https://github.com/TeaShaman-cyber/theseus-dreaming-worker/issues/108#issuecomment-7226359444) | candidate, hosted acceptance pending at draft freeze |
| Repeated workload measurements | [script](experiments/repeated-benchmark.mjs), [samples](data/repeated-benchmark.jsonl) | 18 cases, 7 samples/version, same exact #109/#110 heads |
| Abstract proof check | [Lean files](proofs/), [check log](data/proof-check.txt) | Lean 4.28.0; not implementation refinement |
| Prospective observability | [#133](https://github.com/TeaShaman-cyber/theseus-research/issues/133), [Model Usage Lab #22](https://github.com/TeaShaman-cyber/theseus-model-usage-lab/issues/22) | distinct research, preliminary/negative results; no private traces copied |
| Langfuse context and Zenodo workflow | [#95](https://github.com/TeaShaman-cyber/theseus-research/issues/95), [#96](https://github.com/TeaShaman-cyber/theseus-research/issues/96) | sanitized vendor clarification; no award/application/peer review |

## Formal source identities

- CDC: [exact source file](https://github.com/openai/cdc-lean/blob/577e9d9ea326d520f80672ee69b830bf1d513df5/CDCLean/NashWilliams.lean), commit 577e9d9ea326d520f80672ee69b830bf1d513df5; artifact 154e254c84a94b262f8df022e5e81bea4ee544677830a7de6e1d44b2ea15d978; [accepted release](https://github.com/TeaShaman-cyber/theseus-repo-search-lab/releases/tag/accepted-artifact/openai-cdc-lean/154e254c84a94b26). Theorem reachable_of_adj_reachable lines 757–765, reachableIn_erase_union_singleton_iff_of_cyclic_of_reachable lines 2233–2249, connects_of_internal_of_quotient_connects lines 882–957. Undirected graph context; transfer is independently proved for directed paths.
- DCR: [archived record](https://zenodo.org/records/23160921), SHA256 4601cfef943144d27e4cd0daef5a2b8308f23dddec8cc6f997274585211e7c0f; artifact abd7c1b4e2586c8c7641a459f07a6c0026682796a6e4222fe7bc0a0307d5a0bb; [accepted release](https://github.com/TeaShaman-cyber/theseus-repo-search-lab/releases/tag/accepted-artifact/decreasing-diagrams-complete/abd7c1b4e2586c8c). Regular.lean DCR.Star (65–69), DCR.cone (169–171), DCR.Escape with stepOff. Archive record metadata/rights require audit; web retrieval of record failed.
- Navier–Stokes: source descriptor [data/source-openai-navier-stokes.json](data/source-openai-navier-stokes.json), accepted artifact in catalog; related mathematical investigation in #133, not evidence of successful telemetry transfer here.

Metadata-only graph/context receipts retain declarations, paths, revision, artifact and coverage, with third-party source text omitted pending rights review. Public visibility alone is not a redistribution license. GitHub reports Apache-2.0 for Dreaming Worker and no detected repository-wide license for RepoSearch and CDC. That does not decide all per-file rights. Do not relicense third-party code. No corpus payload, private correspondence or private telemetry is bundled.

## Reproduction commands

With a configured RepoSearch workbench at exact consumer revision, use the public CLI:

```sh
repo-search query graph-search reachable --source openai-cdc-lean --limit 6 --depth 2 --graph-limit 30 --reverse
repo-search query graph-search escape --source decreasing-diagrams-complete --limit 5 --depth 2 --graph-limit 30
repo-search query context openai-cdc-lean CDCLean.FiniteGraph.reachableIn_erase_union_singleton_iff_of_cyclic_of_reachable --depth 1 --token-budget 1800
repo-search query context openai-cdc-lean CDCLean.FiniteGraph.connects_of_internal_of_quotient_connects --depth 1 --token-budget 1800
```

For independent local inspection without hosted account access, fetch the catalog's public accepted releases, verify the release receipt and use the pinned local consumer documented in RepoSearch. This manuscript does not claim a newly executed third-party reconstruction of all 27 artifacts. Graph receipts are not raw model outputs or proof certification.

For implementation comparison, create separate clean checkouts of Dreaming Worker at 681ec80f1d5428b13a2ae13404af1e0af4f945e4 and 5af5588567c009d7b7ce0b71ce048145c748726b; install each lockfile with npm ci using Node 22.23.5. Run:

```sh
node experiments/implementation-parity.mjs /path/to/baseline /path/to/candidate
node experiments/repeated-benchmark.mjs /path/to/baseline /path/to/candidate
python3 experiments/graph-filters.py
node experiments/graph-only-bench.mjs
for f in proofs/*.lean; do lean -j 1 -DwarningAsError=true "$f"; done
```

No real data or model inference is required. Samples are not expected to reproduce identical times. Preserve the full workload and report all shapes, including slowdowns. Operation counts should be deterministic for the pinned implementations.

The earlier PostgreSQL benchmark uses the older #105 accepted tree and #109 exact head; its original destructive fixture manipulations are restricted to a newly created disposable local PostgreSQL database. Reproduce only through the checked dedicated disposable wrapper, never on an existing database:

```sh
experiments/disposable-postgres.sh /path/to/old-d975846 /path/to/new-681ec80
```

The 2026-11-27 rerun is retained in [postgres-reproduction.txt](data/postgres-reproduction.txt); it is a same-team repeat, not independent replication. The canonical integration gate is tools/ci/heavy-postgres from Dreaming Worker.
