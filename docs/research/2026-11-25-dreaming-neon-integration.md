# Dreaming Worker / Session Search: native Neon integration — review candidate

Status: DESIGN_CANDIDATE, not accepted architecture. Owner: #127.
Corrects the premature direct-SQL preference in #127 comment 7170403165.
Implementation coordination: Dreaming Worker #65, Session Search #3/#59/#340.
Goal: internal module consumes changed conversations with the fewest new
components, without reproducing Session Search routing or exposing corpus
credentials. Retain Cloudflare execution and existing Hyperdrive ledger.

## Observed facts (2026-11-25)
- Neon Functions are Node.js HTTP handlers, branch-scoped, with public
  invocation URLs. Inbound authentication is application responsibility;
  branch-injected credentials are outbound service access, not caller auth.
  Same organization is not a function invocation capability.
- Neon Functions supports schedule and object-upload triggers. Neither is
  evidence of reliable durable accepted-source delivery; no trigger needed
  unless measured scheduling need. Cloudflare Service bindings target other
  Cloudflare Workers, not an arbitrary Neon Function. Hyperdrive is DB
  connectivity, not a function invocation protocol.
- Live Neon inventory: Theseus Session Search organization, Free plan, 11
  visible projects; Dreaming and main ChatGPT green data projects in Ohio.
  Two inspected default branches (one green data project and Dreaming) list
  no Functions; this is NOT evidence that existing serving Functions are
  absent. The runbook explicitly separates existing Function hosts and
  green data projects/branches. Resolve current serving identity from the
  existing promotion manifest/catalog, not project-name guesses.
- Session Search main e3e8871da3aa83057486350e544f4fe89b299b0e:
  functions/router/handler.mjs exposes /search, /coverage, /mcp but NOT
  standalone /session-browse. makeSessionBrowser in
  functions/router/session-browse.mjs already implements catalog selection,
  READY/exact generation checks, timeout, cursor and partial payload
  validation, calls shard Function POST /session-read. Shard SQL
  read_generation_session_v1 is restricted to reader role.
  Existing local session_read supports ordered reads of the local projection.
- Dreaming main 20d87df98a203a8ef8714f941dd466d1cfc3950b:
  #50 accepted PG ledger adapter, #65 durable admission/completion; existing
  Hyperdrive in cloud dev environment. Intake spec separates query, source
  authority and checkpoints. #343 accepted optional import delta; #344
  recovery candidate; neither is a durable published handoff or proof that
  a changed conversation is served by the current catalog.

## Alternatives (review before selection)

A. Cloudflare Worker -> existing Neon router Function via ordinary HTTPS
fetch -> existing shard Function -> database. Reuse makeSessionBrowser via
a narrow non-MCP route (provisional POST /session-browse), not another
Function or gateway. Dedicated service credential restricted to that route;
existing broad router/Arcade token must not be copied. Router owns blue/green
selection, generation/cursor semantics and coverage. One small source-side
handler change and consumer adapter; no source DB creds in worker.
Preferred hypothesis for first experiment, subject to review.

B. Worker -> existing shard Function /session-read directly. No new router
handler but must supply trusted current exact shard/generation/host binding,
recreate cursor/payload/failure validation or share existing implementation,
and scope per-shard credentials. Could be thinner if handoff already binds
all these and there is no catalog duplication; never choose hosts by names
or give broad shared shard token to worker merely for convenience.

C. Worker -> database function through Hyperdrive or Neon serverless driver.
Technically possible with restricted role, but requires DB connectivity per
target, target rotation on blue/green and replication of serving semantics.
Compare cost/latency/maintenance only after exact target and auth inventory.
Not default; do not replicate whole router in the worker.

D. Move analysis to Neon Functions (same runtime/branch as data), use Neon
AI Gateway and/or Function Triggers. Native long-running JS runtime and
branch-scoped services make this a legitimate future alternative. But
multi-project shards, cross-family inference, existing Cloudflare deployment
decision, ledger and observability must be preserved. Trigger delivery is
not work completion. Requires comparative benchmark and explicit runtime
decision; not a prerequisite. Realtime/CDC/NOTIFY not a durable source
delta contract; don't add always-on polling or broker for rare refreshes.

E. Existing local/server reader for portable/offline laboratory execution.
Same semantic work contract; no requirement to call a Neon HTTP route for
local fixtures. MCP/Arcade remain agent-facing adapters, not the worker's
internal dependency.

## Proposed normative interface / invariants for review
1. Session Search publishes a bounded durable refresh receipt only after
   accepted source verification and exact serving promotion readback.
   Reuse existing refresh/manifest path; receipt binds previous/current
   accepted membership, contract version, exact per-shard generation vector,
   changed projected session IDs including removed/moved branches, scope,
   currentness and gaps. If data promoted but receipt lost, recover from
   retained membership + canonical rebuild (#344), with explicit contract
   version checks. Compare prior/current full derived source under current
   code only; not historical executable equivalence. Existing verified
   manifests must establish per-shard placement; if mapping not available,
   BLOCKED rather than inventing a new catalog. Design durable receipt
   publication/reconciliation before implementation; no new queue by default.
2. Consumer fetches one selected conversation by exact session/shard/generation
   and bounded pages using existing reader. Request includes session_id,
   shard_id,generation_id,cursor or start_ordinal,limit,max_chars. Reuse current
   validation and response format; distinguish incomplete pagination, partial
   source coverage, unavailable shard, and generation mismatch. No ACTIVE
   fallback, redirects to untrusted hosts, implicit full history or lexical
   miss as no work. Total byte/page/time budget across a work item. Re-read
   only with exact retained generation or replan explicit fresh receipt.
3. Authentication: separate worker-specific secret/token, only read capability
   on selected routes, stored in existing secret mechanisms. Do not reuse
   management API keys, browser OAuth, operator bearer or ledger write role.
   Enforce auth before parsing/dispatch; no MCP feedback/write capability;
   verify denied other routes, rotation, preview isolation, no secret/body logs.
   Public URL is not private networking; account membership is not auth.
4. Evidence source refs bind exact session/message/version and custody.
   The current browse projection drops raw artifact/page hashes and some
   canonical fields: preserve authoritative source references via refresh
   receipt or explicitly scoped evidence sidecar if necessary; do not invent
   full provenance from projected text. Version and hash exact selected
   evidence and dependencies (including relevant order/context/coverage).
   Work identity is scoped, not global accepted set/generation. Keep source
   snapshot/generation lineage separately. Unrelated refresh must not trigger
   inference; changed evidence/dependencies or analysis version must.
5. Existing durable reservation/completion + ledger remains unchanged.
   Retain pending work and advance consumer checkpoint only after all
   relevant work accepted, or explicitly classified non-work. Lost ack
   readback; unavailable/partial is not no work. Removed branch requires
   reconciliation, not deletion of derived history. No automatic inference
   retry under unknown provider outcome.
6. Initial acceptance with synthetic data only, actual two generations and
   two shards, moved branch and stale cursor, failed shard, repeated import,
   lost refresh receipt and replay, wrong token, token misuse against write
   routes, full worker completion readback with zero duplicate model calls.
   Use current SS CI and DW SpecD/PG QA. No new resource or permission
   mutation before separate scoped decision. No private history/model egress.

## Experiment order
E1. Inventory exact serving Function and data branch mappings, current handler
and role contracts; no mutations. Establish whether existing verified
promotion output is enough for handoff and direct shard call (B).
E2. One disposable synthetic contract comparison of A/B; reuse current
router/shard handlers and PG fixtures, exercise two generations/shards,
auth, cursor and failures. Measure requests, credential count, duplicated
logic, latency and compute/egress under actual plan. A canary is not deployment.
E3. Select thinnest passing option. Native SpecD proposal/deltas/verify/design
before protected DW runtime implementation. Define durable handoff,
source dependency identity and exact provenance before autonomous execution.
E4. End-to-end synthetic fixture on existing dev runtime with ledger readback.
Keep existing local/server reader. Only then consider live source and provider
permission as distinct decisions.

## External sources (reviewed 2026-11-25)
- https://neon.com/docs/compute/functions/overview
- https://neon.com/docs/compute/functions/authentication (updated Nov 18)
- https://neon.com/docs/compute/functions/get-started
- https://neon.com/docs/concepts/credentials-access
- https://neon.com/docs/reference/api/functions
- https://developers.cloudflare.com/workers/runtime-apis/fetch/
- https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/
- https://developers.cloudflare.com/workers/databases/third-party-integrations/neon/
- https://neon.com/blog/neon-backend-is-ga
Acumen preflight did not surface specific Neon Functions facts; Exa supplied
the relevant primary documentation. No claim that a special cross-cloud
private function binding is unavailable universally; none was verified.
Existing repository evidence is primary for deployed project architecture.
