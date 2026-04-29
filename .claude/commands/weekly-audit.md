---
description: Manually trigger Synapse weekly Harness audit (周审查手动入口)
---

# Weekly Harness Audit

This skill manually triggers the Sunday 23:00 Dubai automated weekly audit.

## What it does
Runs in sequence:
1. `agent-CEO/dispatch_weekly_audit.py` — HR + Agent capability audit
2. `scripts/frontmatter_lint.py --path obs/` — frontmatter compliance scan
3. `scripts/audit_facts.py` — fact-SSOT drift detection (53 agents / 13 modules)
4. `scripts/check_stale_tasks.py` — active_tasks stale (>14d inbox) detection
5. CLAUDE.md line count check (must <= 350)

## Usage
Type `/weekly-audit` in Claude Code chat. Lysander will dispatch a worker
agent to run all 5 audits and aggregate into a single weekly report at
`obs/01-team-knowledge/HR/weekly-audit/harness-review-week-{ISO_WEEK}.md`.

## Authority
Per CLAUDE.md "Harness 治理规则" Section + president decision ②A (2026-04-27).
Failure to generate for 2 consecutive weeks -> L4 president escalation.

## Output Action Tiers
- PATCH (Lysander auto-fix): All metrics green, no review needed
- MINOR (Lysander dispatch): Yellow flags, schedule fix in next week
- L4 (President escalation): CLAUDE.md > 350 / fact drift >= 5 / CEO Guard breach
