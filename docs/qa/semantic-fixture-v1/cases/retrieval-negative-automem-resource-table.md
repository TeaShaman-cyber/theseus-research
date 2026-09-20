## Embedding results

The remote same-host comparison used the same graph and a fixed 100-query
replay:

| Variant | Recall@10 | MRR | NDCG@10 | API RAM | Mean latency | p95 |
|---|---:|---:|---:|---:|---:|---:|
| BGE-large / 1024d | 0.9100 | 0.7825 | 0.8130 | 2.57 GiB | 682.9 ms | 831.1 ms |
| BGE-base / 768d | 0.9200 | 0.7823 | 0.8152 | 979.6 MiB | 788.7 ms | 927.2 ms |

A second BGE-base replay reproduced the quality metrics. The result is a
resource/quality tradeoff: BGE-base saves roughly 62% of the API model
footprint and is somewhat slower in this test. It is not a proof that it wins
on every corpus.

The local cutover created a separate `memories_base` collection, re-embedded
the graph, and retained the original 1024d collection and volume backups. The
local health endpoint reports a filtered visible count; direct graph/vector ID
comparison found 401/401 IDs with no orphan IDs. The active local runtime now
uses 768d and remains healthy.
