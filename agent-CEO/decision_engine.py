# -*- coding: utf-8 -*-
"""
Synapse v3.0 — Decision Engine
四级决策引擎：L1自动 → L2专家 → L3 Lysander → L4总裁

Phase 3 T6-4: 决策规则引擎
用法:
    from agent_butler.decision_engine import DecisionEngine
    engine = DecisionEngine()
    result = engine.decide({"task_type": "query", "scope": "single_team"})
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# 默认决策日志路径
DEFAULT_LOG_DIR = Path(__file__).parent / "logs"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "decision_log.jsonl"


class DecisionEngine:
    """L1-L4 决策引擎

    决策流程:
        L1: 例行操作自动执行（信息查询、状态确认）
        L2: 专家评审（需要专业判断的任务）
        L3: Lysander CEO 决策（跨团队、高优先级）
        L4: 总裁决策（法律/重大财务/公司存续）
    """

    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = Path(log_file) if log_file else DEFAULT_LOG_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.decision_log: list = []

    # ─── 核心决策 ──────────────────────────────────────────────

    def decide(self, context: dict) -> dict:
        """根据任务上下文自动判断决策级别

        Args:
            context: {
                task_type: str,       # "query" | "routine" | "complex" | "strategic"
                scope: str,           # "single_team" | "cross_team"
                priority: str,        # "P0" | "P1" | "P2" | "P3"
                complexity: str,      # "S" | "M" | "L"
                legal: bool,          # 是否涉及法律/合同
                financial: bool,      # 是否涉及重大财务
                risk_level: str,      # "low" | "medium" | "high" | "critical"
            }

        Returns:
            {
                "level": "L1"|"L2"|"L3"|"L4",
                "action": str,
                "reason": str,
                "next_steps": list[str],
                "timestamp": str
            }
        """
        # P0-5: 冲突检测（L2/L3边界）
        has_conflict, conflict_desc = self._detect_routing_conflict(context)

        # L4: 总裁决策（法律 / 重大财务 / 公司存续）
        if self._needs_president_decision(context):
            result = {
                "level": "L4",
                "action": "escalate_to_president",
                "reason": self._l4_reason(context),
                "next_steps": ["收集完整材料", "准备决策简报", "等待总裁决策"],
                "timestamp": datetime.now().isoformat(),
                # P0-5: 冲突检测结果
                "conflict_detected": has_conflict,
                "conflict_description": conflict_desc if has_conflict else "",
            }
        # L3: Lysander 决策（跨团队 / P0-P1 / 高风险战略）
        elif self._needs_ceo_decision(context):
            result = {
                "level": "L3",
                "action": "escalate_to_ceo",
                "reason": self._l3_reason(context),
                "next_steps": ["召集专家评审", "Lysander 综合意见决策", "派单执行团队"],
                "timestamp": datetime.now().isoformat(),
                # P0-5: 冲突检测结果
                "conflict_detected": has_conflict,
                "conflict_description": conflict_desc if has_conflict else "",
            }
        # L2: 专家评审（复杂度 M/L / 非例行）
        elif self._needs_expert_review(context):
            result = {
                "level": "L2",
                "action": "expert_review",
                "reason": "needs_professional_judgment",
                "next_steps": ["execution_auditor 识别专家", "各专家独立分析", "decision_advisor 综合建议"],
                "timestamp": datetime.now().isoformat(),
                # P0-5: 冲突检测结果
                "conflict_detected": has_conflict,
                "conflict_description": conflict_desc if has_conflict else "",
            }
        # L1: 自动执行（例行 / 查询 / 低风险）
        else:
            result = {
                "level": "L1",
                "action": "auto_execute",
                "reason": "routine_operation",
                "next_steps": ["直接执行", "记录执行日志"],
                "timestamp": datetime.now().isoformat(),
                # P0-5: L1无冲突
                "conflict_detected": False,
                "conflict_description": "",
            }

        # P0-5: 冲突时记录warning日志
        if has_conflict:
            self._log_warning(context, result, conflict_desc)

        self._log_decision(context, result)
        return result

    # ─── L4 判定 ──────────────────────────────────────────────

    def _needs_president_decision(self, ctx: dict) -> bool:
        """L4: 法律 / 重大财务 / 公司存续"""
        if ctx.get("legal"):
            return True
        if ctx.get("financial"):
            return True
        if ctx.get("company_critical"):
            return True
        return False

    def _l4_reason(self, ctx: dict) -> str:
        reasons = []
        if ctx.get("legal"):
            reasons.append("涉及法律/合同协议")
        if ctx.get("financial"):
            reasons.append("涉及重大财务/预算>100万")
        if ctx.get("company_critical"):
            reasons.append("公司存续级不可逆决策")
        return "; ".join(reasons) or "president_explicit_required"

    # ─── L3 判定 ──────────────────────────────────────────────

    def _needs_ceo_decision(self, ctx: dict) -> bool:
        """L3: 跨团队 / P0-P1 / 高风险战略"""
        if ctx.get("scope") == "cross_team":
            return True
        if ctx.get("priority") in ["P0", "P1"]:
            return True
        if ctx.get("risk_level") in ["high", "critical"]:
            return True
        if ctx.get("task_type") in ["strategic", "irreversible"]:
            return True
        return False

    def _l3_reason(self, ctx: dict) -> str:
        if ctx.get("scope") == "cross_team":
            return "cross_team_scope"
        if ctx.get("priority") in ["P0", "P1"]:
            return f"high_priority_{ctx.get('priority')}"
        if ctx.get("risk_level") in ["high", "critical"]:
            return f"high_risk_{ctx.get('risk_level')}"
        return "strategic_or_cross_team"

    # ─── L2 判定 ──────────────────────────────────────────────

    def _needs_expert_review(self, ctx: dict) -> bool:
        """L2: 复杂度 M/L 且非例行"""
        if ctx.get("task_type") in ["query", "status", "check", "list"]:
            return False  # 例行查询走 L1
        if ctx.get("complexity") in ["M", "L"]:
            return True
        if ctx.get("risk_level") == "medium":
            return True
        return False

    # ─── 决策日志 ──────────────────────────────────────────────

    def _log_decision(self, context: dict, result: dict):
        """追加决策到日志"""
        entry = {
            "context": context,
            "decision": result
        }
        self.decision_log.append(entry)
        # 持久化到 JSONL
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _log_warning(self, context: dict, result: dict, conflict_desc: str):
        """P0-5: 冲突警告写入专用日志"""
        import logging as _stdlib_logging
        warning_file = self.log_file.parent / "decision_conflict_warnings.jsonl"
        warning_file.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "level": "WARNING",
            "type": "L2_L3_ROUTING_CONFLICT",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "decision": result,
            "conflict_description": conflict_desc,
        }
        try:
            with open(warning_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def get_decision_history(self, limit: int = 50) -> list:
        """读取最近 N 条决策记录"""
        history = []
        if self.log_file.exists():
            try:
                with open(self.log_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            history.append(json.loads(line))
            except Exception:
                pass
        return history[-limit:]

    # ─── P0-5: L2/L3 路由冲突检测 ─────────────────────────────────

    def _detect_routing_conflict(self, ctx: dict) -> tuple[bool, str]:
        """
        检测 L2/L3 边界冲突：当同一任务同时满足 L2 和 L3 条件时记录冲突

        Returns:
            (has_conflict: bool, conflict_description: str)
        """
        l2_conditions = []
        l3_conditions = []

        # L2 触发条件收集
        if ctx.get("task_type") not in ["query", "status", "check", "list"]:
            if ctx.get("complexity") in ["M", "L"]:
                l2_conditions.append(
                    f"complexity={ctx.get('complexity')}（需专家评审）"
                )
            if ctx.get("risk_level") == "medium":
                l2_conditions.append(
                    f"risk_level=medium（需专家评审）"
                )

        # L3 触发条件收集
        if ctx.get("scope") == "cross_team":
            l3_conditions.append("scope=cross_team（需Lysander决策）")
        if ctx.get("priority") in ["P0", "P1"]:
            l3_conditions.append(
                f"priority={ctx.get('priority')}（需Lysander决策）"
            )
        if ctx.get("risk_level") in ["high", "critical"]:
            l3_conditions.append(
                f"risk_level={ctx.get('risk_level')}（需Lysander决策）"
            )
        if ctx.get("task_type") in ["strategic", "irreversible"]:
            l3_conditions.append(
                f"task_type={ctx.get('task_type')}（需Lysander决策）"
            )

        # 冲突定义：L2 和 L3 条件同时存在
        if l2_conditions and l3_conditions:
            desc = (
                f"L2/L3边界冲突：任务同时触发L2专家评审条件和L3 Lysander决策条件。"
                f"L2触发: {'; '.join(l2_conditions)}。"
                f"L3触发: {'; '.join(l3_conditions)}。"
                f"决策边界模糊，建议提升至L3处理。"
            )
            return True, desc

        return False, ""

    # ─── 辅助方法 ──────────────────────────────────────────────

    def explain(self, context: dict) -> str:
        """生成决策解释（用于日志/调试）"""
        result = self.decide(context)
        lines = [
            f"=== Decision for: {context.get('task_type', 'unknown')} ===",
            f"  Priority: {context.get('priority', 'N/A')}  Scope: {context.get('scope', 'N/A')}",
            f"  Complexity: {context.get('complexity', 'N/A')}  Risk: {context.get('risk_level', 'N/A')}",
            f"  --> LEVEL: {result['level']}",
            f"  --> ACTION: {result['action']}",
            f"  --> REASON: {result['reason']}",
            f"  Next steps: {', '.join(result['next_steps'])}",
        ]
        return "\n".join(lines)


# ─── 使用示例 & 验证 ─────────────────────────────────────────────────────────

def demo():
    """Demonstrate four-level decision engine"""
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 60)
    print("Decision Engine Demo -- Synapse v3.0 Phase 3 T6-4")
    print("=" * 60)

    engine = DecisionEngine()

    cases = [
        {
            "name": "L1: Query",
            "context": {
                "task_type": "query",
                "scope": "single_team",
                "priority": "P3",
                "complexity": "S",
                "risk_level": "low"
            }
        },
        {
            "name": "L1: Status check",
            "context": {
                "task_type": "status",
                "scope": "single_team",
                "priority": "P2",
                "risk_level": "low"
            }
        },
        {
            "name": "L2: Medium complexity",
            "context": {
                "task_type": "complex",
                "scope": "single_team",
                "priority": "P2",
                "complexity": "M",
                "risk_level": "medium"
            }
        },
        {
            "name": "L2: Professional review",
            "context": {
                "task_type": "security_review",
                "scope": "single_team",
                "priority": "P2",
                "complexity": "L",
                "risk_level": "medium"
            }
        },
        {
            "name": "L3: Cross-team",
            "context": {
                "task_type": "process_redesign",
                "scope": "cross_team",
                "priority": "P1",
                "complexity": "L",
                "risk_level": "high"
            }
        },
        {
            "name": "L3: P0 priority",
            "context": {
                "task_type": "urgent_fix",
                "scope": "single_team",
                "priority": "P0",
                "risk_level": "critical"
            }
        },
        {
            "name": "L4: Legal/contract",
            "context": {
                "task_type": "contract_review",
                "legal": True,
                "financial": False,
                "priority": "P1"
            }
        },
        {
            "name": "L4: Major finance",
            "context": {
                "task_type": "budget_allocation",
                "financial": True,
                "priority": "P0"
            }
        },
    ]

    for case in cases:
        result = engine.decide(case["context"])
        print(f"\n[{case['name']}]")
        print(f"  Level={result['level']}  Action={result['action']}  Reason={result['reason']}")
        print(f"  Steps: {' → '.join(result['next_steps'])}")

    return engine


if __name__ == "__main__":
    demo()
