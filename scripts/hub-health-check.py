#!/usr/bin/env python3
"""
hub-health-check.py — Lysander-AI Hub weekly health check
Checks all Hub pages, 工作日志 DB entries, asset delta, and recent artifacts.
Writes report to logs/hub-health-{YYYY-MM-DD}.md and sends Slack notification.

Usage:
    py -3 scripts/hub-health-check.py
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DUBAI_TZ = timezone(timedelta(hours=4))

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

HUB_PAGES = {
    "工作日志 DB":        "34d114fc-090c-81d9-b64f-d42a3d8a99c7",
    "Claude Code 工作台": "34f114fc-090c-8169-b7b7-d5300485c8b2",
    "成果物 Dashboard":   "34f114fc-090c-81dd-b007-c581cbc90177",
    "资产全景":           "34e114fc-090c-817a-ad30-f978d16ed93c",
}

WORKLOG_DB_ID = "34d114fc-090c-81d9-b64f-d42a3d8a99c7"

TRACKED_FIELDS = [
    "agents_count",
    "teams_count",
    "yaml_count",
    "total_scripts",
    "py_count",
    "js_count",
    "active_workflows",
    "sites_count",
]


def ts() -> str:
    return datetime.now(DUBAI_TZ).strftime("%Y-%m-%d %H:%M:%S")


def now_dubai() -> datetime:
    return datetime.now(DUBAI_TZ)


def load_yaml_file(path: Path) -> dict:
    try:
        import yaml
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[{ts()}] WARNING: could not load {path}: {e}")
        return {}


def check_worklog_db(days: int = 7) -> dict:
    """Query 工作日志 DB for entries in the last N days."""
    cutoff = (now_dubai() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        resp = requests.post(
            f"https://api.notion.com/v1/databases/{WORKLOG_DB_ID}/query",
            headers=NOTION_HEADERS,
            json={
                "filter": {
                    "property": "Date",
                    "date": {"on_or_after": cutoff},
                }
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return {"accessible": False, "count": 0, "error": f"HTTP {resp.status_code}"}
        results = resp.json().get("results", [])
        return {"accessible": True, "count": len(results), "error": None}
    except Exception as e:
        return {"accessible": False, "count": 0, "error": str(e)}


def check_page_accessible(page_id: str) -> dict:
    """GET a page and verify it is accessible. Also count top-level blocks."""
    try:
        resp = requests.get(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=NOTION_HEADERS,
            params={"page_size": 100},
            timeout=15,
        )
        if resp.status_code != 200:
            return {"accessible": False, "block_count": 0, "error": f"HTTP {resp.status_code}"}
        blocks = resp.json().get("results", [])
        return {"accessible": True, "block_count": len(blocks), "error": None}
    except Exception as e:
        return {"accessible": False, "block_count": 0, "error": str(e)}


def check_asset_delta() -> dict:
    """Compare hub-sync-state.yaml vs asset_snapshot.yaml."""
    snapshot = load_yaml_file(REPO_ROOT / "logs" / "asset_snapshot.yaml")
    sync_state = load_yaml_file(REPO_ROOT / "logs" / "hub-sync-state.yaml")

    if not snapshot:
        return {"has_delta": False, "delta": {}, "last_sync": "unknown", "note": "asset_snapshot.yaml missing"}
    if not sync_state:
        return {"has_delta": True, "delta": {}, "last_sync": "never", "note": "hub-sync-state.yaml missing — run diff-to-notion.py"}

    prev_values = sync_state.get("values", {})
    last_sync = sync_state.get("last_sync", "unknown")
    delta = {}
    for f in TRACKED_FIELDS:
        current = snapshot.get(f, 0) or 0
        previous = prev_values.get(f, 0) or 0
        if current != previous:
            delta[f] = {"old": previous, "new": current}

    return {
        "has_delta": bool(delta),
        "delta": delta,
        "last_sync": last_sync,
        "note": None,
    }


def scan_recent_artifacts(days: int = 7) -> list[str]:
    """Scan obs/06-daily-reports/ for PDF/DOCX files newer than N days."""
    reports_dir = REPO_ROOT / "obs" / "06-daily-reports"
    if not reports_dir.exists():
        return []

    cutoff = now_dubai() - timedelta(days=days)
    candidates = []
    for f in reports_dir.rglob("*"):
        if f.suffix.lower() not in (".pdf", ".docx"):
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=DUBAI_TZ)
        if mtime >= cutoff:
            candidates.append(str(f.relative_to(REPO_ROOT)))
    return candidates


def send_slack(message: str) -> bool:
    webhook = os.environ.get("N8N_WEBHOOK_URL", "https://n8n.lysander.bond/webhook/notify")
    try:
        resp = requests.post(
            webhook,
            json={
                "recipient": "president",
                "priority": "low",
                "title": "Hub Weekly Health Check",
                "body": message,
                "source": "hub-health-check",
            },
            timeout=10,
        )
        return resp.status_code < 300
    except Exception as e:
        print(f"[{ts()}] Slack notification failed: {e}")
        return False


def build_report(
    date_str: str,
    worklog: dict,
    pages: dict,
    asset_delta: dict,
    artifacts: list,
) -> str:
    lines = [
        f"# Hub Weekly Health Check — {date_str}",
        f"Generated: {ts()} (Dubai)",
        "",
        "## 1. 工作日志 DB (last 7 days)",
    ]
    wl_status = "OK" if worklog["accessible"] and worklog["count"] > 0 else "WARN"
    lines.append(f"- Status: {wl_status}")
    lines.append(f"- Entries: {worklog['count']}")
    if worklog.get("error"):
        lines.append(f"- Error: {worklog['error']}")
    if worklog["count"] == 0:
        lines.append("- WARNING: No entries in last 7 days — check n8n notion_daily_sync trigger")

    lines.append("")
    lines.append("## 2. Page Accessibility")
    accessible_count = 0
    total_pages = len(pages)
    for name, result in pages.items():
        ok = result["accessible"]
        if ok:
            accessible_count += 1
        icon = "OK" if ok else "FAIL"
        block_info = f" ({result['block_count']} blocks)" if ok else ""
        err_info = f" — {result['error']}" if result.get("error") else ""
        lines.append(f"- [{icon}] {name}{block_info}{err_info}")

    lines.append("")
    lines.append("## 3. Asset Delta (hub-sync-state vs asset_snapshot)")
    if asset_delta.get("note"):
        lines.append(f"- Note: {asset_delta['note']}")
    lines.append(f"- Last sync: {asset_delta['last_sync']}")
    if asset_delta["has_delta"] and asset_delta["delta"]:
        lines.append("- Unsynced changes detected:")
        for field, vals in asset_delta["delta"].items():
            lines.append(f"  - {field}: {vals['old']} → {vals['new']}")
        lines.append("- ACTION: Run `py -3 scripts/diff-to-notion.py` to sync")
    elif asset_delta["has_delta"]:
        lines.append("- WARNING: State file missing — sync not yet performed")
    else:
        lines.append("- No unsynced changes")

    lines.append("")
    lines.append("## 4. Recent Artifacts (PDF/DOCX in obs/06-daily-reports, last 7 days)")
    if artifacts:
        lines.append(f"- {len(artifacts)} candidate(s) for Hub upload:")
        for a in artifacts:
            lines.append(f"  - {a}")
    else:
        lines.append("- No new PDF/DOCX artifacts found")

    lines.append("")
    lines.append("## Summary")
    wl_ok = worklog["accessible"] and worklog["count"] > 0
    pages_ok = accessible_count == total_pages
    delta_ok = not asset_delta["has_delta"]
    lines.append(f"- 工作日志: {'OK' if wl_ok else 'WARN'} ({worklog['count']} entries)")
    lines.append(f"- Pages: {accessible_count}/{total_pages} accessible")
    lines.append(f"- Asset delta: {'no change' if delta_ok else 'UNSYNCED CHANGES'}")
    lines.append(f"- New artifacts: {len(artifacts)} candidate(s)")

    return "\n".join(lines)


def build_slack_message(
    date_str: str,
    worklog: dict,
    accessible_count: int,
    total_pages: int,
    asset_delta: dict,
    artifacts: list,
) -> str:
    wl_icon = "OK" if worklog["accessible"] and worklog["count"] > 0 else "WARN"
    pages_icon = "OK" if accessible_count == total_pages else "WARN"
    delta_status = "no change" if not asset_delta["has_delta"] else "UNSYNCED CHANGES"
    delta_icon = "OK" if not asset_delta["has_delta"] else "WARN"

    return (
        f"Hub Weekly Health Check — {date_str}\n"
        f"- 工作日志: {worklog['count']} entries last 7 days [{wl_icon}]\n"
        f"- Pages: {accessible_count}/{total_pages} accessible [{pages_icon}]\n"
        f"- Asset delta: {delta_status} [{delta_icon}]\n"
        f"- New artifacts: {len(artifacts)} candidates for Hub upload"
    )


def main():
    if not NOTION_TOKEN:
        print(f"[{ts()}] ERROR: NOTION_TOKEN environment variable not set")
        sys.exit(1)

    today = now_dubai().strftime("%Y-%m-%d")
    print(f"[{ts()}] hub-health-check starting for {today}...")

    print(f"[{ts()}] Checking 工作日志 DB...")
    worklog = check_worklog_db(days=7)
    print(f"[{ts()}]   entries (last 7d): {worklog['count']}  accessible: {worklog['accessible']}")

    pages_to_check = {
        name: page_id
        for name, page_id in HUB_PAGES.items()
        if name != "工作日志 DB"
    }
    page_results = {}
    for name, page_id in pages_to_check.items():
        print(f"[{ts()}] Checking page: {name}...")
        result = check_page_accessible(page_id)
        page_results[name] = result
        status = "OK" if result["accessible"] else f"FAIL ({result['error']})"
        print(f"[{ts()}]   {name}: {status}")

    print(f"[{ts()}] Checking asset delta...")
    asset_delta = check_asset_delta()
    print(f"[{ts()}]   last_sync: {asset_delta['last_sync']}  has_delta: {asset_delta['has_delta']}")

    print(f"[{ts()}] Scanning recent artifacts...")
    artifacts = scan_recent_artifacts(days=7)
    print(f"[{ts()}]   found {len(artifacts)} PDF/DOCX artifact(s)")

    report_text = build_report(today, worklog, page_results, asset_delta, artifacts)

    report_path = REPO_ROOT / "logs" / f"hub-health-{today}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8")
    print(f"[{ts()}] Report written to {report_path}")

    print(f"\n{'=' * 60}")
    print(report_text)
    print("=" * 60)

    accessible_count = sum(1 for r in page_results.values() if r["accessible"])
    total_pages = len(pages_to_check) + (1 if worklog["accessible"] else 0)
    slack_msg = build_slack_message(today, worklog, accessible_count, total_pages, asset_delta, artifacts)
    ok = send_slack(slack_msg)
    print(f"[{ts()}] Slack notification: {'sent' if ok else 'FAILED'}")

    print(f"[{ts()}] hub-health-check complete.")


if __name__ == "__main__":
    main()
