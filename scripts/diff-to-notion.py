#!/usr/bin/env python3
"""
diff-to-notion.py — 资产快照差异同步到 Notion 资产全景页
Compare logs/asset_snapshot.yaml vs logs/hub-sync-state.yaml.
If any value changed, patch the 资产全景 Notion page blocks.

Usage:
    py -3 scripts/diff-to-notion.py
"""

import os
import re
import sys
import json
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SNAPSHOT_PATH = REPO_ROOT / "logs" / "asset_snapshot.yaml"
SYNC_STATE_PATH = REPO_ROOT / "logs" / "hub-sync-state.yaml"

ASSETS_PAGE_ID = "34e114fc-090c-817a-ad30-f978d16ed93c"
DUBAI_TZ = timezone(timedelta(hours=4))

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

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


def load_yaml_file(path: Path) -> dict:
    import yaml
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_snapshot() -> dict:
    data = load_yaml_file(SNAPSHOT_PATH)
    if not data:
        print(f"[{ts()}] ERROR: {SNAPSHOT_PATH} not found or empty")
        sys.exit(1)
    return data


def load_sync_state() -> dict:
    """Load last synced state; return zero-values if file doesn't exist (force update)."""
    if not SYNC_STATE_PATH.exists():
        print(f"[{ts()}] hub-sync-state.yaml not found — treating all values as 0 (force update)")
        return {"last_sync": None, "values": {f: 0 for f in TRACKED_FIELDS}}
    return load_yaml_file(SYNC_STATE_PATH)


def save_sync_state(snapshot: dict) -> None:
    import yaml
    today = datetime.now(DUBAI_TZ).strftime("%Y-%m-%d")
    values = {f: snapshot.get(f, 0) for f in TRACKED_FIELDS}
    state = {"last_sync": today, "values": values}

    lines = [f'last_sync: "{today}"', "values:"]
    for k, v in values.items():
        lines.append(f"  {k}: {v}")

    SYNC_STATE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[{ts()}] hub-sync-state.yaml updated → last_sync: {today}")


def compute_delta(snapshot: dict, sync_state: dict) -> dict:
    prev = sync_state.get("values", {})
    delta = {}
    for f in TRACKED_FIELDS:
        current_val = snapshot.get(f, 0) or 0
        prev_val = prev.get(f, 0) or 0
        if current_val != prev_val:
            delta[f] = {"old": prev_val, "new": current_val}
    return delta


def get_page_blocks(page_id: str) -> list:
    resp = requests.get(
        f"https://api.notion.com/v1/blocks/{page_id}/children",
        headers=NOTION_HEADERS,
        params={"page_size": 100},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def extract_block_text(block: dict) -> tuple[str, list]:
    """Return (plain_text, original_rich_text_list) for a block."""
    btype = block.get("type", "")
    rich_text = block.get(btype, {}).get("rich_text", [])
    plain = "".join(rt.get("plain_text", "") for rt in rich_text)
    return plain, rich_text


def patch_block(
    block_id: str,
    original_rich_text: list,
    new_text_map: dict,
    block_type: str = "paragraph",
) -> bool:
    """Patch a Notion block by replacing strings inside each rich_text item's
    text.content, preserving all other properties (annotations, href, etc.).

    Args:
        block_id:          Notion block UUID.
        original_rich_text: The original rich_text list from the block.
        new_text_map:       {old_str: new_str} replacements to apply.
        block_type:         Notion block type (paragraph, bulleted_list_item, …).
    """
    import copy

    updated_rich_text = copy.deepcopy(original_rich_text)
    for item in updated_rich_text:
        content = item.get("text", {}).get("content", "")
        for old_str, new_str in new_text_map.items():
            content = content.replace(old_str, new_str)
        if "text" in item:
            item["text"]["content"] = content

    payload = {block_type: {"rich_text": updated_rich_text}}
    resp = requests.patch(
        f"https://api.notion.com/v1/blocks/{block_id}",
        headers=NOTION_HEADERS,
        json=payload,
        timeout=15,
    )
    return resp.status_code == 200


def update_notion_page(snapshot: dict, delta: dict) -> int:
    """Fetch blocks from 资产全景 page and patch any block containing changed values."""
    print(f"[{ts()}] Fetching blocks from 资产全景 page ({ASSETS_PAGE_ID})...")
    blocks = get_page_blocks(ASSETS_PAGE_ID)
    print(f"[{ts()}] Found {len(blocks)} blocks")

    patched_count = 0
    field_labels = {
        "agents_count": ["agents", "agent", "智能体", "成员"],
        "teams_count": ["teams", "team", "团队"],
        "yaml_count": ["yaml", "配置"],
        "total_scripts": ["scripts", "脚本"],
        "py_count": ["python", "py"],
        "js_count": ["js", "javascript"],
        "active_workflows": ["workflow", "工作流"],
        "sites_count": ["sites", "站点"],
    }

    for block in blocks:
        btype = block.get("type", "")
        if btype not in ("paragraph", "bulleted_list_item", "numbered_list_item", "quote", "callout"):
            continue

        block_id = block["id"]
        text, original_rich_text = extract_block_text(block)
        if not text:
            continue

        text_map: dict = {}  # old_str → new_str accumulated for this block

        for field, changed in delta.items():
            old_val = changed["old"]
            new_val = changed["new"]

            keywords = field_labels.get(field, [field])
            keyword_hit = any(kw.lower() in text.lower() for kw in keywords)
            if not keyword_hit:
                continue

            pattern = re.compile(r'\b' + re.escape(str(old_val)) + r'\b')
            if pattern.search(text):
                text_map[str(old_val)] = str(new_val)
                print(f"[{ts()}]   Block {block_id[:8]}...: '{field}' {old_val} → {new_val}")

        if text_map:
            ok = patch_block(block_id, original_rich_text, text_map, btype)
            if ok:
                patched_count += 1
            else:
                print(f"[{ts()}]   WARNING: patch failed for block {block_id[:8]}...")

    return patched_count


def main():
    if not NOTION_TOKEN:
        print(f"[{ts()}] ERROR: NOTION_TOKEN environment variable not set")
        sys.exit(1)

    print(f"[{ts()}] diff-to-notion starting...")

    snapshot = load_snapshot()
    sync_state = load_sync_state()

    print(f"[{ts()}] Snapshot date: {snapshot.get('snapshot_date', 'unknown')}")
    print(f"[{ts()}] Last sync:     {sync_state.get('last_sync', 'never')}")

    delta = compute_delta(snapshot, sync_state)

    if not delta:
        print(f"[{ts()}] No changes detected — Notion page unchanged.")
        return

    print(f"[{ts()}] Changes detected:")
    for field, changed in delta.items():
        print(f"  {field}: {changed['old']} → {changed['new']}")

    patched = update_notion_page(snapshot, delta)
    print(f"[{ts()}] Patched {patched} block(s) in Notion.")

    save_sync_state(snapshot)
    print(f"[{ts()}] Done. Summary: {len(delta)} field(s) changed, {patched} block(s) updated.")


if __name__ == "__main__":
    main()
