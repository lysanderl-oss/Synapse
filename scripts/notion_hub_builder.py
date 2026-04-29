#!/usr/bin/env python3
"""
Lysander-AI Hub Full Content Builder
Creates 3 subpages and appends navigation to Hub landing page.
"""
import json
import urllib.request
import urllib.error

NOTION_TOKEN = "ntn_A46470290049IHNiJROzZb4JhhP8OAb5bpPH4RzFqHkggj"
NOTION_VERSION = "2022-06-28"
HUB_PAGE_ID = "34d114fc-090c-81db-a651-c2386164b46f"
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
        print(f"HTTP ERROR {e.code}: {error_body[:500]}")
        return json.loads(error_body), e.code


def create_page(title, children):
    data = {
        "parent": {"page_id": HUB_PAGE_ID},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        "children": children
    }
    return notion_request("POST", "/pages", data)


def append_blocks(page_id, children):
    return notion_request("PATCH", f"/blocks/{page_id}/children", {"children": children})


def callout(text, icon_emoji, color):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"type": "emoji", "emoji": icon_emoji},
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


def bullet(text):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
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


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


# ─── TASK 2: Products Page ───────────────────────────────────────────────────

PRODUCTS_CHILDREN = [
    callout(
        "Synapse 已上线 6 大 AI 产品，全部在生产环境稳定运行。\n"
        "6 AI products live in production — automated, monitored, and continuously improving.",
        "🤖", "blue_background"
    ),
    callout(
        "PMO Auto | 项目管理自动化系统\n"
        "版本：v2.2.0 GA（生产级） | Version: v2.2.0 GA\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "核心功能：全自动项目初始化 → WBS 导入 → 任务变更通知 → 周报 → 逾期预警\n"
        "Key Function: End-to-end project lifecycle automation\n"
        "成果：36 个活跃项目覆盖 | API: pmo-api.lysander.bond\n"
        "工作流：WF-01 ~ WF-07（7个节点全链路）",
        "✅", "green_background"
    ),
    callout(
        "Intelligence Pipeline | 情报闭环管线\n"
        "状态：每日自动运行 | Status: Daily automated\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "核心功能：AI前沿情报搜索 → 专家评估 → 行动计划 → 自动执行 → 报告生成\n"
        "Key Function: AI intelligence → evaluation → action → report (fully automated)\n"
        "成果：36+ 份历史情报日报 | 每日 08:00 Dubai 自动触发",
        "🔍", "blue_background"
    ),
    callout(
        "Blog Publishing System | 博客自动发布系统\n"
        "状态：已上线 | Status: Live\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "核心功能：会话内容 → 工作日志 → 博客撰写 → QA 审查 → Git Push 全链路\n"
        "Key Function: Session → worklog → blog → QA → publish (zero-touch)\n"
        "成果：24 篇文章已发布 | 网站：lysander.bond",
        "✍️", "orange_background"
    ),
    callout(
        "President OS — Morning Brief | 总裁晨报系统\n"
        "状态：Phase 1 运行中 | Status: Phase 1 active\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "核心功能：每日 06:30 Dubai 自动推送晨报至 Slack，含当日日程、优先任务、系统状态\n"
        "Key Function: Daily automated briefing — calendar, priorities, system health\n"
        "触发：n8n 定时 Routine（06:30 Dubai）",
        "☀️", "yellow_background"
    ),
    callout(
        "CEO Guard | AI 行为治理系统\n"
        "状态：持续运行 | Status: Always active\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "核心功能：AI Agent 工具调用审计、四级决策体系、执行链合规验证\n"
        "Key Function: AI tool-use auditing, 4-level decision governance, execution chain compliance\n"
        "覆盖：所有 44 个 Agent 的工具调用行为 | 日志：logs/ceo-guard-audit.log",
        "🛡️", "purple_background"
    ),
    callout(
        "WF-09 Notification Gateway | 统一通知网关\n"
        "状态：生产运行 | Status: Production | infra v1.0.3\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "核心功能：PMO/系统/Agent 全渠道通知统一路由，HMAC-SHA256 签名验证\n"
        "Key Function: Unified notification routing for all Synapse subsystems\n"
        "路由：#ai-agents-noti | 覆盖：9 个工作流的通知出口",
        "📡", "gray_background"
    ),
    divider(),
    paragraph("🔄 版本数据自动同步 | Auto-synced via notion_daily_sync.py", "gray")
]

# ─── TASK 3: Asset Map Page ───────────────────────────────────────────────────

ASSET_CHILDREN = [
    callout(
        "Synapse System — Asset Snapshot (2026-04-25)\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👥 44 Active AI Agents  |  🏭 12 Core Teams\n"
        "📋 36+ Intelligence Reports  |  ✍️ 24 Blog Articles Published\n"
        "⚙️ 9 n8n Workflows Active  |  🌐 3 Production Websites\n"
        "📁 213 YAML Configs  |  🐍 85+ Scripts (Python/JS)\n"
        "🔧 18 CEO Core Modules",
        "📊", "blue_background"
    ),
    heading2("基础设施 | Infrastructure"),
    callout(
        "lysander.bond — 主站博客\n"
        "状态：已上线 | 24 篇文章已发布\n"
        "Tech Stack: Next.js / Vercel | 内容通过 Git Push 自动更新",
        "🌐", "gray_background"
    ),
    callout(
        "n8n.lysander.bond — n8n Cloud 工作流引擎\n"
        "状态：生产运行 | 9 个工作流已激活\n"
        "负责：PMO 自动化 / 情报管线 / 通知路由 / 定时 Agent 编排",
        "⚙️", "gray_background"
    ),
    callout(
        "pmo-api.lysander.bond — PMO API\n"
        "状态：v2.2.0 GA 生产运行 | SSL 至 2026-07-23\n"
        "36 个活跃项目 | REST API 覆盖全项目生命周期",
        "🔧", "gray_background"
    ),
    heading2("工作流矩阵 | Workflow Matrix"),
    bullet("WF-01 (AnR20HucIRaiZPS7) — 项目初始化 | Project Initialization"),
    bullet("WF-02 (IXEFFpLwnlcggK2E) — 任务变更通知 | Task Change Notification"),
    bullet("WF-03 (uftMqCdR1pRz079z) — 里程碑提醒 | Milestone Reminder"),
    bullet("WF-04 (40mJOR8xXtubjGO4) — PMO 周报 | Weekly Report"),
    bullet("WF-05a (rlEylvNQW55UPbAq) — 逾期预警 | Overdue Alert"),
    bullet("WF-05b (g6wKsdroKNAqHHds) — Assignee 同步 | Assignee Sync"),
    bullet("WF-06 (knVJ8Uq2D1UZmpxr) — 任务依赖链通知 | Task Dependency Notification"),
    bullet("WF-07 (seiXPY0VNzNxQ2L3) — 会议纪要→Asana | Meeting Notes to Asana"),
    bullet("WF-09 (atit1zW3VYUL54CJ) — 统一通知网关 | Notification Gateway"),
    heading2("代码资产 | Code Assets"),
    paragraph(
        "213 个 YAML 配置文件 | 85+ Python / JavaScript 脚本 | 18 个 CEO 核心模块\n"
        "每日通过 asset_counter.py 自动统计，随日报同步至 Notion。"
    ),
    divider(),
    paragraph("🔄 数字每日自动更新 | Auto-updated daily via asset_counter.py", "gray")
]

# ─── TASK 4: Team Structure Page ─────────────────────────────────────────────

TEAMS = [
    ("Graphify 智囊团", "intelligence", 7, "情报分析、决策支持、趋势预判"),
    ("HR 管理团队", "governance", 2, "Agent 入职审批、能力审计、HR 治理"),
    ("驾驭运维部", "infrastructure", 5, "Harness 配置、AI系统开发、知识工程、集成QA"),
    ("Butler 交付运营团队", "operations", 6, "项目交付、IoT、PMO、UAT"),
    ("研发团队", "engineering", 5, "后端/前端/DevOps/QA 全栈研发"),
    ("OBS 知识管理团队", "knowledge", 4, "知识库架构、知识沉淀、检索优化"),
    ("内容运营团队", "content", 8, "内容策略、博客创作、视觉设计、发布"),
    ("总裁直属小组", "executive", 2, "简报汇报、风格校准"),
    ("增长团队", "growth", 4, "GTM战略、用户研究、社区运营"),
    ("AI/ML 工程团队", "engineering", 1, "Claude API、RAG、Prompt 工程"),
    ("领域专家组", "specialist", 2, "法律顾问、财务分析"),
    ("OPC 核心团队", "executive", 4, "OPC CEO/COO/CFO/CTO Agent"),
    ("产品运营团队", "product", 8, "产品规划、需求分析、产品化路线图"),
]

TEAM_ICONS = {
    "intelligence": "🧠",
    "governance": "👔",
    "infrastructure": "⚙️",
    "operations": "📦",
    "engineering": "💻",
    "knowledge": "📚",
    "content": "✍️",
    "executive": "👑",
    "growth": "📈",
    "specialist": "🎓",
    "product": "🏗️",
}

TEAM_CHILDREN = [
    callout(
        "Synapse Multi-Agent System\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "44 Active AI Agents | 12 Core Teams | CEO-Governed | 4-Level Decision System\n"
        "每个 Agent 都有明确的专业分工和入职评分门槛。\n"
        "Each Agent has a defined specialization and onboarding qualification threshold.",
        "🤖", "blue_background"
    ),
    heading2("四级决策体系 | 4-Level Decision System"),
    bullet("L1 — 自动执行 (Auto Execute): 例行操作、标准流程，系统自动处理"),
    bullet("L2 — 专家评审 (Expert Review): 专业问题由领域专家分析，给出建议"),
    bullet("L3 — Lysander 决策 (CEO Decision): 跨团队协调、资源分配，Lysander 最终决策"),
    bullet("L4 — 总裁决策 (President Decision): 法律/重大财务/不可逆战略决策，上报总裁"),
    heading2("CEO Guard 治理 | Governance"),
    paragraph(
        "CEO Guard 是 Synapse 的 AI 行为合规系统。所有 Agent 工具调用均经过 PreToolUse hook 审计，\n"
        "确保执行链合规（派单 → 执行 → QA → 交付）。主对话中的 Lysander 作为纯管理角色，\n"
        "不直接执行代码或文件操作，所有实质工作通过专属 Agent 完成。\n"
        "CEO Guard ensures all AI tool usage is audited and compliant with the 4-step execution chain."
    ),
    heading2("核心团队 | Core Teams"),
]

for name, team_type, count, func in TEAMS:
    icon = TEAM_ICONS.get(team_type, "👥")
    TEAM_CHILDREN.append(bullet(f"{icon} {name} — {func} ({count}个专家)"))

TEAM_CHILDREN.extend([
    divider(),
    paragraph("🔄 团队数据源：organization.yaml | 变更自动同步至 Notion", "gray")
])


def main():
    print("=" * 60)
    print("Lysander-AI Hub 内容建设 — 开始执行")
    print("=" * 60)

    # ── Task 2: Products page
    print("\n[任务二] 创建「产品线详情 | Products」子页面...")
    resp, status = create_page("🏭 产品线详情 | Products", PRODUCTS_CHILDREN)
    if "id" in resp:
        products_id = resp["id"]
        print(f"  ✅ HTTP {status} | page_id: {products_id}")
    else:
        products_id = None
        print(f"  ❌ 失败: {resp.get('message', 'unknown error')[:200]}")

    # ── Task 3: Asset Map page
    print("\n[任务三] 创建「资产全景 | Asset Map」子页面...")
    resp, status = create_page("📊 资产全景 | Asset Map", ASSET_CHILDREN)
    if "id" in resp:
        asset_id = resp["id"]
        print(f"  ✅ HTTP {status} | page_id: {asset_id}")
    else:
        asset_id = None
        print(f"  ❌ 失败: {resp.get('message', 'unknown error')[:200]}")

    # ── Task 4: Team Structure page
    print("\n[任务四] 创建「团队体系 | Team Structure」子页面...")
    resp, status = create_page("👥 团队体系 | Team Structure", TEAM_CHILDREN)
    if "id" in resp:
        team_id = resp["id"]
        print(f"  ✅ HTTP {status} | page_id: {team_id}")
    else:
        team_id = None
        print(f"  ❌ 失败: {resp.get('message', 'unknown error')[:200]}")

    # ── Task 5: Append navigation to Hub landing page
    print("\n[任务五] 在 Hub 落地页末尾追加子页面导航...")

    def notion_url(page_id):
        if page_id:
            return f"https://www.notion.so/{page_id.replace('-', '')}"
        return "(创建失败，无链接)"

    nav_blocks = [
        divider(),
        heading2("探索更多 | Explore"),
        paragraph(
            f"🏭 产品线详情 → {notion_url(products_id)}"
        ),
        paragraph(
            f"📊 资产全景 → {notion_url(asset_id)}"
        ),
        paragraph(
            f"👥 团队体系 → {notion_url(team_id)}"
        ),
    ]

    resp, status = append_blocks(HUB_PAGE_ID, nav_blocks)
    if "results" in resp or resp.get("object") == "list":
        print(f"  ✅ HTTP {status} | 导航区块追加成功")
    else:
        print(f"  ❌ 失败: {resp.get('message', 'unknown error')[:200]}")

    print("\n" + "=" * 60)
    print("执行完成 — 页面 ID 汇总")
    print("=" * 60)
    print(f"  Hub 主页:    https://www.notion.so/{HUB_PAGE_ID.replace('-', '')}")
    print(f"  产品线详情:  {notion_url(products_id)}")
    print(f"  资产全景:    {notion_url(asset_id)}")
    print(f"  团队体系:    {notion_url(team_id)}")


if __name__ == "__main__":
    main()
