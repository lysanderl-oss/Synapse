# Synapse Digital Twin Platform — Phase 4 Expert Panel Review Report

- **Date:** 2026-04-28
- **Review Panel:** product_strategist · think_tank (decision_advisor + execution_auditor) · harness_engineer · integration_qa · knowledge_engineer
- **Decision Authority:** Lysander (AI CEO) + Expert Panel — full decision authority, no president approval required
- **Decision Records:** D-2026-0428-016 · D-2026-0428-017 · D-2026-0428-018 · D-2026-0428-019
- **Baseline:** Phase 3 acceptance report D-015 (91/100, PASS), commit `0d24c15`, branch `phase3-sprint-f`

---

## 1. Executive Summary

**Phase 4 is CLEARED TO START. Readiness score: 90/100. Verdict: PASS.**

Phase 3 closed with 91/100, all 9 Must-Have items delivered, 216/216 tests passing, 0 tsc errors. The structural foundation — PgStore DI, server-side queries, pgvector RAG, SLA alerting, Socket Mode protocol simulation — is complete and sound.

Phase 4 is defined by a single transformative new fact: **real Slack credentials for janussandbox.slack.com are now in hand.** This makes Phase 4 the first phase with genuine production integration. Sprint G's mission is to exercise that integration fully and establish a live E2E test baseline before any further feature work begins.

The four panel decisions are:
- **D-016:** Phase 4 scope = 4 Must-Have items (real Slack E2E, pgvector productionization, PgStore predicate completion, SLA warning DMs). No RBAC, no web dashboard.
- **D-017:** Slack-native slash commands replace web dashboard proposal. D-011 trigger condition not met.
- **D-018:** RBAC deferred to Phase 5. All three D-014 trigger conditions remain unmet.
- **D-019:** chokidar file watcher as primary corpus re-ingestion trigger; cross-agent retrieval added in same sprint.

Phase 4 carries higher integration risk than Phases 1–3 because Sprint G introduces real network calls to external Slack infrastructure. This is accounted for in the WP0 pre-execution checklist and the Sprint G E2E test guard design (`RUN_SLACK_E2E=true` — not run in CI, run in staging/dev).

---

## 2. Phase 4 Scope (MoSCoW)

| # | Item | Priority | Sprint | Complexity |
|---|------|----------|--------|------------|
| M1 | Real Slack Socket Mode E2E test — `tests/e2e/slack-e2e.test.ts`, actual `app.start()` with real SLACK_APP_TOKEN, live bot on janussandbox.slack.com, synthetic message dispatch + bot response verification | Must | G | M |
| M2 | pgvector corpus pipeline productionization — `chokidar` file watcher for incremental re-ingestion + cross-agent retrieval (`retrieveFromAllCorpora`) | Must | H | M |
| M3 | PgStore complex predicate completion — JSONB path queries for UserStore and AgentStore (remaining 2 of 6 domain stores still doing in-memory filter) | Must | H | S |
| M4 | SLA warning DMs — pre-breach Slack DM at configurable threshold (default: 30 min before deadline) in `src/core/sla-monitor.ts` | Must | H | S |
| S1 | Slack-native case reporting — `/case-status [caseId]` and `/cases-active` slash commands with Block Kit structured responses | Should | I | M |
| S2 | RAG system-prompt injection assertion — resolve Vitest OpenAI ESM mock limitation for direct system-prompt content verification | Should | I | S |
| S3 | Query performance baseline benchmarks — latency at 1000+ case scale via live testcontainer (D-011 deferred Should) | Should | I | S |
| C1 | RAG recall quality quantification — golden-set eval pipeline (precision / recall / MRR) | Could | J | M |
| C2 | Agent rubric gate as CI check — integrate `review-rubric.md` assertions as blocking acceptance gate | Could | J | S |
| C3 | RBAC design specification document (no code) — pre-work for Phase 5 | Could | J | S |
| W1 | RBAC / PermissionGate implementation | Won't | Phase 5 | L |
| W2 | Web dashboard (any standalone UI framework) | Won't | Phase 5+ | XL |
| W3 | Multi-tenant Slack workspace support | Won't | Phase 5 | L |
| W4 | Cross-org multi-agent handoff | Won't | Phase 5+ | XL |

---

## 3. 三原则 Review

### 做正确的事 (Strategic Alignment)

**Real Slack E2E is Phase 4's highest-value quick win.** The tokens are in hand. The architectural gap is precisely identified: `app.start()` was never called in any test; Bolt's actual WS connection to `api.slack.com`, token validation, and event signature verification have never been exercised. Sprint G closes this with a single, well-scoped test file. Estimated effort: 1 sprint. Risk if deferred: the platform could ship Phase 5 features without ever having validated the foundational Slack connection at production level.

**RBAC trigger conditions are not met (D-018 confirms).** The platform is single-workspace, single-tenant. The `approval-matrix.yaml` already implements role-based approval authority (the highest-value RBAC concern). Building a `PermissionGate` now for a multi-tenant scenario that has not been scheduled is pure speculative complexity. D-014 trigger conditions stand unchanged.

**Slack-native reporting is the correct visibility surface (D-017).** The D-011 trigger condition for a web dashboard (external demo or non-Slack stakeholder reporting requirement) has not been met. A Slack slash command (`/case-status`, `/cases-active`) uses existing infrastructure (command-handler.ts, message-builder.ts, PgStore) to answer the same operational question. Zero new infrastructure, zero new maintenance surface.

**pgvector productionization closes a real production reliability gap.** Manual `rag:ingest` is a single-point-of-human-failure. When a PM Agent playbook is updated and no one remembers to re-ingest, the RAG context silently becomes stale. The chokidar file watcher eliminates this failure mode with minimal code and a proven dependency.

**Business scenario coverage is complete.** Reviewing the original requirements (7 business dimensions from `synapse-business-scenarios-and-original-requirements.md`): all 7 scenarios from D-011 are implemented and covered by Phase 3's acceptance suite. No uncovered business scenario has been identified that requires a new agent type in Phase 4. Phase 4 is a hardening and reliability phase, not a feature-expansion phase.

**SLA warning DMs address a real operational gap.** Breach-only alerts are reactive. A 30-minute pre-breach warning gives the PM Agent owner (Lysander Liu) time to intervene or escalate. The SLAMonitor architecture already has injectable WebClient and configurable thresholds — this is an S-complexity extension.

### 正确的做事 (Architecture Correctness)

**Real Slack E2E test architecture:**

```
tests/
  e2e/                          ← NEW directory convention (Phase 4)
    slack-e2e.test.ts           ← SLACK_APP_TOKEN live connection test
    README.md                   ← How to run: RUN_SLACK_E2E=true npm run test:e2e
```

Guard pattern:
```typescript
const RUN_E2E = process.env['RUN_SLACK_E2E'] === 'true';
describe.skipIf(!RUN_E2E)('Slack E2E — live janussandbox.slack.com', () => { ... });
```

The test must:
1. Call `app.start()` with real `SLACK_APP_TOKEN` from `.env` (not hardcoded — tokens in `.env`, `.env.example` updated)
2. Verify the WebSocket connection to `api.slack.com` is established (listen for `app.started` event or poll connection state)
3. Use the Slack Web API (`app.client.chat.postMessage`) to post a test message to a designated `#bot-test` channel
4. Verify bot receives the message event (via Bolt's `app.message()` handler)
5. Assert the message body matches
6. Cleanup: delete the test message, `app.stop()`

Tokens are read from environment — NEVER hardcoded in source. The `.env.example` entry uses placeholder values. The real tokens live in `.env` (gitignored).

**chokidar file watcher architecture:**

```typescript
// src/rag/corpus-watcher.ts
export function startCorpusWatcher(ingester: CorpusIngester, watchPath: string): FSWatcher
```

Integrated into `src/index.ts` behind `ENABLE_CORPUS_WATCHER=true` guard. The watcher calls `ingester.ingestFile(filePath)` (new method on `CorpusIngester`) rather than `ingestAll()`, keeping the change incremental.

**Cross-agent retrieval:**

```typescript
// src/rag/semantic-retriever.ts — new method
async retrieveFromAllCorpora(query: string, topK: number, excludeAgentId?: string): Promise<KnowledgeChunk[]>
```

SQL: removes `WHERE agent_id = $1` filter, optionally adds `WHERE agent_id != $1` for self-exclusion. The orchestrator can use this for broad cross-domain context enrichment.

**PgStore UserStore/AgentStore predicates:** Follow the existing `findByField` / `findByJsonPath` pattern established in Phase 3 for CaseStore/AuditStore. No new architectural patterns — completing the existing pattern.

**SLA warning DMs:** Add `warnThresholdMinutes: number` (default 30) to `SLAMonitorDeps`. SLAMonitor checks `now > deadline - threshold` independently of `now > deadline`. Two separate Slack DM calls with distinct message templates.

### 把事做正确 (Quality Gates and Acceptance Criteria)

Phase 4 acceptance criteria are defined in Section 8. Key quality gate additions vs Phase 3:
- E2E tests are gated by `RUN_SLACK_E2E=true` — they are NEVER run in CI automatically; they are run manually in a staging environment with real tokens
- Live Slack E2E test must not leave orphaned messages in the workspace (cleanup is a required step in the test)
- All Slack tokens must be sourced from environment variables in all code paths — the review panel will explicitly verify no token appears as a string literal in any source or test file

---

## 4. Architecture Decisions

### 4.1 `tests/e2e/` Directory Convention

Phase 4 establishes `tests/e2e/` as the directory for tests that require live external services. Conventions:
- Files named `[service]-e2e.test.ts`
- Each test file must have a guard env var (`RUN_[SERVICE]_E2E=true`)
- A `tests/e2e/README.md` documents required env vars and expected external service state
- These tests are excluded from the default `npm test` run (vitest config: `exclude: ['tests/e2e/**']`)
- A separate script `npm run test:e2e` runs them with `RUN_SLACK_E2E=true`

### 4.2 Token Security Contract

All Slack tokens (SLACK_APP_TOKEN, SLACK_BOT_TOKEN) must:
- Be read from `process.env` (via `getConfig()` or direct env read)
- Appear only in `.env` (gitignored) and `.env.example` (with placeholder values)
- Never appear as string literals in any `.ts`, `.test.ts`, or `.md` file in the repository
- The Phase 3 Sprint F report and current conversation contain the real tokens for reference only — they must not be committed

### 4.3 Corpus Watcher Lifecycle

The corpus watcher is a long-running background process. In `src/index.ts`:
```typescript
if (process.env['ENABLE_CORPUS_WATCHER'] === 'true') {
  const watcher = startCorpusWatcher(corpusIngester, './agents');
  process.on('SIGTERM', () => watcher.close());
  process.on('SIGINT', () => watcher.close());
}
```

SIGTERM/SIGINT handlers ensure the watcher is closed cleanly on process exit.

---

## 5. Expert Panel Decisions Summary

| Decision | ID | Verdict |
|----------|----|---------|
| Phase 4 scope MoSCoW | D-2026-0428-016 | 4 Must-Have (Slack E2E, pgvector prod, PgStore completion, SLA warning); RBAC + dashboard = Won't |
| Web dashboard vs Slack-native reporting | D-2026-0428-017 | Slack-native slash commands; D-011 trigger condition not met; web dashboard = Won't Phase 4 |
| RBAC scope | D-2026-0428-018 | Phase 5 (or later); all three D-014 trigger conditions unmet; design spec = Could-Have Sprint J |
| pgvector corpus ingestion trigger | D-2026-0428-019 | chokidar file watcher (Option B) + cross-agent retrieval; manual CLI retained as fallback |

---

## 6. Phase 4 WBS

### Sprint G — Real Slack Socket Mode E2E
**Theme:** Close the last Phase 3 production-confidence gap with live Slack integration.

| Deliverable | Detail | Acceptance Criteria |
|-------------|--------|---------------------|
| `tests/e2e/` directory + `README.md` | Establish e2e test convention; document `RUN_SLACK_E2E=true npm run test:e2e` | Directory exists; README covers required env vars and bot-test channel setup |
| `tests/e2e/slack-e2e.test.ts` | Live `app.start()` against janussandbox.slack.com; post test message via `chat.postMessage`; verify bot receives event; cleanup | Test passes with real tokens; no orphaned messages after test run; test is skipped when `RUN_SLACK_E2E` is unset |
| `.env.example` update | Add `SLACK_APP_TOKEN` and `SLACK_BOT_TOKEN` as named variables with `xapp-` / `xoxb-` placeholder prefixes; confirm SLA_ALERT_USER_ID is present | `.env.example` reflects all required env vars |
| `vitest.config.ts` update | Add `tests/e2e/**` to exclude list; add `test:e2e` script to `package.json` | `npm test` does not run e2e tests; `npm run test:e2e` runs them |

**Dependencies:** Real tokens in `.env` (available). janussandbox.slack.com workspace with bot installed and `#bot-test` channel created.
**Complexity:** M
**All existing tests must continue to pass (216/216 baseline)**

---

### Sprint H — Pipeline + Queries + SLA Warning
**Theme:** Complete the production reliability layer — no more manual steps, no more in-memory filters, no more reactive-only alerting.

| Deliverable | Detail | Acceptance Criteria |
|-------------|--------|---------------------|
| `src/rag/corpus-watcher.ts` | chokidar watcher on `./agents/` watching `**/*.md` and `**/*.json`; 2000ms debounce; calls `ingester.ingestFile(path)` on change; logs `corpus_watcher.file_changed` audit event | Unit tests: file add → ingestFile called; file change → ingestFile called; unlink → deleteChunks called; guard: watcher not started when `ENABLE_CORPUS_WATCHER` is unset |
| `CorpusIngester.ingestFile(path)` | New method: incremental upsert for single file (idempotent, same agent_id+source_file+chunk_index logic as `ingestAll`) | Unit test: single file ingestion creates correct chunks; re-ingestion upserts (no duplicates) |
| `SemanticRetriever.retrieveFromAllCorpora(query, topK)` | Cross-corpus retrieval without agent_id filter; optional `excludeAgentId` param | Unit test: returns chunks from multiple agents; respects topK; excludeAgentId works |
| `src/index.ts` corpus watcher integration | Watcher started when `ENABLE_CORPUS_WATCHER=true`; SIGTERM/SIGINT cleanup | Integration test: watcher lifecycle |
| PgStore UserStore JSONB predicate queries | `findByField` and `findByJsonPath` for UserStore replacing JS in-memory filter | Unit test: server-side WHERE verified (no full table scan); existing UserStore tests pass |
| PgStore AgentStore JSONB predicate queries | Same as UserStore | Unit test: server-side WHERE verified; existing AgentStore tests pass |
| SLA warning DMs | `warnThresholdMinutes` in `SLAMonitorDeps` (default 30); pre-breach DM distinct from breach DM | Unit tests: warning DM sent at threshold; breach DM sent on breach; no double-fire; graceful degradation if no slackClient |
| `.env.example` update | Add `ENABLE_CORPUS_WATCHER=false` | Documented in env reference table |

**Dependencies:** Sprint G must pass (baseline tests at 216+).
**Complexity:** M (corpus watcher + cross-retrieval), S (PgStore predicates), S (SLA warning)

---

### Sprint I — Slash Commands + Test Quality Debt
**Theme:** Operational visibility via Slack-native reporting; close Phase 3 test quality gaps.

| Deliverable | Detail | Acceptance Criteria |
|-------------|--------|---------------------|
| `/case-status [caseId]` command | Extends `src/integrations/slack/command-handler.ts`; queries IStore<T> for case + artifacts + audit tail + SLA status; returns Block Kit message | Unit test: Block Kit message structure; integration test: real case data returned; graceful: case not found → clear error message |
| `/cases-active` command | Returns paginated list (≤10) of open cases with FSM state + SLA indicator; "Load more" overflow action | Unit test: pagination logic; empty state handled |
| RAG injection assertion | Resolve Vitest OpenAI ESM mock limitation; assert `Relevant knowledge retrieved` block in PM Agent system prompt during full case flow | Test passes without `--force-exit`; assertion is inline, not degradation-path only |
| Query performance baseline | `tests/integration/pg-store-benchmarks.test.ts` via live testcontainer; measures p50/p95 latency for all 6 domain stores at 1000-case scale | Benchmark report written to `tests/integration/pg-store-benchmarks-results.json`; p95 < 100ms for single-entity lookup |

**Dependencies:** Sprint H complete.
**Complexity:** M (slash commands), S (RAG assertion), S (benchmarks)

---

### Sprint J — Polish + Phase 4 Acceptance Suite
**Theme:** Production polish, Phase 4 acceptance test suite, optional Could-Have items.

| Deliverable | Detail | Acceptance Criteria |
|-------------|--------|---------------------|
| `tests/acceptance/phase4.test.ts` | Phase 4 acceptance suite: E2E guard-gated Slack test invocation reference, corpus watcher integration, cross-corpus retrieval, warning DM, slash command responses | Suite passes; all assertions against real Phase 4 behavior |
| README update | Phase 4 section: e2e test instructions, corpus watcher usage, slash commands, new env vars | README accurate and complete |
| (Could) RAG golden-set eval | 20-item golden set against PM Agent knowledge; measure precision@5 | Eval script runnable; baseline metrics recorded |
| (Could) RBAC design spec | `docs/phase5-rbac-design.md` — role taxonomy, PermissionGate interface, migration DDL, test matrix | Doc reviewed by harness_engineer; no code committed |
| Phase 4 acceptance score | Panel scores Phase 4 delivery ≥85/100 | PASS |

**Dependencies:** Sprints G+H+I complete.
**Complexity:** S-M

---

## 7. Pre-Execution Corrections (WP0)

The following must be addressed before Sprint G begins. None are blockers to starting Sprint G planning, but items 1-3 must be complete before `npm run test:e2e` is first attempted.

| # | Issue | File | Required Action | Severity |
|---|-------|------|-----------------|----------|
| WP0-1 | `.env.example` does not reflect the SLACK_APP_TOKEN / SLACK_BOT_TOKEN variable names that the E2E test will require (current `.env.example` uses the correct names `SLACK_APP_TOKEN` / `SLACK_BOT_TOKEN` as confirmed in codebase inspection — **this item is pre-verified CLEAR**) | `.env.example` | No action needed — names already correct | N/A (clear) |
| WP0-2 | `src/utils/config.ts` validates `SLACK_APP_TOKEN` must start with `xapp-` and `SLACK_BOT_TOKEN` must start with `xoxb-`. The real tokens match these prefixes — **this item is pre-verified CLEAR** | `src/utils/config.ts` | No action needed | N/A (clear) |
| WP0-3 | `tests/e2e/` directory does not exist. Must be created with `vitest.config.ts` exclude rule and `package.json` `test:e2e` script BEFORE Sprint G test is written | `vitest.config.ts`, `package.json` | Create directory; add exclude; add script | P1 (Sprint G day 1) |
| WP0-4 | `SLA_ALERT_USER_ID` in `.env.example` currently shows `U0XXXXXXXX` placeholder. The real UID is `U0ASLJZMVDE`. Ensure developer `.env` has the real UID before Sprint H SLA DM tests are run | `.env` (developer) | Update local `.env` with `SLA_ALERT_USER_ID=U0ASLJZMVDE` | P2 (Sprint H pre-requisite) |
| WP0-5 | `chokidar` must be confirmed as a package.json dependency before Sprint H. Check whether it's present; add if absent. | `package.json` | Verify or add `chokidar` and `@types/chokidar` | P1 (Sprint H day 1) |
| WP0-6 | `tests/e2e/README.md` must document: required `#bot-test` channel in janussandbox.slack.com, bot must be invited to that channel, tokens must be set in `.env`. This pre-condition must be met before Sprint G E2E test is run. | `tests/e2e/README.md` | Write README as first Sprint G act | P1 (Sprint G day 1) |

**Security note:** The real Slack tokens (SLACK_APP_TOKEN, SLACK_BOT_TOKEN) must be placed in the developer's local `.env` file only. They must never appear in any committed file. The tokens provided in this review session are for reference; they must be transferred to `.env` by the developer before Sprint G E2E testing.

---

## 8. Phase 4 Acceptance Criteria

| # | Criterion | Measurement Method |
|---|-----------|-------------------|
| AC-1 | Real Slack Socket Mode E2E test passes: `app.start()` connects to janussandbox.slack.com, bot receives synthetic message event, bot posts response, test cleans up | `RUN_SLACK_E2E=true npm run test:e2e` exits 0; no orphaned messages in `#bot-test` |
| AC-2 | Corpus file watcher auto-re-ingests on KB file change: modify a `.md` file under `agents/`; within 5 seconds the updated chunk is retrievable via semantic search | Manual verification with `ENABLE_CORPUS_WATCHER=true`; query returns updated content |
| AC-3 | Cross-agent corpus retrieval works: ContentAgent retrieves chunks from PMAgent corpus when using `retrieveFromAllCorpora` | Unit test in Sprint H passes; integration test demonstrates cross-agent chunk retrieval |
| AC-4 | All 6 domain stores use server-side WHERE queries (no in-memory JS filter for any typed query on PgStore backend) | Code review: `pg-store.ts` UserStore and AgentStore methods use SQL parameterized queries; no `.filter()` post-fetch |
| AC-5 | SLA warning DM sent at configurable pre-breach threshold: case approaching SLA deadline triggers DM to `SLA_ALERT_USER_ID` before breach | Unit test (4 new tests): warning fires at threshold; breach fires at deadline; no double-fire; graceful degradation |
| AC-6 | `/case-status [caseId]` returns correct Block Kit message with FSM state, artifact count, and SLA status for any active case | Integration test: command called with known caseId returns structured message with correct fields |
| AC-7 | All existing 216 tests continue to pass (zero regression) | `npm test` exits 0 with ≥216 tests passing |
| AC-8 | tsc compilation: 0 errors across all source and test files | `npx tsc --noEmit` exits 0 |
| AC-9 | No Slack token string literal appears in any committed file: all tokens read from `process.env` | `grep -r "xapp-1-" src/ tests/` returns 0 results; `grep -r "xoxb-" src/ tests/` returns 0 results |
| AC-10 | Phase 4 acceptance test suite (`tests/acceptance/phase4.test.ts`) passes, covering: corpus watcher behavior, cross-corpus retrieval, SLA warning DM, slash command structure | Suite exits 0 as part of `npm test` |

---

## 9. Review Score

| Dimension | Weight | Score | Rationale |
|-----------|--------|-------|-----------|
| Strategic alignment (做正确的事) | 25 | 23 | Slack E2E is correctly the highest-value Phase 4 item (tokens now available, closes last Phase 3 production gap). Dashboard and RBAC correctly deferred (trigger conditions not met). Slack-native reporting is the right visibility surface for current deployment scale. Deduction 2: cross-agent corpus retrieval could have been Phase 3 (architectural gap accepted at 91/100 instead of being a Must-Have); now correctly prioritized as Phase 4 Must-Have. |
| Architecture correctness (正确的做事) | 25 | 23 | E2E test architecture (tests/e2e/, RUN_SLACK_E2E guard, cleanup contract) is correct and production-safe. chokidar file watcher is the right mechanism for current deployment topology. Token security contract is explicit and enforceable. Deduction 2: no RBAC design work is done in Phases 1-4, meaning if Phase 5 RBAC is needed urgently, there's no pre-existing interface design to build from (mitigated by Could-Have RBAC spec in Sprint J). |
| Quality gates (把事做正确) | 20 | 18 | 10 acceptance criteria are specific and measurable. E2E token security check (AC-9: grep for literal tokens) is a novel, non-trivial acceptance gate. The vitest ESM mock gap (RAG system-prompt assertion) is explicitly targeted in Sprint I. Deduction 2: performance benchmark (S3) remains a Should not a Must — if testcontainer is still unavailable due to Docker constraints, this defers again. |
| Risk assessment | 15 | 13 | Phase 4 carries genuine production integration risk (live Slack calls) for the first time. The risk is well-managed: E2E tests are gated and non-CI, cleanup is mandatory, tokens are env-only. Deduction 2: bot must be pre-installed in janussandbox.slack.com workspace and `#bot-test` channel must exist — this is an external dependency the codebase cannot enforce, creating a setup gap risk for Sprint G day 1. |
| WBS completeness | 15 | 13 | Sprint structure G/H/I/J is logical, sequentially dependent (E2E first, then pipeline, then reporting, then polish). Each sprint has clear deliverables and acceptance criteria. Deduction 2: Sprint J Could-Have items (RAG golden-set eval, RBAC spec) have no explicit time-box, making them prone to scope creep or complete deferral. |

**Total: 90/100**

---

## 10. Verdict

**PASS. Phase 4 review score: 90/100 (gate: ≥85).**

Phase 4 is cleared to start. Sprint G begins with two immediate pre-conditions:
1. Developer creates `tests/e2e/` directory with vitest exclude rule and `test:e2e` script
2. Developer writes `tests/e2e/README.md` documenting the bot-install and `#bot-test` channel pre-condition
3. Developer updates local `.env` with real `SLACK_APP_TOKEN`, `SLACK_BOT_TOKEN`, and `SLA_ALERT_USER_ID=U0ASLJZMVDE`

All decisions are binding. RBAC and web dashboard are Phase 5 (with explicit trigger conditions). Slack-native slash commands are Phase 4 Should. Real Slack E2E is Phase 4 Must-Have Sprint G.

---

## Appendix: Decision Chain

```
D-004 (strategic approval)
  → D-005 (P0 correction)
    → D-006 (Phase 1 delivery)
      → D-007 (Phase 2 scope)
        → D-008 (PG adapter)
          → D-009 (ResearchAgent + ContentAgent)
            → D-010 (Phase 2 delivery)
              → D-011 (Phase 3 scope)
                → D-012 (DI refactor)
                  → D-013 (pgvector RAG strategy)
                    → D-014 (RBAC deferral)
                      → D-015 (Phase 3 delivery — 91/100 PASS)
                        → D-016 (Phase 4 scope) ← this report
                        → D-017 (dashboard vs Slack-native) ← this report
                        → D-018 (RBAC Phase 4 or 5?) ← this report
                        → D-019 (corpus ingestion trigger) ← this report
```

*Report completed: 2026-04-28 | Expert Panel: product_strategist · think_tank · harness_engineer · integration_qa · knowledge_engineer | Lysander CEO full decision authority*
