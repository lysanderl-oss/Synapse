"""
情报日报 Agent — Q2 版本（GitHub Actions 调度）

调用链：
    intel-daily.yml (06:00 Dubai, workflow_dispatch)
        → daily_agent.py
        → Claude API (sonnet-4-6)
        → obs/06-daily-reports/{date}-intelligence-daily.html
        → Slack 通知

Usage:
    python daily_agent.py [--date YYYY-MM-DD] [--model MODEL]
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from jinja2 import Template

from shared_context import (
    CLAUDE_MD_MAX_CHARS,
    DEFAULT_MODEL,
    REPO_ROOT,
    REPORTS_DIR,
    TEMPLATES_DIR,
    call_claude,
    extract_json_block,
    load_active_tasks,
    load_claude_md,
    load_organization_yaml,
    load_prompt,
    notify_slack,
)


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------

def _build_system_prompt(prompt_template: str) -> str:
    """将 prompt.md + CLAUDE.md 摘要 + organization.yaml 组装成 system。

    大段内容全部进 system，打开 prompt caching 后可 5 分钟内免费复用。
    """
    claude_md = load_claude_md(truncate=True)
    org_yaml = load_organization_yaml()

    parts = [
        prompt_template,
        "\n\n# Synapse 上下文 — CLAUDE.md（截断至 "
        f"{CLAUDE_MD_MAX_CHARS} 字）\n\n{claude_md}",
    ]
    if org_yaml:
        parts.append(
            "\n\n# Organization YAML（供路由参考）\n\n```yaml\n"
            + org_yaml[:8000]
            + "\n```"
        )
    return "".join(parts)


def _fallback_data(response_text: str, report_date: str) -> dict[str, Any]:
    """Claude 未按 JSON 返回时的兜底：降级为纯文本 executive_summary。"""
    return {
        "intelligence_items": [],
        "executive_summary": [
            "（注：Claude 未按 JSON schema 返回，以下为原始文本降级展示）",
            response_text[:4000],
        ],
        "urgent_items": [],
        "kpi": {
            "min_score": 0,
            "topic_count": 0,
            "decision_level": "L3",
        },
    }


def _render_html(data: dict[str, Any], report_date: str) -> str:
    """用 Jinja2 模板渲染 HTML。"""
    template_path = TEMPLATES_DIR / "intelligence-daily.html.j2"
    template = Template(template_path.read_text(encoding="utf-8"))

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    kpi = data.get("kpi", {}) or {}

    return template.render(
        report_date=report_date,
        generated_at=generated_at,
        executor_id=os.environ.get("EXECUTOR_ID", "github-actions-bot"),
        intelligence_items=data.get("intelligence_items", []) or [],
        executive_summary=data.get("executive_summary", []) or [],
        urgent_items=data.get("urgent_items", []) or [],
        show_kpi=bool(kpi) or bool(data.get("intelligence_items")),
        min_score=kpi.get("min_score", 8),
        topic_count=kpi.get("topic_count", 6),
        decision_level=kpi.get("decision_level", "L3"),
        coverage_period=data.get("coverage_period", "过去 24 小时"),
    )


def run_daily_report(
    date_str: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> Path:
    """生成情报日报，写入 ``obs/06-daily-reports/{date}-intelligence-daily.html``。

    Args:
        date_str: 报告日期（YYYY-MM-DD）。None 则取今日 UTC。
        model: Claude 模型 ID。

    Returns:
        生成的 HTML 文件路径。
    """
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"[Start] 情报日报 for {date_str} (model={model})")

    # 1. 读 prompt
    prompt_template = load_prompt("intelligence-daily")
    system = _build_system_prompt(prompt_template)

    # 2. 构造 user 消息
    user_msg = (
        f"请生成 {date_str} 的 Synapse 情报日报。\n\n"
        "**严格要求输出一个 ```json 代码块**，schema 如下：\n"
        "```json\n"
        "{\n"
        '  "report_date": "YYYY-MM-DD",\n'
        '  "intelligence_items": [\n'
        "    {\n"
        '      "title": "…",\n'
        '      "source_name": "…",\n'
        '      "source_url": "https://…",\n'
        '      "published_at": "YYYY-MM-DD",\n'
        '      "summary": "≤100字核心要点",\n'
        '      "score": {"strategy":5,"product":5,"tech":5,"risk":5,"total":20},\n'
        '      "recommended_action": "inbox|backlog|L2 评审|立即执行",\n'
        '      "tags": ["Anthropic","Agent"]\n'
        "    }\n"
        "  ],\n"
        '  "urgent_items": [],\n'
        '  "executive_summary": ["段落1", "段落2", "段落3"],\n'
        '  "kpi": {"min_score":8,"topic_count":6,"decision_level":"L3"}\n'
        "}\n"
        "```\n\n"
        "目标 6-9 条精华情报。所有中文内容。"
    )

    # 3. 调用 Claude（prompt caching + task_budget 已内置）
    response_text = call_claude(
        system=system,
        user=user_msg,
        model=model,
        max_tokens=8000,
        task_budget=50_000,
        cache_system=True,
    )

    # 4. 解析 JSON（fallback 到纯文本）
    data = extract_json_block(response_text)
    if data is None:
        print("[Warn] 无法解析 JSON 响应，降级为纯文本摘要模式")
        data = _fallback_data(response_text, date_str)

    # 5. 渲染 HTML
    html = _render_html(data, date_str)

    # 6. 写入 obs/06-daily-reports/
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = REPORTS_DIR / f"{date_str}-intelligence-daily.html"
    output_file.write_text(html, encoding="utf-8")
    print(f"[Done] 情报日报已写入 {output_file} ({len(html)} chars)")

    # 7. Slack 通知（best-effort）
    # NOTE: WF-09 Unified Notification (atit1zW3VYUL54CJ) 已切换为 keypair 模式（2026-04-25 by 总裁），自动安全转义 \n
    # 故恢复富文本 body（含路径 / 换行 / emoji）以充分利用通道能力
    webhook = os.environ.get("SLACK_WEBHOOK_N8N")
    if webhook:
        n_items = len(data.get("intelligence_items", []) or [])
        success = notify_slack(
            webhook_url=webhook,
            title=f"📊 Synapse 情报日报 {date_str}",
            body=(
                f"已生成 {n_items} 条情报\n"
                f"报告：obs/06-daily-reports/{date_str}-intelligence-daily.html\n"
                f"模型：{model}\n"
                f"HTML 大小：{len(html)} chars"
            ),
            source="intel-daily",
            priority="info",
        )
        print(
            f"[Notify] Slack notification {'sent' if success else 'failed'} "
            f"(daily, {date_str})",
            flush=True,
        )
    else:
        print(
            "[Notify] SLACK_WEBHOOK_N8N not set, skipped (daily)",
            flush=True,
        )

    return output_file


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Synapse 情报日报 Agent")
    parser.add_argument(
        "--date",
        default="",
        help="报告日期 YYYY-MM-DD（空则今日 UTC）",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Claude 模型 ID（默认 {DEFAULT_MODEL}）",
    )
    args = parser.parse_args()

    run_daily_report(
        date_str=args.date or None,
        model=args.model,
    )


if __name__ == "__main__":
    main()
