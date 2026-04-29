#!/usr/bin/env python3
"""
publish_to_bond.py — 将 Synapse-Mini 情报报告发布到 lysander-bond Content Collections

用途：
  - 情报快报 HTML → lysander-bond/src/content/intelligence/daily/{date}.md
  - 行动报告 MD   → lysander-bond/src/content/intelligence/results/{date}.md
  - 决策日志 MD   → lysander-bond/src/content/intelligence/decisions/{id}.md

调用方式：
  python publish_to_bond.py --type daily --date 2026-04-28
  python publish_to_bond.py --type results --date 2026-04-28
  python publish_to_bond.py --type decisions --id D-2026-0428-001
  python publish_to_bond.py --backfill-daily   # 回填所有历史日报
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ── 路径配置 ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
SYNAPSE_ROOT = SCRIPT_DIR.parent.parent
DAILY_REPORTS_DIR = SYNAPSE_ROOT / "obs" / "06-daily-reports"
DECISION_LOG_DIR = SYNAPSE_ROOT / "obs" / "04-decision-knowledge" / "decision-log"

# lysander-bond 仓库路径（GHA 中通过环境变量指定，本地默认相邻目录）
BOND_ROOT = Path(os.environ.get("BOND_REPO_DIR", str(SYNAPSE_ROOT.parent / "lysander-bond")))
BOND_INTEL_DAILY = BOND_ROOT / "src" / "content" / "intelligence" / "daily"
BOND_INTEL_RESULTS = BOND_ROOT / "src" / "content" / "intelligence" / "results"
BOND_INTEL_DECISIONS = BOND_ROOT / "src" / "content" / "intelligence" / "decisions"


def extract_html_intel(html_path: Path) -> dict:
    """从 HTML 日报提取结构化数据"""
    html = html_path.read_text(encoding="utf-8", errors="ignore")

    # 提取日期
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", html_path.name)
    date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    # 提取情报条目标题
    titles = re.findall(r'class="item-title"[^>]*>([^<]+)<', html)
    if not titles:
        titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', html)
    # 若标题正则均未命中，尝试从 KPI 数字或 class="item" 计数中回填
    if not titles:
        kpi_match = re.search(r'<div class="num">(\d+)</div><div class="label">精选情报条目</div>', html)
        if kpi_match and int(kpi_match.group(1)) > 0:
            titles = [f"item_{i}" for i in range(int(kpi_match.group(1)))]
        else:
            item_divs = re.findall(r'class="item"', html)
            if item_divs:
                titles = [f"item_{i}" for i in range(len(item_divs))]

    # 提取总结
    summary_match = re.search(r'class="summary-box"[^>]*>(.*?)</div>', html, re.DOTALL)
    summary_text = ""
    if summary_match:
        raw = summary_match.group(1)
        summary_text = re.sub(r'<[^>]+>', '', raw).strip()[:300]

    # 提取分数
    scores = re.findall(r'"total":\s*(\d+)', html)
    top_score = max([int(s) for s in scores]) if scores else None

    # 生成 markdown 正文
    items_md = ""
    item_blocks = re.findall(r'class="item"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
    for block in item_blocks[:10]:  # 最多取 10 条
        title = re.search(r'class="item-title"[^>]*>([^<]+)<', block)
        summary = re.search(r'class="item-summary"[^>]*>([^<]+)<', block)
        action = re.search(r'class="recommended-action"[^>]*>([^<]+)<', block)
        total = re.search(r'"total":\s*(\d+)', block)
        if title:
            items_md += f"\n### {title.group(1).strip()}\n"
            if summary:
                items_md += f"\n{summary.group(1).strip()}\n"
            if action:
                items_md += f"\n**建议行动：** {action.group(1).strip()}\n"
            if total:
                items_md += f"\n**综合评分：** {total.group(1)}/20\n"

    return {
        "date": date,
        "title": f"{date} 情报快报",
        "summary": summary_text[:200] if summary_text else f"Synapse AI 团队 {date} 情报扫描报告",
        "itemCount": len(titles),
        "topScore": top_score,
        "tags": ["情报快报", "AI动态", date[:7]],
        "items_md": items_md,
    }


def publish_daily(date: str = None, html_path: Path = None):
    """发布情报快报到 lysander-bond"""
    if html_path is None:
        date = date or datetime.now().strftime("%Y-%m-%d")
        html_path = DAILY_REPORTS_DIR / f"{date}-intelligence-daily.html"

    if not html_path.exists():
        print(f"[SKIP] HTML not found: {html_path}")
        return False

    data = extract_html_intel(html_path)
    date = data["date"]

    out_path = BOND_INTEL_DAILY / f"{date}.md"
    if out_path.exists():
        print(f"[SKIP] Already exists: {out_path.name}")
        return False

    BOND_INTEL_DAILY.mkdir(parents=True, exist_ok=True)
    content = f"""---
title: "{data['title']}"
date: "{date}"
publishDate: {date}T08:00:00.000Z
summary: "{data['summary'].replace(chr(10), ' ').replace(chr(13), ' ').replace('"', "'")[:300].strip()}"
itemCount: {data['itemCount']}
{f"topScore: {data['topScore']}" if data['topScore'] else ""}
lang: zh
tags:
{chr(10).join(f"  - {t}" for t in data['tags'])}
source: intel-daily-agent
---

## 今日情报摘要

{data['summary']}

## 精选情报

{data['items_md'] if data['items_md'] else '_情报详情请查看完整报告_'}

---

> 本报告由 Synapse AI 团队情报管线自动生成，每日 Dubai 08:00 更新。
"""
    out_path.write_text(content, encoding="utf-8")
    print(f"[OK] Published daily: {out_path.name}")
    return True


def publish_results(date: str = None, md_path: Path = None):
    """发布行动结果到 lysander-bond"""
    if md_path is None:
        date = date or datetime.now().strftime("%Y-%m-%d")
        md_path = DAILY_REPORTS_DIR / f"{date}-action-report.md"

    if not md_path.exists():
        print(f"[SKIP] MD not found: {md_path}")
        return False

    raw = md_path.read_text(encoding="utf-8")

    # 提取 date
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", md_path.name)
    date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    # 提取行动数量
    # 优先从概览表格中提取（"进入行动清单 | 7" 或 "新增行动任务 | 7"）
    actions_table = re.search(r'(?:进入行动清单|新增行动任务)[^|]*\|\s*(\d+)', raw)
    if actions_table:
        actions = list(range(int(actions_table.group(1))))  # placeholder list for len()
    else:
        actions = re.findall(r'- id: (INTEL-\S+)', raw)
    completed = re.findall(r'status: (completed|approved)', raw)

    # 提取摘要（取前 200 字）
    summary_match = re.search(r'##\s+.{2,20}\n+(.{50,})', raw)
    summary = summary_match.group(1)[:200] if summary_match else f"{date} 行动报告"

    out_path = BOND_INTEL_RESULTS / f"{date}.md"
    if out_path.exists():
        print(f"[SKIP] Already exists: {out_path.name}")
        return False

    BOND_INTEL_RESULTS.mkdir(parents=True, exist_ok=True)
    content = f"""---
title: "{date} 执行行动报告"
date: "{date}"
publishDate: {date}T10:00:00.000Z
summary: "{summary.replace(chr(10), ' ').replace(chr(13), ' ').replace('"', "'")[:300].strip()}"
actionsCount: {len(actions)}
completedCount: {len(completed)}
lang: zh
tags:
  - 执行结果
  - 行动报告
  - {date[:7]}
source: intel-action-agent
---

{raw}
"""
    out_path.write_text(content, encoding="utf-8")
    print(f"[OK] Published results: {out_path.name}")
    return True


def _parse_decision_file(raw: str, md_file: Path) -> dict | None:
    """解析决策文件，支持 YAML frontmatter 和 Markdown 标题两种格式"""
    # 格式 A：YAML frontmatter
    fm_match = re.search(r'^---\n(.*?)\n---', raw, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        doc_id = re.search(r'id:\s*(\S+)', fm)
        title_m = re.search(r'title:\s*["\']?([^"\'\n]+)', fm)
        # decided_at / date / published_at いずれかを受け入れる
        date_m = (re.search(r'decided_at:\s*(\S+)', fm)
                  or re.search(r'(?<!published_)date:\s*(\S+)', fm)
                  or re.search(r'published_at:\s*["\']?(\d{4}-\d{2}-\d{2})', fm))
        level_m = re.search(r'decision_level:\s*(\S+)', fm)
        decided_m = (re.search(r'decided_by:\s*(.+)', fm)
                     or re.search(r'(?:approved_by|approver):\s*(.+)', fm))
        if not doc_id:
            return None
        if not date_m:
            # 从文件名取日期
            fn_date = re.search(r'(\d{4}-\d{2}-\d{2})', md_file.name)
            date_val = fn_date.group(1) if fn_date else "2026-01-01"
        else:
            date_val = date_m.group(1).strip().strip('"').strip("'")
        body = raw[fm_match.end():].strip()
        # 从文件名或正文中取 title
        if title_m:
            title_val = title_m.group(1).strip()
        else:
            heading = re.search(r'^#\s+(.+)', body, re.MULTILINE)
            title_val = heading.group(1).strip() if heading else md_file.stem
        # 规范化 id（全小写时退回文件名）
        raw_id = doc_id.group(1).strip()
        canonical_id = md_file.stem if raw_id == raw_id.lower() and '-' in raw_id else raw_id
        return {
            "id": canonical_id,
            "title": title_val,
            "date": date_val,
            "level": level_m.group(1).strip() if level_m else "L3",
            "decided_by": decided_m.group(1).strip() if decided_m else "Lysander",
            "body": body,
        }

    # 格式 B：纯 Markdown 标题格式（旧格式）
    id_match = re.search(r'决策\s*ID[^\w]*(D-[\w-]+)', raw)
    if not id_match:
        # 从文件名中取 ID
        file_id = md_file.stem
    else:
        file_id = id_match.group(1).strip()

    date_m = re.search(r'日期[^\d]*(2026-\d{2}-\d{2})', raw)
    if not date_m:
        date_m = re.search(r'(2026-\d{2}-\d{2})', md_file.name)
        date_val = date_m.group(1) if date_m else "2026-04-01"
    else:
        date_val = date_m.group(1)

    heading = re.search(r'^#\s+(.+)', raw, re.MULTILINE)
    title_val = heading.group(1).strip() if heading else file_id

    level_m = re.search(r'决策级别[^\w]*(L\d)', raw)
    decided_m = re.search(r'决策者[^：:\n]*[：:]\s*(.+)', raw)

    return {
        "id": file_id,
        "title": title_val,
        "date": date_val,
        "level": level_m.group(1) if level_m else "L3",
        "decided_by": decided_m.group(1).strip() if decided_m else "Lysander",
        "body": raw,
    }


def publish_decisions():
    """同步所有决策日志到 lysander-bond"""
    BOND_INTEL_DECISIONS.mkdir(parents=True, exist_ok=True)
    count = 0
    for md_file in sorted(DECISION_LOG_DIR.glob("D-*.md")):
        raw = md_file.read_text(encoding="utf-8")

        parsed = _parse_decision_file(raw, md_file)
        if not parsed:
            print(f"[SKIP] Cannot parse: {md_file.name}")
            continue

        out_path = BOND_INTEL_DECISIONS / f"{parsed['id']}.md"
        if out_path.exists():
            continue

        # 构造摘要（取正文第一有效段）
        summary_match = re.search(r'\n\n([^\n#]{30,})', parsed["body"])
        summary = summary_match.group(1).strip()[:200] if summary_match else parsed["title"]

        content = f"""---
id: "{parsed['id']}"
title: "{parsed['title'].replace('"', "'")}"
date: "{parsed['date']}"
publishDate: {parsed['date']}T00:00:00.000Z
decisionLevel: "{parsed['level']}"
decidedBy: "{parsed['decided_by'].replace('"', "'")}"
summary: "{summary.replace(chr(10), ' ').replace(chr(13), ' ').replace('"', "'")[:300].strip()}"
lang: zh
tags:
  - 执行决策
  - {parsed['level']}
---

{parsed['body']}
"""
        out_path.write_text(content, encoding="utf-8")
        print(f"[OK] Published decision: {out_path.name}")
        count += 1

    print(f"Synced {count} decision(s)")
    return count


def backfill_daily():
    """回填所有历史情报日报"""
    html_files = sorted(DAILY_REPORTS_DIR.glob("*-intelligence-daily.html"))
    print(f"Found {len(html_files)} HTML daily reports to process")
    published = 0
    for f in html_files:
        if publish_daily(html_path=f):
            published += 1
    print(f"Backfill complete: {published}/{len(html_files)} published")


def backfill_results():
    """回填所有历史行动报告"""
    md_files = sorted(DAILY_REPORTS_DIR.glob("*-action-report.md"))
    print(f"Found {len(md_files)} action report(s)")
    published = 0
    for f in md_files:
        if publish_results(md_path=f):
            published += 1
    print(f"Backfill complete: {published}/{len(md_files)} published")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["daily", "results", "decisions"])
    parser.add_argument("--date")
    parser.add_argument("--id")
    parser.add_argument("--backfill-daily", action="store_true")
    parser.add_argument("--backfill-results", action="store_true")
    parser.add_argument("--backfill-decisions", action="store_true")
    args = parser.parse_args()

    if args.backfill_daily:
        backfill_daily()
    elif args.backfill_results:
        backfill_results()
    elif args.backfill_decisions or (args.type == "decisions"):
        publish_decisions()
    elif args.type == "daily":
        publish_daily(date=args.date)
    elif args.type == "results":
        publish_results(date=args.date)
    else:
        parser.print_help()
