"""
任务恢复 Agent — Q2 版本（GitHub Actions 调度）

职责：
    1. 读取 active_tasks.yaml
    2. 调用 task-resume prompt，让 Claude 评估 in_progress / blocked 任务
    3. 解析返回的更新后 YAML，写回 active_tasks.yaml（保留顺序与注释）
    4. 追加一条 resume_log 条目
    5. 可选：输出 obs/06-daily-reports/{date}-resume-summary.md

调用链：
    task-resume.yml (02:00 Dubai → 每日 06:00 Dubai cron)
        → resume_agent.py
        → Claude API
        → 覆盖 agent-CEO/config/active_tasks.yaml
        → 可选摘要 MD
        → Slack 通知

Usage:
    python resume_agent.py [--dry-run] [--model MODEL]

写回策略：
    - 优先使用 ruamel.yaml（保序 + 保注释）。ruamel 不可用时 fallback 到 pyyaml。
    - Claude 返回的 YAML 若不完整（缺失 tasks），拒绝写回并打 warning。
"""
from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from shared_context import (
    ACTIVE_TASKS_YAML,
    DEFAULT_MODEL,
    REPORTS_DIR,
    call_claude,
    load_active_tasks,
    load_claude_md,
    load_prompt,
    load_recent_commits,
    notify_slack,
)


def _build_system_prompt(prompt_template: str) -> str:
    """组装 resume prompt 的 system（含 CLAUDE.md 摘要，启用缓存）。"""
    claude_md = load_claude_md(truncate=True)
    return (
        prompt_template
        + "\n\n# Synapse 上下文 — CLAUDE.md（截断）\n\n"
        + claude_md
    )


def _current_timestamp_dubai() -> str:
    """返回 ISO8601 时间戳（标注 Dubai UTC+4）。"""
    # GitHub Actions 默认 UTC；这里手动 +4 小时表示 Dubai 时间
    # （更精确做法可装 zoneinfo/pytz，但避免额外依赖）
    from datetime import timedelta
    now_utc = datetime.now(timezone.utc)
    dubai = now_utc + timedelta(hours=4)
    return dubai.strftime("%Y-%m-%dT%H:%M Dubai")


def _extract_yaml_block(text: str) -> Optional[str]:
    """从 Claude 响应中提取 ```yaml ... ``` 块。"""
    m = re.search(r"```ya?ml\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else None


def _safe_write_yaml(new_yaml_text: str, *, dry_run: bool = False) -> bool:
    """写回 active_tasks.yaml，做最小合法性检查。

    检查项：
        - 必须能被 yaml 解析
        - 顶层必须含 ``tasks:`` 列表
        - 长度不得骤减（新 YAML 任务数 < 原任务数 × 0.5 → 拒绝）

    Returns:
        True = 写入成功；False = 拒绝写入（打印原因）。
    """
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        print(f"[SafeWrite] pyyaml 未安装: {exc}")
        return False

    try:
        new_data = yaml.safe_load(new_yaml_text)
    except yaml.YAMLError as exc:
        print(f"[SafeWrite] 解析 Claude 返回的 YAML 失败: {exc}")
        return False

    if not isinstance(new_data, dict) or "tasks" not in new_data:
        print("[SafeWrite] 返回的 YAML 无 `tasks:` 顶层键，拒绝写入")
        return False

    new_task_count = len(new_data.get("tasks") or [])

    # 对比原有任务数防止灾难性缩减
    try:
        old_data = yaml.safe_load(load_active_tasks())
        old_task_count = len(((old_data or {}).get("tasks")) or [])
    except Exception:
        old_task_count = 0

    if old_task_count > 0 and new_task_count < max(1, old_task_count * 0.5):
        print(
            f"[SafeWrite] 任务数骤减 {old_task_count} → {new_task_count}，"
            "疑似 Claude 截断，拒绝写入"
        )
        return False

    if dry_run:
        print(
            f"[DryRun] 验证通过：原 {old_task_count} → 新 {new_task_count} 任务，"
            "未实际写入"
        )
        return True

    # 优先 ruamel（保序/保注释），fallback pyyaml
    try:
        from ruamel.yaml import YAML  # type: ignore

        ry = YAML()
        ry.preserve_quotes = True
        ry.width = 4096
        with ACTIVE_TASKS_YAML.open("w", encoding="utf-8") as f:
            # 重新从 Claude 返回文本 load（保留其原始结构）
            ry.dump(ry.load(new_yaml_text), f)
        print(f"[SafeWrite] 使用 ruamel.yaml 写回 {ACTIVE_TASKS_YAML}")
    except Exception as exc:
        print(f"[SafeWrite] ruamel 不可用或失败（{exc}），fallback pyyaml")
        ACTIVE_TASKS_YAML.write_text(new_yaml_text, encoding="utf-8")

    return True


def run_resume(model: str = DEFAULT_MODEL, dry_run: bool = False) -> Optional[Path]:
    """执行任务恢复检查。

    Args:
        model: Claude 模型 ID。
        dry_run: True 则不实际写回 active_tasks.yaml。

    Returns:
        摘要报告路径（若生成），否则 None。
    """
    current_ts = _current_timestamp_dubai()
    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"[Start] 任务恢复检查 {current_ts} (model={model}, dry_run={dry_run})")

    # 1. 读 prompt + 上下文
    prompt_template = load_prompt("task-resume")
    system = _build_system_prompt(prompt_template)

    active_tasks = load_active_tasks()
    recent_commits = load_recent_commits(hours=24)

    # 2. 构造 user 消息
    user_msg = (
        f"当前时间戳：{current_ts}\n"
        f"报告日期：{report_date}\n\n"
        "## active_tasks.yaml 当前全文\n\n```yaml\n"
        + active_tasks
        + "\n```\n\n"
        "## 过去 24 小时 commit（判断 blocker 是否已解除）\n\n```\n"
        + (recent_commits or "（无近期 commit）")
        + "\n```\n\n"
        "**严格输出一份完整的 active_tasks.yaml**（用 ```yaml 包裹），"
        "要求：\n"
        "1. 保留所有原任务（不可删除）\n"
        "2. 更新 `last_resume_check` 为上方时间戳\n"
        "3. 在顶层 `resume_log:` 列表追加一条新条目\n"
        "4. 对需变更状态的任务更新其 status / priority / notes\n\n"
        "另可附一份 Markdown 摘要（```markdown 包裹），列出状态变化、"
        "L4 候选、仍阻塞项。"
    )

    # 3. 调用 Claude
    response_text = call_claude(
        system=system,
        user=user_msg,
        model=model,
        max_tokens=8000,
        task_budget=50_000,
        cache_system=True,
    )

    # 4. 提取 YAML 并安全写回
    yaml_block = _extract_yaml_block(response_text)
    if yaml_block:
        ok = _safe_write_yaml(yaml_block, dry_run=dry_run)
        if not ok:
            print("[Warn] YAML 写回失败，active_tasks.yaml 未改动")
    else:
        print("[Warn] Claude 未返回 YAML 代码块，active_tasks.yaml 未改动")

    # 5. 提取 Markdown 摘要（可选）
    summary_path: Optional[Path] = None
    md_match = re.search(
        r"```markdown\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE
    )
    if md_match:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        summary_path = REPORTS_DIR / f"{report_date}-resume-summary.md"
        summary_path.write_text(md_match.group(1), encoding="utf-8")
        print(f"[Done] 摘要报告已写入 {summary_path}")

    # 6. Slack 通知
    # NOTE: WF-09 Unified Notification (atit1zW3VYUL54CJ) 已切换为 keypair 模式（2026-04-25 by 总裁），自动安全转义 \n
    # 故恢复富文本 body（含路径 / 换行 / emoji）以充分利用通道能力
    webhook = os.environ.get("SLACK_WEBHOOK_N8N")
    if webhook:
        summary_line = (
            f"摘要：obs/06-daily-reports/{summary_path.name}"
            if summary_path is not None
            else "摘要：（本次未生成 Markdown 摘要）"
        )
        yaml_status = (
            "active_tasks.yaml: 已更新"
            if not dry_run and yaml_block
            else "active_tasks.yaml: 未改动"
        )
        success = notify_slack(
            webhook_url=webhook,
            title=f"🔄 Synapse 任务恢复检查 {report_date}",
            body=(
                f"检查时间：{current_ts}\n"
                f"模型：{model}\n"
                f"{yaml_status}\n"
                f"{summary_line}"
            ),
            source="task-resume",
            priority="info",
        )
        print(
            f"[Notify] Slack notification {'sent' if success else 'failed'} "
            f"(resume, {current_ts})",
            flush=True,
        )
    else:
        print(
            "[Notify] SLACK_WEBHOOK_N8N not set, skipped (resume)",
            flush=True,
        )

    return summary_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Synapse 任务恢复 Agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="不实际写回 active_tasks.yaml，仅打印验证结果",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Claude 模型 ID（默认 {DEFAULT_MODEL}）",
    )
    args = parser.parse_args()

    run_resume(model=args.model, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
