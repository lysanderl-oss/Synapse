#!/usr/bin/env python3
"""Notion daily sync script.
Reads Claude Code git commits + intercept log, generates AI summary, writes to Notion DB.
Credentials are loaded from Windows environment variables — never hardcoded.

Usage:
    py -3 scripts/notion_daily_sync.py [--date YYYY-MM-DD]
"""

import os
import sys
import json
import re
import requests
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\lysanderl_janusd\Synapse-Mini")
DUBAI_TZ = timezone(timedelta(hours=4))
BUFFER_PATH = REPO_ROOT / "logs" / "notion-sync-buffer.json"

# Credentials from environment variables ONLY — never hardcoded
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_DB_ID = os.environ.get("NOTION_DB_ID", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def get_asset_snapshot():
    """读取当日 asset_snapshot.yaml，返回资产数据字典"""
    import yaml as _yaml
    snapshot_path = Path(__file__).parent.parent / "logs" / "asset_snapshot.yaml"
    if not snapshot_path.exists():
        return {}
    try:
        with open(snapshot_path, encoding="utf-8") as f:
            return _yaml.safe_load(f) or {}
    except Exception:
        return {}


def count_active_tasks():
    """统计 active_tasks.yaml 中的 in_progress 任务数"""
    import yaml as _yaml
    tasks_path = Path(__file__).parent.parent / "agent-CEO" / "config" / "active_tasks.yaml"
    if not tasks_path.exists():
        return 0
    try:
        with open(tasks_path, encoding="utf-8") as f:
            data = _yaml.safe_load(f) or {}
        tasks = data.get("tasks", [])
        return sum(1 for t in tasks if t.get("status") in ("in_progress", "scheduled", "pending"))
    except Exception:
        return 0


def generate_report_with_claude(data: dict, date: str) -> dict:
    """Call Claude API to generate structured daily report summary."""
    try:
        import anthropic
    except ImportError:
        print("[notion-sync] anthropic package not installed, skipping AI summary")
        return _fallback_report(data)

    commits = data.get("commits", [])
    intercepts = data.get("intercepts", [])

    if not commits and not intercepts:
        return {
            "summary": "Today no records",
            "key_outcomes": "",
            "key_decisions": "",
            "next_steps": "",
        }

    if not ANTHROPIC_API_KEY:
        print("[notion-sync] ANTHROPIC_API_KEY not set, using fallback report")
        return _fallback_report(data)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Build asset context block
    snapshot = get_asset_snapshot()
    asset_context = ""
    if snapshot:
        asset_context = f"""
当日资产快照：
- YAML配置：{snapshot.get('yaml_count', 'N/A')} 个
- Python/JS脚本：{snapshot.get('total_scripts', 'N/A')} 个
- 活跃 Agent：{snapshot.get('agents_count', 'N/A')} 个
- 待处理任务：{count_active_tasks()} 个
- 版本：{snapshot.get('versions', {})}
如有资产变化（delta不为空），在摘要中提及。
"""

    prompt = f"""Based on the following Claude Code daily work data, generate a structured daily report.

Date: {date}
Git Commits ({len(commits)} total):
{json.dumps(commits, ensure_ascii=False, indent=2)}

User request records ({len(intercepts)} total):
{json.dumps([{"input": e.get("original_input", "")[:100], "status": e.get("status", "")} for e in intercepts], ensure_ascii=False, indent=2)}
{asset_context}
Output JSON (strict format, no other text):
{{
  "summary": "One-line core conclusion (<=50 chars, must include most important delivery or key finding)",
  "key_outcomes": "- Outcome 1\\n- Outcome 2\\n- Outcome 3 (start with verb, has actual deliverable, <=4 items)",
  "key_decisions": "- L3/L4 decision summary (empty string if none)",
  "next_steps": "- Next step 1\\n- Next step 2 (<=3 items)"
}}"""

    try:
        resp = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group())
        return {"summary": text[:100], "key_outcomes": "", "key_decisions": "", "next_steps": ""}
    except Exception as e:
        print(f"[notion-sync] Claude API error: {e}")
        return _fallback_report(data)


def _fallback_report(data: dict) -> dict:
    """Fallback report when AI is unavailable."""
    commits = data.get("commits", [])
    outcomes = []
    for c in commits[:4]:
        tag = f"[{c['type']}]" if c.get("type") != "other" else ""
        scope = f"({c['scope']})" if c.get("scope") else ""
        outcomes.append(f"- {tag}{scope} {c['subject']}")
    return {
        "summary": f"{len(commits)} commits",
        "key_outcomes": "\n".join(outcomes),
        "key_decisions": "",
        "next_steps": "",
    }


def find_existing_page(date_str: str, source: str = "Claude Code") -> str | None:
    """Find existing Notion page for the given date and source."""
    if not NOTION_DB_ID:
        return None
    try:
        resp = requests.post(
            f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query",
            headers=NOTION_HEADERS,
            json={
                "filter": {
                    "and": [
                        {"property": "Date", "date": {"equals": date_str}},
                        {"property": "Source", "select": {"equals": source}},
                    ]
                }
            },
            timeout=15,
        )
        results = resp.json().get("results", [])
        return results[0]["id"] if results else None
    except Exception:
        return None


def write_page(
    date_str: str,
    report: dict,
    commits_count: int,
    source: str = "Claude Code",
    level: str = "日报",
    sync_status: str = "auto",
) -> str:
    """Create a new Notion page in the database."""
    title = f"[{source}] {date_str} 工作日报" if level == "日报" else f"[{source}] {date_str} {report.get('summary', '')[:30]}"
    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "icon": {"type": "emoji", "emoji": "\U0001f4cb"},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Date": {"date": {"start": date_str}},
            "Source": {"select": {"name": source}},
            "Level": {"select": {"name": level}},
            "Summary": {"rich_text": [{"text": {"content": report.get("summary", "")[:2000]}}]},
            "KeyOutcomes": {"rich_text": [{"text": {"content": report.get("key_outcomes", "")[:2000]}}]},
            "KeyDecisions": {"rich_text": [{"text": {"content": report.get("key_decisions", "")[:2000]}}]},
            "NextSteps": {"rich_text": [{"text": {"content": report.get("next_steps", "")[:2000]}}]},
            "CommitCount": {"number": commits_count},
            "SyncStatus": {"select": {"name": sync_status}},
        },
    }

    # Enrich with asset snapshot data
    snapshot = get_asset_snapshot()
    active_count = count_active_tasks()

    if active_count > 0:
        payload["properties"]["ActiveTasks"] = {"number": active_count}

    delta_parts = []
    delta = snapshot.get("delta_from_yesterday", {})
    if delta:
        for k, v in delta.items():
            if v is not None and v != 0:
                delta_parts.append(f"{k}: {'+' if v > 0 else ''}{v}")
    if delta_parts:
        payload["properties"]["AssetDelta"] = {"rich_text": [{"text": {"content": ", ".join(delta_parts)}}]}

    versions = snapshot.get("versions", {})
    if versions:
        ver_str = " | ".join(f"{k}={v}" for k, v in versions.items() if v)
        if ver_str:
            payload["properties"]["SystemVersion"] = {"rich_text": [{"text": {"content": ver_str}}]}

    resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers=NOTION_HEADERS,
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def update_page(page_id: str, report: dict, commits_count: int) -> None:
    """Update an existing Notion page."""
    payload = {
        "properties": {
            "Summary": {"rich_text": [{"text": {"content": report.get("summary", "")[:2000]}}]},
            "KeyOutcomes": {"rich_text": [{"text": {"content": report.get("key_outcomes", "")[:2000]}}]},
            "KeyDecisions": {"rich_text": [{"text": {"content": report.get("key_decisions", "")[:2000]}}]},
            "NextSteps": {"rich_text": [{"text": {"content": report.get("next_steps", "")[:2000]}}]},
            "CommitCount": {"number": commits_count},
        }
    }
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=NOTION_HEADERS,
        json=payload,
        timeout=15,
    )


def notify_slack(title: str, body: str) -> None:
    """Send notification via WF-09 webhook."""
    webhook = "https://n8n.lysander.bond/webhook/notify"
    try:
        requests.post(
            webhook,
            json={
                "recipient": "president",
                "priority": "low",
                "title": title,
                "body": body,
                "source": "notion-daily-sync",
            },
            timeout=10,
        )
    except Exception:
        pass


def run_sync(date_str: str | None = None) -> None:
    """Main sync entrypoint."""
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.claude_code_collector import collect_all_data, get_today_dubai

    if not NOTION_TOKEN:
        print("[notion-sync] ERROR: NOTION_TOKEN environment variable not set")
        sys.exit(1)
    if not NOTION_DB_ID:
        print("[notion-sync] ERROR: NOTION_DB_ID environment variable not set")
        sys.exit(1)

    if not date_str:
        date_str = get_today_dubai()

    print(f"[notion-sync] Starting sync for {date_str}")

    data = collect_all_data(date_str)
    report = generate_report_with_claude(data, date_str)
    commits_count = len(data.get("commits", []))
    codex_work = data.get("codex_work", "")

    # Claude Code daily report
    try:
        existing = find_existing_page(date_str, "Claude Code")
        if existing:
            update_page(existing, report, commits_count)
            print(f"[notion-sync] Updated Claude Code entry: {date_str} ({commits_count} commits)")
        else:
            page_id = write_page(date_str, report, commits_count, "Claude Code")
            print(f"[notion-sync] Created Claude Code entry: {page_id}")

        # Codex entry if there are records today
        if codex_work:
            codex_existing = find_existing_page(date_str, "Codex")
            codex_report = {
                "summary": f"Codex work records {date_str}",
                "key_outcomes": codex_work,
                "key_decisions": "",
                "next_steps": "",
            }
            if codex_existing:
                update_page(codex_existing, codex_report, 0)
                print("[notion-sync] Updated Codex entry")
            else:
                write_page(date_str, codex_report, 0, "Codex")
                print("[notion-sync] Created Codex entry")

        notify_slack(
            f"Notion daily report synced {date_str}",
            f"Claude Code: {commits_count} commits | {report.get('summary', '')[:80]}"
            + (f"\nCodex: {len(codex_work.splitlines())} records" if codex_work else ""),
        )
        print("[notion-sync] Sync complete")

    except Exception as e:
        # Fallback: write to local buffer
        buffer = []
        if BUFFER_PATH.exists():
            try:
                buffer = json.loads(BUFFER_PATH.read_text(encoding="utf-8"))
            except Exception:
                buffer = []
        buffer.append(
            {"date": date_str, "report": report, "commits_count": commits_count}
        )
        BUFFER_PATH.write_text(
            json.dumps(buffer, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[notion-sync] FAILED, buffered: {e}")
        notify_slack(
            "Notion sync failed",
            f"Date: {date_str}\nError: {str(e)[:200]}",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync daily work log to Notion")
    parser.add_argument("--date", default=None, help="Date in YYYY-MM-DD format (default: today Dubai TZ)")
    args = parser.parse_args()
    run_sync(args.date)
