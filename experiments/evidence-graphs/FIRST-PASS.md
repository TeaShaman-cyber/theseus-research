# First-pass result

Issue: TeaShaman-cyber/theseus-research#37

## Observed result

The preregistered cheap baseline separates the frozen cases without needing a structural classifier:

| Case | Baseline | Analogy edges | Theorem-level edge fraction |
|---|---:|---:|---:|
| Wiles/Taylor-Wiles FLT | PASS | 0/8 | 1.000 |
| Perelman/Poincare | PASS | 0/7 | 0.714 |
| historical TID control | FAIL | 4/6 | 0.000 |

The preregistered topology-only features do not provide an obvious additional discriminator:

- all three graphs are DAGs;
- all three have one weak component;
- node/edge counts overlap closely;
- longest directed path is 5 (FLT), 7 (Perelman), and 4 (TID), which does not define a useful success rule from three cases.

An independent Wolfram pass reproduced node count, edge count, DAG status, weak-component count, and longest-path length exactly.

## Disposition

`REJECT` a topology-only structural classifier for this first bounded experiment.

`KEEP AS HEURISTIC` the evidence-bearing graph representation because it makes theorem/reduction/analogy provenance explicit and gives CI a deterministic contract, but do not claim that graph shape itself identifies productive mathematical discovery.

This is the issue's preregistered falsifier working as intended: source/evidence labels explain the separation more cheaply than graph structure.

## Important limitations

- These are intentionally high-level extracted graphs, not the full 29,500-theorem FLT Prove2Me DAG or a machine-formalized Perelman proof graph.
- Prove2Me's whole-tree API requires authenticated access; no user credential was requested merely to enlarge the first pass.
- The historical TID Session Search id was no longer retrievable from the current live index during this run. The already-read-back #37 checkpoint is therefore the durable provenance source, and the degradation is recorded in the case itself.
- No post-hoc weights, score, classifier, or extra metric were introduced after observing the result.
