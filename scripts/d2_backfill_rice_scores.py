"""
回填 active_tasks.yaml 中今日 7 条 INTEL 的 rice.score
（从 notes / summary regex 提取"综合评分 X/20"）

仅一次性使用，回填后保留作参考但不进 cron。

D2 数据契约修复（方案 X）配套脚本：
- action_agent.py 的 _normalize_rice 函数已修复未来写入路径
- 本脚本修复历史已写入但 rice=None 的 INTEL
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ACTIVE_TASKS = REPO_ROOT / "agent-CEO" / "config" / "active_tasks.yaml"


def extract_score(text: str) -> Optional[int]:
    """从文本中提取评分（"综合评分 X/20" / "综合评分均 X/20" / "评分 X" / "score: X"）。"""
    if not text:
        return None
    # 优先匹配 "综合评分 X/20" 或 "综合评分均 X/20"（容忍 1 个中文助词字符）
    m = re.search(r"综合评分[一-鿿]?[:：\s]*(\d+)/20", text)
    if m:
        return int(m.group(1))
    # 其次匹配 "评分 X" / "score X"
    m = re.search(r"(?:评分|score)[一-鿿]?[:：\s]*(\d+)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def main() -> int:
    if not ACTIVE_TASKS.exists():
        print(f"[ERROR] active_tasks.yaml 不存在：{ACTIVE_TASKS}")
        return 1

    with open(ACTIVE_TASKS, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        print("[ERROR] tasks 字段非列表")
        return 1

    backfilled = 0
    no_score = 0
    skipped_existing = 0

    for t in tasks:
        if not isinstance(t, dict):
            continue
        if t.get("status") != "approved-pending-dispatch":
            continue

        rice = t.get("rice")
        # 跳过已有正确 score 的（dict 含 int score）
        if isinstance(rice, dict) and isinstance(rice.get("score"), int):
            skipped_existing += 1
            continue

        # 从 notes / summary 提取
        notes = t.get("notes", "") or ""
        summary = t.get("summary", "") or ""
        score = extract_score(notes) or extract_score(summary)

        task_id = t.get("id", "?")
        if score is not None:
            t["rice"] = {
                "score": score,
                "extracted_from": "notes_regex_backfill",
            }
            print(f"  Backfilled {task_id}: score={score}")
            backfilled += 1
        else:
            t["rice"] = {
                "score": None,
                "extracted_from": "missing",
            }
            print(f"  No score found for {task_id}")
            no_score += 1

    # 写回（保持中文 + 顺序）
    with open(ACTIVE_TASKS, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=False,
            width=4096,
            default_flow_style=False,
        )

    print()
    print(f"Total backfilled: {backfilled}")
    print(f"No score found:   {no_score}")
    print(f"Already correct:  {skipped_existing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
