"""
OPC CFO Agent — 财务管控核心
职责：成本监控、预算管理、ROI 分析、财务预警
设计：Phase 2 T3-1 | execution_auditor | 2026-04-22
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional
import json
import os

# ─── 数据模型 ────────────────────────────────────────────────────────────────

@dataclass
class CostRecord:
    timestamp: str
    task_id: str
    agent_id: str
    tokens_used: int
    input_tokens: int = 0          # 输入 token 数（分离计费）
    output_tokens: int = 0         # 输出 token 数（分离计费）
    input_cost_usd: float = 0.0    # 输入费用
    output_cost_usd: float = 0.0    # 输出费用
    cost_usd: float = 0.0          # 总费用（含折扣）
    batch_discount_applied: bool = False  # 批量优惠（>100K tokens 打9折）
    task_value: float = 0.0         # 任务预估价值（美元）
    task_type: str = "unknown"      # S/M/L 分级


@dataclass
class BudgetStatus:
    daily_limit: float
    daily_spent: float
    alert_threshold: float
    remaining: float
    status: str  # "normal" / "warning" / "critical" / "exceeded"
    tasks_today: int = 0


@dataclass
class TaskBudgetCheck:
    task_cost_estimate: float
    remaining_budget: float
    can_execute: bool
    daily_status: str
    recommendation: str  # "approve" / "defer_or_optimize"
    estimated_tokens: int


@dataclass
class DailyFinancialReport:
    date: str
    budget: BudgetStatus
    total_tokens: int
    total_value: float
    roi: float
    top_agents: list[tuple[str, float]]  # [(agent_id, cost), ...]
    task_breakdown: list[dict]  # [{task_id, cost, value, roi}, ...]
    generated_at: str


# ─── CFO Agent 主体 ─────────────────────────────────────────────────────────

class CFOAgent:
    """OPC CFO Agent — 财务管控核心"""

    # Claude Sonnet 4.6 定价（美元/token，输入/输出分离计费）
    # 输入：$3/1M tokens | 输出：$15/1M tokens
    INPUT_COST_PER_TOKEN: float = 0.000003    # $3 / 1M
    OUTPUT_COST_PER_TOKEN: float = 0.000015    # $15 / 1M
    # 兼容旧接口（单向计费作为默认值）
    COST_PER_TOKEN: float = 0.000003
    BATCH_DISCOUNT_THRESHOLD_TOKENS: int = 100_000  # 批量优惠阈值
    BATCH_DISCOUNT_RATE: float = 0.90           # 批量优惠：9折

    def __init__(
        self,
        daily_budget: float = 50.0,
        alert_threshold: float = 0.8,
        warn_threshold: float = 0.6,
        input_cost_per_token: float = None,
        output_cost_per_token: float = None,
    ):
        self.daily_budget = daily_budget
        self.alert_threshold = alert_threshold  # 80% → critical
        self.warn_threshold = warn_threshold    # 60% → warning
        self.input_cost_per_token = input_cost_per_token or self.INPUT_COST_PER_TOKEN
        self.output_cost_per_token = output_cost_per_token or self.OUTPUT_COST_PER_TOKEN
        self.cost_records: list[CostRecord] = []
        self._state_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config", "cfo_state.json"
        )
        self._load_state()

    # ── 核心操作 ──────────────────────────────────────────────────────────────

    def record_task_cost(
        self,
        task_id: str,
        agent_id: str,
        tokens_used: int,
        task_value: float = 0.0,
        task_type: str = "unknown",
        input_tokens: int = None,
        output_tokens: int = None,
    ) -> CostRecord:
        """
        记录任务成本（分离计费 + 批量折扣）

        Args:
            input_tokens: 输入 token 数（若不传入则默认 total*0.7）
            output_tokens: 输出 token 数（若不传入则默认 total*0.3）
        """
        total = tokens_used
        inp = input_tokens if input_tokens is not None else int(total * 0.7)
        out = output_tokens if output_tokens is not None else int(total * 0.3)
        # 确保 inp + out = total
        if input_tokens is None and output_tokens is None:
            inp, out = total - min(total // 3, 5000), min(total // 3, 5000)
            if inp + out != total:
                inp = total - out

        input_cost = inp * self.input_cost_per_token
        output_cost = out * self.output_cost_per_token
        subtotal = input_cost + output_cost

        # 批量折扣：单次请求 > 100K tokens 享 9 折
        batch_discount = subtotal * (1 - self.BATCH_DISCOUNT_RATE) if total > self.BATCH_DISCOUNT_THRESHOLD_TOKENS else 0.0
        final_cost = subtotal - batch_discount

        record = CostRecord(
            timestamp=datetime.now().isoformat(),
            task_id=task_id,
            agent_id=agent_id,
            tokens_used=total,
            input_tokens=inp,
            output_tokens=out,
            input_cost_usd=round(input_cost, 6),
            output_cost_usd=round(output_cost, 6),
            cost_usd=round(final_cost, 6),
            batch_discount_applied=total > self.BATCH_DISCOUNT_THRESHOLD_TOKENS,
            task_value=round(task_value, 2),
            task_type=task_type,
        )
        self.cost_records.append(record)
        self._save_state()
        return record

    def get_daily_status(self, for_date: date = None) -> BudgetStatus:
        """获取当日预算状态"""
        target = for_date or date.today()
        today_records = [
            r for r in self.cost_records
            if datetime.fromisoformat(r.timestamp).date() == target
        ]
        total_spent = sum(r.cost_usd for r in today_records)
        remaining = max(0.0, self.daily_budget - total_spent)
        usage_ratio = total_spent / self.daily_budget if self.daily_budget > 0 else 0

        if usage_ratio >= 1.0:
            status = "exceeded"
        elif usage_ratio >= self.alert_threshold:
            status = "critical"
        elif usage_ratio >= self.warn_threshold:
            status = "warning"
        else:
            status = "normal"

        return BudgetStatus(
            daily_limit=self.daily_budget,
            daily_spent=round(total_spent, 4),
            alert_threshold=self.alert_threshold,
            remaining=round(remaining, 4),
            status=status,
            tasks_today=len(today_records),
        )

    def check_task_budget(
        self,
        estimated_tokens: int,
        task_value: float = 0.0,
    ) -> TaskBudgetCheck:
        """检查任务是否在预算内（pre-execution 验证）"""
        estimated_cost = estimated_tokens * self.cost_per_token
        status = self.get_daily_status()
        can_execute = estimated_cost <= status.remaining

        return TaskBudgetCheck(
            task_cost_estimate=round(estimated_cost, 6),
            remaining_budget=status.remaining,
            can_execute=can_execute,
            daily_status=status.status,
            recommendation="approve" if can_execute else "defer_or_optimize",
            estimated_tokens=estimated_tokens,
        )

    def get_roi(self, for_date: date = None) -> float:
        """计算指定日期的投资回报率"""
        target = for_date or date.today()
        records = [
            r for r in self.cost_records
            if datetime.fromisoformat(r.timestamp).date() == target
        ]
        total_cost = sum(r.cost_usd for r in records)
        total_value = sum(r.task_value for r in records)
        return round(total_value / total_cost, 3) if total_cost > 0 else 0.0

    def get_cost_breakdown(self, for_date: date = None) -> dict:
        """按 Agent 维度的成本分解"""
        target = for_date or date.today()
        records = [
            r for r in self.cost_records
            if datetime.fromisoformat(r.timestamp).date() == target
        ]
        agent_costs: dict[str, dict] = {}
        for r in records:
            if r.agent_id not in agent_costs:
                agent_costs[r.agent_id] = {"total_cost": 0.0, "tokens": 0, "tasks": 0}
            agent_costs[r.agent_id]["total_cost"] += r.cost_usd
            agent_costs[r.agent_id]["tokens"] += r.tokens_used
            agent_costs[r.agent_id]["tasks"] += 1

        # 按成本排序
        sorted_agents = sorted(
            agent_costs.items(), key=lambda x: x[1]["total_cost"], reverse=True
        )
        return {
            agent: {
                "cost_usd": round(data["total_cost"], 4),
                "tokens": data["tokens"],
                "tasks": data["tasks"],
                "cost_share": round(data["total_cost"] / sum(
                    d["total_cost"] for d in agent_costs.values()
                ) * 100, 2) if agent_costs else 0,
            }
            for agent, data in sorted_agents
        }

    # ── 报告生成 ──────────────────────────────────────────────────────────────

    def generate_daily_report(self, for_date: date = None) -> DailyFinancialReport:
        """生成每日财务报告（返回结构化对象）"""
        target = for_date or date.today()
        status = self.get_daily_status(target)
        records = [
            r for r in self.cost_records
            if datetime.fromisoformat(r.timestamp).date() == target
        ]
        total_tokens = sum(r.tokens_used for r in records)
        total_value = sum(r.task_value for r in records)
        roi = round(total_value / status.daily_spent, 3) if status.daily_spent > 0 else 0.0

        breakdown = [
            {
                "task_id": r.task_id,
                "agent_id": r.agent_id,
                "cost_usd": round(r.cost_usd, 4),
                "value": round(r.task_value, 2),
                "roi": round(r.task_value / r.cost_usd, 2) if r.cost_usd > 0 else 0,
                "type": r.task_type,
            }
            for r in sorted(records, key=lambda x: x.cost_usd, reverse=True)
        ]

        top = [
            (agent, round(data["cost_usd"], 4))
            for agent, data in list(self.get_cost_breakdown(target).items())[:5]
        ]

        return DailyFinancialReport(
            date=target.isoformat(),
            budget=status,
            total_tokens=total_tokens,
            total_value=round(total_value, 2),
            roi=roi,
            top_agents=top,
            task_breakdown=breakdown,
            generated_at=datetime.now().isoformat(),
        )

    def cost_prediction(self, for_date: date = None) -> dict:
        """
        基于7日历史平均消耗，预测当日峰值消耗

        Returns:
            {
                "date": str,
                "predicted_peak_cost": float,     # 预测当日峰值
                "daily_avg_7d": float,           # 7日平均
                "daily_max_7d": float,           # 7日最高单日
                "trend": str,                    # "rising" | "stable" | "declining"
                "confidence": str,                # "high" | "medium" | "low"
                "daily_spend_actual": float,      # 当日实际消耗（如有记录）
                "over_prediction": float,         # 预测偏差（如有实际值）
            }
        """
        target = for_date or date.today()
        today_records = [
            r for r in self.cost_records
            if datetime.fromisoformat(r.timestamp).date() == target
        ]
        today_actual = sum(r.cost_usd for r in today_records)

        # 取前7天历史数据
        window_days = 7
        cutoff = target - timedelta(days=window_days)
        daily_totals: dict[date, float] = {}
        for r in self.cost_records:
            d = datetime.fromisoformat(r.timestamp).date()
            if cutoff < d < target:
                daily_totals[d] = daily_totals.get(d, 0.0) + r.cost_usd

        if not daily_totals:
            return {
                "date": target.isoformat(),
                "predicted_peak_cost": 0.0,
                "daily_avg_7d": 0.0,
                "daily_max_7d": 0.0,
                "trend": "unknown",
                "confidence": "low",
                "daily_spend_actual": round(today_actual, 4),
                "over_prediction": 0.0,
            }

        values = list(daily_totals.values())
        avg_7d = sum(values) / len(values)
        max_7d = max(values)
        # 预测峰值 = 均值 × 1.5（保守估算）
        predicted = round(avg_7d * 1.5, 4)

        # 趋势判断
        sorted_days = sorted(daily_totals.keys())
        if len(sorted_days) >= 2:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            if avg_second > avg_first * 1.1:
                trend = "rising"
            elif avg_second < avg_first * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        # 置信度
        confidence = "high" if len(values) >= 5 else "medium" if len(values) >= 3 else "low"

        result = {
            "date": target.isoformat(),
            "predicted_peak_cost": predicted,
            "daily_avg_7d": round(avg_7d, 4),
            "daily_max_7d": round(max_7d, 4),
            "trend": trend,
            "confidence": confidence,
            "daily_spend_actual": round(today_actual, 4),
            "over_prediction": 0.0,
        }

        # 计算偏差（如已有实际值）
        if today_actual > 0:
            result["over_prediction"] = round(today_actual - predicted, 4)

        return result

    def format_daily_report(self, for_date: date = None) -> str:
        """生成每日财务报告（Markdown 格式）"""
        report = self.generate_daily_report(for_date)
        budget = report.budget

        task_rows = ""
        for item in report.task_breakdown:
            task_rows += f"| {item['task_id']} | {item['agent_id']} | ${item['cost_usd']:.4f} | ${item['value']:.2f} | {item['roi']:.2f}x | {item['type'].upper()} |\n"

        top_rows = ""
        for agent, cost in report.top_agents:
            pct = 0
            if budget.daily_spent > 0:
                pct = round(cost / budget.daily_spent * 100, 1)
            top_rows += f"| {agent} | ${cost:.4f} | {pct}% |\n"

        # 预测数据
        prediction = self.cost_prediction(for_date)

        return f"""# CFO 每日财务报告 — {report.date}

## 预算状态
| 指标 | 值 |
|------|---|
| 日预算 | ${budget.daily_limit} |
| 已消耗 | ${budget.daily_spent} |
| 剩余 | ${budget.remaining} |
| 状态 | **{budget.status.upper()}** |
| 任务数 | {budget.tasks_today} |

## 消耗预测 vs 实际（7日趋势分析）
| 指标 | 值 |
|------|---|
| 7日平均消耗 | ${prediction['daily_avg_7d']:.4f} |
| 7日峰值 | ${prediction['daily_max_7d']:.4f} |
| 今日预测峰值 | ${prediction['predicted_peak_cost']:.4f} |
| 今日实际消耗 | ${prediction['daily_spend_actual']:.4f} |
| 预测偏差 | ${prediction['over_prediction']:+.4f} |
| 7日趋势 | {prediction['trend'].upper()} |
| 预测置信度 | {prediction['confidence'].upper()} |

## ROI 摘要
| 指标 | 值 |
|------|---|
| 总成本 | ${budget.daily_spent} |
| 总价值 | ${report.total_value:.2f} |
| ROI | {report.roi}x |
| 总 Token | {report.total_tokens:,} |

## Top 消耗 Agent
| Agent | 成本 | 占比 |
|-------|------|------|
{top_rows}

## 任务明细
| 任务 | Agent | 成本 | 价值 | ROI | 分级 |
|------|-------|------|------|-----|------|
{task_rows or "| — | — | — | — | — | — |\n"}

---
生成时间：{report.generated_at}
"""

    # ── 持久化 ────────────────────────────────────────────────────────────────

    def _save_state(self) -> None:
        """持久化到 JSON（重启后恢复）"""
        try:
            data = {
                "daily_budget": self.daily_budget,
                "alert_threshold": self.alert_threshold,
                "warn_threshold": self.warn_threshold,
                "records": [
                    {
                        "timestamp": r.timestamp,
                        "task_id": r.task_id,
                        "agent_id": r.agent_id,
                        "tokens_used": r.tokens_used,
                        "input_tokens": getattr(r, "input_tokens", 0),
                        "output_tokens": getattr(r, "output_tokens", 0),
                        "input_cost_usd": getattr(r, "input_cost_usd", 0.0),
                        "output_cost_usd": getattr(r, "output_cost_usd", 0.0),
                        "cost_usd": r.cost_usd,
                        "batch_discount_applied": getattr(r, "batch_discount_applied", False),
                        "task_value": r.task_value,
                        "task_type": r.task_type,
                    }
                    for r in self.cost_records
                ],
            }
            with open(self._state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 非关键，忽略持久化失败

    def _load_state(self) -> None:
        """从 JSON 恢复状态"""
        if not os.path.exists(self._state_file):
            return
        try:
            with open(self._state_file, encoding="utf-8") as f:
                data = json.load(f)
            self.daily_budget = data.get("daily_budget", self.daily_budget)
            self.alert_threshold = data.get("alert_threshold", self.alert_threshold)
            self.warn_threshold = data.get("warn_threshold", self.warn_threshold)
            self.cost_records = [
                CostRecord(
                    timestamp=r["timestamp"],
                    task_id=r["task_id"],
                    agent_id=r["agent_id"],
                    tokens_used=r["tokens_used"],
                    input_tokens=r.get("input_tokens", 0),
                    output_tokens=r.get("output_tokens", 0),
                    input_cost_usd=r.get("input_cost_usd", 0.0),
                    output_cost_usd=r.get("output_cost_usd", 0.0),
                    cost_usd=r["cost_usd"],
                    batch_discount_applied=r.get("batch_discount_applied", False),
                    task_value=r.get("task_value", 0.0),
                    task_type=r.get("task_type", "unknown"),
                )
                for r in data.get("records", [])
            ]
        except Exception:
            pass


# ─── 演示 ─────────────────────────────────────────────────────────────────────

def demo():
    cfo = CFOAgent(daily_budget=50.0)

    # 模拟记录任务成本（分离计费演示）
    print("=== CFO 成本模型精细化演示 ===\n")

    # 普通任务
    r1 = cfo.record_task_cost("T6-1", "harness_engineer", 50000, task_value=10.0, task_type="S")
    print(f"T6-1: {r1.tokens_used} tokens → "
          f"in={r1.input_tokens} out={r1.output_tokens} | "
          f"in_cost=${r1.input_cost_usd:.4f} out_cost=${r1.output_cost_usd:.4f} | "
          f"total=${r1.cost_usd:.4f} discount={r1.batch_discount_applied}")

    # 大任务（触发批量折扣）
    r2 = cfo.record_task_cost("T2-1", "capability_architect", 150000, task_value=15.0, task_type="M")
    print(f"T2-1: {r2.tokens_used} tokens → "
          f"in={r2.input_tokens} out={r2.output_tokens} | "
          f"in_cost=${r2.input_cost_usd:.4f} out_cost=${r2.output_cost_usd:.4f} | "
          f"total=${r2.cost_usd:.4f} discount={r2.batch_discount_applied} ← 批量9折!")

    r3 = cfo.record_task_cost("T1-3", "knowledge_engineer", 30000, task_value=8.0, task_type="S")

    status = cfo.get_daily_status()
    print(f"Daily Status: {status.status.upper()} — ${status.daily_spent}/${status.daily_limit}")
    print(f"Remaining: ${status.remaining}")

    # 检查新任务预算
    check = cfo.check_task_budget(200000)
    print(f"\nNew task check (200k tokens):")
    print(f"  can_execute: {check.can_execute}")
    print(f"  cost estimate: ${check.task_cost_estimate:.4f}")
    print(f"  recommendation: {check.recommendation}")

    # 成本预测
    pred = cfo.cost_prediction()
    print(f"\n[Cost Prediction]")
    print(f"  7d avg: ${pred['daily_avg_7d']:.4f}  peak: ${pred['daily_max_7d']:.4f}")
    print(f"  Predicted today: ${pred['predicted_peak_cost']:.4f}")
    print(f"  Actual today: ${pred['daily_spend_actual']:.4f}")
    print(f"  Trend: {pred['trend']}  Confidence: {pred['confidence']}")

    # ROI
    roi = cfo.get_roi()
    print(f"\nROI: {roi}x")

    # 按 Agent 成本分解
    breakdown = cfo.get_cost_breakdown()
    print("\nCost Breakdown by Agent:")
    for agent, data in breakdown.items():
        print(f"  {agent}: ${data['cost_usd']:.4f} ({data['cost_share']}%)")

    # 打印完整报告
    print(cfo.format_daily_report())


if __name__ == "__main__":
    demo()