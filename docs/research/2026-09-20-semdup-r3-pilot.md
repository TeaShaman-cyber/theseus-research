# semdup R3 advisory pilot

**Date:** 2026-09-20

**Tracking:** `TeaShaman-cyber/theseus-research#57`

**Roadmap node:** `semdup-advisory-pilot`

**Disposition:** COMPLETE / KEEP AS ADVISORY CANDIDATE / NO THRESHOLD PROMOTED

Machine-readable receipt:
`docs/research/2026-09-20-semdup-r3-pilot-receipt.json`

## Question

Can upstream semdup provide useful local semantic-duplication evidence on the
frozen Theseus fixture without an LLM API, account-bound inference, or a custom
embedding checker?

For this pilot, semdup is evaluated only in its intended duplication role.
Failure-class retrieval remains a separate Semble/Needle experiment.

## Frozen inputs

Fixture:

`theseus-semantic-qa-v1`

Fixture root digest:

`df3bf51cee0a7a57786b140979586ae28f4df7951fb2968e2a39eb1a1ed7048b`

semdup source:

`829f90ad94f453b73a24e46413202e9ece0b49e8`

Runtime reported:

- semdup 0.2.0;
- `nomic-ai/CodeRankEmbed@fast`;
- CPU provider;
- exact scan index;
- function units;
- minimum effective lines = 1.

The source/model identity was frozen in R1 before this fixture was executed.

## Hosted witness

Final hosted run:

`35531526801`

Exact PR branch head:

`46ea459c239c89dd462b3794f392e7a2d3850065`

Conclusion: SUCCESS.

Raw artifact:

- artifact id `10611895521`;
- retained by GitHub until 2026-10-04;
- durable normalized evidence is preserved in the machine-readable receipt so
  the research conclusion does not depend on artifact retention.

The first hosted attempt failed before semdup ran because the temporary pilot
wrapper compared the filename portion of `sha256sum` output as well as the
digest. That setup failure is excluded from semantic evidence.

## Duplicate-control result

The planted semantics-preserving rewrite scored:

`0.7816283`

The intentionally similar-but-distinct control scored:

`0.4370852`

Observed margin:

`0.3445431`

The predeclared scan sweep produced:

| threshold | reported pairs |
| ---: | ---: |
| 0.50 | 1 |
| 0.60 | 1 |
| 0.70 | 1 |
| 0.80 | 0 |
| 0.90 | 0 |
| 0.95 | 0 |

At 0.50, 0.60 and 0.70 the only reported pair was the planted near-duplicate.
No repository threshold is promoted from this tiny fixture.

## PR-style diff behavior

A temporary Git repository was created from the already-frozen planted control:

1. base commit contained the original function;
2. candidate commit added the semantic rewrite;
3. semdup's upstream `ci --mode diff --refresh-base --policy new-pairs`
   path compared the candidate to the base corpus.

At threshold 0.70:

- cosine: 0.7816283;
- verdict: `DUP`;
- exit code: 1.

At threshold 0.80:

- cosine: 0.7816283;
- verdict: `REVIEW`;
- exit code: 0.

This is useful separation already supplied by upstream: the same semantic signal
can remain visible as advisory REVIEW without becoming a blocking DUP. Theseus
does not need custom verdict logic for this distinction.

The upstream composite GitHub Action itself was not invoked in R3. The exact
semdup CLI and its upstream CI wrapper were executed on a GitHub-hosted runner.
Composite-action integration belongs to the later CI-integration node if semdup
survives comparison.

## Runtime and cache result

Final run measurements:

- cold fixture wall time: 2491 ms;
- warm cached wall time: 14 ms;
- cold embed peak RSS: 149924 KiB;
- warm embed peak RSS: 14768 KiB;
- model cache after cold run: 156429571 bytes;
- warm cache delta: 0 bytes;
- embedding DB: 57344 bytes.

The cold log explicitly recorded one-time download of
`nomic-ai/CodeRankEmbed@fast` and embedding six texts.

The warm run was executed with deliberately broken HTTP/HTTPS/ALL proxy values
and still succeeded with zero cache-size delta. This proves the cached warm path
did not require working network access. It does not prove that no network
attempt was made, so `network_attempted_warm` remains UNKNOWN.

Cold and warm raw pair reports were byte-identical:

`084d45f7a1d00d86c451677cc234dc08c10bee4237159ed982e0b836afc0064a`

## Bootstrap cost

The final hosted job took 236 seconds.

Of that, installing the exact semdup source through Cargo took 227 seconds.
The semantic fixture step took 3 seconds and the diff-control step 2 seconds.

Therefore the dominant observed cost was cold Rust compilation, not semantic
inference. If semdup later reaches CI integration, binary/toolchain caching or a
verified prebuilt-binary route should be evaluated before making it routine.

That optimization is not part of R3 and does not change the semantic result.

## Interpretation

### FACT

- exact-source local CPU semdup completed on a GitHub-hosted runner without an
  embedding API key;
- the planted rewrite scored substantially above the intentionally distinct
  control;
- the predeclared 0.50-0.70 scan thresholds reported only the planted pair;
- 0.80 and above reported no scan pair in this fixture;
- diff mode classified the same 0.7816283 signal as blocking DUP at 0.70 and
  non-blocking REVIEW at 0.80;
- cold and warm pair JSON were byte-identical;
- the warm cached path succeeded with broken proxy settings;
- cold source compilation cost far more wall time than the semantic run.

### INFERENCE

semdup is a credible advisory candidate for the semantic-duplication layer.
It already supplies extraction, embeddings, exact cosine search, caching,
machine-readable output and blocking-versus-review semantics that Theseus
should not reimplement.

### UNKNOWN

- a repository-wide production threshold;
- precision/recall on a larger historical duplicate corpus;
- whether the warm path made any unsuccessful network attempt;
- the value of the upstream composite GitHub Action versus direct exact-source
  CLI integration in Theseus.

## R3 disposition

Keep semdup as an advisory candidate for the later cross-pilot comparison.

Do not promote a threshold or blocking gate from this fixture.

The roadmap can now continue independently with R4 Semble and R5 Needle 3.
The graph still requires all surviving pilots to meet at
`compare-pilot-receipts` before role selection or CI promotion.
