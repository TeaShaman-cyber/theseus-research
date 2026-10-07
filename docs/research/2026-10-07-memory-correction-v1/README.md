# Memory correction intervention v1

Issue: #90 (sub-issue of #81)

This directory freezes the first parser-valid correction intervention for the
Schrodinger Memory black-box study.

It does not claim that ChatGPT Memory or Dreaming understands this grammar
natively. The grammar is an operator-side control that keeps intervention
semantics stable across comparison conditions.

## Conditions

- A: free-form natural-language correction.
- B: raw parser-valid structured correction.
- C: deterministic controlled-prose rendering of B's parsed AST.

`fixtures.json` freezes the shared semantic contract and the three intervention
surfaces. `correction.lark` freezes the bounded language used by condition B.

## Deterministic QA

The repository tests cover parser acceptance, canonical clause ordering,
unsupported-clause rejection, and deterministic B -> C rendering.

The initial Lark differential witness was run against Lark 1.3.1 from the
existing Sonar QA environment:

```text
CASES=30
VALID=24
INVALID=6
MISMATCH=0
LARK_DIFFERENTIAL_PASS
```

The Lark witness is currently research evidence, not part of the every-commit
`tools/dev/check` dependency surface. The canonical repository gate remains
self-contained.

## Current boundary

This slice proves only that the intervention language is bounded and
reproducible. It does not yet prove any improvement in OpenAI Memory retention,
correction precedence, or Dreaming synthesis.

The black-box outcome remains UNKNOWN until an observable Memory intervention
and later independent readback can be performed.
