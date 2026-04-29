"""
情报行动 Agent — Q2 版本（GitHub Actions 调度）

职责：消化昨日情报日报，做 4 专家评分 + 决策 + 派单，生成行动报告 Markdown。

调用链：
    intel-action.yml (10:00 Dubai, workflow_dispatch)
        → action_agent.py
        → 读 obs/06-daily-reports/{yesterday}-intelligence-daily.html
        → Claude API (sonnet-4-6 / opus-4-6)
        → obs/06-daily-reports/{today}-action-report.md
        → Slack 通知

Usage:
    python action_agent.py [--target-date YYYY-MM-DD] [--model MODEL]

注：target-date 指"昨日情报日报的日期"，默认取今日 UTC 的前一天。
行动报告本身的日期 = target-date + 1。
"""
from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from shared_context import (
    ACTIVE_TASKS_YAML,
    CLAUDE_MD_MAX_CHARS,
    DEFAULT_MODEL,
    REPO_ROOT,
    REPORTS_DIR,
    call_claude,
    load_active_tasks,
    load_claude_md,
    load_organization_yaml,
    load_prompt,
    notify_slack,
)


def _resolve_target_date(arg: str) -> str:
    """--target-date 默认 = 今日 UTC - 1 天。"""
    if arg:
        return arg
    today = datetime.now(timezone.utc).date()
    return (today - timedelta(days=1)).strftime("%Y-%m-%d")


def _load_yesterday_report(target_date: str) -> tuple[str, str]:
    """加载 target_date 的情报日报文件（HTML 优先，缺失则空串 + fallback）。

    Returns:
        (report_content, source_filename)
    """
    candidates = [
        REPORTS_DIR / f"{target_date}-intelligence-daily.html",
        REPORTS_DIR / f"{target_date}-intelligence-daily.md",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8"), path.name
    print(f"[Warn] 未找到 {target_date} 的情报日报，进入无输入兜底模式")
    return "", f"{target_date}-intelligence-daily.html (missing)"


def _build_system_prompt(prompt_template: str) -> str:
    """组装行动 prompt 的 system 消息（可缓存的大段上下文）。"""
    claude_md = load_claude_md(truncate=True)
    org_yaml = load_organization_yaml()
    active_tasks = load_active_tasks()

    return (
        prompt_template
        + "\n\n# Synapse 上下文 — CLAUDE.md（截断）\n\n"
        + claude_md
        + "\n\n# Organization YAML（派单路由依据）\n\n```yaml\n"
        + org_yaml[:8000]
        + "\n```\n\n# active_tasks.yaml（现有任务负载）\n\n```yaml\n"
        + active_tasks[:8000]
        + "\n```"
    )


def _extract_intel_tasks_from_response(response_text: str) -> list[dict[str, Any]]:
    """从 Claude action 响应中提取 ```yaml ... ``` 任务列表块。

    Prompt 约定：Markdown 之外可附一个 ```yaml 代码块，列出要追加到
    active_tasks.yaml 的新任务条目（INTEL-YYYYMMDD-NNN）。

    解析策略：
        1. 找出所有 fenced ```yaml ... ``` 块
        2. 选取第一个能解析为 list[dict] 且首项包含 ``id`` 字段以
           ``INTEL-`` 开头的块
        3. 失败 → 返回空列表（不影响 markdown 主链路）

    Returns:
        任务条目列表（每个为 dict，含 id/title/priority/team/...）。
    """
    if not response_text:
        return []

    # 找出所有 ```yaml ... ``` 围栏块（DOTALL 跨行）
    blocks = re.findall(
        r"```ya?ml\s*\n(.*?)\n```",
        response_text,
        re.DOTALL | re.IGNORECASE,
    )

    for block in blocks:
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as exc:
            print(
                f"[Intel-Loop] 跳过非法 yaml 块: {type(exc).__name__}: "
                f"{str(exc)[:120]}",
                flush=True,
            )
            continue

        if not isinstance(data, list) or not data:
            continue

        first = data[0]
        if not isinstance(first, dict):
            continue

        first_id = str(first.get("id", ""))
        if first_id.startswith("INTEL-"):
            print(
                f"[Intel-Loop] 命中 INTEL 任务 yaml 块，共 {len(data)} 条",
                flush=True,
            )
            return [item for item in data if isinstance(item, dict)]

    print(
        "[Intel-Loop] 响应中未发现 INTEL 任务 yaml 块（可能本次无新增任务）",
        flush=True,
    )
    return []


def _normalize_rice(
    it_rice: Any,
    fallback_notes: str = "",
    fallback_summary: str = "",
) -> dict[str, Any]:
    """规范化 rice 字段，确保 D2 dispatch_rules 可消费的 score 数字字段。

    数据契约修复（D2 100% 闭环）：
        - dispatch_rules 期望 ``task.rice.score`` 为整数
        - 但模型常返回 rice=None，评分嵌入 notes 文本（"综合评分 X/20"）
        - 本函数提供四级 fallback，保证 rice 始终是含 score 的字典

    优先级：
        1. it_rice 是字典且含 score → 强转 int 后保留
        2. it_rice 是数字 → 包装为 {"score": N}
        3. 从 fallback_notes / fallback_summary regex 提取
        4. 全部失败 → {"score": None, "extracted_from": "missing"}（触发 D2 fallback 规则）

    Args:
        it_rice: 模型给出的 rice 字段（可能是 dict / int / None / str）。
        fallback_notes: notes 文本，regex 提取兜底。
        fallback_summary: summary 文本，regex 提取兜底。

    Returns:
        规范化后的 rice 字典，至少含 ``score`` 键（值为 int 或 None）。
    """
    # 优先 1：it_rice 是字典且含 score
    if isinstance(it_rice, dict) and "score" in it_rice:
        try:
            normalized = dict(it_rice)
            normalized["score"] = int(normalized["score"])
            return normalized
        except (ValueError, TypeError):
            pass

    # 优先 2：it_rice 是数字（直接做 score）
    if isinstance(it_rice, (int, float)) and not isinstance(it_rice, bool):
        try:
            return {"score": int(it_rice)}
        except (ValueError, TypeError):
            pass

    # 优先 3：从 fallback 文本中 regex 提取
    score: Optional[int] = None
    for text in (fallback_notes, fallback_summary):
        if not text:
            continue
        # 匹配 "综合评分 X/20" / "综合评分均 X/20" / "评分 X" / "score: X" 等
        # [一-鿿]? 容忍 1 个中文助词字符（如"均"）
        m = re.search(
            r"(?:综合评分|评分|score)[一-鿿]?[:：\s]*(\d+)(?:/20)?",
            text,
            re.IGNORECASE,
        )
        if m:
            try:
                score = int(m.group(1))
                break
            except ValueError:
                continue

    if score is not None:
        return {"score": score, "extracted_from": "notes_regex"}

    # fallback：score 为 None（表示无数据，触发 D2 fallback 规则）
    return {"score": None, "extracted_from": "missing"}


def append_intel_tasks_to_active_tasks_yaml(
    active_tasks_path: Path,
    intel_tasks: list[dict[str, Any]],
    target_date: str,
) -> int:
    """把 intel-action 解析出的 INTEL 任务 append 到 active_tasks.yaml。

    规则：
        - 仅 ``status`` 为 ``inbox`` / ``in_progress`` / ``approved-pending-dispatch``
          的任务进入（排除 deferred / rejected / vetoed）
        - 已存在相同 ``id`` 的任务跳过（防止 cron 重跑导致重复入库）
        - 入库时统一覆盖 ``status=approved-pending-dispatch``，
          等 Lysander 主对话审查 + 派单（A3 闭环设计）
        - 写回时使用 ``yaml.safe_dump(allow_unicode=True, sort_keys=False)``
          保持中文 + 字段顺序

    Args:
        active_tasks_path: active_tasks.yaml 绝对路径。
        intel_tasks: 从模型响应解析得到的任务条目列表。
        target_date: 报告日期（YYYY-MM-DD），用于 last_updated + notes。

    Returns:
        实际新增的任务数量（已扣除重复 / 非法状态）。
    """
    if not intel_tasks:
        print("[Intel-Loop] intel_tasks 为空，无需写入", flush=True)
        return 0

    if not active_tasks_path.exists():
        print(
            f"[Intel-Loop] active_tasks.yaml 不存在：{active_tasks_path}",
            flush=True,
        )
        return 0

    raw = active_tasks_path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        print(
            f"[Intel-Loop] 解析 active_tasks.yaml 失败: "
            f"{type(exc).__name__}: {str(exc)[:200]}",
            flush=True,
        )
        return 0

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        tasks = []
        data["tasks"] = tasks

    existing_ids: set[str] = {
        str(t.get("id"))
        for t in tasks
        if isinstance(t, dict) and t.get("id")
    }

    accepted_statuses = {"inbox", "in_progress", "approved-pending-dispatch"}
    written = 0
    skipped_dup = 0
    skipped_status = 0

    for it in intel_tasks:
        intel_id = str(it.get("id", "")).strip()
        if not intel_id:
            continue

        raw_status = str(it.get("status", "")).strip().lower()
        # status 可能为空，按 inbox 兜底
        effective_status = raw_status or "inbox"
        if effective_status not in accepted_statuses:
            skipped_status += 1
            continue

        if intel_id in existing_ids:
            skipped_dup += 1
            continue

        existing_notes = str(it.get("notes") or "").strip()
        existing_summary = str(it.get("summary") or "").strip()
        decision_label = effective_status

        # D2 数据契约修复：rice 必须含 score 数字字段
        rice_normalized = _normalize_rice(
            it.get("rice"),
            fallback_notes=existing_notes,
            fallback_summary=existing_summary,
        )

        new_task: dict[str, Any] = {
            "id": intel_id,
            "title": it.get("title", ""),
            "status": "approved-pending-dispatch",
            "priority": it.get("priority", "P2"),
            "team": it.get("team", "harness_ops"),
            "assigned_to": it.get("assigned_to", "TBD"),
            "co_assigned": it.get("co_assigned"),
            "created": it.get("created", target_date),
            "follow_up": it.get("follow_up"),
            "execution_stage": "0",
            "blocker": None,
            "source": "intel-action 自动评估",
            "rice": rice_normalized,
            "summary": existing_summary[:500] if existing_summary else "",
            "notes": (
                existing_notes
                + (f" [A3 闭环：{target_date} 评估={decision_label}，"
                   f"自动入池待 Lysander 主对话派单]"
                   if existing_notes
                   else f"[A3 闭环：{target_date} 评估={decision_label}，"
                        f"自动入池待 Lysander 主对话派单]")
            )[:1500],
        }

        tasks.append(new_task)
        existing_ids.add(intel_id)
        written += 1

    if written > 0:
        data["last_updated"] = f"{target_date}T intel-action auto"

    print(
        f"[Intel-Loop] 入池统计：写入={written} 重复跳过={skipped_dup} "
        f"非法状态跳过={skipped_status} 模型给出={len(intel_tasks)}",
        flush=True,
    )

    if written > 0:
        with active_tasks_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                data,
                f,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=4096,
            )

    return written


def notify_intel_tasks_added(
    written_count: int,
    target_date: str,
    webhook: Optional[str] = None,
) -> bool:
    """WF-09 通知：今日新增 N 条 INTEL 自动入池。

    心跳策略：即使 written_count=0 也发一条 info 通知，
    便于总裁感知 A3 闭环每日运行心跳。

    Returns:
        True = Slack 投递成功；False = 失败 / 跳过。
    """
    if webhook is None:
        webhook = os.environ.get("SLACK_WEBHOOK_N8N")
    if not webhook:
        print(
            "[Intel-Loop] SLACK_WEBHOOK_N8N 未配置，跳过通知",
            flush=True,
        )
        return False

    title = f"📥 情报评估入池 {target_date}"
    if written_count > 0:
        body = (
            f"intel-action 自动评估完成\n"
            f"新增 {written_count} 条 INTEL 任务到 active_tasks.yaml\n"
            f"status=approved-pending-dispatch\n"
            f"等 Lysander 主对话审查 + 派单"
        )
    else:
        body = (
            f"intel-action 评估完成（{target_date}）\n"
            "本次无符合阈值的新任务（可能全部 deferred/rejected 或日报缺失）\n"
            "active_tasks.yaml 未变更"
        )

    return notify_slack(
        webhook_url=webhook,
        title=title,
        body=body,
        source="intel-action",
        priority="info",
    )


def run_action_report(
    target_date: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> Path:
    """生成行动报告 Markdown。

    Args:
        target_date: 昨日情报日报的日期（YYYY-MM-DD）。
        model: Claude 模型 ID。

    Returns:
        生成的 Markdown 文件路径。
    """
    target_date = _resolve_target_date(target_date or "")
    report_date = (
        datetime.strptime(target_date, "%Y-%m-%d").date() + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    print(
        f"[Start] 行动报告 target={target_date} report_date={report_date} "
        f"(model={model})"
    )

    # 1. 读 prompt + 昨日日报
    prompt_template = load_prompt("intelligence-action")
    system = _build_system_prompt(prompt_template)

    yesterday_report, source_filename = _load_yesterday_report(target_date)

    # 2. 构造 user 消息（注入昨日日报）
    user_msg = (
        f"目标日期：{report_date}\n"
        f"情报来源：{source_filename}\n"
        f"紧凑日期（任务 ID 用）：{report_date.replace('-', '')}\n\n"
        "## 昨日情报日报全文\n\n"
        + (yesterday_report if yesterday_report else "（昨日日报缺失，尽力评估）")
        + "\n\n---\n\n"
        "**严格输出一份 Markdown 行动报告**，按 prompt 规定的结构（包含"
        "评估概览 / 专家评估矩阵 / 行动任务清单 / 关键洞察 / 系统状态）。\n"
        "Markdown 之外可附一个 ```yaml 代码块，列出要追加到 active_tasks.yaml"
        "的新任务条目。"
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

    # 4. 写入 Markdown（response_text 本身就是 Markdown，按 prompt 约定）
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = REPORTS_DIR / f"{report_date}-action-report.md"

    header = (
        f"# 情报行动报告 {report_date}\n\n"
        f"**生成时间**：{datetime.now(timezone.utc).isoformat()}\n"
        f"**执行者**：ai_ml_engineer（情报评估）+ harness_engineer（报告生成）\n"
        f"**情报来源**：[{source_filename}]({source_filename})\n\n"
        "---\n\n"
    )

    # 如果模型已经输出了 `# 情报行动报告` 标题，就不重复加 header
    if response_text.lstrip().startswith("# 情报行动报告"):
        final_md = response_text
    else:
        final_md = header + response_text

    output_file.write_text(final_md, encoding="utf-8")
    print(f"[Done] 行动报告已写入 {output_file} ({len(final_md)} chars)")

    # 4.5 OBJ-INTEL-LOOP-CLOSURE 档 A3：解析 yaml 块 → append 到 active_tasks.yaml
    # 闭环范围：L2 评估层 → L3 inbox 层（派单仍归 Lysander 主对话）
    intel_tasks = _extract_intel_tasks_from_response(response_text)
    written = append_intel_tasks_to_active_tasks_yaml(
        ACTIVE_TASKS_YAML, intel_tasks, report_date
    )
    print(
        f"[Intel-Loop] 入池 {written} 条 INTEL 任务（闭环 L3）",
        flush=True,
    )

    # WF-09 通知（心跳：0 条也发，便于总裁感知运行）
    notify_intel_tasks_added(written, report_date)

    # 5. Slack 通知
    # NOTE: WF-09 Unified Notification (atit1zW3VYUL54CJ) 已切换为 keypair 模式（2026-04-25 by 总裁），自动安全转义 \n
    # 故恢复富文本 body（含路径 / 换行 / emoji）以充分利用通道能力
    webhook = os.environ.get("SLACK_WEBHOOK_N8N")
    if webhook:
        success = notify_slack(
            webhook_url=webhook,
            title=f"📋 Synapse 行动报告 {report_date}",
            body=(
                f"已评估并生成行动报告\n"
                f"报告：obs/06-daily-reports/{report_date}-action-report.md\n"
                f"情报来源：{source_filename}\n"
                f"报告大小：{len(final_md)} chars"
            ),
            source="intel-action",
            priority="info",
        )
        print(
            f"[Notify] Slack notification {'sent' if success else 'failed'} "
            f"(action, {report_date})",
            flush=True,
        )
    else:
        print(
            "[Notify] SLACK_WEBHOOK_N8N not set, skipped (action)",
            flush=True,
        )

    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Synapse 情报行动 Agent")
    parser.add_argument(
        "--target-date",
        default="",
        help="昨日情报日报的日期 YYYY-MM-DD（默认今日 UTC - 1）",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Claude 模型 ID（默认 {DEFAULT_MODEL}）",
    )
    args = parser.parse_args()

    run_action_report(
        target_date=args.target_date or None,
        model=args.model,
    )


if __name__ == "__main__":
    main()
