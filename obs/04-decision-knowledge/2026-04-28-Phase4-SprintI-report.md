# Phase 4 Sprint I — Slack-native Reporting Slash Commands

**Date:** 2026-04-28  
**Branch:** `phase4-sprint-i`  
**Commit:** `13adaa8`  
**Base:** `phase4-sprint-h` @ `adb9d33` (236/236 tests, 0 tsc errors)

---

## Goal Status

| Goal | Description | Status |
|------|-------------|--------|
| A | `/synapse cases [status] [agent]` — active case dashboard | DONE |
| B | `/synapse case {id}` — full case detail view | DONE |
| C | `/synapse stats [7d|30d|all]` — agent performance metrics | DONE |
| D | Wire slash commands in Bolt app (`registerCommandHandlers`) | DONE |
| E | Message builder helpers: `buildCaseDashboard`, `buildCaseDetail`, `buildAgentStats` | DONE |
| F | E2E Test 5 (cases) + Test 6 (stats) — direct handler call pattern | DONE |
| G | Unit tests: `command-handler-reporting` + `message-builder-reporting` | DONE |

---

## Test Count

| Suite | Before | After |
|-------|--------|-------|
| Unit (`npm test`) | 236 | **255** (+19) |
| E2E (`npm run test:e2e`) | 4 defined | **6 defined** (+2, skip without real creds) |

**tsc:** 0 errors before and after.

---

## Files Changed

- `src/types/stats.ts` — new: `AgentStats`, `OverallStats`, `SlaStatus` interfaces
- `src/types/index.ts` — added `export * from './stats.js'`
- `src/integrations/slack/message-builder.ts` — added `buildCaseDashboard`, `buildCaseDetail`, `buildAgentStats`, `getSlaStatus`; updated `STATUS_EMOJI` colors for reporting (`:blue_circle:` IN_PROGRESS, `:yellow_circle:` AWAITING_APPROVAL, `:red_circle:` BLOCKED)
- `src/integrations/slack/command-handler.ts` — full rewrite: new imports + `/synapse` command handler alongside existing `/case`
- `tests/unit/command-handler-reporting.test.ts` — 9 unit tests (getSlaStatus, buildCaseDashboard, buildAgentStats)
- `tests/unit/message-builder-reporting.test.ts` — 10 unit tests (buildCaseDashboard overflow, buildCaseDetail sections/actions, buildAgentStats empty state)
- `tests/e2e/slack-live.test.ts` — added Test 5 (`/synapse cases`) and Test 6 (`/synapse stats`)

---

## Sample Block Kit Output — `/synapse cases`

```json
[
  { "type": "header", "text": { "type": "plain_text", "text": "Active Cases (3 total)", "emoji": true } },
  { "type": "divider" },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": ":blue_circle: *`CASE-20260428-0001`* — Weekly report draft\n*Type:* weekly_report  *Status:* in_progress\n*Agent:* agent.pm_zh  *Created:* 2026-04-28\n*SLA:* On track"
    }
  },
  { "type": "divider" },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": ":yellow_circle: *`CASE-20260428-0002`* — Board meeting prep\n*Type:* meeting_prep  *Status:* awaiting_approval\n*Agent:* agent.pm  *Created:* 2026-04-28\n*SLA:* :warning: Warning"
    }
  },
  { "type": "divider" },
  {
    "type": "section",
    "text": { "type": "mrkdwn", "text": "_Last updated: 2026-04-28 09:36:15 UTC_" }
  }
]
```

**Status color coding:**
- `:blue_circle:` IN_PROGRESS
- `:yellow_circle:` AWAITING_APPROVAL
- `:red_circle:` BLOCKED
- `:white_check_mark:` COMPLETED

---

## E2E Test Pattern (Tests 5 & 6)

Tests 5 and 6 call the message builder functions directly with mocked/live store data, bypassing Slack's HTTP delivery mechanism. This is intentional: Slack delivers slash commands via HTTP POST to a public endpoint (or Socket Mode WebSocket), neither of which is available in local test environments. The tests validate the complete Block Kit generation path — filtering, SLA calculation, block structure — which is the business logic under test. This mirrors the existing Test 3 pattern that calls `handleSlackMessageEvent` directly.

---

## Sprint J Readiness

Sprint I establishes the full reporting read path. Sprint J candidates:

1. **Interactive approval flow** — wire the `approve_case` `action_id` in `action-handler.ts` to the FSM APPROVE transition, so the [Approve] button in `/synapse case` actually works
2. **Pagination** — `/synapse cases` currently caps at 10; add `page` argument
3. **Webhook push** — proactively push case status changes to a Slack channel via the existing `buildCaseCompletedMessage` / `buildSLAWarningMessage` builders
4. **SLA digest** — `/synapse sla` subcommand showing cases by SLA urgency band (overdue / warning / on_track)
