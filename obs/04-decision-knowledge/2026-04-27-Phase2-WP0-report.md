# Phase 2 WP0 Fix Report
**Date:** 2026-04-27  
**Branch:** `phase2-wp0` (based on `sprint-a-wp4`)  
**WP0 Commit Hash:** `606c9b9`

---

## Blocker 1: EvidenceBundle Auto-Persist on Approval

### Problem
`registerActionHandlers` in `action-handler.ts` fired `approve_case` and called `ApprovalGate.approve()` (via `CaseService.transitionStatus`) but never persisted an `EvidenceBundle` capturing the approval event. Documented WP4 caveat.

### Fix — Files Changed
1. **`src/integrations/slack/action-handler.ts`**
   - Added optional `evidenceBundleStore?: EvidenceBundleStore` parameter to `registerActionHandlers`
   - After `caseService.transitionStatus(…, COMPLETED)` succeeds, calls `evidenceBundleStore.save()` with a new `EvidenceBundle` containing: `caseId`, `approvalEnvelopeId`, `title`, `description`, `artifacts: []`, `summary` (approver + timestamp + case ID), `compiledAt`, `compiledBy: human:<userId>`
   - Uses `generateEvidenceId()` (prefix `EVB-`) from the existing id-generator
   - The `evidenceBundleStore` parameter is optional (`?`) — existing tests that don't pass it continue working without change (backward-compatible)

2. **`src/index.ts`**
   - Added `EvidenceBundleStore` import
   - Instantiated `evidenceBundleStore` in `bootstrap()`
   - Passed it as third argument to `registerActionHandlers(app, caseService, evidenceBundleStore)`

### Approach
Injected `EvidenceBundleStore` at the call site in `index.ts` (not inside `ApprovalGate`) — consistent with the existing DI pattern. Optional parameter preserves backward compat. Persist is inside the `approve_case` action handler only (rejection does not create an EvidenceBundle by design — only approvals generate audit evidence).

---

## Blocker 2: routing-rules.yaml Phase 2 Agent Routing

### Problem
All 4 new scenario types (`research_request`, `data_analysis`, `content_draft`, `decision_brief`) pointed to `agent.ops` (ServiceAgent). Sprint B registers `agent.research` and `agent.content`, so these routes would dispatch to the wrong agent.

### Fix — Files Changed
1. **`config/routing-rules.yaml`**
   - `research_request` → `agent.research`
   - `data_analysis` → `agent.research`
   - `content_draft` → `agent.content`
   - `decision_brief` → `agent.content`
   - Phase 1 routes (`weekly_report`, `meeting_prep`, `internal_service`, `fallback`) unchanged

### AgentRegistry / Crash Risk
Checked `AgentRegistry` and `AgentOrchestrator`: the YAML file is **not validated against registered runners at startup**. `AgentOrchestrator` uses its own `runners: Map<string, AgentRunner>` — unregistered agents in the YAML won't cause a crash. The IntakeClassifier populates `ownerAgent` from its own classification results; the YAML is a standalone routing reference doc for the Sprint B routing engine. No graceful fallback code needed — the existing architecture already handles this safely.

---

## Tests

| Metric | Before | After |
|--------|--------|-------|
| Test files | 16 | 17 |
| Tests passing | 83 | 90 |
| tsc errors | 0 | 0 |

### New Tests Added
- **`tests/integration/approval-action.test.ts`** (2 new tests appended):
  - `persists an EvidenceBundle with type approval_envelope after approve_case fires` — asserts `evidenceBundleStore.findByCaseId()` returns a bundle with matching `approvalEnvelopeId`
  - `does NOT persist EvidenceBundle when no store is provided (backward compat)` — asserts no crash when called without store

- **`tests/unit/routing-rules.test.ts`** (5 new tests, new file):
  - `routes research_request to agent.research`
  - `routes data_analysis to agent.research`
  - `routes content_draft to agent.content`
  - `routes decision_brief to agent.content`
  - `Phase 1 routes remain unchanged`

---

## Surprises / Follow-up Notes for Sprint B

1. **`routing-rules.yaml` is currently unused at runtime** — the `IntakeClassifier` + `OrchestratorAgent` path sets `ownerAgent` from Claude's classification response, not from this YAML. Sprint B should wire a `RoutingRulesEngine` that reads this file and uses it for deterministic routing when classification is bypassed (similar to how `ApprovalGate` reads `approval-matrix.yaml`).

2. **`EvidenceBundleStore` in tests** — the new evidence-bundle tests use `RUNTIME_DATA_DIR = ./test-runtime-data-approval-action` (shared with the existing approval-action tests). Cleanup is handled by the shared `beforeEach`/`afterEach` in the new describe block.

3. **`generateEvidenceId()` prefix is `EVB-`** — if the expert panel expects `type: 'approval_envelope'` as a distinct field, note the current `EvidenceBundle` schema has no explicit `type` field; the `approvalEnvelopeId` field serves as the discriminator. Sprint B may want to add `type: string` to `EvidenceBundle`.

---

## Verdict

**Sprint B is unblocked.**

Both WP0 blockers are resolved, 90/90 tests pass, tsc 0 errors.
