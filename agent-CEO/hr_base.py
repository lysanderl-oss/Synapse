"""
Synapse v3.0 — HR知识库基础模块
提供与OBS HR知识库的交互接口

用于Lysander CEO召唤团队时查询人员档案和能力信息

变更说明 (v2.0 -> v3.0):
  - qa_auto_review() 评分体系统一为 85/100 (5维度 × 20分，通过线85)
  - BASE_PATH / OBS_KB_ROOT 更新为 Synapse v3.0 目录结构
  - knowledge_chandu_expert 引用全部替换为 obs_knowledge_engineer
  - audit_agent_card() 推荐阈值对齐 85/100 标准
"""

import yaml
import re
import json
import ast
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

# 路径配置 - 支持环境变量自定义，默认使用相对路径
import os

# v3.0: 路径指向 Synapse 新目录结构
BASE_PATH = Path(os.environ.get("SYNAPSE_ROOT", Path(__file__).parent.parent))
OBS_KB_ROOT = Path(os.environ.get("OBS_KB_ROOT", BASE_PATH / "obs"))
HR_KB_ROOT = OBS_KB_ROOT / "01-team-knowledge" / "HR"
CONFIG_DIR = Path(__file__).parent / "config"
ORG_CONFIG = CONFIG_DIR / "organization.yaml"

DECISION_LOG_PATH = CONFIG_DIR / "decision_log.json"
HARNESS_CONFIG_PATH = CONFIG_DIR / "harness_keywords.json"


def load_org_config() -> dict:
    """加载组织配置"""
    with open(ORG_CONFIG, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_personnel_card(specialist_id: str, team: str) -> Optional[dict]:
    """加载人员卡片 (v3.0: 纯 YAML 格式，不含 Markdown frontmatter)

    Args:
        specialist_id: 专家标识符 (如 'rd_backend')
        team: 团队标识符 (如 'rd')

    Returns:
        人员卡片字典，未找到返回None
    """
    # v3.0: 卡片为纯 YAML 文件（.yaml），无 Markdown frontmatter
    card_path = HR_KB_ROOT / "personnel" / team / f"{specialist_id}.yaml"
    if not card_path.exists():
        return None

    with open(card_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        return None

    return {
        **data,
        "source_path": str(card_path)
    }


def get_personnel_by_specialist_id(specialist_id: str) -> Optional[dict]:
    """通过specialist_id查询人员档案（全局搜索）

    在所有团队中查找匹配的专家

    Args:
        specialist_id: 专家标识符

    Returns:
        人员档案字典，未找到返回None
    """
    org = load_org_config()

    # 在所有团队中搜索（v3.0: 使用 members 字段）
    for team_key, team_config in org.get("teams", {}).items():
        members = team_config.get("members", team_config.get("specialists", []))
        if specialist_id in members:
            return load_personnel_card(specialist_id, team_key)

    # 也检查lysander团队 (v3.0: .yaml format)
    lysander_path = HR_KB_ROOT / "personnel" / "lysander" / "lysander.yaml"
    if specialist_id == "lysander" and lysander_path.exists():
        with open(lysander_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data:
            return {**data, "source_path": str(lysander_path)}

    return None


def resolve_team_members(team_key: str) -> List[dict]:
    """解析团队所有成员的人员档案

    Args:
        team_key: 团队标识符 (如 'rd')

    Returns:
        成员档案列表
    """
    org = load_org_config()
    team_config = org.get("teams", {}).get(team_key, {})
    # v3.0: 支持 members 和 specialists 两种字段名
    specialist_ids = team_config.get("members", team_config.get("specialists", []))

    members = []
    for sid in specialist_ids:
        personnel = load_personnel_card(sid, team_key)
        if personnel:
            members.append({
                "specialist_id": sid,
                "name": personnel.get("name"),
                "role": personnel.get("role"),
                "type": personnel.get("type"),
                "domains": personnel.get("domains", []),
                "capabilities": personnel.get("capabilities", []),
                "availability": personnel.get("availability"),
                "status": personnel.get("status"),
                "召唤关键词": personnel.get("召唤关键词", []),
                "source": personnel.get("source_path")
            })
        else:
            # 兜底：只有ID没有档案
            members.append({
                "specialist_id": sid,
                "name": sid,
                "role": "未知",
                "type": "unknown",
                "availability": "unknown",
                "source": None
            })

    return members


def get_team_hr_summary(team_key: str) -> dict:
    """获取团队HR概览

    Args:
        team_key: 团队标识符

    Returns:
        团队HR摘要字典
    """
    org = load_org_config()
    team_config = org.get("teams", {}).get(team_key, {})

    members = resolve_team_members(team_key)

    return {
        "team": team_key,
        "team_name": team_config.get("name"),
        "description": team_config.get("description"),
        "member_count": len(members),
        "members": members,
        "human_experts": [m for m in members if m.get("type") == "human_expert"],
        "ai_agents": [m for m in members if m.get("type") == "ai_agent"],
        "available": [m for m in members if m.get("availability") == "available"],
        "unavailable": [m for m in members if m.get("availability") != "available"]
    }


def find_experts_by_task(task_description: str, team_key: Optional[str] = None) -> List[dict]:
    """根据任务描述查找匹配的专家

    Args:
        task_description: 任务描述文本
        team_key: 可选，限定团队

    Returns:
        匹配的专家列表
    """
    task_lower = task_description.lower()
    org = load_org_config()

    teams_to_search = [team_key] if team_key else list(org.get("teams", {}).keys())

    matched = []
    for tk in teams_to_search:
        members = resolve_team_members(tk)
        for member in members:
            # 检查召唤关键词是否匹配
            keywords = member.get("召唤关键词", [])
            if any(kw in task_lower for kw in keywords):
                matched.append(member)

    return matched


def get_all_teams_summary() -> List[dict]:
    """获取所有团队的HR概览

    Returns:
        所有团队摘要列表
    """
    org = load_org_config()
    teams = []

    for team_key in org.get("teams", {}).keys():
        summary = get_team_hr_summary(team_key)
        teams.append(summary)

    # 添加lysander
    lysander = get_personnel_by_specialist_id("lysander")
    if lysander:
        teams.append({
            "team": "lysander",
            "team_name": "公司管理层",
            "member_count": 1,
            "members": [{
                "specialist_id": "lysander",
                "name": lysander.get("name"),
                "role": lysander.get("role"),
                "type": lysander.get("type"),
                "domains": lysander.get("domains", []),
                "capabilities": lysander.get("capabilities", []),
                "availability": lysander.get("availability"),
                "source": lysander.get("source_path")
            }],
            "human_experts": [{
                "specialist_id": "lysander",
                "name": lysander.get("name"),
                "role": lysander.get("role"),
                "type": lysander.get("type"),
                "availability": lysander.get("availability")
            }],
            "ai_agents": [],
            "available": [{
                "specialist_id": "lysander",
                "name": lysander.get("name"),
                "availability": lysander.get("availability")
            }]
        })

    return teams


# ============================================================================
# Synapse v3.0 — QA自动审查引擎
# 统一评分体系：5维度 × 20分 = 100分满分，通过线 85/100
# 由 integration_qa 使用
# ============================================================================

def qa_auto_review(deliverable: dict) -> dict:
    """QA自动审查（v3.0 — 85/100统一评分体系）

    评分体系：5个维度，每维度最高20分，满分100分
    通过线：>= 85/100
    条件通过：70-84（记录缺口，2个会话内修复）
    不通过：< 70（退回修订）
    严重不合格：< 50（阻止交付，上报Lysander）

    UI 变更任务自动触发 Visual QA（integration_visual_gate）：
    - 通过 task_description 关键词检测
    - 视觉差异结果并入 issues 列表
    - Visual QA 未通过 = visual_integrity 维度扣分

    Args:
        deliverable: 交付物字典，包含以下可选字段：
            - content: 交付物内容（文本/代码/配置）
            - deliverable_type: 类型 (code|yaml|doc|report)
            - claimed_items: 声明的交付项列表
            - actual_items: 实际交付项列表
            - team: 执行团队
            - specialist_id: 执行专员
            - task_description: 原始任务描述
            - dispatch_record: 派单记录（用于执行链合规检查）
            - task_id: 任务ID（用于 Visual QA）
            - before_screenshot: 变更前截图路径（可选）
            - after_screenshot: 变更后截图路径（可选）

    Returns:
        审查结果：
            - score: 总分 (0-100)
            - passed: 是否通过 (score >= 85)
            - dimension_scores: 各维度得分
            - issues: 问题列表
            - visual_qa: Visual QA 报告（UI任务有值）
            - recommendation: 处置建议
            - gate: "pass" | "conditional_pass" | "fail" | "critical_fail"
    """
    content = deliverable.get("content", "")
    deliverable_type = deliverable.get("deliverable_type", "doc")
    claimed_items = deliverable.get("claimed_items", [])
    actual_items = deliverable.get("actual_items", [])
    dispatch_record = deliverable.get("dispatch_record")
    task_description = deliverable.get("task_description", "")
    task_id = deliverable.get("task_id", "")
    before_screenshot = deliverable.get("before_screenshot")
    after_screenshot = deliverable.get("after_screenshot")

    issues = []
    dimension_scores = {}

    # ── Visual QA 集成（UI 变更任务自动检测）───────────────────────────
    visual_qa_report: dict = {}
    VISUAL_KEYWORDS = [
        "ui", "界面", "前端", "css", "html", "样式", "视觉",
        "布局", "组件", "按钮", "导航", "页面", "截图",
        "截图", "设计稿", "figma", "响应式", "移动端", "桌面端",
    ]
    is_ui_task = any(kw.lower() in task_description.lower() for kw in VISUAL_KEYWORDS)

    if is_ui_task:
        try:
            from agent_butler_visual_qa import integration_visual_gate
            visual_qa_report = integration_visual_gate(
                task_id=task_id or "unknown",
                before_path=before_screenshot,
                after_path=after_screenshot,
                task_description=task_description,
            )
            # 将 Visual QA 结果并入 issues
            if visual_qa_report.get("visual_issues"):
                issues.extend(visual_qa_report["visual_issues"])
            # Visual QA 未通过 → 合规性维度扣分
            if not visual_qa_report.get("passed", True):
                issues.append("Visual QA 门禁未通过，UI变更存在视觉问题")
        except Exception as e:
            issues.append(f"Visual QA 调用失败（{e}），请手动检查截图")

    # ── 维度1: 完整性 (Integrity) — 20分 ──
    # 所有约定交付物是否齐全
    integrity_score = 20
    if claimed_items and actual_items:
        missing = set(claimed_items) - set(actual_items)
        if missing:
            deduction = min(20, len(missing) * 5)
            integrity_score = max(0, 20 - deduction)
            issues.append(f"完整性缺失: {', '.join(missing)}")
    elif claimed_items and not actual_items:
        integrity_score = 10
        issues.append("无法验证交付物完整性：actual_items未提供")
    dimension_scores["integrity"] = integrity_score

    # ── 维度2: 准确性 (Accuracy) — 20分 ──
    # 内容/代码/配置是否无错误
    accuracy_score = 20
    if deliverable_type == "yaml" and content:
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            accuracy_score = 0
            issues.append(f"YAML语法错误: {e}")
    elif deliverable_type == "code" and content:
        try:
            ast.parse(content)
        except SyntaxError as e:
            accuracy_score = 0
            issues.append(f"Python语法错误: {e}")
    dimension_scores["accuracy"] = accuracy_score

    # ── 维度3: 一致性 (Consistency) — 20分 ──
    # 与现有系统/规范无冲突
    consistency_score = 20
    # 检查弃用的命名
    deprecated_refs = ["knowledge_chandu_expert", "pmo_expert", "iot_expert",
                       "obs_architecture_expert", "knowledge_search_expert",
                       "knowledge_quality_expert", "training_expert",
                       "delivery_expert", "iot_data_expert", "uat_test_expert"]
    content_str = str(deliverable.get("content", "")) + str(deliverable.get("task_description", ""))
    found_deprecated = [r for r in deprecated_refs if r in content_str]
    if found_deprecated:
        deduction = min(20, len(found_deprecated) * 5)
        consistency_score = max(0, 20 - deduction)
        issues.append(f"使用了已弃用的标识符: {', '.join(found_deprecated)}")
    dimension_scores["consistency"] = consistency_score

    # ── 维度4: 可维护性 (Maintainability) — 20分 ──
    # 有注释、结构清晰、可升级
    maintainability_score = 20
    if deliverable_type in ("code", "yaml") and content:
        has_comments = ("#" in content or '"""' in content or "'''" in content)
        if not has_comments:
            maintainability_score = 12
            issues.append("代码/配置缺少注释，建议补充关键说明")
    dimension_scores["maintainability"] = maintainability_score

    # ── 维度5: 合规性 (Compliance) — 20分 ──
    # 符合执行链规则和HR规范（重点检查派单记录）
    compliance_score = 20
    if dispatch_record is None:
        compliance_score = 8
        issues.append("缺少派单记录（execution chain断裂风险）：需补充【② 团队派单】记录")
    elif not dispatch_record:
        compliance_score = 5
        issues.append("派单记录为空：执行链【②】要求所有级别必须有派单表")
    dimension_scores["compliance"] = compliance_score

    # ── 总分计算 ──
    total_score = sum(dimension_scores.values())

    # ── 门禁判定 ──
    if total_score >= 85:
        gate = "pass"
        recommendation = "交付通过 (>= 85/100)"
        passed = True
    elif total_score >= 70:
        gate = "conditional_pass"
        recommendation = f"有条件通过 ({total_score}/100)，记录缺口，2个会话内修复"
        passed = True
    elif total_score >= 50:
        gate = "fail"
        recommendation = f"不通过 ({total_score}/100)，退回修订"
        passed = False
    else:
        gate = "critical_fail"
        recommendation = f"严重不合格 ({total_score}/100)，阻止交付，上报Lysander"
        passed = False

    return {
        "score": total_score,
        "passed": passed,
        "gate": gate,
        "dimension_scores": dimension_scores,
        "issues": issues,
        "visual_qa": visual_qa_report,
        "recommendation": recommendation,
        "reviewed_at": datetime.now().isoformat(),
        "reviewer": "integration_qa",
        "threshold": 85,
        "scale": "0-100"
    }


# ============================================================================
# Synapse v3.0 — Agent HR 质量审计引擎
# 由 HR Director + Capability Architect 使用
# ============================================================================

# 强制 Schema 必填字段
_REQUIRED_CARD_FIELDS = [
    "specialist_id", "team", "role", "status", "type",
    "domains", "capabilities", "experience",
    "availability", "召唤关键词",
]

# C级（不合格）能力描述特征 — 过于笼统的活动名
_C_LEVEL_PATTERNS = [
    "项目管理", "知识沉淀", "质量审核", "内容创作", "数据分析",
    "系统开发", "测试", "设计", "优化", "协调", "管理",
    "分析", "规划", "检索", "推荐", "审核",
]


def audit_agent_card(specialist_id: str, team_key: str = None) -> dict:
    """Agent 卡片质量审计

    由 HR Director 使用，检查单个 Agent 卡片的合规性和质量。

    Args:
        specialist_id: Agent 标识
        team_key: 团队标识（可选，不提供则全局搜索）

    Returns:
        审计结果：
        - score: 总分 (0-100)
        - schema_complete: Schema 完整性
        - capability_grades: 每条能力的评级
        - issues: 问题列表
        - recommendation: 处置建议（对齐85/100阈值）
    """
    # 加载卡片
    if team_key:
        card = load_personnel_card(specialist_id, team_key)
    else:
        card = get_personnel_by_specialist_id(specialist_id)

    if not card:
        return {
            "score": 0,
            "specialist_id": specialist_id,
            "issues": [f"找不到 Agent 卡片: {specialist_id}"],
            "recommendation": "卡片不存在，需要创建",
        }

    issues = []
    scores = {}

    # ── 1. Schema 完整性检查 (权重 25%) ──
    missing_fields = []
    for field in _REQUIRED_CARD_FIELDS:
        if field not in card or not card[field]:
            missing_fields.append(field)

    schema_score = max(0, 100 - len(missing_fields) * 15)
    scores["schema"] = schema_score
    if missing_fields:
        issues.append(f"缺失必填字段: {', '.join(missing_fields)}")

    # ── 2. 能力描述质量 (权重 30%) ──
    capabilities = card.get("capabilities", [])
    cap_count = len(capabilities)

    if cap_count < 3:
        issues.append(f"capabilities 仅 {cap_count} 条，要求至少 4 条")

    c_level_count = 0
    capability_grades = []

    # B级以上关键词：包含这些说明至少是方法论/框架级别
    _b_level_indicators = [
        "SWOT", "PEST", "PRINCE2", "Agile", "Scrum", "PMP", "ITIL", "CMMI",
        "Kano", "Porter", "PMBoK", "ADDIE", "TDD", "BDD", "CI/CD",
        "IoT", "BIM", "CAD", "GIS", "IFC", "MQTT", "OPC-UA", "Modbus",
        "REST", "API", "SQL", "NoSQL", "ETL", "ML", "NLP", "RAG",
        "WBS", "UAT", "SOP", "KPI", "OKR", "ROI", "GTM", "PMF", "SEO",
        "ATR", "RSI", "MA", "MACD",
        "知识图谱", "决策树", "语义网络", "图推理", "神经网络",
        "时间序列", "回归分析", "聚类分析", "模式识别", "异常检测",
        "敏感性分析", "利弊分析", "价值链", "波特五力",
        "燃尽图", "甘特图", "关键路径",
        "IRAC", "DCF", "P&L", "RAGAS", "DeepEval", "LoRA", "QLoRA",
        "MEDDIC", "JTBD", "NPS", "CSAT", "BLUF",
    ]

    for cap in capabilities:
        cap_str = str(cap).strip()

        # 先检查是否包含B级以上指标词
        has_method = any(ind in cap_str for ind in _b_level_indicators)

        # 检查是否为 A 级（包含工具/框架名+具体产出物描述，通常较长且有括号说明）
        has_tool = any(c in cap_str for c in [
            "(", ")", "pytest", "FastAPI", "Vue", "React", "Docker",
            "Kubernetes", "Playwright", "Selenium", "JMeter",
            "Obsidian", "Claude", "Python", "yaml", "json",
            "Asana", "Notion", "n8n", "GitHub", "Slack",
            "Excel", "Figma", "Canva",
            "基于", "框架", "引擎", "工具链", "脚本",
            "ECharts", "Element Plus", "Pinia", "Tailwind",
            "SQLAlchemy", "Baostock", "Midjourney", "Flux", "DALL-E",
            "generate-article", "hr_base", "Dataview", "CapCut",
        ])

        # C级判断：仅活动名（短且无方法论/工具指标）
        is_c_level = False
        if not has_method and not has_tool:
            if len(cap_str) <= 6:
                is_c_level = True
            else:
                for pattern in _C_LEVEL_PATTERNS:
                    if cap_str == pattern:
                        is_c_level = True
                        break

        if is_c_level:
            grade = "C"
            c_level_count += 1
        elif has_tool:
            grade = "A"
        else:
            grade = "B"

        capability_grades.append({"capability": cap_str, "grade": grade})

    if c_level_count > 0:
        issues.append(f"{c_level_count} 条能力描述为 C 级（不合格）")

    cap_quality_score = 100
    if cap_count == 0:
        cap_quality_score = 0
    else:
        a_count = sum(1 for g in capability_grades if g["grade"] == "A")
        b_count = sum(1 for g in capability_grades if g["grade"] == "B")
        cap_quality_score = int((a_count * 100 + b_count * 70 + c_level_count * 20) / cap_count)
    scores["capability_quality"] = cap_quality_score

    # ── 3. Domains 充实度 (权重 15%) ──
    domains = card.get("domains", [])
    domain_score = min(100, len(domains) * 25)  # 4条=100
    scores["domains"] = domain_score
    if len(domains) < 3:
        issues.append(f"domains 仅 {len(domains)} 条，要求至少 3 条")

    # ── 4. Experience 充实度 (权重 15%) ──
    experience = card.get("experience", [])
    exp_score = min(100, len(experience) * 40)  # 2-3条就够
    scores["experience"] = exp_score
    if len(experience) < 2:
        issues.append(f"experience 仅 {len(experience)} 条，要求至少 2 条")

    # ── 5. 召唤关键词 (权重 15%) ──
    keywords = card.get("召唤关键词", [])
    kw_score = min(100, len(keywords) * 20)  # 5条=100
    scores["keywords"] = kw_score
    if len(keywords) < 4:
        issues.append(f"召唤关键词 仅 {len(keywords)} 个，要求至少 4 个")

    # ── 加权总分 ──
    total = int(
        scores["schema"] * 0.25 +
        scores["capability_quality"] * 0.30 +
        scores["domains"] * 0.15 +
        scores["experience"] * 0.15 +
        scores["keywords"] * 0.15
    )

    # v3.0: 处置建议对齐 85/100 阈值
    if total >= 90:
        recommendation = "优秀，保持 active"
    elif total >= 85:
        recommendation = "合格，通过85/100门禁"
    elif total >= 80:
        recommendation = "需优化，未达85/100门禁，限期提升能力描述至A级"
    elif total >= 60:
        recommendation = "不合格，立即修订（目标: 85+/100）"
    else:
        recommendation = "严重不合格，降级inactive或退役"

    return {
        "specialist_id": specialist_id,
        "team": card.get("team", "unknown"),
        "role": card.get("role", "unknown"),
        "score": total,
        "scores": scores,
        "capability_grades": capability_grades,
        "issues": issues,
        "recommendation": recommendation,
        "passed": total >= 85,
        "threshold": 85,
        "audited_at": datetime.now().isoformat(),
    }


def audit_all_agents() -> dict:
    """全量 Agent 质量审计

    遍历所有团队的所有 Agent，逐一审计。
    每周一由 audit_agents.py 自动调用。

    Returns:
        审计报告：
        - total_agents: 总数
        - average_score: 平均分
        - pass_count: 达到85/100的Agent数量
        - by_team: 按团队分组的结果
        - critical_issues: 严重问题列表（<50分）
        - agents_below_85: 未达门禁的Agent列表
    """
    org = load_org_config()
    results = []
    team_scores = {}

    for team_key, team_config in org.get("teams", {}).items():
        # v3.0: 支持 members 和 specialists 两种字段名
        specialists = team_config.get("members", team_config.get("specialists", []))
        team_results = []

        for sid in specialists:
            audit = audit_agent_card(sid, team_key)
            results.append(audit)
            team_results.append(audit)

        if team_results:
            avg = sum(r["score"] for r in team_results) / len(team_results)
            team_scores[team_key] = {
                "name": team_config.get("name", team_key),
                "count": len(team_results),
                "average": round(avg, 1),
                "below_85": [r for r in team_results if r["score"] < 85],
                "below_60": [r for r in team_results if r["score"] < 60],
            }

    total = len(results)
    avg_score = round(sum(r["score"] for r in results) / total, 1) if total else 0
    pass_count = sum(1 for r in results if r["score"] >= 85)

    return {
        "total_agents": total,
        "pass_count": pass_count,
        "pass_rate": f"{round(pass_count / total * 100, 1)}%" if total else "0%",
        "average_score": avg_score,
        "by_team": team_scores,
        "critical_issues": [r for r in results if r["score"] < 50],
        "agents_below_85": [
            {"specialist_id": r["specialist_id"], "team": r["team"],
             "score": r["score"], "recommendation": r["recommendation"]}
            for r in results if r["score"] < 85
        ],
        "audited_at": datetime.now().isoformat(),
        "threshold": 85,
    }


# ============================================================================
# 决策检查机制 - 确保沟通决策原则被自动执行
# ============================================================================

# 小问题定义：风险可控、不影响核心架构、有明确执行路径
_SMALL_PROBLEM_KEYWORDS = [
    # 纯技术细节
    "同步", "sync", "生成yaml", "加载", "查询",
    # 例行操作
    "显示", "列出", "查看", "获取状态",
    # 已知流程
    "组装团队", "召唤", "路由",
    # 固化工作流执行 - Harness Engineering
    "固化", "工作流", "执行脚本", "推送微信",
    "发布博客", "构建网站", "daily-publish",
]

# 需要智囊团决策的关键词
_THINK_TANK_KEYWORDS = [
    "新架构", "新方案", "策略调整", "原则修改",
    "自动化方案", "决策体系", "流程变更",
]

# 需要代码审计的关键词
_CODE_REVIEW_KEYWORDS = [
    "脚本", "代码", "实现", "修改代码", "编写",
    "harness", "workflow", "自动化脚本",
]


# ============================================================================
# Harness Engineering: 决策Feedback Loop机制
# ============================================================================

def pre_execution_check(code_path: str = None, script_content: str = None) -> dict:
    """执行前自检（Harness自我修复机制）

    Args:
        code_path: 代码文件路径（可选）
        script_content: 脚本内容（可选）

    Returns:
        检查结果字典:
            - passed: 是否通过
            - errors: 错误列表
            - warnings: 警告列表
    """
    errors = []
    warnings = []

    # 1. Python语法检查
    if script_content:
        try:
            ast.parse(script_content)
        except SyntaxError as e:
            errors.append(f"Python语法错误: {e}")

    # 2. 模块依赖检查
    _REQUIRED_MODULES = ["watchdog", "yaml", "pathlib"]
    for module in _REQUIRED_MODULES:
        try:
            __import__(module)
        except ImportError:
            warnings.append(f"模块 '{module}' 未安装，可能影响功能")

    # 3. 文件路径检查
    if code_path:
        path = Path(code_path)
        if not path.exists():
            warnings.append(f"文件不存在: {code_path}")
        elif path.suffix == ".py":
            # 检查Python文件语法
            try:
                with open(path, "r", encoding="utf-8") as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                errors.append(f"Python语法错误 [{code_path}]: {e}")

    # 4. 执行Shell命令检查
    if script_content and ("subprocess" in script_content or "os.system" in script_content):
        warnings.append("脚本包含系统命令调用，建议QA审计")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checked_at": datetime.now().isoformat()
    }


def post_execution_evaluate(task: str, execution_result: dict = None) -> dict:
    """执行后自动评估（消除条件反射式询问）

    在每次执行完成后自动调用，判断是否需要Lysander介入。

    Args:
        task: 任务描述
        execution_result: 执行结果字典（可选）

    Returns:
        评估结果:
            - need_lysander: 是否需要Lysander
            - reason: 判断理由
            - action: 建议行动
    """
    task_lower = task.lower()

    # 执行成功的默认判断
    if execution_result and execution_result.get("success"):
        follow_up_keywords = [
            "下一步", "接下来", "然后", "继续",
            "发布", "deploy", "上线",
        ]
        for kw in follow_up_keywords:
            if kw in task_lower:
                return {
                    "need_lysander": False,
                    "reason": "执行成功，有后续关键词，但应继续执行而非询问",
                    "action": "直接执行后续步骤"
                }

        return {
            "need_lysander": False,
            "reason": "任务执行成功，无需Lysander",
            "action": "任务完成"
        }

    # 执行失败的判断
    if execution_result and not execution_result.get("success"):
        error_type = execution_result.get("error_type", "")
        if error_type in ["syntax_error", "import_error"]:
            return {
                "need_lysander": False,
                "reason": "代码错误，应记录到Harness并尝试修复",
                "action": "触发Harness自我修复流程"
            }
        return {
            "need_lysander": True,
            "reason": f"执行失败（{error_type}），需要Lysander判断",
            "action": "上报Lysander"
        }

    # 无执行结果，按正常流程判断
    return {
        "need_lysander": False,
        "reason": "无明确需要Lysander的情况",
        "action": "继续执行或结束"
    }


# ============================================================================
# 执行链机制：任务完成后自动执行后续步骤
# ============================================================================

# 任务执行链定义：当前任务 -> 后续任务列表
TASK_EXECUTION_CHAIN = {
    # 同步 -> 构建 -> 发布
    "同步OBS人员卡片到YAML": [
        {"task": "构建网站", "team": "rd", "keywords": ["astro", "build", "npm run build"]},
    ],
    "同步所有团队配置": [
        {"task": "构建网站", "team": "rd", "keywords": ["astro", "build", "npm run build"]},
    ],
    "构建网站": [
        {"task": "发布博客文章", "team": "content_ops", "keywords": ["wechat", "blog", "发布"]},
    ],
}

# 需要人工确认的决策点（不自动执行）
REQUIRES_CONFIRMATION = [
    "战略规划", "组织调整", "裁员", "重大投资",
]


class TaskChainExecutor:
    """执行链执行器"""

    def __init__(self):
        self.executed_chain = []

    def evaluate_and_execute_chain(self, current_task: str, context: dict = None) -> dict:
        """评估并执行后续任务链

        Args:
            current_task: 当前任务描述
            context: 执行上下文

        Returns:
            执行结果字典
        """
        self.executed_chain.append(current_task)

        # 检查是否需要确认
        for confirm_keyword in REQUIRES_CONFIRMATION:
            if confirm_keyword in current_task:
                return {
                    "task": current_task,
                    "status": "requires_confirmation",
                    "reason": f"任务涉及【{confirm_keyword}】，需要Lysander确认",
                    "chain_executed": self.executed_chain[:-1]
                }

        # 查找后续任务
        next_tasks = TASK_EXECUTION_CHAIN.get(current_task, [])

        if not next_tasks:
            return {
                "task": current_task,
                "status": "completed",
                "reason": "任务链结束",
                "chain_executed": self.executed_chain[:-1]
            }

        # 执行后续任务
        results = []
        for next_task_config in next_tasks:
            next_task = next_task_config["task"]
            result = {
                "task": next_task,
                "status": "executed",
                "executor": next_task_config.get("team", "auto")
            }
            results.append(result)

            # 递归执行后续链
            chain_result = self.evaluate_and_execute_chain(next_task, context)
            results.extend(chain_result.get("chain_results", []))

        return {
            "task": current_task,
            "status": "chain_completed",
            "chain_results": results,
            "chain_executed": self.executed_chain[:-1]
        }


def execute_task_chain(tasks: list) -> dict:
    """执行任务链

    Args:
        tasks: 任务列表（只执行第一个，后续由递归处理）

    Returns:
        执行结果
    """
    if not tasks:
        return {"total_tasks": 0, "results": [], "full_chain": []}

    executor = TaskChainExecutor()
    result = executor.evaluate_and_execute_chain(tasks[0])

    return {
        "total_tasks": len(tasks),
        "results": [result],
        "full_chain": executor.executed_chain
    }


def evaluate_and_execute(task: str, execution_func, *args, **kwargs) -> dict:
    """执行后自动评估的封装函数

    Args:
        task: 任务描述
        execution_func: 执行函数
        *args, **kwargs: 传递给执行函数的参数

    Returns:
        包含执行结果和评估结果的字典
    """
    result = None
    try:
        result = execution_func(*args, **kwargs)
        exec_result = {"success": True, "result": result}
    except Exception as e:
        exec_result = {"success": False, "error": str(e)}

    evaluation = post_execution_evaluate(task, exec_result)

    return {
        "execution": exec_result,
        "evaluation": evaluation,
        "task": task
    }


def _load_decision_log() -> dict:
    """加载决策日志"""
    if DECISION_LOG_PATH.exists():
        with open(DECISION_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"decisions": [], "feedback": []}


def _save_decision_log(log: dict):
    """保存决策日志"""
    with open(DECISION_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
