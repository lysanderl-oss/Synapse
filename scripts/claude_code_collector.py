#!/usr/bin/env python3
"""Claude Code daily data collector.
Collects git commits, intercept log entries, and Codex work for a given date (Dubai TZ).
"""

import subprocess
import re
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\lysanderl_janusd\Synapse-Mini")
DUBAI_TZ = timezone(timedelta(hours=4))


def get_today_dubai() -> str:
    return datetime.now(DUBAI_TZ).strftime("%Y-%m-%d")


def get_git_commits_today(date_str: str) -> list:
    """git log --since --before, parse conventional commits."""
    result = subprocess.run(
        [
            "git", "log",
            f"--since={date_str} 00:00:00",
            f"--before={date_str} 23:59:59",
            "--format=%H|||%ad|||%s",
            "--date=format:%H:%M",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    commits = []
    for line in result.stdout.strip().splitlines():
        if "|||" not in line:
            continue
        parts = line.split("|||", 2)
        if len(parts) < 3:
            continue
        h, t, s = parts
        m = re.match(
            r"^(feat|fix|chore|docs|refactor|test|style)\(([^)]+)\):\s*(.+)", s
        )
        commits.append(
            {
                "hash": h[:7],
                "time": t,
                "type": m.group(1) if m else "other",
                "scope": m.group(2) if m else "",
                "subject": m.group(3) if m else s,
            }
        )
    return commits


def get_intercept_log_today(date_str: str) -> list:
    """Read agent-CEO intercept log entries for today."""
    try:
        import yaml
    except ImportError:
        return []

    log_path = REPO_ROOT / "agent-CEO" / "data" / "intercept_log.yaml"
    if not log_path.exists():
        return []
    try:
        raw = yaml.safe_load(log_path.read_text(encoding="utf-8")) or []
        return [
            e
            for e in raw
            if isinstance(e, dict)
            and date_str in str(e.get("timestamp", ""))
            and e.get("status") in ("completed", "in_progress")
        ]
    except Exception:
        return []


def get_codex_work_today(date_str: str) -> str:
    """Read Codex daily log entries for today."""
    codex_log = REPO_ROOT / "logs" / "codex-daily.md"
    if not codex_log.exists():
        return ""
    lines = []
    for line in codex_log.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"| {date_str}"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                lines.append(f"- {parts[2]} -> {parts[3]} [{parts[4]}]")
    return "\n".join(lines) if lines else ""


def collect_all_data(date_str: str) -> dict:
    """Collect all data sources for the given date."""
    return {
        "commits": get_git_commits_today(date_str),
        "intercepts": get_intercept_log_today(date_str),
        "codex_work": get_codex_work_today(date_str),
    }


if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else get_today_dubai()
    data = collect_all_data(date)
    print(f"Date: {date}")
    print(f"Commits: {len(data['commits'])}")
    for c in data["commits"]:
        print(f"  {c['hash']} {c['time']} [{c['type']}] {c['subject']}")
    print(f"Intercepts: {len(data['intercepts'])}")
    print(f"Codex work lines: {len(data['codex_work'].splitlines()) if data['codex_work'] else 0}")
