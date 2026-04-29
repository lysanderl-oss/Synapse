#!/usr/bin/env python3
"""Codex daily work log append tool.

Usage:
    py -3 scripts/codex_log_append.py "Task description" "Output artifact" "done"

Arguments:
    task    - Brief task description (default: "Work record")
    output  - Output artifact or deliverable (default: "-")
    status  - Status: done / in_progress / blocked (default: "done")

The log file is at logs/codex-daily.md and is auto-created if absent.
"""

import sys
import io
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Fix Windows console encoding for CJK/emoji output
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DUBAI_TZ = timezone(timedelta(hours=4))
LOG = Path(__file__).parent.parent / "logs" / "codex-daily.md"


def ensure_log_exists() -> None:
    """Create log file with header if it does not exist."""
    if not LOG.exists():
        LOG.parent.mkdir(parents=True, exist_ok=True)
        LOG.write_text(
            "# Codex Daily Log\n\n"
            "<!-- Format: | Date | Task description | Output | Status | -->\n"
            "<!-- Usage: py -3 scripts/codex_log_append.py \"task\" \"output\" \"done\" -->\n\n"
            "| Date | Task | Output | Status |\n"
            "| --- | --- | --- | --- |\n",
            encoding="utf-8",
        )
        print(f"[Codex] Created log file: {LOG}")


def append_entry(task: str, output: str, status: str) -> None:
    """Append a new entry to the Codex daily log."""
    ensure_log_exists()
    date = datetime.now(DUBAI_TZ).strftime("%Y-%m-%d")
    entry = f"| {date} | {task} | {output} | {status} |\n"

    with LOG.open("a", encoding="utf-8") as f:
        f.write(entry)

    print(f"[Codex] Logged: {date} | {task} | {output} | {status}")


def main() -> None:
    task = sys.argv[1] if len(sys.argv) > 1 else "Work record"
    output = sys.argv[2] if len(sys.argv) > 2 else "-"
    status = sys.argv[3] if len(sys.argv) > 3 else "done"

    valid_statuses = ("done", "in_progress", "blocked")
    if status not in valid_statuses:
        print(f"[Codex] WARNING: status '{status}' not in {valid_statuses}, using 'done'")
        status = "done"

    append_entry(task, output, status)


if __name__ == "__main__":
    main()
