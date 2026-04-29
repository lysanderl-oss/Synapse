# Sprint A WP4 Report — Synapse Platform Phase 1 Closeout

**Date:** 2026-04-27
**Branch:** `sprint-a-wp4`
**Commit:** `14c359a`
**Baseline (WP3):** `106df04` — 68/68 tests, 6 tsc errors

## Headline

- **Tests:** 68 → **83** passing (+15)
- **tsc errors:** 6 → **0**
- **Phase 1 scope (3 scenarios):** all delivered and acceptance-tested

## Files Modified / Created

**New:**
- `src/agents/service-agent.ts` — ServiceAgent (`agent.ops`) for internal_service
- `agents/service-agent/playbooks/service-request.md` — ITIL-flavored playbook
- `agents/service-agent/templates/service-request.md` — ticket output template
- `tests/integration/service-request-e2e.test.ts` — Goal A
- `tests/integration/bolt-wiring.test.ts` — Goal B
- `tests/integration/approval-action.test.ts` — Goal C
- `tests/acceptance/phase1.test.ts` — Goal E

**Modified:**
- `src/agents/intake-classifier.ts` — added `detectServiceRequestSignal` keyword pre-check
- `src/core/sla-monitor.ts` — fix tsc TS2352 via `unknown` cast
- `src/integrations/slack/action-handler.ts` — narrow envelopeId, fix container cast, add delivery postMessage
- `src/integrations/slack/command-handler.ts` — fix duplicate `channel` and exactOptional metadata
- `tests/unit/intake-classifier.test.ts` — keyword detection + short-circuit unit tests

## Goal Status

| Goal | Status | Notes |
|------|--------|-------|
| A — service_request E2E | DONE | 1 new E2E test; mirrors weekly-report / meeting-prep shape |
| B — Bolt wiring tested | DONE | `registerEventHandlers` driven via FakeBoltApp; 3 tests |
| C — Approval action E2E | DONE | FakeBoltApp drives `approve_case` / `reject_case`; delivery postMessage asserted; 3 tests |
| D — 6 tsc errors | DONE | 6 → 0; fixes are minimal/local, no semantic changes |
| E — Phase 1 acceptance suite | DONE | 4 tests: 3 individual scenarios + 1 sequential run |

## Phase 1 Acceptance Test Result

`tests/acceptance/phase1.test.ts` — **4 / 4 passing**:
1. weekly_report end to end
2. meeting_prep end to end
3. internal_service end to end
4. all 3 in sequence on shared harness

Each scenario asserts: case lifecycle (INTAKE → ARCHIVED), artifact persisted,
audit events (CASE_CREATED, AGENT_INVOKED, AGENT_COMPLETED, CASE_COMPLETED).

## Phase 1 Completion Checklist (vs `docs/PHASE1-SCOPE-LOCK.md`)

- [x] weekly_report E2E (`tests/integration/weekly-report-e2e.test.ts`, since WP2)
- [x] meeting_prep E2E (`tests/integration/meeting-prep-e2e.test.ts`, since WP3)
- [x] service_request (internal_service) E2E (`tests/integration/service-request-e2e.test.ts`, WP4)
- [x] Slack intake wired — pure handler `handleSlackMessageEvent` covered by `slack-intake.test.ts` (5 tests, WP3); Bolt wiring layer covered by `bolt-wiring.test.ts` (3 tests, WP4)
- [x] ApprovalGate approval action wired — `approval-action.test.ts` drives the real registered Bolt listener via FakeBoltApp; AWAITING_APPROVAL → COMPLETED + delivery postMessage asserted
- [x] Audit trail + EvidenceBundle for all 3 — every E2E asserts AuditEventType set; PMAgent and ServiceAgent persist Artifact + EvidenceBundle
- [x] tsc clean — 0 errors
- [x] All tests green — 83/83

## Honest Caveats

- The Bolt wiring tests use `FakeBoltApp` (a hand-rolled fake) rather than booting a real `@slack/bolt` `App`. This is a deliberate choice — booting Bolt requires a Slack signing secret + websocket connection and Bolt does not export a clean test harness. The fake faithfully captures the listener registration shape (`app.action(id, listener)`, `app.message(listener)`) and synthesises payloads; coverage is the **contract** between Synapse code and the Bolt API, not Bolt itself.
- The approval-action test seeds the case at AWAITING_APPROVAL with a hand-set envelope id, then drives the registered listener. ApprovalGate semantics (matrix YAML, hardened transitions) are still exercised end-to-end; the gate's `requiresHumanApproval` runs inside `caseService.transitionStatus` during the test.
- ServiceAgent is a peer of PMAgent (separate `agent.ops`) rather than folded into PMAgent. Lower friction than retrofitting PMAgent and matches `config/case-types.yaml` (`internal_service.owner_agent: agent.ops`).
- `internal_service` is `requires_approval: false` per case-types.yaml; the E2E and acceptance suite still drive AWAITING_APPROVAL → COMPLETED to keep lifecycle uniform with the other two scenarios. If future product wants to bypass approval for internal_service, drop the AWAITING_APPROVAL step in the FSM transition.

## Outstanding Follow-ups for Phase 2

- **PostgreSQL migration**: `CaseStore`/`AuditStore`/`ArtifactStore`/`EvidenceBundleStore` currently file-backed (RUNTIME_DATA_DIR). Phase 2 to move to Postgres with proper indices, transactions, retention policy.
- **Vector store / RAG for PMAgent and ServiceAgent**: knowledge ingestion + retrieval beyond the static `expert-knowledge-base.md` block.
- **Additional scenarios**: `research_request`, `content_draft`, `data_analysis`, `decision_brief` — enums exist, scope-locked out of Phase 1, ready to graduate in Phase 2.
- **Real Bolt integration test in CI**: optional; would need a Slack mock-server (slack-mocker / nock-based shim) to validate listener wiring against live Bolt.
- **Approval evidence persistence in handler**: extend `action-handler` to save an EvidenceBundle with `approvalEnvelopeId` on each approval (currently only the case `approvalIds` array is updated — the EvidenceBundle wiring exists in the data model but isn't auto-populated by the handler).
- **Delivery message routing**: current delivery posts to the same channel as the approval message. If approvals happen in a different channel from the original request thread, plumb through `slackChannelId`/`slackThreadTs` from the case metadata.

