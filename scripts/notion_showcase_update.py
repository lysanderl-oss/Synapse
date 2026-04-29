#!/usr/bin/env python3
"""
Notion Showcase Update Script
Updates the Lysander-AI Hub main page with external showcase content.

Execution: py -3 scripts/notion_showcase_update.py
"""

import os
import json
import requests
import sys

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Configuration ──────────────────────────────────────────────────────────────

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
if not NOTION_TOKEN:
    print("[ERROR] NOTION_TOKEN environment variable not set.")
    sys.exit(1)

PAGE_ID = "34d114fc-090c-81db-a651-c2386164b46f"
API_BASE = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def rich_text(content: str) -> list:
    """Build a plain rich_text array from a string."""
    return [{"type": "text", "text": {"content": content}}]


def get_page_blocks() -> list:
    """Retrieve all top-level blocks of the page (handles pagination)."""
    blocks = []
    url = f"{API_BASE}/blocks/{PAGE_ID}/children"
    params = {}
    while True:
        resp = requests.get(url, headers=HEADERS, params=params)
        print(f"  GET  /blocks/{PAGE_ID}/children  ->  {resp.status_code}")
        if resp.status_code != 200:
            print(f"       Response: {resp.text[:300]}")
            break
        data = resp.json()
        blocks.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        params["start_cursor"] = data["next_cursor"]
    return blocks


def delete_block(block_id: str, block_type: str) -> bool:
    """Delete a single block; skip child_database blocks."""
    if block_type == "child_database":
        print(f"  SKIP child_database block {block_id}")
        return False
    resp = requests.delete(f"{API_BASE}/blocks/{block_id}", headers=HEADERS)
    print(f"  DELETE block {block_id} (type={block_type})  ->  {resp.status_code}")
    if resp.status_code not in (200, 404):
        print(f"         Response: {resp.text[:200]}")
    return resp.status_code in (200, 404)


def append_blocks(children: list) -> dict:
    """Append blocks to the page."""
    url = f"{API_BASE}/blocks/{PAGE_ID}/children"
    payload = {"children": children}
    resp = requests.patch(url, headers=HEADERS, json=payload)
    print(f"  PATCH /blocks/{PAGE_ID}/children  ->  {resp.status_code}")
    if resp.status_code != 200:
        print(f"        Response: {resp.text[:500]}")
    return resp.json()

# ── Block Definitions ──────────────────────────────────────────────────────────

def build_showcase_blocks() -> list:
    """Return the ordered list of showcase blocks to prepend."""

    # 1. Stats Callout
    stats_callout = {
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "🧠"},
            "color": "blue_background",
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": (
                            "Synapse AI System — Powered by Claude Code\n"
                            "━━━━━━━━━━━━━━━━━━━━━━\n"
                            "44 Active AI Agents  |  36+ Intelligence Reports  |  "
                            "9 n8n Workflows  |  PMO Auto V2.0 GA\n"
                            "Daily Auto-Sync Active ✅ | External Showcase: 2026-05-02"
                        )
                    },
                }
            ],
        },
    }

    # 2. Intro paragraph — Chinese
    intro_cn = {
        "type": "paragraph",
        "paragraph": {
            "rich_text": rich_text(
                "Synapse 是 Janus Digital 的 AI 协作运营体系 — 知识、决策、执行的神经中枢。"
            )
        },
    }

    # 3. Intro paragraph — English
    intro_en = {
        "type": "paragraph",
        "paragraph": {
            "rich_text": rich_text(
                "Synapse is Janus Digital's AI-powered operational brain — "
                "the neural hub connecting knowledge, decisions, and execution.\n\n"
                "Built with Claude Code | 44 AI Agents | Automated daily intelligence pipeline"
            )
        },
    }

    # 4. Divider
    divider_1 = {"type": "divider", "divider": {}}

    # 5. Three-line Callout blocks
    callout_claude = {
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "🔵"},
            "color": "blue_background",
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": (
                            "Claude Code — 神经中枢 | Operations Core\n"
                            "Synapse 系统的主执行层，负责架构、配置、自动化管道的全程运营。\n"
                            "Primary execution layer — architecture, configuration, and automated pipelines.\n"
                            "✅ 每日自动同步 | Auto-synced daily"
                        )
                    },
                }
            ],
        },
    }

    callout_codex = {
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "🟢"},
            "color": "green_background",
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": (
                            "Codex — 前沿雷达 | Innovation Frontier\n"
                            "探索 Agent-to-Agent 服务架构、Company Agent Service 体系搭建。\n"
                            "Exploring agent-to-agent service architectures and company-level agent systems.\n"
                            "📝 半自动记录 | Semi-automatic logging"
                        )
                    },
                }
            ],
        },
    }

    callout_trae = {
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "🟠"},
            "color": "orange_background",
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": (
                            "Trae — 传播使者 | Knowledge Transfer\n"
                            "协助团队和同事搭建 Synapse 体系，提升组织整体 AI 生产力。\n"
                            "Helping teams adopt Synapse and elevate organizational AI productivity.\n"
                            "✋ 手动更新 | Manual updates"
                        )
                    },
                }
            ],
        },
    }

    # 6. Milestones heading
    milestones_heading = {
        "type": "heading_2",
        "heading_2": {
            "rich_text": rich_text("Key Milestones / 关键里程碑"),
            "is_toggleable": False,
        },
    }

    # 7. Milestone bullet points
    milestone_items = [
        "PMO Auto System V2.0 GA (2026-04-23) — Production deployment with 36 active projects",
        "CEO Guard Governance System (2026-04-24) — Enterprise-grade AI behavior compliance framework",
        "Unified Slack Notification Layer (2026-04-25) — Real-time multi-channel alerting infrastructure (infra v1.0.3)",
        "Synapse V2.1 Sprint Launch (2026-04-25) — WBS chain verification & idempotency improvements",
        "Lysander-AI Hub Launch (2026-04-25) — AI work tracking, daily auto-sync, external showcase",
    ]

    bullet_blocks = [
        {
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": rich_text(item)},
        }
        for item in milestone_items
    ]

    # 8. Divider before work log
    divider_2 = {"type": "divider", "divider": {}}

    # 9. Work log heading
    worklog_heading = {
        "type": "heading_2",
        "heading_2": {
            "rich_text": rich_text("Daily Work Log / 每日工作日志"),
            "is_toggleable": False,
        },
    }

    return (
        [stats_callout, intro_cn, intro_en, divider_1,
         callout_claude, callout_codex, callout_trae,
         milestones_heading]
        + bullet_blocks
        + [divider_2, worklog_heading]
    )

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n=== Lysander-AI Hub — Showcase Update ===\n")

    # Step 1: Retrieve existing blocks
    print("[1] Fetching existing page blocks...")
    existing_blocks = get_page_blocks()
    print(f"    Found {len(existing_blocks)} block(s).\n")

    # Step 2: Delete all non-database blocks
    print("[2] Deleting existing blocks (preserving child_database)...")
    for block in existing_blocks:
        bid = block.get("id", "")
        btype = block.get("type", "unknown")
        delete_block(bid, btype)
    print()

    # Step 3: Prepend showcase blocks
    print("[3] Appending showcase blocks...")
    showcase_blocks = build_showcase_blocks()
    result = append_blocks(showcase_blocks)

    added = len(result.get("results", []))
    print(f"\n    Blocks written: {added}\n")

    # Step 4: Summary
    if "results" in result:
        print("[✅] Page update complete.")
        for i, blk in enumerate(result["results"], 1):
            print(f"    {i:02d}. type={blk.get('type','?')}  id={blk.get('id','?')}")
    else:
        print("[❌] Update may have failed. Full response:")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])

    print("\n=== Done ===\n")


if __name__ == "__main__":
    main()
