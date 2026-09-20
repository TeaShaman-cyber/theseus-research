# Semantic QA fixture v1

This directory freezes the R2 input set for `theseus-research#57`.

It must be merged before semdup, Semble, or Needle 3 are run against it.

The fixture has three intentionally separate roles:

1. four historical retrieval positives, represented as exact accepted fix diffs
   whose failure-class disposition was already known before this experiment;
2. three retrieval negatives, including unrelated research prose and benign
   code, used to measure misleading similarity rather than to force a threshold;
3. two synthetic duplicate controls: one planted semantic rewrite and one
   structurally similar but intentionally distinct pair.

Expected labels live only in `manifest.json`, not in candidate files.

`fixture.sha256` binds every materialized candidate and the manifest. R2 does
not select a tool, set a blocking threshold, or run any semantic model.
