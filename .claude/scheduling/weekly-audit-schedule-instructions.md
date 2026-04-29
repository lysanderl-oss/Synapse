# Weekly Harness Audit - Schedule Setup

> Per president 2026-04-27 directive: "mechanisms cannot be paper-only".
> Three layers of automation activate the weekly Harness audit on
> **Sunday 23:00 Asia/Dubai (= Sunday 19:00 UTC)**.

## Layer 1: Windows Task Scheduler (PRIMARY, already installed)

**Status**: Active on this workstation as of 2026-04-23.

```powershell
# Verify
Get-ScheduledTask -TaskName SynapseWeeklyHarnessAudit | Get-ScheduledTaskInfo

# Manual test run
Start-ScheduledTask -TaskName SynapseWeeklyHarnessAudit

# Reinstall / update
powershell.exe -ExecutionPolicy Bypass -File scripts\install-windows-scheduled-task.ps1
```

The task runs as the current user only when logged in (avoids credential
storage). For 24/7 server-grade scheduling, see Layer 2.

## Layer 2: Claude Code `schedule` Skill (CROSS-PLATFORM, recommended for laptop-off scenarios)

The `schedule` Skill creates a remote Claude Code agent that fires on cron
regardless of whether this workstation is online.

### One-time setup (run from Lysander main dialogue or president)

User types in Claude Code chat:

```
/schedule create
```

Or natural language:

> "Create a scheduled remote agent that runs every Sunday 23:00 Dubai
> and triggers /weekly-audit"

### Expected configuration

| Field | Value |
|-------|-------|
| Frequency | Weekly |
| Day | Sunday |
| Time | 23:00 Asia/Dubai (= 19:00 UTC) |
| Action | Trigger `/weekly-audit` Skill command |
| Output | `obs/01-team-knowledge/HR/weekly-audit/harness-review-week-{ISO_WEEK}.md` |
| Notification | Slack on success/failure (via WF-09 if configured) |

### Why a worker agent cannot run this directly

The `schedule` Skill must be invoked from the main dialogue (Lysander or
president), not from a worker subagent. Worker agents prepare the
configuration; activation is a one-time main-dialogue action.

## Layer 3: Manual fallback (always available)

```
/weekly-audit
```

In Claude Code chat. Lysander dispatches a worker agent that runs:
1. `python3 -X utf8 agent-CEO/dispatch_weekly_audit.py`
2. `python3 scripts/audit_facts.py`
3. `python3 scripts/check_stale_tasks.py`
4. `python3 scripts/frontmatter_lint.py --path obs/`
5. CLAUDE.md line-count check (must be <= 350)

Or directly from CLI:

```bash
cd /c/Users/lysanderl_janusd/Synapse-Mini
python3 -X utf8 agent-CEO/dispatch_weekly_audit.py
```

## Output location

`obs/01-team-knowledge/HR/weekly-audit/harness-review-week-{ISO_WEEK}.md`

Existing reports (verified 2026-04-23):
- `2026-W17-audit.md`
- `week-audit-2026-W16.md`

## Failure escalation policy

- 1 missed week  -> Lysander auto-dispatches `harness_engineer` to backfill
- 2 missed weeks -> L4 president escalation (per CLAUDE.md decision tier)

## History

- 2026-04-27: President directive "mechanisms cannot be paper-only"
- 2026-04-23: Three-layer scheduling implemented (this commit)
  - Windows Task Scheduler PS1 installer + active task registration
  - `schedule` Skill setup documentation
  - Manual `/weekly-audit` Skill verified
