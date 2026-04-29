# Sprint A WP2 — Weekly Report E2E Happy Path

**Date:** 2026-04-27
**Branch:** `sprint-a-wp2`
**Author:** Sub-agent (recovery run)

## Recovery context

This WP2 work was completed in two passes. A first sub-agent ran 41 tool
calls, did the bulk of the PMAgent + ArtifactStore + Claude-client wiring,
then died with `API Error: Unable to connect` before writing the E2E test,
committing, or producing a report.

This second (recovery) sub-agent:
1. Surveyed the working tree, confirmed the dead agent's edits were sound
   but uncommitted.
2. Fixed an unterminated string literal in `pm-agent.ts` (a `.join('\n')`
   that had a real newline byte instead of an escape sequence) that was
   breaking `tsc`.
3. Wired `ownerAgent` through `UpdateCaseInput` / `CaseService.updateCase`
   so the orchestrator can dispatch a case to its assigned agent.
4. Added specialized `CASE_COMPLETED` / `CASE_CANCELLED` audit events on
   top of the existing generic `CASE_STATUS_CHANGED`.
5. Wrote `tests/integration/weekly-report-e2e.test.ts` covering the full
   lifecycle with a vitest-mocked Claude SDK.
6. Committed everything as a single Sprint A WP2 commit.

## Commit hashes

| Stage | Hash | Branch |
|-------|------|--------|
| WP1.5 | `ac427ab` | `wp1.5-corrections` |
| WP2   | `2702340` | `sprint-a-wp2` (branched from `wp1.5-corrections`) |

## Files modified / created

**Modified**
- `src/agents/pm-agent.ts` — loads profile/memory/KB/playbook/template,
  forwards as `extraSystemBlocks` with `cache_control: ephemeral`,
  persists Artifact + EvidenceBundle.
- `src/integrations/claude/client.ts` — accepts `extraSystemBlocks`,
  exposes `__setClaudeTestOverride` test seam.
- `src/core/case-service.ts` — emits specialized `CASE_COMPLETED` and
  `CASE_CANCELLED` events; `updateCase` now respects `ownerAgent`.
- `src/core/audit-logger.ts` — minor edits from prior WP2 pass.
- `src/types/case.ts` — `UpdateCaseInput.ownerAgent` added.
- `src/utils/id-generator.ts` — `generateArtifactId` / `generateEvidenceId`.
- `tests/integration/audit-trail.test.ts` — adapted to artifact wiring.

**Created**
- `src/storage/artifact-store.ts` — `ArtifactStore` + `EvidenceBundleStore`.
- `tests/integration/weekly-report-e2e.test.ts` — full lifecycle E2E.
- `.env.example`, `.eslintrc.json`, `.prettierrc` — repo hygiene.

## Test results

**Before WP2 (baseline at start of session):** 60 passing / 1 failing / 61 total.
The single pre-existing failure is in `tests/unit/id-generator.test.ts`
("different prefixes maintain independent sequences") — a test isolation
problem caused by `tests/unit/id-generator.test.ts` and
`tests/integration/case-flow.test.ts` both pointing
`RUNTIME_DATA_DIR=./test-runtime-data` and racing on the shared counter
file when vitest runs them in parallel. Pre-existing; left untouched per
instructions ("don't break the 60/61 baseline").

**After WP2:** 61 passing / 1 failing / 62 total. The new
`weekly-report-e2e.test.ts` passes; the same pre-existing id-generator
failure remains.

## tsc result

`npx tsc --noEmit` reports 24 errors, all pre-existing in
`src/utils/logger.ts`, `src/storage/audit-store.ts`,
`src/integrations/slack/*.ts`, `src/core/sla-monitor.ts`, etc.
No tsc errors are introduced by WP2 code (`pm-agent.ts`,
`artifact-store.ts`, `case-service.ts`, `weekly-report-e2e.test.ts`).
The `pm-agent.ts` parse error introduced by the dead agent has been
fixed — it now parses cleanly.

## E2E test outcome

`tests/integration/weekly-report-e2e.test.ts` passes. It drives a single
weekly_report case from `INTAKE` → `TRIAGED` → `PLANNED` → `IN_PROGRESS`
(via `AgentOrchestrator.executeCase`) → `AWAITING_REVIEW` →
`AWAITING_APPROVAL` → `COMPLETED` → `ARCHIVED`, with a vitest-mocked
Claude SDK. Asserts:
- `callClaude` called exactly once with `cacheSystemPrompt: true`
- `extraSystemBlocks` includes both the playbook and the output template
- One Artifact persisted with `cacheReadTokens` propagated through
- One EvidenceBundle persisted, referencing the artifact
- Audit trail contains `CASE_CREATED`, `AGENT_INVOKED`,
  `AGENT_COMPLETED`, `CASE_COMPLETED`

## Honest gaps

- **Slack intake not E2E-tested.** `src/integrations/slack/event-handler.ts`
  acknowledges DMs but does not yet hand off to `IntakeClassifier` →
  `CaseService.create()`. The E2E test bypasses Slack and calls
  `caseService.createCase` directly. Wiring the real intake path
  (Slack message → classified → case created) is open work.
- **Slack delivery not E2E-tested.** The action handler approves cases
  on button click and updates the original message, but actually posting
  the finished report back to the user/channel is not exercised by any
  test.
- **Pre-existing tsc errors (24)** in `logger.ts`, slack integration,
  `sla-monitor.ts`, `audit-store.ts` predate WP2 and were not addressed
  here — the project is not currently `tsc`-clean.
- **id-generator test isolation bug** is real, not flaky. Two test
  files write the same `./test-runtime-data/id-counters.json` under
  parallel vitest workers. Worth a one-line `RUNTIME_DATA_DIR` rename
  in a follow-up.
- **`pm-agent.ts` resolved-path heuristic** tries three candidate
  parent dirs to find `agents/pm-agent/...`. Robust enough for vitest
  + dist + cwd, but it would be cleaner to inject the asset root via
  config rather than walk relative paths.
- **MEETING_PREP path** exists in `PMAgent.run` (loads
  `meeting-prep.md` playbook + template) but has no E2E test; that is
  WP3 territory.

## WP3 preview (meeting_prep, 5 lines)

1. Promote the `meeting_prep` branch in `PMAgent.run` to a tested path:
   add `tests/integration/meeting-prep-e2e.test.ts` mirroring the
   weekly-report test structure.
2. Verify `agents/pm-agent/playbooks/meeting-prep.md` and
   `templates/meeting-prep.md` produce a usable agenda + briefing pack.
3. Tighten approval-matrix entries for `meeting_prep` (currently shares
   the generic AWAITING_APPROVAL → COMPLETED gate; may want a lighter
   review path given the 2h SLA).
4. Add an `IntakeClassifier` rule that recognises "meeting prep" /
   "会议准备" Slack messages and routes them to this case type.
5. Capture an artifact-type distinction (`AGENDA` vs `REPORT`) so
   downstream consumers can filter — currently both flow through the
   `DRAFT` enum value.
