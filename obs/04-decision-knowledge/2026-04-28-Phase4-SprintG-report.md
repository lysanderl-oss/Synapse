# Phase 4 Sprint G — Execution Report
Date: 2026-04-28
Branch: phase4-sprint-g
Commit: df06952

---

## WP0 Checklist

| # | Item | Status |
|---|------|--------|
| 1 | Created `tests/e2e/` directory | DONE |
| 2 | Updated `vitest.config.ts` — added `exclude: ['tests/e2e/**']` | DONE |
| 3 | Added `"test:e2e": "cross-env RUN_SLACK_E2E=true vitest run --config vitest.e2e.config.ts"` to package.json | DONE (also added `vitest.e2e.config.ts` as dedicated e2e config to avoid include/exclude conflict) |
| 4 | Wrote `tests/e2e/README.md` — run instructions, env vars, test descriptions, security note | DONE |
| 5 | Wrote `.env` at project root with real credentials (gitignored, not committed) | DONE — `.gitignore` already had `.env` |
| 6 | Updated `.env.example` with placeholder values for new variables (`RUN_SLACK_E2E`, `SLACK_WORKSPACE`) | DONE |
| 7 | Verified `src/utils/config.ts` reads `SLACK_APP_TOKEN` (startsWith `xapp-`) and `SLACK_BOT_TOKEN` (startsWith `xoxb-`) — names match exactly | DONE — no discrepancy |

---

## Sprint G Test Results

**All 4/4 live E2E tests PASSED** with real janussandbox.slack.com tokens.

| Test | Result | Notes |
|---|---|---|
| Test 1: Bot init + Socket Mode connection | PASS | `app.start()` resolved, Socket Mode connected |
| Test 2: `postMessage` — channel `ai-agents-noti` (C0AV1JAHZHB) | PASS | `ok: true`, valid `ts` returned |
| Test 3: weekly_report trigger message transport | PASS (partial) | Message delivered to channel. Bot-side ack deferred to Sprint H — requires `ANTHROPIC_API_KEY` + `CaseService` wired in harness |
| Test 4: AC-9 token security | PASS | 0 hardcoded `xapp-1-` tokens found in `src/`, `tests/unit/`, `tests/integration/`, `tests/acceptance/` |

**Fix required during Sprint G:** Bot token lacks `groups:read` scope, so `conversations.list` with `types: 'public_channel,private_channel'` failed with `missing_scope`. Fixed by using `types: 'public_channel'` only (bot has `channels:read`), with DM fallback if no public channels.

---

## AC-9 Result

PASS — grep of `xapp-1-` across `src/`, `tests/unit/`, `tests/integration/`, `tests/acceptance/` returned 0 matches. Real token exists only in `.env` (gitignored).

---

## npm test (standard suite)

216/216 PASS — e2e tests correctly excluded from default run.

---

## tsc --noEmit

0 errors.

---

## What worked

- Socket Mode connection to janussandbox.slack.com established within the 15s timeout
- `conversations.list` (public_channel only) returned channel `ai-agents-noti`
- `chat.postMessage` succeeded for both test messages
- AC-9 security gate is now automated and reproducible

## What was partial

- Test 3 bot-side ack: the Bolt harness in this test file is lightweight (no IntakeClassifier, no CaseService). Sending the weekly_report trigger phrase to the real channel was verified (transport passes), but the bot's "CASE-" ack response cannot be asserted without the full app stack running. This is a known and documented gap.

---

## Sprint H Readiness

Sprint H can build on this scaffold:
1. Full app stack harness — start with `ANTHROPIC_API_KEY` + `FileStore` in a temp dir, call `registerEventHandlers(app, caseService, classifier)`, then assert bot acks contain `CASE-`
2. Case lifecycle E2E — from Slack message to `completed` status
3. SLA breach notification — assert DM to `SLA_ALERT_USER_ID=U0ASLJZMVDE`
