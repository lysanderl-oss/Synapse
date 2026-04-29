#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synapse Dashboard Creator
Creates Claude Code 成果物 Dashboard in Lysander-AI Hub.
"""
import json
import urllib.request
import urllib.error
import sys

NOTION_TOKEN = "ntn_A46470290049IHNiJROzZb4JhhP8OAb5bpPH4RzFqHkggj"
NOTION_VERSION = "2022-06-28"
HUB_PAGE_ID = "34d114fc-090c-8161-a690-f613c4401b6a"
API_BASE = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}


def notion_request(method, path, data=None):
    url = f"{API_BASE}{path}"
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        sys.stderr.buffer.write(f"HTTP ERROR {e.code}: {error_body[:500]}\n".encode("utf-8"))
        return json.loads(error_body), e.code


def create_page(parent_id, title, children=None):
    data = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        }
    }
    if children:
        data["children"] = children[:100]
    return notion_request("POST", "/pages", data)


def append_blocks(page_id, children):
    # Notion API: max 100 blocks per request
    for i in range(0, len(children), 100):
        batch = children[i:i+100]
        resp, status = notion_request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
        if status not in (200, 201):
            return resp, status
    return resp, status


# ─── Block helpers ────────────────────────────────────────────────────────────

def callout(text, icon="📋", color="blue_background"):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"type": "emoji", "emoji": icon},
            "color": color
        }
    }


def heading2(text):
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def heading3(text):
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def paragraph(text, color=None):
    block = {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }
    if color:
        block["paragraph"]["color"] = color
    return block


def bullet(text):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def toggle(title, children):
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": title}}],
            "children": children
        }
    }


def table_row(cells):
    return {
        "object": "block",
        "type": "table_row",
        "table_row": {
            "cells": [[{"type": "text", "text": {"content": c}}] for c in cells]
        }
    }


def table_block(rows, has_column_header=True):
    """rows: list of lists of strings. First row = header."""
    children = [table_row(r) for r in rows]
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": len(rows[0]) if rows else 3,
            "has_column_header": has_column_header,
            "has_row_header": False,
            "children": children
        }
    }


# ─── Dashboard blocks ─────────────────────────────────────────────────────────

DASHBOARD_BLOCKS = [
    # Block 1: Callout — page intro
    callout(
        "本页汇总 Synapse 体系通过 Claude Code 生成的所有有价值成果物，共 52 项，按类型分层展示。"
        "最后更新：2026-04-27",
        "📋", "blue_background"
    ),

    # Block 2: Overview stats
    heading2("总览 · 整体维度"),
    callout("A类（对外商业）：9 项 | 3 份可下载附件", "🏆", "yellow_background"),
    callout("B类（体系里程碑）：17 项 | PMO GA x3 + 情报管线 + 战略决策", "🚀", "green_background"),
    callout("C类（知识沉淀）：19 项 | 方法论 + SOP + 架构设计", "📚", "purple_background"),
    callout("D类（运营数据）：7 组 | 情报日报 + 行动报告 + 审计", "📊", "gray_background"),

    divider(),

    # Block 4: A类成果物
    heading2("A类 — 对外展示 / 商业材料"),
    paragraph("这些文档可直接对外展示，适合向潜在客户、合作方或投资人传递。"),

    table_block([
        ["文档名称", "描述", "格式 / 路径"],
        [
            "Synapse 商业价值白皮书",
            "全景商业价值文档，五层架构、56 Agent、Level 5（前0.5%）定位，2026-04-26 快照，主对外宣传文件",
            "PDF | obs/06-daily-reports/synapse-commercial-value.pdf"
        ],
        [
            "Synapse for 金融租赁 — 推广提案",
            "面向金融租赁企业的定制应用方案，含监管约束、业务映射、三阶段落地路径，智囊团评审通过",
            "PDF | obs/06-daily-reports/finlease-synapse-proposal.pdf"
        ],
        [
            "金融租赁开发团队调研问卷",
            "企业 AI 能力评估问卷，25题，涵盖开发环境/工具/AI成熟度/合规约束",
            "DOCX | obs/06-daily-reports/finlease-dev-survey.docx"
        ],
        [
            "Synapse v3.0 产品介绍页",
            "高质量深色主题 HTML 产品落地页，定位「AI 多智能体操作系统」，适合对外展示",
            "HTML"
        ],
        [
            "Synapse 成果展示 PPT（HTML）",
            "深色主题演示文件，Janus Digital 2026.04 成果展示版，适合演示场合",
            "HTML"
        ],
        [
            "Synapse 咨询服务销售单页",
            "面向企业管理者的服务一页纸，核心价值主张+差异化+服务内容",
            "MD"
        ],
        [
            "Synapse v3.0 设计提案（英文）",
            "英文版 Canonical System Design Proposal，体系最权威英文对外文档",
            "MD"
        ],
    ]),

    paragraph(
        "可下载附件本地路径：\n"
        "  白皮书 PDF → obs/06-daily-reports/synapse-commercial-value.pdf\n"
        "  金融租赁提案 PDF → obs/06-daily-reports/finlease-synapse-proposal.pdf\n"
        "  调研问卷 DOCX → obs/06-daily-reports/finlease-dev-survey.docx",
        "gray"
    ),

    divider(),

    # Block 6: B类里程碑
    heading2("B类 — 体系里程碑 / 技术成就"),
    paragraph("记录 Synapse 体系重大技术里程碑，是体系建设能力的实证材料。"),

    toggle(
        "📦 PMO Auto 产品系列（V2.0 → V2.3 GA）",
        [
            bullet("PMO Auto V2.0 GA 验收报告 — 首个 GA 里程碑，6 项测试全通过，2026-04-23"),
            bullet("PMO Auto V2.2 GA 验收报告 — Webhook 监控+WF-09 告警+git 部署，2026-04-24"),
            bullet("PMO Auto V2.3 发布报告 — Docker 重建+邮箱传参修复，镜像 sha256 留证，2026-04-25"),
            bullet("产品委员会 V2.0 GA 评审纪要 — 首份正式产品委员会记录，2026-04-23"),
        ]
    ),

    toggle(
        "🔄 情报管线自动化系列",
        [
            bullet("Q2 情报管线 Week 2 完成报告 — 迁移至 GitHub Actions+Claude API，三 workflow 通过，2026-04-24"),
            bullet("情报管线全自动方案重评估报告 — OBJ-INTEL-LOOP-CLOSURE 关键决策，2026-04-26"),
            bullet("情报管线自进化闭环审计报告 — integration_qa 独立实证，四步闭环状态确认，2026-04-26"),
            bullet("D2 全自动 INTEL 消化设计文档 — dispatch_rules 5 条规则，技术设计核心，2026-04-26"),
            bullet("OBJ-BLOG-PIPELINE-CLOUD 完成报告 — 博客管线完全云端化，infra v1.0.6，2026-04-26"),
            bullet("OBJ-N8N-WORKFLOW-AUDIT 完成报告 — 47 条工作流全量审计，infra v1.0.5，2026-04-25"),
        ]
    ),

    toggle(
        "🏗️ 体系评审与战略决策",
        [
            bullet("Synapse 体系综合评审报告（2026-04-22）— 三维度综合评审，技术架构 7.1/10，行业定位领先"),
            bullet("Synapse Multi-Agent 体系进化方案主报告（2026-04-21）— 完整进化路线图，10 条决议"),
            bullet("双目录整合决策报告 — ai-team-system 与 Synapse-Mini 整合，整合价值评级高"),
            bullet("战略审批包 2026-04-26 — 三大议题综评，16项P0立即执行"),
            bullet("战略审批包 2026-04-27 — 14个机制实际运行状态实证，8机制硬上限决策"),
            bullet("v1.0-bilingual 发布审批包 — 全站108个URL双语化达成，两轮 UAT 通过"),
            bullet("W17 Agent 能力周审计 — 46 Agent 全员100%达标，体系治理成熟度证明"),
        ]
    ),

    divider(),

    # Block 8: C类知识沉淀
    heading2("C类 — 知识沉淀 / 方法论"),
    paragraph("这些文档是 Synapse 体系的知识资产，是培训、咨询和产品化的基础。"),

    toggle(
        "🧠 核心方法论",
        [
            bullet("Harness Engineering 实践指南 — \"Agent=Model+Harness\"核心公式，四要素体系，培训理论基础"),
            bullet("Synapse 体系综合评审报告 — 三维度成熟度评审框架"),
            bullet("OBS 第二大脑 2.0 系统说明 — 基于 Karpathy Software 2.0 的知识管理架构"),
        ]
    ),

    toggle(
        "💼 商业化与产品化",
        [
            bullet("Synapse 商业化战略方案 — AI 咨询市场数据+差异化竞争优势分析"),
            bullet("Synapse 产品化架构方案 — Core/Ops 分离+订阅升级模型"),
            bullet("Synapse Practitioner 认证课程大纲（SCP）— 8小时培训课程，结业可运行最小体系"),
            bullet("Synapse Forge Closed Beta 运营手册 — Founding 30 阶段 KPI+招募+退出标准"),
        ]
    ),

    toggle(
        "📋 SOP 与流程规范",
        [
            bullet("Agent HR 管理制度 — 56人 AI 团队完整生命周期管理"),
            bullet("PMO Auto V2.0 PRD — 权威产品需求文档，总裁批准版"),
            bullet("产品委员会章程 V2 — 产品治理根本规则，2026-04-24 总裁批准"),
            bullet("双语博客生产 SOP v1.1 — 新博客必须同时产出中英双语版"),
            bullet("战略对齐审查 SOP — 智囊团独立路径规范，D-2026-0427-001"),
            bullet("PSL 总裁直属服务体系 — SPE+PBS 双条线设计规范"),
        ]
    ),

    toggle(
        "🏗️ 架构设计",
        [
            bullet("情报管线多租户架构指南 — SaaS化架构设计，Q3 灰度路线图"),
            bullet("lysander.bond 网站战略重构方案 — 从个人博客到商业平台"),
            bullet("全站 i18n 架构升级方案（Stage 4）— 双语URL架构，hreflang自动生成"),
            bullet("SSOT + i18n 综合评审 — 4团队方案对齐，53U工程量"),
        ]
    ),

    divider(),

    # Block 10: D类运营数据
    heading2("D类 — 运营数据 / 管线维度"),
    paragraph("自动化管线持续产出的运营数据，是体系健康度的实证。"),

    callout(
        "情报管线\n"
        "每日自动运行 | 已产出情报日报 7 份（2026-04-17 ~ 04-26）+ 行动报告 6 份\n"
        "状态：全自动闭环（OBJ-INTEL-LOOP-CLOSURE shipped 2026-04-26）",
        "📡", "blue_background"
    ),

    callout(
        "基础设施管线\n"
        "- n8n Workflow 全量审计（47条，2026-04-25）\n"
        "- Synapse 全量定时任务清单（50个 active，2026-04-26）\n"
        "- Task Scheduler 审计（Synapse相关任务全量核查）",
        "⚙️", "gray_background"
    ),

    callout(
        "团队治理管线\n"
        "- W16/W17 Harness 周审计（Agent 46/56人，100%达标）\n"
        "- Beta 倡导者名单（Founding 30 跟踪）",
        "👥", "purple_background"
    ),

    divider(),

    # Block 12: Footer
    callout(
        "本清单由 OBS 团队 + knowledge_engineer 于 2026-04-27 自动检索生成\n"
        "数据来源：obs/ 全目录检索，52 项成果物，4 类分层\n"
        "附件更新：3 份可下载文档（PDF x2 + DOCX x1）",
        "📝", "gray_background"
    ),
]


def main():
    log = lambda msg: sys.stdout.buffer.write((msg + "\n").encode("utf-8"))

    log("=" * 60)
    log("Synapse Dashboard Builder — 开始执行")
    log("=" * 60)

    # Step 1: Create Claude Code workspace page under Hub
    log("\n[Step 1] 在 Hub 根页面下创建「Claude Code 工作台」主题页...")
    workspace_title = "Claude Code 工作台 — 成果物全览"
    resp, status = create_page(HUB_PAGE_ID, workspace_title)
    if "id" not in resp:
        log(f"  FAIL HTTP {status}: {resp.get('message', 'unknown')[:200]}")
        sys.exit(1)
    workspace_id = resp["id"]
    workspace_url = f"https://www.notion.so/{workspace_id.replace('-', '')}"
    log(f"  OK HTTP {status} | page_id: {workspace_id}")
    log(f"  URL: {workspace_url}")

    # Step 2: Create Dashboard sub-page under workspace page
    log("\n[Step 2] 在工作台页面下创建「成果物 Dashboard」子页面...")
    dashboard_title = "成果物 Dashboard — Synapse by Claude Code"
    # Pass first batch of children at creation
    first_batch = DASHBOARD_BLOCKS[:20]
    resp, status = create_page(workspace_id, dashboard_title, first_batch)
    if "id" not in resp:
        log(f"  FAIL HTTP {status}: {resp.get('message', 'unknown')[:200]}")
        sys.exit(1)
    dashboard_id = resp["id"]
    dashboard_url = f"https://www.notion.so/{dashboard_id.replace('-', '')}"
    log(f"  OK HTTP {status} | page_id: {dashboard_id}")
    log(f"  URL: {dashboard_url}")
    log(f"  First batch: {len(first_batch)} blocks written")

    # Step 3: Append remaining blocks
    remaining = DASHBOARD_BLOCKS[20:]
    if remaining:
        log(f"\n[Step 3] Appending {len(remaining)} remaining blocks...")
        resp, status = append_blocks(dashboard_id, remaining)
        if status not in (200, 201):
            log(f"  WARN HTTP {status}: {resp.get('message', 'unknown')[:200]}")
        else:
            log(f"  OK HTTP {status} | {len(remaining)} blocks appended")

    total = len(DASHBOARD_BLOCKS)
    log(f"\n  Total blocks written: {total}")

    log("\n" + "=" * 60)
    log("执行完成 — 页面汇总")
    log("=" * 60)
    log(f"  Claude Code 工作台: {workspace_url}")
    log(f"  成果物 Dashboard:   {dashboard_url}")
    log("")
    log("附件处理结果:")
    log("  - synapse-commercial-value.pdf → obs/06-daily-reports/synapse-commercial-value.pdf（本地路径，未在 git 追踪）")
    log("  - finlease-synapse-proposal.pdf → obs/06-daily-reports/finlease-synapse-proposal.pdf（本地路径，未在 git 追踪）")
    log("  - finlease-dev-survey.docx → obs/06-daily-reports/finlease-dev-survey.docx（本地路径，未在 git 追踪）")


if __name__ == "__main__":
    main()
