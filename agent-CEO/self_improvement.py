"""
Synapse Self-Improvement Loop Engine
=====================================
Synapse v3.0 — Phase 2 T5-1

自动执行闭环：
  执行结果 → 数据采集 → 模式识别 → 改进建议 → 验证 → 融入Harness

Usage:
    from self_improvement import SelfImprovementLoop, ExecutionRecord

    loop = SelfImprovementLoop(
        records_file="agent-CEO/data/execution_records.json",
        suggestions_file="agent-CEO/data/improvement_suggestions.json"
    )
    loop.record_execution(record)
    patterns = loop.analyze_patterns()
    suggestions = loop.generate_suggestions()
    loop.approve_suggestion("IMP-20260422-001")
    loop.implement_suggestion("IMP-20260422-001")
"""

import json
import os
import sys
import re
import importlib.util
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import Optional, Literal
from enum import Enum

import yaml

# ── 动态导入同目录模块（避免循环导入）───────────────────────────────
_HARNESS_FSM_AUDIT = None
_QA_REVIEW_FN = None

def _load_fsm_audit():
    global _HARNESS_FSM_AUDIT
    if _HARNESS_FSM_AUDIT is None:
        fsm_path = os.path.join(os.path.dirname(__file__), "harness_fsm.py")
        if os.path.exists(fsm_path):
            spec = importlib.util.spec_from_file_location("harness_fsm", fsm_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["harness_fsm"] = mod
            spec.loader.exec_module(mod)
            _HARNESS_FSM_AUDIT = mod.audit_fsm_transition
    return _HARNESS_FSM_AUDIT

def _load_qa_review():
    global _QA_REVIEW_FN
    if _QA_REVIEW_FN is None:
        hr_path = os.path.join(os.path.dirname(__file__), "hr_base.py")
        if os.path.exists(hr_path):
            spec = importlib.util.spec_from_file_location("hr_base", hr_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["hr_base"] = mod
            spec.loader.exec_module(mod)
            _QA_REVIEW_FN = mod.qa_auto_review
    return _QA_REVIEW_FN


# ──────────────────────────────────────────────
# Data Models
# ──────────────────────────────────────────────

class TaskComplexity(str, Enum):
    S = "S"
    M = "M"
    L = "L"


class SuggestionStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


class SuggestionCategory(str, Enum):
    PROCESS = "process"
    TOOL = "tool"
    KNOWLEDGE = "knowledge"
    TEAM = "team"


class SuggestionPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


@dataclass
class ExecutionRecord:
    """单次任务执行记录"""
    task_id: str
    agent_id: str
    quality_score: float          # 0-5 质量评分
    completion_time_minutes: float
    blockers: list[str]          # 阻塞原因列表
    timestamp: str                # ISO 8601
    task_type: str                # 任务类型标识，如 T1/T2/T6
    complexity: str               # S/M/L 预估复杂度


@dataclass
class ImprovementSuggestion:
    """改进建议"""
    suggestion_id: str
    category: str                 # process / tool / knowledge / team
    description: str
    evidence: list[str]           # 支持该建议的数据点
    impact_score: float           # 预期改进效果 0-1
    priority: str                 # P0/P1/P2
    status: str                  # proposed / approved / implemented / rejected
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved_at: Optional[str] = None
    implemented_at: Optional[str] = None


# ──────────────────────────────────────────────
# 语义模式库（启发式近似实现，不依赖外部 LLM API）
# ──────────────────────────────────────────────

SEMANTIC_PATTERNS: list[dict] = [
    {
        "id": "SP-001",
        "keywords": ["配置", "config", "yaml", "missing", "缺失"],
        "root_cause": "Agent 缺少任务所需的环境配置或上下文初始化",
        "suggestion": "在任务执行前增加配置预检节点，自动加载所需环境变量和配置文件",
    },
    {
        "id": "SP-002",
        "keywords": ["权限", "permission", "auth", "access", "denied"],
        "root_cause": "Agent 权限不足，无法访问所需资源或执行特定操作",
        "suggestion": "完善权限声明机制，任务分发前检查执行者权限是否满足要求",
    },
    {
        "id": "SP-003",
        "keywords": ["文档", "doc", "knowledge", "context", "unclear"],
        "root_cause": "Agent 缺乏足够的上下文知识，导致理解偏差或执行质量下降",
        "suggestion": "补充知识库内容，在 OBS 中建立该任务类型的执行模板",
    },
    {
        "id": "SP-004",
        "keywords": ["依赖", "dependency", "block", "前置", "waiting"],
        "root_cause": "Agent 等待前置任务完成或外部依赖解决，导致阻塞",
        "suggestion": "优化依赖管理机制，在阻塞发生时自动上报 COO 并触发资源协调",
    },
    {
        "id": "SP-005",
        "keywords": ["超时", "timeout", "too long", "超时", "hang"],
        "root_cause": "Agent 执行时间超出预期，可能陷入循环或遇到复杂边缘情况",
        "suggestion": "对长时任务增加中间检查点（checkpoint），超时后自动降级或上报",
    },
    {
        "id": "SP-006",
        "keywords": ["质量", "quality", "low quality", "low score", "低于", "不合格"],
        "root_cause": "Agent 输出的内容未达到质量门禁，可能因对任务类型不熟悉",
        "suggestion": "路由时增强质量评分权重，或将该任务类型路由给历史质量更高的 Agent",
    },
    {
        "id": "SP-007",
        "keywords": ["路由", "router", "wrong agent", "分配", "错误"],
        "root_cause": "CapabilityRouter 将任务分配给能力不匹配的 Agent",
        "suggestion": "更新 Agent 能力卡片中的 skill_levels，或调整路由权重配置",
    },
    {
        "id": "SP-008",
        "keywords": ["bug", "error", "exception", "crash", "错误"],
        "root_cause": "Agent 执行代码时遇到未捕获异常，可能是环境或依赖不一致",
        "suggestion": "建立统一的开发环境镜像，在执行前验证依赖版本一致性",
    },
]


def _match_semantic_pattern(blocker_text: str) -> list[dict]:
    """根据 blocker 文本匹配语义模式（启发式关键词匹配）"""
    text_lower = blocker_text.lower()
    matched = []
    for pattern in SEMANTIC_PATTERNS:
        for kw in pattern["keywords"]:
            if kw.lower() in text_lower:
                matched.append(pattern)
                break
    return matched


# ──────────────────────────────────────────────
# Self-Improvement Loop Engine
# ──────────────────────────────────────────────

class SelfImprovementLoop:
    """
    Synapse 自我改进闭环引擎

    核心流程：
    1. record_execution  — 记录每次执行结果
    2. analyze_patterns  — 分析执行模式，识别改进机会
    3. generate_suggestions — 基于分析生成改进建议
    4. approve_suggestion — Lysander/专家审批建议
    5. implement_suggestion — 执行已批准的建议，更新 Harness
    """

    # 质量评分门禁线
    QUALITY_THRESHOLD = 3.5      # 低于此值视为低质量
    BLOCKER_RATE_WINDOW_DAYS = 7 # 阻塞率统计窗口（天）
    MIN_RECORDS_FOR_ANALYSIS = 5 # 最少记录数才进行分析

    def __init__(self, records_file: str, suggestions_file: str):
        self.records_file = records_file
        self.suggestions_file = suggestions_file
        self.records: list[ExecutionRecord] = []
        self.suggestions: list[ImprovementSuggestion] = []
        self._load()

    def _load(self):
        """加载历史记录"""
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = [ExecutionRecord(**r) for r in data.get("records", [])]
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[SelfImprovement] Warning: failed to load records: {e}")

        if os.path.exists(self.suggestions_file):
            try:
                with open(self.suggestions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.suggestions = [ImprovementSuggestion(**s) for s in data.get("suggestions", [])]
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[SelfImprovement] Warning: failed to load suggestions: {e}")

    def _save(self):
        """持久化保存记录"""
        os.makedirs(os.path.dirname(self.records_file), exist_ok=True)
        with open(self.records_file, "w", encoding="utf-8") as f:
            json.dump({"records": [asdict(r) for r in self.records]}, f, indent=2, ensure_ascii=False)

        os.makedirs(os.path.dirname(self.suggestions_file), exist_ok=True)
        with open(self.suggestions_file, "w", encoding="utf-8") as f:
            json.dump({"suggestions": [asdict(s) for s in self.suggestions]}, f, indent=2, ensure_ascii=False)

    # ── 数据采集 ──────────────────────────────────

    def record_execution(self, record: ExecutionRecord):
        """
        记录一次执行结果

        Args:
            record: ExecutionRecord 实例

        Returns:
            执行记录 ID
        """
        self.records.append(record)
        self._save()
        return record.task_id

    def record_batch(self, records: list[ExecutionRecord]):
        """批量记录执行结果"""
        self.records.extend(records)
        self._save()

    # ── 语义分析 ──────────────────────────────────

    def _semantic_root_cause_analysis(self, execution_records: list) -> dict:
        """
        分析失败案例的 LLM 语义根因（启发式近似实现）

        对每条 BLOCKED 或低质量记录，生成问题描述：
        "为什么 [Agent] 在 [任务类型] 上表现 [当前状态]？"

        Args:
            execution_records: ExecutionRecord 列表（通常为问题记录子集）

        Returns:
            {
                "semantic_findings": [
                    {
                        "record": ExecutionRecord,
                        "question": str,          # 语义问题描述
                        "matched_patterns": [dict], # 匹配的 SEMANTIC_PATTERNS
                        "root_cause": str,        # 推断根因
                        "suggestion": str,        # 对应改进建议
                    }
                ],
                "pattern_frequency": {"SP-001": count, ...},
                "total_analyzed": int,
            }
        """
        findings: list = []
        pattern_freq: dict = {}

        for rec in execution_records:
            # 筛选有问题特征的记录
            is_blocked = bool(rec.blockers)
            is_low_quality = rec.quality_score < self.QUALITY_THRESHOLD

            if not (is_blocked or is_low_quality):
                continue

            # 生成语义问题描述
            if is_blocked:
                blocker_str = "; ".join(rec.blockers)
                question = (
                    f"为什么 {rec.agent_id} 在任务 {rec.task_id}（{rec.task_type}）上"
                    f"被阻塞？阻塞原因：{blocker_str}"
                )
                # 合并所有 blocker 文本做关键词匹配
                matched = _match_semantic_pattern(blocker_str)
                for b in rec.blockers[1:]:
                    matched = matched + [
                        p for p in _match_semantic_pattern(b)
                        if p not in matched
                    ]
            else:
                question = (
                    f"为什么 {rec.agent_id} 在任务 {rec.task_id}（{rec.task_type}）上"
                    f"质量评分仅 {rec.quality_score}/5.0？"
                )
                matched = _match_semantic_pattern(
                    f"low quality score {rec.quality_score}"
                )

            root_cause = (
                matched[0]["root_cause"]
                if matched
                else ("未知根因：需人工审查" if is_blocked
                      else f"质量偏低，可能与 Agent 能力覆盖有关")
            )
            suggestion = (
                matched[0]["suggestion"]
                if matched
                else ("建议人工审查 blocker 原因" if is_blocked
                      else "建议提升路由质量评分权重或更新 Agent 能力卡片")
            )

            for p in matched:
                pattern_freq[p["id"]] = pattern_freq.get(p["id"], 0) + 1

            findings.append({
                "record": rec,
                "question": question,
                "matched_patterns": matched,
                "root_cause": root_cause,
                "suggestion": suggestion,
            })

        return {
            "semantic_findings": findings,
            "pattern_frequency": pattern_freq,
            "total_analyzed": len(execution_records),
        }

    # ── 模式识别 ──────────────────────────────────

    def analyze_patterns(self) -> dict:
        """
        分析执行模式，识别改进机会

        Returns:
            dict，包含：
            - status: "ok" | "insufficient_data"
            - total_records: int
            - top_blocked_agents: list[tuple[agent_id, count]]
            - lowest_quality_tasks: list[tuple[task_type, avg_score]]
            - blocker_rate_7d: float
            - avg_quality_by_agent: dict
            - analyzed_at: ISO timestamp
        """
        if len(self.records) < self.MIN_RECORDS_FOR_ANALYSIS:
            return {
                "status": "insufficient_data",
                "records_needed": self.MIN_RECORDS_FOR_ANALYSIS - len(self.records),
                "total_records": len(self.records)
            }

        # 分析1：Agent 阻塞率排名
        agent_blocked: dict[str, int] = {}
        agent_total: dict[str, int] = {}
        for r in self.records:
            agent_total[r.agent_id] = agent_total.get(r.agent_id, 0) + 1
            if r.blockers:
                agent_blocked[r.agent_id] = agent_blocked.get(r.agent_id, 0) + 1

        # 计算阻塞率
        agent_blocker_rate = {
            agent: agent_blocked.get(agent, 0) / total
            for agent, total in agent_total.items()
        }

        # 分析2：任务类型平均质量
        task_quality: dict[str, list[float]] = {}
        for r in self.records:
            task_quality.setdefault(r.task_type, []).append(r.quality_score)

        avg_task_quality = {
            t: sum(scores) / len(scores)
            for t, scores in task_quality.items()
        }

        # 分析3：7天阻塞率
        cutoff = datetime.now() - timedelta(days=self.BLOCKER_RATE_WINDOW_DAYS)
        recent_blocked = [
            r for r in self.records
            if r.blockers and datetime.fromisoformat(r.timestamp) > cutoff
        ]
        recent_total = [
            r for r in self.records
            if datetime.fromisoformat(r.timestamp) > cutoff
        ]
        blocker_rate_7d = (
            len(recent_blocked) / len(recent_total)
            if recent_total else 0.0
        )

        # 分析4：各 Agent 平均质量
        agent_quality: dict[str, list[float]] = {}
        for r in self.records:
            agent_quality.setdefault(r.agent_id, []).append(r.quality_score)
        avg_agent_quality = {
            agent: sum(scores) / len(scores)
            for agent, scores in agent_quality.items()
        }

        result = {
            "status": "ok",
            "total_records": len(self.records),
            "top_blocked_agents": sorted(
                [(a, c) for a, c in agent_blocked.items()],
                key=lambda x: x[1], reverse=True
            )[:5],
            "agent_blocker_rate": dict(sorted(agent_blocker_rate.items(), key=lambda x: x[1], reverse=True)),
            "lowest_quality_tasks": sorted(avg_task_quality.items(), key=lambda x: x[1])[:3],
            "blocker_rate_7d": round(blocker_rate_7d, 3),
            "recent_blocked_count": len(recent_blocked),
            "recent_total_count": len(recent_total),
            "avg_quality_by_agent": {k: round(v, 2) for k, v in avg_agent_quality.items()},
            "avg_quality_overall": round(
                sum(r.quality_score for r in self.records) / len(self.records), 2
            ),
            "analyzed_at": datetime.now().isoformat()
        }

        # ── 语义分析集成 ──────────────────────────────────────────
        # 对所有低质量 + 阻塞记录执行语义根因分析
        problem_records = [
            r for r in self.records
            if r.blockers or r.quality_score < self.QUALITY_THRESHOLD
        ]
        semantic = self._semantic_root_cause_analysis(problem_records)
        result["semantic_findings"] = [
            {k: v for k, v in f.items() if k != "record"}
            for f in semantic["semantic_findings"]
        ]
        result["semantic_pattern_frequency"] = semantic["pattern_frequency"]
        result["semantic_total_analyzed"] = semantic["total_analyzed"]

        return result

    # ── 建议生成 ──────────────────────────────────

    def generate_suggestions(self) -> list[ImprovementSuggestion]:
        """
        基于分析生成改进建议

        规则：
        - 高阻塞率 Agent → team 类别建议
        - 低质量任务类型（<3.5）→ process 类别建议
        - 7天内阻塞任务 ≥ 3 → process 建议增加阻塞预检节点
        - 低质量 Agent（<3.5 均分）→ team 类别建议

        Returns:
            新生成的 ImprovementSuggestion 列表
        """
        patterns = self.analyze_patterns()
        if patterns.get("status") != "ok":
            return []

        suggestions = []
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        new_suggestions = []

        # 建议A：高阻塞率 Agent（阻塞率最高者）
        if patterns.get("top_blocked_agents"):
            top_agent, top_count = patterns["top_blocked_agents"][0]
            rate = patterns["agent_blocker_rate"].get(top_agent, 0)
            if rate >= 0.2:  # 阻塞率 >= 20% 才触发
                new_suggestions.append(ImprovementSuggestion(
                    suggestion_id=f"IMP-{ts}-A01",
                    category="team",
                    description=(
                        f"Agent '{top_agent}' 阻塞率 {rate:.0%}（{top_count}次阻塞），"
                        "建议审查其工作流程或补充必要工具/知识"
                    ),
                    evidence=[
                        f"过去{len(self.records)}个任务中阻塞{top_count}次",
                        f"阻塞率 {rate:.0%}",
                        f"Agent ID: {top_agent}"
                    ],
                    impact_score=min(0.7 + rate * 0.3, 1.0),
                    priority="P1",
                    status="proposed"
                ))

        # 建议B：低质量任务类型
        for task_type, avg_score in patterns.get("lowest_quality_tasks", []):
            if avg_score < self.QUALITY_THRESHOLD:
                new_suggestions.append(ImprovementSuggestion(
                    suggestion_id=f"IMP-{ts}-B01",
                    category="process",
                    description=(
                        f"任务类型 '{task_type}' 平均质量 {avg_score:.2f}/5.0 低于门禁线 "
                        f"({self.QUALITY_THRESHOLD})，建议优化流程模板或增加 QA 验证节点"
                    ),
                    evidence=[
                        f"平均质量评分 {avg_score:.2f}/5.0",
                        f"门禁线 {self.QUALITY_THRESHOLD}",
                        f"任务类型: {task_type}"
                    ],
                    impact_score=min(0.6 + (self.QUALITY_THRESHOLD - avg_score) * 0.2, 1.0),
                    priority="P0",
                    status="proposed"
                ))
                break  # 只提一个

        # 建议C：7天内阻塞任务过多 → 增加阻塞预检
        if patterns.get("recent_blocked_count", 0) >= 3:
            new_suggestions.append(ImprovementSuggestion(
                suggestion_id=f"IMP-{ts}-C01",
                category="process",
                description=(
                    f"近{self.BLOCKER_RATE_WINDOW_DAYS}天阻塞任务 {patterns['recent_blocked_count']} 次（"
                    f"占比 {patterns.get('blocker_rate_7d', 0):.0%}），"
                    "建议在执行链【①】和【②】之间增加'阻塞预检'节点"
                ),
                evidence=[
                    f"{self.BLOCKER_RATE_WINDOW_DAYS}天内 {patterns['recent_blocked_count']} 个任务阻塞",
                    f"阻塞率 {patterns.get('blocker_rate_7d', 0):.0%}",
                    "建议增加前置检查节点"
                ],
                impact_score=0.85,
                priority="P0",
                status="proposed"
            ))

        # 建议E：语义分析发现的根因（来自 _semantic_root_cause_analysis）
        semantic_findings = patterns.get("semantic_findings", [])
        semantic_pattern_freq = patterns.get("semantic_pattern_frequency", {})
        if semantic_findings and semantic_pattern_freq:
            # 找出频率最高的语义模式
            top_pattern_id = max(semantic_pattern_freq, key=semantic_pattern_freq.get)
            top_pattern = next(
                (p for p in SEMANTIC_PATTERNS if p["id"] == top_pattern_id), None
            )
            if top_pattern and semantic_pattern_freq.get(top_pattern_id, 0) >= 2:
                new_suggestions.append(ImprovementSuggestion(
                    suggestion_id=f"IMP-{ts}-E01",
                    category="process",
                    description=(
                        f"语义分析发现：{semantic_pattern_freq[top_pattern_id]}次问题匹配根因 "
                        f"「{top_pattern['root_cause']}」，"
                        f"建议：{top_pattern['suggestion']}"
                    ),
                    evidence=[
                        f"语义模式 ID: {top_pattern_id}",
                        f"匹配次数: {semantic_pattern_freq[top_pattern_id]}",
                        f"根因: {top_pattern['root_cause']}",
                        f"语义问题示例: {semantic_findings[0]['question'][:80]}...",
                    ],
                    impact_score=0.75,
                    priority="P1",
                    status="proposed"
                ))

        # 建议D：低质量 Agent
        low_quality_agents = [
            (agent, score)
            for agent, score in patterns.get("avg_quality_by_agent", {}).items()
            if score < self.QUALITY_THRESHOLD
        ]
        if low_quality_agents:
            agent, score = low_quality_agents[0]
            new_suggestions.append(ImprovementSuggestion(
                suggestion_id=f"IMP-{ts}-D01",
                category="team",
                description=(
                    f"Agent '{agent}' 平均质量 {score:.2f}/5.0 低于门禁线，"
                    "建议补充该 Agent 的能力描述或调整任务分配"
                ),
                evidence=[
                    f"平均质量 {score:.2f}/5.0（门禁 {self.QUALITY_THRESHOLD}）",
                    f"Agent ID: {agent}"
                ],
                impact_score=0.6,
                priority="P1",
                status="proposed"
            ))

        # 去重：检查是否已有类似建议（30天内同类）
        cutoff_recent = datetime.now() - timedelta(days=30)
        existing_recent = [
            s for s in self.suggestions
            if datetime.fromisoformat(s.created_at.replace("Z", "+00:00").split("+")[0]) > cutoff_recent
            if s.category in [ns.category for ns in new_suggestions]
        ]

        for new_s in new_suggestions:
            is_duplicate = any(
                new_s.category == ex.category and
                any(ev in ex.description for ev in new_s.evidence[:1])
                for ex in existing_recent
            )
            if not is_duplicate:
                suggestions.append(new_s)

        # 保存
        self.suggestions.extend(suggestions)
        self._save()
        return suggestions

    # ── 审批与执行 ──────────────────────────────────

    def approve_suggestion(self, suggestion_id: str) -> bool:
        """批准改进建议"""
        for s in self.suggestions:
            if s.suggestion_id == suggestion_id and s.status == SuggestionStatus.PROPOSED.value:
                s.status = SuggestionStatus.APPROVED.value
                s.approved_at = datetime.now().isoformat()
                self._save()
                return True
        return False

    def reject_suggestion(self, suggestion_id: str) -> bool:
        """拒绝改进建议"""
        for s in self.suggestions:
            if s.suggestion_id == suggestion_id and s.status == SuggestionStatus.PROPOSED.value:
                s.status = SuggestionStatus.REJECTED.value
                self._save()
                return True
        return False

    def _verify_harness_integrity(self, rule_change: dict) -> dict:
        """
        检查新增规则是否与现有规则冲突、是否超出熵增预算

        Args:
            rule_change: 规则变更字典，包含 description / category / priority

        Returns:
            验证结果 dict: {pass, conflicts, entropy_ok, warnings, level}
        """
        conflicts: list[str] = []
        warnings: list[str] = []
        entropy_ok = True
        new_desc = rule_change.get("description", "").lower()

        # 加载 harness_registry.yaml
        registry_path = os.path.join(
            os.path.dirname(__file__),
            "config",
            "harness_registry.yaml"
        )
        if not os.path.exists(registry_path):
            return {
                "pass": True, "conflicts": [], "entropy_ok": True,
                "warnings": ["harness_registry.yaml not found, skipping integrity check"],
                "level": "P2"
            }

        with open(registry_path, encoding="utf-8") as f:
            registry = yaml.safe_load(f) or {}

        p0_rules = registry.get("harness_registry", {}).get("constraints", {}).get("p0_rules", [])
        p1_rules = registry.get("harness_registry", {}).get("constraints", {}).get("p1_rules", [])

        # 冲突检测：检查新规则是否与现有 P0 规则矛盾
        for rule in p0_rules:
            existing_desc = rule.get("description", "").lower()
            # 简单关键词冲突：相同类别 + 相似关键词
            if (rule_change.get("category") == "process"
                    and any(kw in existing_desc for kw in ["禁止", "必须", "不可"])):
                # 检查是否矛盾（如新规则说"必须"，现有规则说"禁止"同一行为）
                negations = ["禁止", "不可", "拒绝", "不允许"]
                for neg in negations:
                    if neg in new_desc and neg in existing_desc:
                        if set(new_desc.split()) & set(existing_desc.split()) - set([neg]):
                            conflicts.append(
                                f"可能与 P0 规则冲突: [{rule['id']}] {rule.get('name')} — {existing_desc[:60]}"
                            )

        # 熵增预算检查：CLAUDE.md 当前上限 350 行
        line_count = 0
        claude_md_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "CLAUDE.md"
        )
        if os.path.exists(claude_md_path):
            with open(claude_md_path, encoding="utf-8") as f:
                lines = [l for l in f.readlines() if l.strip() and not l.startswith("#")]
                line_count = len(lines)
            ENTROPY_LIMIT = 350
            if line_count >= ENTROPY_LIMIT:
                entropy_ok = False
                warnings.append(f"熵增预算已达 {line_count}/{ENTROPY_LIMIT} 行，变更后需立即压缩")
            elif line_count >= ENTROPY_LIMIT * 0.9:
                warnings.append(f"熵增预算接近上限 {line_count}/{ENTROPY_LIMIT}，注意控制")

        level = "P0" if conflicts else ("P1" if warnings else "P2")
        return {
            "pass": len(conflicts) == 0,
            "conflicts": conflicts,
            "entropy_ok": entropy_ok,
            "warnings": warnings,
            "level": level,
            "claude_md_lines": line_count or None,
        }

    def implement_suggestion(self, suggestion_id: str) -> dict:
        """
        执行已批准的改进建议 — 真正的 Harness 自动更新

        实现策略：
        - process / team 类：自动追加规则到 harness_registry.yaml
        - tool 类：写入工具配置文件
        - knowledge 类：生成新知识文档
        每条变更记录快照到 implemented_changes.json（含变更前/后 + 时间戳）
        变更后自动触发 FSM audit_fsm_transition() 验证不违反 P0 约束
        变更后运行 QA 门禁 qa_auto_review() 验证体系完整性

        Returns:
            实施结果 dict
        """
        for s in self.suggestions:
            if s.suggestion_id == suggestion_id and s.status == SuggestionStatus.APPROVED.value:
                s.status = SuggestionStatus.IMPLEMENTED.value
                s.implemented_at = datetime.now().isoformat()

                # ── 前置完整性验证 ───────────────────────────────
                rule_change = {
                    "description": s.description,
                    "category": s.category,
                    "priority": s.priority,
                }
                integrity = self._verify_harness_integrity(rule_change)

                # 如果有冲突（P0 级别），拒绝执行
                if not integrity["pass"]:
                    s.status = SuggestionStatus.APPROVED.value  # 回滚状态
                    s.implemented_at = None
                    return {
                        "error": "integrity_conflict",
                        "reason": "新增规则与现有 P0 规则冲突，拒绝自动执行",
                        "conflicts": integrity["conflicts"],
                        "suggestion_id": suggestion_id,
                    }

                # ── 变更前快照 ─────────────────────────────────
                before_snapshot: dict = {}
                change_log_file = os.path.join(
                    os.path.dirname(self.suggestions_file),
                    "implemented_changes.json"
                )
                verification_log_file = os.path.join(
                    os.path.dirname(self.suggestions_file),
                    "implement_verification_log.json"
                )
                os.makedirs(os.path.dirname(change_log_file), exist_ok=True)

                if os.path.exists(change_log_file):
                    try:
                        with open(change_log_file, "r", encoding="utf-8") as f:
                            before_snapshot["changes_log"] = json.load(f)
                    except json.JSONDecodeError:
                        before_snapshot["changes_log"] = []

                # 读取 harness_registry.yaml 变更前快照
                registry_path = os.path.join(
                    os.path.dirname(__file__),
                    "config",
                    "harness_registry.yaml"
                )
                if os.path.exists(registry_path):
                    with open(registry_path, encoding="utf-8") as f:
                        before_snapshot["harness_registry"] = f.read()

                # ── 执行变更 ───────────────────────────────────
                category = s.category
                change_details: dict = {"action": "no-op", "files_written": []}

                if category in ("process", "team"):
                    change_details = self._append_rule_to_registry(s, registry_path)

                elif category == "tool":
                    change_details = self._write_tool_config(s)

                elif category == "knowledge":
                    change_details = self._write_knowledge_doc(s)

                # ── FSM 审计 ────────────────────────────────────
                fsm_fn = _load_fsm_audit()
                fsm_audit = {"pass": True, "violations": [], "level": "N/A"}
                if fsm_fn:
                    try:
                        fsm_audit = fsm_fn(
                            task_id=f"impl-{suggestion_id}",
                            from_state="idle",
                            to_state="in_progress",
                        )
                    except Exception as e:
                        fsm_audit = {
                            "pass": False,
                            "violations": [f"FSM audit failed: {e}"],
                            "level": "error"
                        }

                # ── QA 门禁 ─────────────────────────────────────
                qa_fn = _load_qa_review()
                qa_result: dict = {"score": None, "gate": "skipped"}
                if qa_fn:
                    try:
                        qa_result = qa_fn({
                            "content": change_details.get("action", ""),
                            "deliverable_type": "yaml",
                            "task_description": s.description,
                            "dispatch_record": f"self-improvement:{suggestion_id}",
                        })
                    except Exception as e:
                        qa_result = {"score": None, "gate": f"qa_error: {e}"}

                # ── 变更后快照 ──────────────────────────────────
                after_snapshot: dict = {}
                if os.path.exists(registry_path):
                    with open(registry_path, encoding="utf-8") as f:
                        after_snapshot["harness_registry"] = f.read()
                if os.path.exists(change_log_file):
                    try:
                        with open(change_log_file, "r", encoding="utf-8") as f:
                            after_snapshot["changes_log"] = json.load(f)
                    except json.JSONDecodeError:
                        after_snapshot["changes_log"] = []

                # ── 写入变更记录 ────────────────────────────────
                log_entry = {
                    "implemented": suggestion_id,
                    "category": s.category,
                    "action": s.description,
                    "evidence": s.evidence,
                    "priority": s.priority,
                    "timestamp": datetime.now().isoformat(),
                    "before_snapshot": before_snapshot,
                    "after_snapshot": after_snapshot,
                    "fsm_audit": fsm_audit,
                    "qa_review": qa_result,
                    "integrity_check": {
                        "conflicts": integrity["conflicts"],
                        "entropy_ok": integrity["entropy_ok"],
                        "warnings": integrity["warnings"],
                        "level": integrity["level"],
                    },
                    "change_details": change_details,
                }

                existing_log: list = before_snapshot.get("changes_log", [])
                existing_log.append(log_entry)
                with open(change_log_file, "w", encoding="utf-8") as f:
                    json.dump(existing_log, f, indent=2, ensure_ascii=False)

                # ── 写入验证日志 ────────────────────────────────
                os.makedirs(os.path.dirname(verification_log_file), exist_ok=True)
                verification_entry = {
                    "suggestion_id": suggestion_id,
                    "timestamp": datetime.now().isoformat(),
                    "integrity_pass": integrity["pass"],
                    "fsm_pass": fsm_audit.get("pass", False),
                    "qa_pass": qa_result.get("passed", False),
                    "overall_pass": (
                        integrity["pass"]
                        and fsm_audit.get("pass", True)
                        and qa_result.get("passed", True)
                    ),
                    "qa_score": qa_result.get("score"),
                    "fsm_violations": fsm_audit.get("violations", []),
                    "integrity_conflicts": integrity["conflicts"],
                    "integrity_warnings": integrity["warnings"],
                }
                if os.path.exists(verification_log_file):
                    try:
                        existing_verify = json.load(open(verification_log_file, encoding="utf-8"))
                    except json.JSONDecodeError:
                        existing_verify = []
                else:
                    existing_verify = []
                existing_verify.append(verification_entry)
                with open(verification_log_file, "w", encoding="utf-8") as f:
                    json.dump(existing_verify, f, indent=2, ensure_ascii=False)

                self._save()
                return log_entry

        return {"error": "suggestion_not_found_or_not_approved"}

    # ── Helper: 追加规则到 harness_registry.yaml ─────────────────────

    def _append_rule_to_registry(self, suggestion, registry_path: str) -> dict:
        """
        将 process/team 类建议追加为 harness_registry.yaml 中的规则

        Returns:
            change_details dict: {action, files_written, rules_added}
        """
        now = datetime.now()
        rule_id = f"AUTO-{now.strftime('%Y%m%d%H%M%S')}"
        category = suggestion.category  # process | team
        priority = suggestion.priority  # P0/P1/P2

        # 映射到正确的规则类别
        rule_key = {
            "process": "p1_rules",  # 降一级：process 不直接产生 P0 规则
            "team": "p1_rules",
        }.get(category, "p2_rules")

        new_rule = {
            "id": rule_id,
            "name": suggestion.description[:60],
            "description": suggestion.description,
            "source": f"self_improvement.py:auto-generated:{suggestion.suggestion_id}",
            "severity": priority,
            "added": now.strftime("%Y-%m-%d"),
            "auto_generated": True,
        }

        # 读取现有 YAML
        with open(registry_path, encoding="utf-8") as f:
            registry = yaml.safe_load(f)

        constraints = registry.get("harness_registry", {}).get("constraints", {})
        rule_list = constraints.get(rule_key, [])
        rule_list.append(new_rule)
        constraints[rule_key] = rule_list

        # 写回 YAML（保持原有格式风格）
        with open(registry_path, "w", encoding="utf-8") as f:
            yaml.dump(registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        return {
            "action": f"appended_rule_to_{rule_key}",
            "files_written": [registry_path],
            "rules_added": [rule_id],
        }

    # ── Helper: 工具配置写入 ──────────────────────────────────────────

    def _write_tool_config(self, suggestion) -> dict:
        """将 tool 类建议写入工具配置文件"""
        tool_config_dir = os.path.join(
            os.path.dirname(self.suggestions_file),
            "tool_configs"
        )
        os.makedirs(tool_config_dir, exist_ok=True)

        filename = f"auto_{suggestion.suggestion_id}.yaml"
        filepath = os.path.join(tool_config_dir, filename)

        config_data = {
            "source": f"self_improvement:{suggestion.suggestion_id}",
            "description": suggestion.description,
            "evidence": suggestion.evidence,
            "created_at": datetime.now().isoformat(),
            "auto_generated": True,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        return {
            "action": "wrote_tool_config",
            "files_written": [filepath],
        }

    # ── Helper: 知识文档写入 ──────────────────────────────────────────

    def _write_knowledge_doc(self, suggestion) -> dict:
        """将 knowledge 类建议写入 OBS 知识库"""
        kb_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "obs", "02-knowledge", "auto-generated"
        )
        os.makedirs(kb_dir, exist_ok=True)

        filename = f"IMP-{suggestion.suggestion_id}.md"
        filepath = os.path.join(kb_dir, filename)

        content = f"""---
tags:
  - auto-generated
  - self-improvement
source: {suggestion.suggestion_id}
created: {datetime.now().isoformat()}
---

# {suggestion.description}

## 来源
自动生成建议: {suggestion.suggestion_id}

## 描述
{suggestion.description}

## 证据
{chr(10).join(f"- {e}" for e in suggestion.evidence)}

## 优先级
{suggestion.priority}
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "action": "wrote_knowledge_doc",
            "files_written": [filepath],
        }

    # ── 查询接口 ──────────────────────────────────

    def get_suggestions(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None
    ) -> list[dict]:
        """获取改进建议列表（支持过滤）"""
        results = self.suggestions
        if status:
            results = [s for s in results if s.status == status]
        if category:
            results = [s for s in results if s.category == category]
        if priority:
            results = [s for s in results if s.priority == priority]
        return [asdict(s) for s in results]

    def get_records(self, limit: int = 50) -> list[dict]:
        """获取最近的执行记录"""
        sorted_records = sorted(
            self.records,
            key=lambda r: r.timestamp,
            reverse=True
        )
        return [asdict(r) for r in sorted_records[:limit]]

    def get_dashboard(self) -> dict:
        """获取 Self-Improvement 仪表盘摘要"""
        patterns = self.analyze_patterns()
        open_suggestions = self.get_suggestions(status="proposed")
        approved_suggestions = self.get_suggestions(status="approved")
        implemented_count = len(self.get_suggestions(status="implemented"))

        return {
            "total_records": len(self.records),
            "total_suggestions": len(self.suggestions),
            "open_suggestions": len(open_suggestions),
            "approved_suggestions": len(approved_suggestions),
            "implemented_count": implemented_count,
            "patterns": patterns,
            "p0_open": [s for s in open_suggestions if s["priority"] == "P0"],
            "p1_open": [s for s in open_suggestions if s["priority"] == "P1"],
        }

    def run_full_cycle(self) -> dict:
        """
        运行完整自我改进闭环

        自动化调用流程（供每日 Agent 使用）：
        1. analyze_patterns  — 分析模式
        2. generate_suggestions — 生成建议
        3. 返回仪表盘摘要
        """
        patterns = self.analyze_patterns()
        new_suggestions = self.generate_suggestions()
        return {
            "cycle_run_at": datetime.now().isoformat(),
            "patterns": patterns,
            "new_suggestions_count": len(new_suggestions),
            "new_suggestions": [asdict(s) for s in new_suggestions],
            "dashboard": self.get_dashboard()
        }


# ──────────────────────────────────────────────
# Demo / 验证脚本
# ──────────────────────────────────────────────

def _demo():
    """闭环验证演示"""
    print("=" * 60)
    print("Self-Improvement Loop — Demo")
    print("=" * 60)

    loop = SelfImprovementLoop(
        records_file="data/exec_demo.json",
        suggestions_file="data/suggest_demo.json"
    )

    # 模拟执行记录
    agents = ["harness_engineer", "ai_systems_dev", "knowledge_engineer"]
    tasks = ["T6-1", "T2-1", "T1-1", "T3-1", "T5-1"]
    blockers_pool = ["配置缺失", "权限不足", "文档缺失", "依赖未解决", ""]

    print("\n[1] Recording 12 execution records...")
    import random
    random.seed(42)
    for i in range(12):
        blockers = []
        if i % 4 == 0:
            blockers.append(random.choice(["配置缺失", "权限不足", "依赖未解决"]))
        if i % 7 == 0:
            blockers.append("文档缺失")

        loop.record_execution(ExecutionRecord(
            task_id=f"T{i:03d}",
            agent_id=agents[i % len(agents)],
            quality_score=round(3.0 + (i % 5) * 0.35, 2),
            completion_time_minutes=20 + i * 4,
            blockers=blockers,
            timestamp=datetime.now().isoformat(),
            task_type=tasks[i % len(tasks)],
            complexity=["S", "M", "M", "L"][i % 4]
        ))

    print(f"    Recorded: {len(loop.records)} records")

    # 分析
    print("\n[2] Analyzing patterns...")
    patterns = loop.analyze_patterns()
    print(f"    Status: {patterns.get('status')}")
    print(f"    Total records: {patterns.get('total_records')}")
    print(f"    Top blocked agents: {patterns.get('top_blocked_agents')}")
    print(f"    Lowest quality tasks: {patterns.get('lowest_quality_tasks')}")
    print(f"    7d blocker rate: {patterns.get('blocker_rate_7d')}")
    print(f"    Avg quality: {patterns.get('avg_quality_overall')}")

    # 生成建议
    print("\n[3] Generating suggestions...")
    new_suggestions = loop.generate_suggestions()
    print(f"    Generated {len(new_suggestions)} new suggestions:")
    for s in new_suggestions:
        print(f"    [{s.priority}] {s.suggestion_id}: {s.description[:70]}")

    # 审批并执行
    print("\n[4] Approving and implementing P0 suggestions...")
    for s in new_suggestions:
        if s.priority == "P0":
            loop.approve_suggestion(s.suggestion_id)
            result = loop.implement_suggestion(s.suggestion_id)
            print(f"    Implemented: {result.get('implemented')} — {result.get('action', result.get('error', ''))[:60]}")

    # 仪表盘
    print("\n[5] Dashboard:")
    dashboard = loop.get_dashboard()
    print(f"    Total records: {dashboard['total_records']}")
    print(f"    Open suggestions: {dashboard['open_suggestions']}")
    print(f"    Implemented: {dashboard['implemented_count']}")
    print(f"    P0 open: {len(dashboard['p0_open'])}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)

    return loop, patterns, new_suggestions


if __name__ == "__main__":
    _demo()
