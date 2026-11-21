# Session Search reverse-tracing baseline

Issue: https://github.com/TeaShaman-cyber/theseus-research/issues/130

This document is a **human-readable control ruler** for the reverse-tracing
research. It is deliberately simpler than a formal requirements system.

The question for every rule is:

> What did we promise a human, and what evidence proves that the implementation
> still means the same thing?

A green test suite is useful evidence, but it is not automatically evidence for
every architectural promise.

## Status words

- **STRONG** — this pass found executable code plus a focused deterministic
  test, or a bounded independent runtime readback, that directly exercises the
  promise.
- **PARTIAL** — some of the promise is encoded and checked, but a stronger
  semantic claim still depends on documentation, operator discipline, or an
  untested boundary.
- **DOCUMENTED** — the promise is explicit in the architecture, but this pass
  did not find a direct executable proof for the whole statement.
- **HISTORICAL CONTROL** — not a current defect claim; a known old drift that
  we can use to test whether a proposed reverse-tracer would have caught it.

These labels describe the evidence seen in this bounded pass. They are not
permanent truth.

---

## 1. EVIDENCE-01 — History is evidence, not present-day authority

### Human promise

Session Search can tell us what was actually recorded in an old conversation.
It must not silently turn an old statement into current truth.

If an old chat says one thing but current Git, a live deployment, or another
current authority says another, the historical chat is evidence about the
past, not permission to override the current source.

### Why this matters

Without this boundary, better retrieval can make the assistant **more
confidently wrong**: it can retrieve an old decision perfectly and then apply
it after the decision has changed.

### Evidence found

The repository README and architecture explicitly state this boundary.
Search/reconciliation results are also typed as non-authoritative retrieval in
several paths.

### Current status

**PARTIAL.**

The boundary is explicit and appears in tool/result semantics, but no finite
test can prove that every future agent using Session Search will interpret every
retrieved passage correctly.

---

## 2. CORPUS-01 — Accepted evidence defines the corpus; the search database does not

### Human promise

The durable accepted artifact bytes plus their accepted-ledger membership are
the corpus evidence boundary.

SQLite/FTS, Postgres/Neon, indexes, caches, and other search structures are
copies built from that evidence. We may delete and rebuild those copies without
changing what was accepted.

### Why this matters

If the search database itself becomes the authority, corruption or an
experimental migration can silently rewrite history.

### Evidence found

Current code reads accepted-ledger membership explicitly; rebuild enumerates
accepted members; verification detects ledger/projection disagreement.
Repository docs repeatedly state that the projection is disposable.

### Current status

**STRONG.**

This promise has both implementation and focused deterministic checks.

---

## 3. VERIFY-01 — A weak check must not be reported as a stronger check

### Human promise

If we only checked that the projection is internally consistent, we must not
say that we proved full derivation from immutable source evidence.

In particular:

`PROJECTION_CONSISTENT` is not the same claim as full `VERIFIED`.

### Why this matters

A system can be internally self-consistent and still be consistently derived
from the wrong input.

### Evidence found

The current projection-consistency path explicitly reports
`derivation_verified=false`. Documentation names the stronger full verification
path separately, and regression tests cover the distinction.

### Current status

**STRONG.**

---

## 4. PORT-01 — Session Search must remain recoverable without the current serving vendor

### Human promise

MarcoPolo, Neon, Arcade, browser capture, Google Drive transport, and similar
components may be useful today, but none of them is allowed to become the only
way Session Search can exist.

Given accepted portable evidence, a standalone local runtime must remain a real
recovery path.

### Why this matters

Otherwise an experiment in convenience quietly becomes vendor lock-in and a
single failure domain.

### Evidence found

The portable runtime is built as a deterministic artifact with no MarcoPolo,
Google Drive, corpus-data, credential, or third-party Python dependency.
Hosted acceptance produces the runtime in one job and consumes it in a fresh
job.

### Current status

**STRONG for runtime portability. PARTIAL for every possible disaster-recovery
scenario.**

The current tests strongly prove that the packaged runtime is independent.
They do not prove that every external operator will still possess the required
accepted artifacts at the moment of a real vendor failure.

---

## 5. BIND-01 — “This is what the runtime serves” is not “this is verified evidence”

### Human promise

A runtime pointer, environment variable, symlink, deployment ID, or active
generation may tell us **what is currently being served**.

That observation must not be promoted into the stronger claim that the served
data was fully derived from accepted evidence.

### Why this matters

Operational state and evidence authority answer different questions.
Confusing them was already a source of historical drift.

### Evidence found

Architecture and QA docs explicitly separate promotion/binding readback from
full corpus verification.

### Current status

**PARTIAL.**

The separation is explicit and some bounded checks exist, but this is also an
operator/agent reasoning rule: future automation can still overclaim unless the
claim type becomes mechanically enforced.

---

## 6. FAIL-01 — One stalled shard must not hang healthy results

### Human promise

If one federated search shard is unavailable or stalls, healthy shards must
still be able to return useful results within a bounded time, and the result
must say that it is partial.

### Why this matters

“Handles errors” is weaker than “cannot hang forever.” This was a real gap in
the historical PR #66 implementation.

### Evidence found

Current router code has a bounded shard timeout. A deterministic test creates a
shard whose body never resolves and proves that the healthy shard survives as
`PARTIAL` with `TIMEOUT`.

### Current status

**STRONG on current main.**

### Historical control

PR #66 had a green canonical QA suite but no application timeout. The test
covered an explicit error, not a never-finishing shard. This is a primary
reverse-tracing benchmark.

---

## 7. ROUTE-01 — Invalid filters must fail before they distort routing

### Human promise

Provider, session, and time filters are not merely optional fields. Their
meaning must be checked before those values influence which shards are queried.

Malformed or inverted bounds must not masquerade as a legitimate
`NO_SIGNAL` or `PARTIAL` search result.

### Why this matters

Otherwise the system can report “nothing found” when the real problem is “the
question was invalid.”

### Evidence found

Current router input validation rejects invalid session/time values and inverted
time bounds; focused tests exercise those cases.

### Current status

**STRONG on current main.**

### Historical control

The earlier federated router validated query/scopes/limit but not the full
session/time contract at the router boundary.

---

## 8. GEN-01 — READY means immutable searchable content

### Human promise

Once generation X is declared READY, “generation X” must keep meaning the same
searchable content.

A materializer may build a generation, verify it, then mark it READY. It must
not later append or rewrite child data under that same identity.

### Why this matters

Provenance is meaningless if an identifier points to changing content.

### Evidence found

The lifecycle migration requires generation creation to start BUILDING and
rejects child mutation after READY. Contract tests assert the guard text and
the lifecycle has been exercised in live canaries historically.

### Current status

**STRONG on current main.**

### Historical control

PR #65/#66 exposed a safe BUILDING -> READY path but did not make that safe path
the only possible materializer path.

---

## 9. PIN-01 — The router must search the exact generation it claims

### Human promise

If the router says a result came from generation X, it must actually ask the
shard for X. It may not silently use whatever generation happens to be ACTIVE
and then attach X-shaped metadata afterward.

### Why this matters

Otherwise the provenance label and the queried data can disagree while every
individual service still returns HTTP 200.

### Evidence found

Current pinned-generation path requires an explicit generation, checks a
`router_pinned_v1` witness, rejects mismatches as `STALE_GENERATION` or
`PINNING_NOT_CONFIRMED`, and has deterministic tests including no fallback to
ACTIVE.

### Current status

**STRONG on current main.**

---

## 10. PROV-01 — Every useful result must keep its origin

### Human promise

A retrieved result must retain enough provenance to answer: which provider,
which shard, which generation, and which historical occurrence produced it.

Deduplication may collapse presentation duplicates, but it must not erase the
historical occurrences that justify the result.

### Why this matters

Without provenance, retrieval becomes an attractive assertion generator rather
than evidence.

### Evidence found

Current router/grouping tests preserve shard/generation identity and grouped
occurrences. Corpus results also preserve session/message provenance.

### Current status

**STRONG.**

---

## 11. COVERAGE-01 — Latest indexed time is not proof of complete source history

### Human promise

Seeing messages up to Tuesday does not prove that every ChatGPT conversation up
to Tuesday was captured.

If there is no authoritative source watermark, the truthful state remains
`UNKNOWN_WITHOUT_SOURCE_WATERMARK`.

### Why this matters

This prevents a search miss from being misreported as “that conversation never
happened.”

### Evidence found

Current local and federated coverage code carries the explicit unknown state.
Focused tests verify that healthy serving, index bounds, and ordinary misses do
not manufacture source completeness.

### Current status

**STRONG for the encoded claim.**

### Historical control

Issue #275 came from a real case where recent-history search risked confusing a
stale corpus with a relevance/search-quality problem.

---

## 12. TOOL-ID-01 — Backend upgrades must not silently change the consumer tool identity

### Human promise

The user-facing Session Search capability has one stable identity. Replacing a
router/backend should not create a sibling production tool that the selector
may ignore or choose inconsistently.

### Why this matters

A technically correct new backend is useless if the ChatGPT host continues
selecting the old tool.

### Evidence found

The current serving-plane documentation explicitly requires the stable
`TheseusSessionSearch.session_search` identity and describes in-place worker
update / tool refresh instead of a version-suffixed production sibling.

### Current status

**PARTIAL.**

The architecture rule is now explicit and was validated during the historical
rollback/cutover work, but this pass did not find one deterministic repository
test that proves every future control-plane change preserves the external tool
identity.

### Historical control

The attempted side-by-side `session_search_v2` route looked locally sensible
but drifted from the real gateway/selector architecture. It was reverted.

---

## 13. SEC-01 — Search must fail closed at trust boundaries

### Human promise

Public HTTP reachability must not imply search authority.

The router requires its own bearer; router-to-shard traffic uses a separate
secret; shard database roles receive only bounded query capability, not broad
table/superuser access.

Credentials must not leak through normal application errors.

### Why this matters

A search feature that is correct but over-authorized is still architecturally
wrong.

### Evidence found

Current router and shard handlers reject missing/invalid credentials before
dispatch. Auth tests cover `401 UNAUTHORIZED`. Serving docs record limited
roles without direct message/session SELECT and without `neon_superuser`.
Error-redaction tests exist.

### Current status

**STRONG for application auth/error handling; PARTIAL for the full external
cloud IAM state because repository tests cannot by themselves prove current
provider configuration.**

---

## 14. OBS-01 — Observability describes behavior; it does not become configuration authority

### Human promise

Grafana/PostHog/telemetry can tell us what was observed. They must not be used
as proof of endpoint configuration, current deployment identity, accepted
corpus authority, or Git exact head when those claims require another source.

The service-owning repository owns Session Search monitoring configuration;
the machine/tool used to edit Grafana does not.

### Why this matters

A trace showing “router X handled a request” is not the same statement as
“router X is the configured canonical endpoint now.”

### Evidence found

README and Grafana runbook make the authority split explicit; dashboard
configuration has deterministic contract tests.

### Current status

**PARTIAL.**

The dashboard/config structure is tested; the epistemic rule about what an
operator or agent may infer from telemetry remains partly a reasoning
discipline.

### Historical control

Monitoring ownership was once incorrectly assigned to the repository/runtime
where the Grafana management tool happened to run, rather than to the Session
Search service repository.

---

## 15. PRIV-01 — Public research artifacts must not contain private session material or secrets

### Human promise

Real conversation text, raw captures, private URLs, provider IDs, credentials,
and account-specific metadata stay out of the public repository.

Synthetic fixtures and bounded public receipts are the public evidence path.

### Why this matters

A research system for memory/continuity has an unusually high cost of accidental
data exposure.

### Evidence found

The repository rule is explicit; authentication/error paths include
credential-redaction tests; public tests are synthetic.

### Current status

**PARTIAL.**

Focused leakage classes are tested, but “the entire future repository contains
no sensitive material” is an open-ended property and should not be claimed from
a few tests alone.

---

# Historical drift corpus for the reverse-tracer

These are candidate benchmark cases. They are **not all current defects**.

## H1 — Green CI but missing federation postconditions

PR #65/#66 -> issue #69/#70:
- stalled shard could hang the whole router;
- invalid routing filters were under-validated;
- READY generation mutability was not fully closed.

Expected reverse-tracer behavior: detect that the implementation/test evidence
proved weaker statements than the human requirements.

## H2 — Canonical Git and installed runtime diverged

An installed cumulative-corpus/runtime fix existed while canonical source still
described/implemented an older single-SQLite binding.

Expected behavior: distinguish “runtime currently works” from “canonical
versioned source contains the same architecture.”

## H3 — Stable tool identity drift

A side-by-side `session_search_v2` looked like a normal migration technique,
but the Arcade gateway allowlist and ChatGPT selector semantics meant the new
identity did not transparently replace the old consumer capability.

Expected behavior: reason across the external control-plane contract, not only
the new backend code.

## H4 — Search miss / coverage overclaim

A miss against an incomplete or stale corpus was at risk of being interpreted
as evidence that the conversation/fact did not exist.

Expected behavior: keep retrieval evidence, corpus coverage, and upstream source
completeness as separate claims.

## H5 — False COMPLETE from weak provenance

Historical accepted captures included untagged pages. Treating weak page
membership as enough to infer complete-session coverage could create false
`COMPLETE` and therefore false absence claims.

Expected behavior: identify that the evidence is insufficient for the stronger
coverage label rather than inventing membership from title/time/text/majority
heuristics.

## H6 — Ephemeral storage mistaken for durable handoff

Historical operational work kept durable handoff state in `/tmp`; environment
shutdown erased it.

Expected behavior: notice that the implementation contradicts the durability
promise even if the happy-path handoff works before shutdown.

---

# What this baseline does and does not prove

## It does

- give the project a stable, human-readable set of promises;
- separate human meaning from implementation detail;
- identify where current evidence is strong vs partial;
- provide real historical failures for mutation/reverse-tracing experiments.

## It does not

- prove that these 15 promises are the complete Session Search specification;
- prove that every current implementation satisfies every promise;
- authorize a production gate or new dependency;
- prove that SpecD, Spec Kit, StrictDoc, OpenFastTrace, or an LLM reviewer is
  useful.

Those tools must now compete against this baseline. A tool earns adoption only
if it detects real drift that this simple map plus existing deterministic QA
would otherwise miss, at acceptable maintenance cost.
