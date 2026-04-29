# Synapse Digital Twin Platform — Phase 3 Expert Panel Review Report

- **Date:** 2026-04-27
- **Panel composition:** product_strategist · think_tank (decision advisor + execution auditor) · harness_engineer · integration_qa · knowledge_engineer
- **Authorization:** Lysander CEO + Expert Panel, full decision authority (L3)
- **Deliverable to president:** Final report only
- **Phase 2 baseline:** 93/100 PASS, 161/161 tests, 7 scenarios, branch `phase2-sprint-c`, commit `eb990e1`
- **Gate threshold:** ≥ 85/100 to proceed
- **Related decisions:** D-2026-0427-011 · D-2026-0427-012 · D-2026-0427-013 · D-2026-0427-014

---

## 1. Executive Summary

**Phase 3 is approved to execute. Scope verdict: PASS (88/100).**

Phase 2 delivered a 93/100 platform with 7 scenarios, IStore<T> adapter pattern, and PgStore implemented but not yet end-to-end wired. Phase 3 has a clear and executable mandate: complete the storage backend migration that Phase 2 architected but intentionally deferred, then build the RAG layer on top of the real Postgres backend, then close the remaining production-confidence gaps (real Socket Mode, SLA alerting).

**The single most important finding of this review:** `STORAGE_BACKEND=postgres` does not actually write to PostgreSQL. `createStores()` in `src/index.ts` creates a `Pool` object and then passes `new CaseStore()` — which constructs `FileStore` internally — regardless of the env var. PgStore is implemented and tested, but it is never wired into any domain store in production. This is a known, intentional deferral (documented in Sprint C report and D-2026-0427-008), but it means Phase 2's "PostgreSQL migration" is only half-complete. Sprint D closes this gap as the mandatory first sprint of Phase 3.

**Phase 3 scope:** Four sprints.
- **Sprint D (mandatory first):** Domain store DI refactor + server-side query optimization + live testcontainer integration tests
- **Sprint E:** pgvector RAG pipeline (corpus ingestion + semantic retrieval for agent context enrichment)
- **Sprint F:** Real Slack Socket Mode integration test + SLA Slack alerting
- **Sprint G (conditional):** Web dashboard — deferred to Phase 4; Sprint G slot reserved only if a concrete user story emerges

**RBAC is Phase 4** (binding decision D-2026-0427-014). No current user story justifies it.

---

## 2. Phase 3 Scope (MoSCoW)

| # | Item | Priority | Sprint | Complexity | Business Value | Build Cost |
|---|------|----------|--------|------------|----------------|------------|
| 1 | Domain store DI refactor (6 stores accept IStore<T> via injection) | Must | Sprint D | M | High — completes Phase 2's core architectural goal | Low-Medium |
| 2 | PgStore server-side typed query methods (findWhere JSONB, date-range WHERE) | Must | Sprint D | M | High — eliminates O(n) table scans on audit_logs | Medium |
| 3 | StoreFactory wires PgStore instances to all domain stores when STORAGE_BACKEND=postgres | Must | Sprint D | S | Critical — without this, Postgres backend is non-functional | Low |
| 4 | Live DB integration tests via @testcontainers/postgresql | Must | Sprint D | M | High — production confidence that PgStore actually works | Medium |
| 5 | pgvector: vector columns + HNSW index (migration 003/004) | Must | Sprint E | S | Foundation for RAG | Low |
| 6 | Corpus ingestion pipeline: embed agent knowledge bases + playbooks | Must | Sprint E | L | High — PM Agent knowledge becomes semantically searchable | High |
| 7 | Semantic retrieval for PM Agent context enrichment at case intake | Must | Sprint E | M | High — grounds agent responses in prior cases + knowledge base | Medium |
| 8 | Real Slack Socket Mode integration test (beyond nock shim) | Must | Sprint F | M | Medium — production-confidence gap closure | Medium |
| 9 | SLA Slack alerting via DM when SLA is breached | Must | Sprint F | S | High — SLAMonitor marks breaches but no one is notified | Low |
| 10 | EvidenceBundle server-side query by caseId / type / date range | Should | Sprint D | S | Medium — eliminates JS filter on evidence retrieval | Low |
| 11 | Agent output quality rubric gate for ResearchAgent / ContentAgent | Should | Sprint E | S | Medium — closes Phase 2 scoring gap (no rubric for new agents) | Low |
| 12 | Query performance baselines at 1000+ case scale | Should | Sprint D | S | Medium — quantified latency SLAs before production load | Low |
| 13 | RBAC / multi-tenant authorization | Won't (Phase 3) | Phase 4 | L | Zero (no user story) | High |
| 14 | Web dashboard / reporting layer | Won't (Phase 3) | Phase 4 | XL | Zero (no user story) | Very High |
| 15 | Cross-org multi-agent handoff | Won't (Phase 3) | Phase 4 | XL | Zero (no user story) | Very High |

---

## 3. 三原则 Review

### 3.1 做正确的事 (Strategic Alignment)

**Finding 1 — Completing the PgStore wiring is not optional; it is a debt repayment.**

The Phase 2 acceptance report scored the platform at 93/100, with two explicit deductions in the "代码与架构质量" dimension for (a) PgStore.find() in-memory scanning and (b) domain stores not completing the DI wiring. These are not cosmetic issues. The strategic promise of Phase 2 was "production-grade PostgreSQL storage." That promise is not fulfilled as delivered. Sprint D fulfills it.

Without Sprint D, Sprint E (pgvector RAG) would be building a semantic retrieval layer over a Postgres DB that the application does not actually write to. That is architecturally incoherent. Sprint D is the prerequisite for all of Phase 3.

**Finding 2 — pgvector RAG at Phase 3 is correctly timed and has a real corpus.**

Phase 2 deferred RAG with the rationale: "No current user story; premature without production load data." Phase 3 reverses this because:

1. The corpus exists now: 7 agent knowledge base files, 9 playbooks, and accumulated runtime artifacts from the test suite and any production usage. The PM Agent's `expert-knowledge-base.md` alone is 372 lines of curated PM methodology.
2. The user story is concrete: PM Agent should retrieve similar prior cases at intake and inject them into context, grounding responses in demonstrated organizational patterns rather than generic Claude knowledge.
3. The infrastructure gap (Postgres not actually wired) is closed by Sprint D, removing the Phase 2 blocker.

The original business vision (Section 2.2 of the original requirements doc) explicitly calls out that agents should become more like the actual owner over time — "贴近 Lysander Liu 的高级项目经理." RAG over the owner's curated knowledge base is the mechanism that enables this. Phase 3 is the right time.

**Finding 3 — Original requirements coverage assessment.**

The original requirements defined 7 layers of meaning. Current coverage at Phase 2 close:

| Requirement Layer | Coverage | Phase 3 Delta |
|-------------------|----------|---------------|
| 每人角色型数字分身 (role-typed agent per person) | Partial — 3 agent types (PM/Research/Content), ServiceAgent | No change in Phase 3 |
| Agent 间协作 (inter-agent collaboration) | Partial — orchestrator routes to single agent; no agent-to-agent handoff | No change in Phase 3 |
| 围绕 case 协作 (case-centric workflow) | Complete — 7 scenarios fully E2E | No change |
| 人类保留审批 (human approval boundary) | Complete — ApprovalGate + approval-matrix.yaml | No change |
| 真实工具环境 (real tool environment) | Partial — Slack Bolt production-confidence gap (Socket Mode smoke test) | Sprint F closes |
| 多语言多角色协同 (multilingual, multi-role) | Partial — Chinese language support in agent knowledge bases; single human role | No Phase 3 change |
| 可用业务成果 (actionable business deliverables) | Partial — artifacts are generated; quality depends on agent knowledge | Sprint E (RAG) improves |

**Finding 4 — Business value × build cost matrix (Phase 3 Must-Have ranking).**

| Item | Business Value | Build Cost | V/C Ratio |
|------|---------------|------------|-----------|
| StoreFactory PgStore wiring | Critical | Low | Highest |
| Domain store DI refactor | High | Medium | High |
| SLA Slack alerting | High | Low | High |
| PgStore server-side queries | High | Medium | High |
| Live testcontainer tests | High | Medium | High |
| Corpus ingestion pipeline | High | High | Medium-High |
| Semantic retrieval (PM Agent) | High | Medium | High |
| Real Socket Mode test | Medium | Medium | Medium |

The ordering confirms the Sprint D → E → F sequence: infrastructure first (high V/C), then capabilities (high V/C), then production hardening (medium V/C).

**Strategic Alignment Score: 23/25**

---

### 3.2 正确的做事 (Architecture Review)

**Finding 5 — The DI gap is a concrete architectural defect, not a design choice.**

Evidence from `src/index.ts` (inspected directly):

```typescript
// createStores() postgres branch (current state):
const { Pool } = require('pg');
// Pool is constructed but...
void Pool; // Referenced for future direct PgStore injection in Phase 3
return {
  caseStore: new CaseStore(),      // FileStore-backed
  auditStore: new AuditStore(),    // FileStore-backed
  evidenceBundleStore: new EvidenceBundleStore(), // FileStore-backed
};
```

The `void Pool` comment in production code is the clearest possible signal that this is intentionally incomplete. D-2026-0427-012 defines the exact refactor: thin optional constructor injection with FileStore default, StoreFactory creates PgStore instances.

**Finding 6 — PgStore.find() full-table-scan is acceptable at Phase 2 scale; it is not acceptable at Phase 3 scale.**

At 7 scenarios × average 20 cases per run = 140 cases in development. At Phase 3 with live Postgres, accumulation accelerates. The `AuditStore.query()` method currently calls `this.store.list()` (fetches all audit events into memory) then applies JS filter. A platform with 10,000 audit events across 500 cases would load all 10,000 events into Node.js heap to answer a single `query({ caseId: 'x' })` call. This is a P1 regression risk at Phase 3 scale.

The correct fix (D-2026-0427-012): JSONB containment queries for equality filters (`data @> '{"status": "COMPLETED"}'::jsonb`) and explicit `WHERE` for date-range and caseId queries in AuditStore. These are standard PostgreSQL patterns; the `data JSONB NOT NULL` column design already supports them without a schema change.

**Finding 7 — The pgvector schema design is clean and follows industry standards.**

The `001_create_tables.sql` schema uses `id TEXT PRIMARY KEY, data JSONB NOT NULL`. Adding `embedding vector(1536)` to existing tables is a simple `ALTER TABLE ADD COLUMN` — the migration `003_add_embeddings.sql` is a minimal additive change. HNSW index (`m=16, ef_construction=64`) is the recommended pgvector configuration for low-latency retrieval at this corpus size.

The knowledge_chunks table design (D-2026-0427-013) correctly separates chunked document embeddings from case embeddings — these are logically distinct retrieval targets and should not be conflated.

**Finding 8 — SLAMonitor is not a stub; it is functionally complete but missing the notification output.**

After direct inspection: SLAMonitor correctly marks cases with `sla.breachedAt`, logs to audit log, and emits SLA_WARNING / SLA_BREACH audit events. What it does not do is send a Slack notification. This is a 1-2 method addition: SLAMonitor needs a Slack client injected (it currently does not accept one) and calls `client.chat.postMessage()` to the PM Agent owner's DM channel. This is genuinely S complexity.

**Finding 9 — The @testcontainers/postgresql approach is correct for live DB tests.**

`@testcontainers/postgresql` is the Node.js standard for integration testing with Postgres. It starts a Docker-based Postgres container per test suite, runs migrations, executes tests, and tears down. This is the right tool. CI requirement: Docker available in the CI environment (standard in GitHub Actions). The vitest configuration needs a `--testTimeout=60000` override for testcontainer setup time.

**Architecture Score: 23/25**

---

### 3.3 把事做正确 (Quality Gates)

**Finding 10 — Phase 3 must not repeat the Phase 2 "PgStore is tested with mocked Pool" gap.**

Phase 2 Sprint C accepted mocked pg.Pool tests as a known limitation. This was a reasonable tradeoff given Sprint C's scope. Phase 3 cannot make the same trade. The DI refactor (Sprint D) must be accompanied by real testcontainer tests that verify:
- Every domain store can save/get/list/find with real Postgres
- Migration UP runs cleanly against a real Postgres instance
- Migration DOWN restores clean state

**Finding 11 — The RAG pipeline needs failure-mode handling to preserve platform reliability.**

If OpenAI embeddings API is unavailable or OPENAI_API_KEY is not set, the PM Agent intake flow must not fail. Semantic retrieval must be optional enrichment. The acceptance criterion (D-2026-0427-013 item 9) is explicit: "application starts without it — RAG context enrichment is gracefully disabled when key is absent." This must be enforced at the Sprint E gate.

**Finding 12 — Performance SLAs must be defined and measured in Sprint D before Sprint E adds load.**

Phase 2 defined: case creation ≤ 50ms p99 (storage layer only). Phase 3 must extend this to:
- Single-entity get/save (CaseStore, AuditStore): ≤ 10ms p99
- Filtered list (CaseStore.list with filter, AuditStore.query with caseId): ≤ 50ms p99 at 10,000 rows
- pgvector similarity search (top-5): ≤ 100ms p99 at 10,000 chunks

These must be measured and recorded in Sprint D acceptance before Sprint E builds on top of them.

**Finding 13 — Test count trajectory and coverage gaps.**

Current baseline: 161 tests (27 test files). Phase 3 additions required:

| Sprint | New Tests | Target |
|--------|-----------|--------|
| Sprint D | DI wiring test, testcontainer integration suite (≥15), server-side query tests (≥8), latency benchmarks (≥3) | ≥ 187 |
| Sprint E | corpus-ingester unit (≥8), RAG retrieval integration (≥5), rubric gate tests (≥4) | ≥ 204 |
| Sprint F | Socket Mode integration (≥5), SLA alerting unit (≥4) | ≥ 213 |

Phase 3 should close at ≥ 210 tests total (161 + ~50 net new).

**Finding 14 — Pre-execution corrections (WP0 for Phase 3) assessment.**

No Phase 2 bugs require correction before Sprint D begins. The known issues are intentional deferrals, not defects:
- PgStore not wired: intentional deferral, addressed by Sprint D
- find() in-memory scan: intentional deferral, addressed by Sprint D
- No testcontainer tests: intentional deferral, addressed by Sprint D

Zero WP0 items. Phase 3 Sprint D can begin immediately on the Phase 2 Sprint C codebase (`phase2-sprint-c` branch, commit `eb990e1`).

**Quality Gates Score: 21/25**

Deduction: (-2) No concrete corpus size / quality metric defined for RAG pipeline — the acceptance criteria specify "7 files embedded" but do not specify a minimum quality gate (e.g., "top-1 retrieval for 5 test queries must match expected document"). (-2) Socket Mode test specification is underspecified in this review — "beyond nock shim" needs a concrete test design before Sprint F begins.

---

## 4. Architecture Decisions

### ADR-6: Domain Store DI — Optional Constructor Injection

**Decision:** Each domain store's constructor gains an optional `IStore<T>` parameter. When omitted, behavior is identical to Phase 2. StoreFactory in `src/index.ts` injects PgStore instances when `STORAGE_BACKEND=postgres`. See D-2026-0427-012.

Special cases:
- UserStore: two IStore<T> parameters (profileStore, dossierStore)
- AgentStore: two IStore<T> parameters (memoryStore, roleStore)
- All 161 existing tests pass without modification (they construct stores without arguments)

### ADR-7: PgStore Query Optimization — JSONB Containment

**Decision:** Add `findWhere(conditions: Record<string, unknown>): Promise<T[]>` to PgStore using JSONB containment (`data @> $1::jsonb`). Domain stores redirect their typed methods (findByStatus, findByCaseId) to this method when possible, and to explicit WHERE clauses for date-range queries. No schema changes required.

### ADR-8: pgvector RAG — text-embedding-3-small + HNSW

**Decision:** OpenAI text-embedding-3-small (1536-dim), HNSW index (m=16, ef_construction=64), direct pgvector SQL (no abstraction layer), knowledge_chunks table for document embeddings, embedding columns on cases and artifacts tables. See D-2026-0427-013.

### ADR-9: RBAC Timing — Phase 4 with Binding Trigger

**Decision:** RBAC deferred to Phase 4. Trigger conditions: first multi-workspace deployment OR explicit president requirement for submission restrictions. Existing controls (AgentRole.authorized_tools + approval-matrix.yaml) are sufficient for Phase 3. See D-2026-0427-014.

### ADR-10: SLAMonitor Alerting — Slack DM Injection

**Decision:** SLAMonitor constructor gains an optional `slackClient` parameter (WebClient from @slack/web-api). When present, SLA breach triggers `chat.postMessage` to the Slack DM channel of the case's `ownerAgent`'s human owner, using `user-bindings.json` for agent-to-human-ID lookup. Graceful degradation: if slackClient is not injected, current behavior (audit log only) is preserved.

---

## 5. Expert Panel Decisions (D-011 to D-014)

| Decision | Number | Summary | Verdict |
|----------|--------|---------|---------|
| Phase 3 scope (MoSCoW) | D-2026-0427-011 | Foundation-first (Sprint D) then RAG (Sprint E) then production hardening (Sprint F). RBAC/dashboard to Phase 4. | APPROVED |
| Domain store DI refactor approach | D-2026-0427-012 | Optional constructor injection; all 161 tests pass unchanged; StoreFactory wires PgStore when STORAGE_BACKEND=postgres | APPROVED |
| pgvector RAG implementation strategy | D-2026-0427-013 | text-embedding-3-small, HNSW index, knowledge_chunks table, case-level embeddings, semantic retrieval at PM Agent intake | APPROVED |
| RBAC timing | D-2026-0427-014 | Phase 4. Trigger: first multi-workspace deployment or explicit president submission-restriction requirement | APPROVED |

---

## 6. Phase 3 WBS

### Sprint D — Domain Store DI Refactor + Live DB Tests + Query Optimization

**Must complete before Sprint E begins.**

**Deliverables:**

WP D1 — Constructor injection for all 6 domain stores
- `src/storage/case-store.ts`: `constructor(store?: IStore<Case>)`
- `src/storage/audit-store.ts`: `constructor(store?: IStore<AuditEvent>)`
- `src/storage/artifact-store.ts` (ArtifactStore + EvidenceBundleStore): `constructor(store?: IStore<Artifact>)`, `constructor(store?: IStore<StoredEvidenceBundle>)`
- `src/storage/user-store.ts`: `constructor(profileStore?: IStore<UserProfile>, dossierStore?: IStore<...>)`
- `src/storage/agent-store.ts`: `constructor(memoryStore?: IStore<...>, roleStore?: IStore<StoredAgentRole>)`

WP D2 — StoreFactory wiring in `src/index.ts`
- `createStores()` creates Pool, instantiates PgStore<T> for each store type, passes to domain store constructors
- Removes the `void Pool` dead-code comment

WP D3 — PgStore server-side queries
- `PgStore.findWhere(conditions)`: JSONB containment query
- `CaseStore.findByStatus()` / `findByType()`: delegate to findWhere
- `AuditStore.query()`: push caseId / date-range / eventType to SQL WHERE
- `EvidenceBundleStore.findByCaseId()`: SQL WHERE on data->>'caseId'

WP D4 — Live testcontainer integration tests
- `tests/integration/pg-domain-stores.test.ts`: testcontainer Postgres, run migrations, test all 6 stores
- `tests/integration/pg-query-perf.test.ts`: insert 10,000 rows, measure p99 latency for all query patterns
- All 161 existing tests still pass (FileStore path unchanged)

WP D5 — Query performance benchmarks (recorded in `docs/perf-baselines.md`)

**Acceptance Criteria:**
1. All 161 existing tests pass (FileStore path, no changes required)
2. `STORAGE_BACKEND=postgres` with real Postgres: all domain store operations pass testcontainer tests
3. `AuditStore.query({ caseId: 'x' })` generates a SQL WHERE clause (verified by query logging in tests), not JS filter
4. Latency benchmarks recorded: p99 ≤ 10ms for get/save, ≤ 50ms for filtered list at 10,000 rows
5. `tsc --noEmit`: 0 errors
6. QA score ≥ 85/100

**Complexity:** M-L
**Dependencies:** None (starts from phase2-sprint-c, commit eb990e1)

---

### Sprint E — pgvector RAG Pipeline

**Depends on Sprint D (Postgres must be actually wired).**

**Deliverables:**

WP E1 — Schema migration 003/004
- `src/storage/migrations/003_add_embeddings.sql`: ALTER TABLE + HNSW indexes
- `src/storage/migrations/004_down_embeddings.sql`: DROP INDEX + DROP COLUMN
- Update `run-migrations.ts` to handle new migration files

WP E2 — Knowledge chunks table + ingestion pipeline
- `src/storage/migrations/003_add_embeddings.sql`: CREATE TABLE knowledge_chunks
- `src/rag/corpus-ingester.ts`: reads agent knowledge files, chunks by section boundary, calls OpenAI embeddings API, upserts to knowledge_chunks
- `npm run rag:ingest` script entry in package.json
- `src/rag/text-chunker.ts`: markdown section-boundary chunker (H2/H3 split, 512-token max, 64-token overlap)

WP E3 — Case and artifact embedding hooks
- `src/rag/case-embedder.ts`: hooks into CaseService AGENT_COMPLETED event to embed artifact content
- Case creation: embed `case.requestText`, store in `cases.embedding`

WP E4 — Semantic retrieval + PM Agent context injection
- `src/rag/retriever.ts`: `findSimilarCases(embedding, limit)` and `findRelevantChunks(embedding, limit)` — direct SQL
- `src/agents/pm-agent.ts`: at `run()` entry, call retriever to get top-5 similar cases + top-3 knowledge chunks, inject as "Relevant prior context" section in system prompt
- Graceful degradation: if OPENAI_API_KEY absent or embeddings unavailable, proceed without RAG context

WP E5 — Agent output quality rubric gate
- `agents/research-agent/review-rubric.md`: scoring rubric for research_request and data_analysis outputs
- `agents/content-agent/review-rubric.md`: scoring rubric for content_draft and decision_brief outputs
- `tests/unit/agent-rubric.test.ts`: validate rubric structure (not output quality — that requires Claude API; structure-only unit tests)

**Acceptance Criteria:**
1. `003_add_embeddings.sql` runs cleanly; `004_down_embeddings.sql` cleanly removes all vector columns/indexes
2. `npm run rag:ingest` embeds all 7+ agent knowledge files without error
3. `npm run rag:ingest` is idempotent (identical row count on second run)
4. At case intake with OPENAI_API_KEY set: PM Agent system prompt contains "Relevant prior context" section with at least 1 retrieved chunk
5. At case intake without OPENAI_API_KEY: platform starts and processes cases normally (no error)
6. Similarity search latency: < 100ms p99 for top-5 query against 10,000 knowledge_chunks (measured in testcontainer)
7. All Sprint D tests still pass (161+ tests)
8. `tsc --noEmit`: 0 errors
9. QA score ≥ 85/100

**Complexity:** L
**Dependencies:** Sprint D must be complete (PgStore must be wired end-to-end)

---

### Sprint F — Real Slack Socket Mode + SLA Alerting

**Depends on Sprint D (can run in parallel with Sprint E if resources allow).**

**Deliverables:**

WP F1 — Real Slack Socket Mode integration test
- Design: Use a lightweight mock Slack gateway (e.g., `@slack/socket-mode` with a controlled test token, or a local WebSocket server that mimics the Slack socket-mode handshake protocol)
- `tests/integration/slack-socket-mode.test.ts`: connects a real Bolt App with socket-mode transport to the mock gateway, sends a synthetic `app_mention` event, verifies that `event-handler.ts` listener fires and produces a case via CaseService
- This test is distinct from `bolt-init.test.ts` (which tests App instantiation) — it tests the full event dispatch chain with socket transport
- Gate: runs in CI with `SLACK_APP_TOKEN=xapp-test` env var pointing to mock gateway

WP F2 — SLA Slack alerting
- `src/core/sla-monitor.ts`: add optional `slackClient?: WebClient` to constructor
- When slackClient injected and SLA breach detected: call `slackClient.chat.postMessage({ channel: ownerDmChannelId, text: '...' })`
- `src/utils/agent-human-resolver.ts`: maps agentId → human Slack userId using user-bindings config (or AgentRole.ownerId field)
- `tests/unit/sla-monitor-alerting.test.ts`: verify that breach event triggers postMessage with correct channel and message text (mock slackClient)
- `src/index.ts`: inject slackClient into SLAMonitor when SLACK_BOT_TOKEN is present

**Acceptance Criteria:**
1. Socket Mode integration test passes: real Bolt App processes synthetic event through full handler chain
2. SLA breach triggers Slack DM to case owner's human user (verified by mock slackClient in unit test)
3. SLAMonitor without slackClient injection: behavior unchanged from Phase 2 (no regression)
4. All Sprint E tests still pass
5. `tsc --noEmit`: 0 errors
6. QA score ≥ 85/100

**Complexity:** M
**Dependencies:** Sprint D (for testcontainer infrastructure pattern); can overlap with Sprint E

---

### Sprint G — Conditional (Phase 4 candidate)

Web dashboard and RBAC are deferred to Phase 4 per D-2026-0427-011 and D-2026-0427-014. Sprint G is reserved but not scoped. Phase 3 delivery is Sprint D + E + F.

---

## 7. Pre-Execution Corrections (WP0)

**WP0 assessment: NONE REQUIRED.**

No Phase 2 bugs were found that block Phase 3 execution. All gaps are intentional deferrals documented in Sprint C report and D-2026-0427-008.

The `void Pool` comment in `src/index.ts` is dead code but does not cause any test or compilation failure — it is cleaned up as part of Sprint D WP D2.

**Phase 3 can begin immediately from `phase2-sprint-c`, commit `eb990e1`.**

---

## 8. Phase 3 Acceptance Criteria

The following 10 criteria define Phase 3 "done." All must pass before the Phase 3 delivery report is submitted to the president.

| # | Criterion | Sprint | Verification Method |
|---|-----------|--------|---------------------|
| AC-1 | `STORAGE_BACKEND=postgres`: all domain store operations verified against real Postgres via testcontainer (save/get/list/find for all 6 store classes) | Sprint D | `tests/integration/pg-domain-stores.test.ts` |
| AC-2 | All 161+ Phase 2 tests pass without modification (FileStore path unaffected by DI refactor) | Sprint D | `npm test` |
| AC-3 | Server-side query verification: `AuditStore.query({ caseId: 'x' })` and `CaseStore.list({ status: 'COMPLETED' })` generate SQL WHERE clauses (not JS filter) | Sprint D | Query log assertion in integration tests |
| AC-4 | Latency baselines recorded and met: p99 ≤ 10ms (single entity), ≤ 50ms (filtered list at 10,000 rows) | Sprint D | `tests/integration/pg-query-perf.test.ts` |
| AC-5 | `npm run rag:ingest` successfully embeds all agent knowledge base files; idempotent on re-run | Sprint E | `tests/unit/corpus-ingester.test.ts` + manual run |
| AC-6 | PM Agent system prompt contains retrieved context section when similar cases exist; platform starts normally without OPENAI_API_KEY | Sprint E | `tests/integration/rag-retrieval.test.ts` |
| AC-7 | Similarity search latency < 100ms p99 for top-5 query against 10,000-chunk corpus | Sprint E | Latency benchmark in testcontainer |
| AC-8 | Real Slack Socket Mode integration test: Bolt App processes synthetic event through full handler chain | Sprint F | `tests/integration/slack-socket-mode.test.ts` |
| AC-9 | SLA Slack DM alert fires when SLA is breached (verified by mock slackClient injection) | Sprint F | `tests/unit/sla-monitor-alerting.test.ts` |
| AC-10 | Phase 3 final test count ≥ 210, 0 failures, 0 tsc errors | Sprint F | `npm test && tsc --noEmit` |

---

## 9. Review Score

### Rubric

| Dimension | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Strategic alignment (做正确的事) | 25 | 23 | Scope is tightly coupled to business value. Foundation-first ordering is correct. RBAC and dashboard deferral is sound — no user story driving either. RAG is correctly timed with Phase 2's PgStore foundation. Minor deduction: no explicit metric for "how much better" RAG makes PM Agent output — the business value is asserted but not measurable at review time. |
| Architecture soundness (正确的做事) | 25 | 23 | DI refactor approach (optional constructor injection) is clean, backward-compatible, and follows the established codebase pattern. JSONB containment queries are the correct server-side filter approach for this schema design. pgvector HNSW configuration is industry-standard. Minor deduction: RAG retrieval injected at PM Agent only in Sprint E; ResearchAgent and ContentAgent do not receive context enrichment — this is acceptable for Phase 3 but should be tracked. |
| Quality gates (把事做正确) | 25 | 21 | Live testcontainer tests and performance baselines are well-defined. RAG graceful degradation is explicit. Test count trajectory is concrete. Deductions: (1) Socket Mode test design is "beyond nock shim" but the exact mock gateway approach is underspecified — needs a concrete design before Sprint F kickoff. (2) No rubric-score-gate for RAG output quality — the rubric files are created but no automated scoring of agent output against rubric. (3) Corpus quality (whether embeddings actually improve retrieval relevance) is not measured before Sprint E is declared done. |
| Phase 2 codebase readiness | 15 | 13 | Phase 2 left a clean, 0-error, 161/161 codebase. The IStore<T> interface is the right abstraction. PgStore is fully implemented. The optional-injection pattern requires zero test changes. Minor deduction: `void Pool` in production code is a code smell that signals incomplete work — while intentional, it should not have been committed to the production branch without a follow-up issue. |
| Execution plan completeness | 10 | 8 | Sprint D/E/F deliverables are file-level specific. Acceptance criteria are measurable. Dependency chain (D before E) is explicit. Deduction: Sprint F Socket Mode test needs a pre-sprint design decision on the mock gateway approach (is it a real WS server? a nock intercept? a test Slack app token?). This must be resolved at Sprint F kickoff, not left open. |

**Total: 88/100**

---

## 10. Verdict

**PASS — Phase 3 approved to execute.**

Score: **88/100** (gate threshold: 85/100, margin: +3)

**Execution sequence:**
1. Sprint D → verify AC-1 through AC-4 → Sprint E
2. Sprint E → verify AC-5 through AC-7 → Sprint F (can overlap with Sprint E)
3. Sprint F → verify AC-8 through AC-10 → Phase 3 delivery report to president

**Pre-sprint F condition:** Socket Mode test design must be finalized before Sprint F kickoff. Panel recommendation: use a minimal local WebSocket server (Node.js `ws` package) that implements the Slack socket-mode handshake protocol. This is ~50 lines of test infrastructure and avoids any dependency on real Slack credentials in CI.

**No president decision required** until Phase 3 delivery report submission.

---

## Appendix: Source Documents Reviewed

| Document | Path | Status |
|----------|------|--------|
| Phase 2 acceptance report | `obs/04-decision-knowledge/2026-04-27-Phase2-acceptance-report.md` | Read |
| Phase 2 expert review report | `obs/04-decision-knowledge/2026-04-27-Phase2-review-report.md` | Read |
| Phase 2 scope decision | `obs/04-decision-knowledge/decision-log/D-2026-0427-007.md` | Read |
| PostgreSQL migration decision | `obs/04-decision-knowledge/decision-log/D-2026-0427-008.md` | Read |
| Phase 2 Sprint C report | `obs/04-decision-knowledge/2026-04-27-Phase2-SprintC-report.md` | Read |
| Original business requirements | `Codex/Synapse-for-Codex/docs/synapse-business-scenarios-and-original-requirements.md` | Read |
| src/index.ts (codebase) | `Projects/synapse-platform/src/index.ts` | Read (head -60) |
| src/storage/case-store.ts | `Projects/synapse-platform/src/storage/case-store.ts` | Read |
| src/storage/audit-store.ts | `Projects/synapse-platform/src/storage/audit-store.ts` | Read |
| src/storage/artifact-store.ts | `Projects/synapse-platform/src/storage/artifact-store.ts` | Read |
| src/storage/pg-store.ts | `Projects/synapse-platform/src/storage/pg-store.ts` | Read |
| src/storage/user-store.ts | `Projects/synapse-platform/src/storage/user-store.ts` | Read |
| src/storage/agent-store.ts | `Projects/synapse-platform/src/storage/agent-store.ts` | Read |
| src/core/sla-monitor.ts | `Projects/synapse-platform/src/core/sla-monitor.ts` | Read |
| agents/ directory | `Projects/synapse-platform/agents/` | Listed |
| tests/ directory structure | `Projects/synapse-platform/tests/` | Listed |

*Review completed: 2026-04-27 | Expert Panel | Lysander CEO full authority (L3)*
