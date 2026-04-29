"""
n8n Workflow Snapshot Exporter

每日 export 所有 n8n workflow JSON 到 harness/n8n-snapshots/
配合 GitHub Actions cron + auto-commit 形成 workflow 版本历史。

使用方式：
  python scripts/n8n/export_workflows.py

环境变量：
  N8N_API_KEY: n8n API token（生产用 GitHub Secrets，本地用环境变量）
  N8N_BASE_URL: 默认 https://n8n.lysander.bond

输出：
  harness/n8n-snapshots/{workflow_id}.json (每个 workflow 一份)
  harness/n8n-snapshots/_index.md（清单 + updatedAt）
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = REPO_ROOT / "harness" / "n8n-snapshots"
N8N_BASE = os.environ.get("N8N_BASE_URL", "https://n8n.lysander.bond")


def fetch_all_workflows(api_key: str) -> list:
    """分页拉取所有 workflow 定义"""
    workflows = []
    cursor = None
    while True:
        params = {"limit": 100}
        if cursor:
            params["cursor"] = cursor
        r = requests.get(
            f"{N8N_BASE}/api/v1/workflows",
            headers={"X-N8N-API-KEY": api_key, "Accept": "application/json"},
            params=params,
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        workflows.extend(data.get("data", []))
        cursor = data.get("nextCursor")
        if not cursor:
            break
    return workflows


def fetch_workflow_full(api_key: str, wf_id: str) -> dict:
    """取 workflow 完整定义（含 nodes / connections / settings）"""
    r = requests.get(
        f"{N8N_BASE}/api/v1/workflows/{wf_id}",
        headers={"X-N8N-API-KEY": api_key, "Accept": "application/json"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def normalize_for_diff(wf: dict) -> dict:
    """删除每次都变的字段（如 nodes 内部的 webhookId UUID 变化），保留稳定字段"""
    # 复制避免改原对象
    clean = json.loads(json.dumps(wf))
    # 移除高频 churning 字段
    clean.pop("triggerCount", None)
    clean.pop("staticData", None)
    return clean


def main():
    api_key = os.environ.get("N8N_API_KEY")
    if not api_key:
        print("ERROR: N8N_API_KEY env not set", file=sys.stderr)
        sys.exit(1)

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[Export] Fetching workflow list from {N8N_BASE}")
    summary_list = fetch_all_workflows(api_key)
    print(f"[Export] Found {len(summary_list)} workflows")

    index_lines = [
        "# n8n Workflow Snapshots",
        "",
        f"Last sync: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Auto-exported daily by `.github/workflows/n8n-snapshot.yml`",
        "",
        "| ID | Name | Active | updatedAt |",
        "|----|------|:------:|-----------|",
    ]

    successful = 0
    for wf_summary in summary_list:
        wf_id = wf_summary["id"]
        wf_name = wf_summary.get("name", "(unnamed)")
        try:
            wf_full = fetch_workflow_full(api_key, wf_id)
            wf_clean = normalize_for_diff(wf_full)
            output_file = SNAPSHOT_DIR / f"{wf_id}.json"
            output_file.write_text(
                json.dumps(wf_clean, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            successful += 1
            active = "✅" if wf_full.get("active") else "❌"
            updated = wf_full.get("updatedAt", "")
            # Markdown 安全：转义 |
            safe_name = wf_name.replace("|", "\\|")
            index_lines.append(f"| `{wf_id}` | {safe_name} | {active} | {updated} |")
        except Exception as e:
            print(f"[Export] FAILED {wf_id} ({wf_name}): {e}", file=sys.stderr)

    index_file = SNAPSHOT_DIR / "_index.md"
    index_file.write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    print(f"[Export] Done. Wrote {successful}/{len(summary_list)} workflow snapshots.")


if __name__ == "__main__":
    main()
