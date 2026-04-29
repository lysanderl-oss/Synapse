#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Week 2.2 Golden Set Equivalence Diff"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
import json
import re

REPORTS = Path(r"C:\Users\lysanderl_janusd\Synapse-Mini\obs\06-daily-reports")

# ============ 步骤 1：情报日报 HTML diff ============
try:
    from bs4 import BeautifulSoup
    HAVE_BS4 = True
except ImportError:
    HAVE_BS4 = False

GOLDEN_HTML = ["2026-04-19-intelligence-daily.html", "2026-04-20-intelligence-daily.html", "2026-04-21-intelligence-daily.html"]
NEW_HTML = "2026-04-24-intelligence-daily.html"

def analyze_html_bs4(path):
    html = (REPORTS / path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    all_classes = []
    for el in soup.find_all():
        cls = el.get("class")
        if cls:
            all_classes.extend(cls)
    features = {
        "file": path,
        "title_exists": bool(soup.find("h1") or soup.find("title")),
        "has_kpi": bool(soup.select(".kpi-row, .summary-box, .kpi, .stats, .kpi-card, .metric")),
        "items_count": len(soup.select(".item, .intelligence-item, article, .card, .news-item, .entry")),
        "urgent_items": len(soup.select(".urgent, .item-urgent, .high-priority")),
        "tags_used": sorted(list(set([cls for el in soup.select(".tag, .badge, .label") for cls in el.get("class", [])]))),
        "css_class_set": sorted(list(set(all_classes)))[:40],
        "total_length": len(html),
        "has_style_block": bool(soup.find("style")),
        "h1_count": len(soup.find_all("h1")),
        "h2_count": len(soup.find_all("h2")),
        "h3_count": len(soup.find_all("h3")),
    }
    return features

def analyze_html_regex(path):
    """Fallback if bs4 missing"""
    html = (REPORTS / path).read_text(encoding="utf-8")
    classes = re.findall(r'class=["\']([^"\']+)["\']', html)
    class_set = set()
    for c in classes:
        for token in c.split():
            class_set.add(token)
    features = {
        "file": path,
        "title_exists": bool(re.search(r'<h1[\s>]|<title>', html)),
        "has_kpi": bool(re.search(r'class="[^"]*(kpi|summary-box|stats|metric)', html)),
        "items_count": len(re.findall(r'<(article|div)[^>]*class="[^"]*(item|intelligence-item|card|news-item|entry)[^"]*"', html)),
        "urgent_items": len(re.findall(r'class="[^"]*(urgent|item-urgent|high-priority)', html)),
        "tags_used": sorted([c for c in class_set if 'tag' in c.lower() or 'badge' in c.lower()])[:20],
        "css_class_set": sorted(list(class_set))[:40],
        "total_length": len(html),
        "has_style_block": '<style' in html,
        "h1_count": len(re.findall(r'<h1[\s>]', html)),
        "h2_count": len(re.findall(r'<h2[\s>]', html)),
        "h3_count": len(re.findall(r'<h3[\s>]', html)),
    }
    return features

analyze_html = analyze_html_bs4 if HAVE_BS4 else analyze_html_regex
print(f"[HTML analyzer] using {'bs4' if HAVE_BS4 else 'regex fallback'}")

golden_html_feats = [analyze_html(f) for f in GOLDEN_HTML]
new_html_feats = analyze_html(NEW_HTML)

def equiv_html(golden_list, new):
    field_match = 0
    total_fields = 4
    # title
    if any(g["title_exists"] for g in golden_list) == new["title_exists"]: field_match += 1
    # kpi
    if any(g["has_kpi"] for g in golden_list) == new["has_kpi"]: field_match += 1
    # style block
    if any(g["has_style_block"] for g in golden_list) == new["has_style_block"]: field_match += 1
    # h2 presence
    if (sum(g["h2_count"] for g in golden_list) > 0) == (new["h2_count"] > 0): field_match += 1

    avg_items = sum(g["items_count"] for g in golden_list) / max(1, len(golden_list))
    if avg_items == 0:
        in_range = (new["items_count"] == 0)
    else:
        in_range = avg_items * 0.5 <= new["items_count"] <= avg_items * 1.5

    golden_classes = set()
    for g in golden_list:
        golden_classes.update(g["css_class_set"])
    new_classes = set(new["css_class_set"])
    overlap = len(golden_classes & new_classes) / len(golden_classes) if golden_classes else 0

    avg_length = sum(g["total_length"] for g in golden_list) / max(1, len(golden_list))
    length_ratio = new["total_length"] / avg_length if avg_length else 0

    return {
        "field_match": f"{field_match}/{total_fields}",
        "field_match_pct": field_match / total_fields,
        "items_in_range": in_range,
        "avg_golden_items": avg_items,
        "new_items": new["items_count"],
        "css_overlap_rate_pct": round(overlap * 100, 1),
        "golden_class_union_size": len(golden_classes),
        "new_class_set_size": len(new_classes),
        "shared_classes": sorted(list(golden_classes & new_classes))[:30],
        "avg_golden_length": int(avg_length),
        "new_length": new["total_length"],
        "length_ratio": round(length_ratio, 2),
    }

html_score = equiv_html(golden_html_feats, new_html_feats)

# ============ 步骤 2：行动报告 Markdown diff ============
# Note: 2026-04-21-action-report.md doesn't exist; substituting 2026-04-17-action-report.md as 3rd golden
# Note: 2026-04-25-action-report.md (Week 2 batch 1) doesn't exist — reporting as blocker
GOLDEN_MD = ["2026-04-17-action-report.md", "2026-04-19-action-report.md", "2026-04-20-action-report.md"]
NEW_MD = "2026-04-25-action-report.md"

def analyze_md(path):
    p = REPORTS / path
    if not p.exists():
        return {"file": path, "missing": True}
    text = p.read_text(encoding="utf-8")
    features = {
        "file": path,
        "missing": False,
        "h1_count": len(re.findall(r"^# ", text, re.MULTILINE)),
        "h2_count": len(re.findall(r"^## ", text, re.MULTILINE)),
        "h3_count": len(re.findall(r"^### ", text, re.MULTILINE)),
        "table_rows": len(re.findall(r"^\|", text, re.MULTILINE)),
        "has_strategy_expert": bool(re.search(r"战略|strategy_advisor|graphify_strategist", text, re.IGNORECASE)),
        "has_product_expert": bool(re.search(r"产品|synapse_product_owner|product_owner", text, re.IGNORECASE)),
        "has_tech_expert": bool(re.search(r"技术|ai_ml_engineer|harness_engineer|tech", text, re.IGNORECASE)),
        "has_financial_expert": bool(re.search(r"财务|financial_analyst|finance", text, re.IGNORECASE)),
        "has_execute_decision": bool(re.search(r"execute|执行|批准", text, re.IGNORECASE)),
        "has_inbox_decision": bool(re.search(r"inbox|收件箱|待办", text, re.IGNORECASE)),
        "has_deferred_decision": bool(re.search(r"deferred|延期|推迟|defer", text, re.IGNORECASE)),
        "has_summary_section": bool(re.search(r"总结|summary|关键洞察|系统状态|key insight", text, re.IGNORECASE)),
        "total_length": len(text),
        "line_count": text.count("\n") + 1,
    }
    return features

golden_md_feats = [analyze_md(f) for f in GOLDEN_MD]
new_md_feats = analyze_md(NEW_MD)

def equiv_md(golden_list, new):
    if new.get("missing"):
        return {"error": "NEW markdown file missing", "new_file": new["file"]}
    valid_golden = [g for g in golden_list if not g.get("missing")]
    if not valid_golden:
        return {"error": "All golden markdown missing"}

    fields = ["has_strategy_expert", "has_product_expert", "has_tech_expert", "has_financial_expert",
              "has_execute_decision", "has_inbox_decision", "has_deferred_decision", "has_summary_section"]
    field_match = 0
    field_detail = {}
    for f in fields:
        g_val = any(g[f] for g in valid_golden)
        n_val = new[f]
        match = (g_val == n_val)
        if match: field_match += 1
        field_detail[f] = {"golden_any": g_val, "new": n_val, "match": match}

    avg_h2 = sum(g["h2_count"] for g in valid_golden) / len(valid_golden)
    avg_tables = sum(g["table_rows"] for g in valid_golden) / len(valid_golden)
    avg_length = sum(g["total_length"] for g in valid_golden) / len(valid_golden)

    return {
        "field_match": f"{field_match}/{len(fields)}",
        "field_match_pct": field_match / len(fields),
        "field_detail": field_detail,
        "avg_golden_h2": avg_h2,
        "new_h2": new["h2_count"],
        "avg_golden_tables": avg_tables,
        "new_tables": new["table_rows"],
        "avg_golden_length": int(avg_length),
        "new_length": new["total_length"],
        "length_ratio": round(new["total_length"] / avg_length, 2) if avg_length else 0,
    }

md_score = equiv_md(golden_md_feats, new_md_feats)

# ============ 输出 ============
result = {
    "html_diff": {
        "golden_features": golden_html_feats,
        "new_features": new_html_feats,
        "score": html_score,
    },
    "md_diff": {
        "golden_features": golden_md_feats,
        "new_features": new_md_feats,
        "score": md_score,
    }
}

out_path = Path(r"C:\Users\lysanderl_janusd\Synapse-Mini\logs\week2-golden-diff-raw.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[OK] raw diff saved to {out_path}")
print("\n====== HTML SCORE ======")
print(json.dumps(html_score, ensure_ascii=False, indent=2))
print("\n====== MD SCORE ======")
print(json.dumps(md_score, ensure_ascii=False, indent=2))
