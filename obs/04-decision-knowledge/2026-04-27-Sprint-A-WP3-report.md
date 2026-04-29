# Sprint A WP3 Report

**Date:** 2026-04-27
**Branch:** `sprint-a-wp3`
**Commit:** `106df04`
**Base:** `sprint-a-wp2` @ `2702340`

## Summary

WP3 closes the meeting_prep E2E loop, wires Slack intake to the case pipeline,
and chops the pre-existing tsc-error backlog by 75% (24 -> 6). All 68 tests
green (up from 61/62 in WP2 baseline).

## Goals & Status

| Goal | Status |
|------|--------|
| A. meeting_prep E2E | DONE — full lifecycle test, artifact structure asserted |
| B. Slack intake wiring | DONE — handler routes DMs through classifier + CaseService, 5 tests |
| C. tsc cleanup (time-boxed) | DONE — 24 -> 6 errors, slack action/command-handler left as noted |
| D. id-generator test isolation | DONE — per-worker counter file, 62/62 fully green |

## Files Modified / Created

**New:**
- `tests/integration/meeting-prep-e2e.test.ts`
- `tests/integration/slack-intake.test.ts`

**Modified:**
- `src/integrations/slack/event-handler.ts` — exports `handleSlackMessageEvent` pure handler; routes through `IntakeClassifier` + `CaseService.createCase`; posts ack to thread; stores `slackChannel` + `slackThreadTs` in `case.metadata`.
- `src/utils/id-generator.ts` — per-worker counter file (`id-counters-w<id>.json`) via `VITEST_WORKER_ID`; mkdirSync-safe.
- `src/utils/logger.ts` — typed `Logger` interface; conditional optional fields under `exactOptionalPropertyTypes`.
- `src/core/audit-logger.ts` — omit-when-undefined assignments for `caseId` / `before` / `after` / `metadata`.
- `src/core/fsm-engine.ts` — `delete updated.blockedReason` (was `= undefined`).
- `src/core/sla-monitor.ts` — `delete this.intervalHandle` on stop.
- `src/integrations/claude/client.ts` — conditional `caseId` in log context.
- `src/storage/file-store.ts` — relaxed generic constraint to `T extends { id: string }` (drops `updatedAt` requirement; AuditEvent is immutable).
- `tests/unit/id-generator.test.ts` — uses dedicated `./test-runtime-data-idgen` dir + `rmSync` for clean isolation.

## Test Counts

| Stage | Files | Tests | Pass | Fail |
|-------|-------|-------|------|------|
| WP2 baseline | 10 | 62 | 61 | 1 (id-generator) |
| WP3 final | 12 | 68 | 68 | 0 |

Net delta: +6 new tests (1 meeting_prep E2E, 5 slack-intake), 1 pre-existing flake fixed.

## tsc Errors

| Stage | Count |
|-------|-------|
| WP2 baseline | 24 |
| WP3 final | 6 |

**Cleared (18):** `logger.ts` (8), `audit-logger.ts` (3), `audit-store.ts` (2),
`fsm-engine.ts` (1), `sla-monitor.ts` (1), `claude/client.ts` (1),
`slack/event-handler.ts` (1), `id-generator.ts` (impacted 1).

**Remaining (6) — all in slack action/command-handler:**
- `slack/action-handler.ts` (3): Bolt `BlockAction` payload narrowing for `body.user.id` and `body.container.channel_id` — needs proper type guards rather than the current `as` casts. Non-trivial; left for a focused pass.
- `slack/command-handler.ts` (3): `ChatPostMessageArguments` overlap + `metadata.event_payload` shape mismatch with Slack's strict type; also a duplicate `channel` key warning. Same Bolt-typing class of issue.

These do not block runtime — Slack tests pass and command-handler runs in WP2.

## Slack Wiring Test Result

`tests/integration/slack-intake.test.ts` — 5/5 passing:

1. weekly_report DM -> CaseType.WEEKLY_REPORT case + thread ack
2. meeting_prep DM -> CaseType.MEETING_PREP case + thread ack
3. classifier returns null -> CaseType.INTERNAL_SERVICE with `needs-routing` tag
4. unauthorized user -> ignored, no case, no post
5. bot subtype message -> ignored, classifier never called

The pure `handleSlackMessageEvent` is what the tests exercise. The Bolt `registerEventHandlers` wrapper that wires `app.message` calls into the pure handler is NOT unit-tested — verifying it requires either booting Bolt in socket mode against a fake Slack or refactoring to inject a Bolt-style mock. Documented as a follow-up; the unit layer covers the actual logic.

## meeting_prep E2E Test Result

`tests/integration/meeting-prep-e2e.test.ts` — 1/1 passing.

Asserts:
- INTAKE -> TRIAGED -> PLANNED -> IN_PROGRESS -> AWAITING_REVIEW -> AWAITING_APPROVAL -> COMPLETED -> ARCHIVED
- PMAgent loads playbook + template + profile + memory + KB; `extraSystemBlocks` length >= 2; blocks include `meeting-prep`, `Output Template`, `Execution Playbook`
- Artifact persisted as DRAFT with RACI (Decider/Consulted/Informed/Responsible) + Agenda + SCQA
- EvidenceBundle saved
- Audit trail covers CASE_CREATED / AGENT_INVOKED / AGENT_COMPLETED / CASE_COMPLETED
- Cache-token metric (1700) round-trips into artifact metadata

## Honest Gaps Remaining for WP4

- **service_request E2E** — not built, this is WP4 scope.
- **Slack Bolt-end live verification** — `registerEventHandlers` wiring is covered only at the pure-handler layer. A real Bolt socket-mode boot test (or a richer Bolt mock) would catch wiring-layer regressions; the unit test does not.
- **6 residual tsc errors** in slack action/command-handler. Should be resolved before any production Slack interaction reaches users — they signal real type-safety gaps in payload extraction.
- **AuditEvent loses `updatedAt` constraint** in FileStore — fine because AuditEvent is append-only, but worth a follow-up if a future store backend cares about it.
- **OrchestratorAgent.processRequest** still hard-codes the `ownerAgent` override and bypasses `CaseService.updateCase` for it — comment in code acknowledges this, not addressed in WP3.

## WP4 Preview (5 lines)

1. service_request E2E test mirroring weekly_report / meeting_prep.
2. Build a `ServiceRequestAgent` (or extend PMAgent) for INTERNAL_SERVICE / RESEARCH_REQUEST routing.
3. Close the 6 slack-handler tsc errors with proper Bolt payload narrowing.
4. Add an integration smoke test that boots Bolt in mocked socket mode and verifies the `app.message` -> `handleSlackMessageEvent` wiring end-to-end.
5. Begin SLA monitor evidence path: persist breach events to AuditStore so the approval gate sees real SLA history.