# Evidence-graph experiment (#37)

This directory implements the first bounded experiment from TeaShaman-cyber/theseus-research#37.

## Frozen cases

The first comparison uses exactly three cases, added only after this preregistration commit:

1. Wiles/FLT successful dependency path, with the 2026 Lean formalization used as an independent verification layer.
2. Perelman/Poincare-geometrization successful dependency path.
3. One historical failed/inconclusive TID sketch with exact Session Search provenance.

## Direction and vocabulary

Edges point from prerequisite/evidence to the claim or construction that depends on it.

Node roles are limited to:

- `problem`
- `reformulation`
- `reduction`
- `bridge_theorem`
- `construction`
- `invariant`
- `repair`
- `verification`
- `consequence`
- `analogy`

Edge roles are limited to:

- `depends_on`
- `reduces_to`
- `bridges`
- `constructs`
- `repairs`
- `verifies`
- `implies`
- `analogy`

Evidence classes are limited to:

- `kernel_checked` — checked by a proof kernel or equivalently formal verifier.
- `established_theorem` — established theorem/proof in the mathematical literature.
- `primary_exposition` — authoritative primary or expert exposition supporting the represented dependency.
- `historical_record` — historical project/chat record; provenance evidence, not mathematical validation.
- `analogy_only` — analogy or conjectural relation without a theorem-level bridge.
- `unknown` — evidence status is not resolved.

Every non-`analogy` edge must name at least one source reference. An `analogy` edge must use `analogy_only` or `historical_record` evidence.

## Cheap baseline (evaluated before structural features)

A case passes the baseline only when:

1. it has at least one directed path from a `problem` node to a `consequence` node;
2. every edge on at least one such path is non-analogy;
3. every edge on that path has evidence in `kernel_checked`, `established_theorem`, or `primary_exposition`;
4. at least two distinct source references occur on that path or one path edge is `kernel_checked` and at least one other source reference is present.

The baseline is intentionally qualitative. It is not a discovery score.

## Frozen structural/evidence features

The first pass reports only:

- node count;
- edge count;
- DAG status;
- weak component count;
- longest directed path length when acyclic;
- count and fraction of `analogy` edges;
- count and fraction of edges with theorem-level evidence (`kernel_checked` or `established_theorem`);
- count of `repair` edges;
- count of `verification` edges;
- number of distinct source references used by edges;
- cheap-baseline result.

No weights, learned classifier, or post-hoc scalar score are permitted in this first pass.

## Comparison rule

The experiment earns a `REFINE` disposition only if the frozen features add a useful distinction beyond the cheap baseline. If source/evidence labels alone explain the separation, record `KEEP AS HEURISTIC` or `REJECT` rather than inventing more metrics.

## Reproduce

```bash
python experiments/evidence-graphs/compare.py \
  --cases experiments/evidence-graphs/cases \
  --receipt experiments/evidence-graphs/receipts/latest.json

python -m unittest discover -s experiments/evidence-graphs/tests -v
```
