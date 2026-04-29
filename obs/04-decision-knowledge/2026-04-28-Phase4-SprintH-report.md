# Phase 4 Sprint H — Delivery Report

**Date:** 2026-04-28
**Commit:** adb9d331
**Branch:** phase4-sprint-h (base: phase4-sprint-g @ df06952)

---

## Summary

Sprint H delivered all 4 goals on a single commit. Test count grew from 216 to 236 (unit pass rate 100%). E2E bot-ack test (Test 3) now passes against real Slack (janussandbox.slack.com). tsc: 0 errors.

---

## Goal A: Bot-ack E2E (Test 3) — COMPLETE

**File:** tests/e2e/slack-live.test.ts

Test 3 upgraded from a transport-only stub to a full ack assertion.
Strategy: call handleSlackMessageEvent() directly with a mocked IntakeClassifier that returns a fixed WEEKLY_REPORT classification. No ANTHROPIC_API_KEY required.
- The mocked post function captures the ack text and mirrors it to the real Slack channel.
- Assertions: result.status classified, result.case.id matches /^CASE-/, ack text contains "new case" (case-insensitive) or CASE-.

**E2E run result:** 4/4 tests passed. Bot created CASE-20260428-0002 (weekly_report), posted "New case: Weekly report draft: [test]" to channel C0AV1JAHZHB.

---

## Goal B: pgvector Corpus File Watcher — COMPLETE

**New file:** src/rag/corpus-watcher.ts
**Updated:** src/rag/semantic-retriever.ts, src/index.ts

- startCorpusWatcher(agentsDir, pool) watches agents/**/*.{md,json} with chokidar.
- 2000ms debounce per file path; calls ingestAgentCorpus(agentId, agentsDir, pool).
- Guards: ENABLE_CORPUS_WATCHER=true AND pool != null.
- Cross-platform path handling via path.sep (no backslash regex).
- .env.example updated: ENABLE_CORPUS_WATCHER=false, AGENTS_DIR=agents, SLA_WARNING_MINUTES=30.

**Cross-agent retrieval:** retrieveContext() accepts optional agentIds?: string[].
- omitted -> single-agent (backward-compatible)
- [] -> search ALL agents
- ["pm-agent", "research-agent"] -> filtered multi-agent

**Tests:** tests/unit/corpus-watcher.test.ts (7 tests, vi.hoisted mocks, fake timers)

---

## Goal C: PgStore Server-side Queries — COMPLETE

**Updated:** src/storage/user-store.ts, src/storage/agent-store.ts

Same hasFindByField() pattern as CaseStore. New server-side methods:
- UserStore.findBySlackId(slackId) -> findByField("slackUserId", slackId)
- AgentStore.findByAgentId(agentId) -> findByField("agentId", agentId)
- AgentStore.findByStatus(active) -> findByField("active", active)

FileStore fallback preserved via type-guard.

**Tests:** tests/unit/store-pgfield.test.ts (7 tests, mocked PgStore + FileStore stubs)

---

## Goal D: SLA Pre-breach Warning DMs — COMPLETE

**Updated:** src/core/sla-monitor.ts

New: warnThresholdMinutes (from SLA_WARNING_MINUTES, default 30), warnedCaseIds Set.
New: notifySlackWarning() posts warning DM with format:
  Warning text: "SLA Warning — Case {id} ({type}) / SLA deadline in {N} min | Status: {status}"

Dedup: each case warned at most once per SLAMonitor lifecycle.
Existing fraction-based warning and breach DM path are unchanged.

**Tests:** tests/unit/sla-monitor-warning.test.ts (5 tests)
- Warning fires at 29 min
- No warning at 31 min
- No double-warning (dedup)
- Breach DM fires at 0 min (existing behavior intact)
- Warning but not breach at 15 min

---

## Test Metrics

| Metric | Before | After |
|--------|--------|-------|
| Unit tests | 216 | 236 |
| tsc errors | 0 | 0 |
| E2E tests | 3/4 (Test 3 partial) | 4/4 (Test 3 full ack) |

New test files: corpus-watcher.test.ts (+7), sla-monitor-warning.test.ts (+5), store-pgfield.test.ts (+7)
Modified: sla-monitor.test.ts (fraction-warning case changed 0.5h -> 0.75h remaining to avoid pre-breach intercept)

---

## Cross-agent Retrieval Design Note

The agentIds parameter is optional and additive (no existing callers affected).
Use case: PM Agent retrieves from ResearchAgent corpus:
  retrieveContext(query, "pm-agent", pool, 5, ["pm-agent", "research-agent"])
Empty array ([]) queries all agents with no agent_id WHERE clause.

---

## Sprint I Readiness

Recommended next goals:
1. Knowledge re-ingestion on boot (diff knowledge_chunks vs agents/ files)
2. CorpusWatcher.close() wired to graceful shutdown signal handler
3. SLA_WARNING_MINUTES per-case-type override
4. E2E Test 3 upgrade: real user-token Slack send + conversations.history poll for full transport validation