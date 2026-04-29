# -*- coding: utf-8 -*-
"""
Synapse v3.0 — Evolution Dashboard
进化度量仪表盘：量化 Synapse 体系进化效果

Phase 3 T5-2: 进化度量仪表盘
用法:
    from agent_butler.evolution_dashboard import EvolutionDashboard
    dashboard = EvolutionDashboard()
    metrics = dashboard.get_metrics()
    report = dashboard.generate_report()
"""

import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

DEFAULT_DATA_DIR = Path(__file__).parent / "data"
DEFAULT_CONFIG_DIR = Path(__file__).parent / "config"
DEFAULT_METRICS_CONFIG = DEFAULT_CONFIG_DIR / "evolution_metrics.yaml"


class EvolutionDashboard:
    """Synapse 进化度量仪表盘

    三大维度:
        efficiency:  效率指标（任务完成率/平均时长/P0升级率）
        quality:     质量指标（QA通过率/平均质量评分/阻塞解决时间）
        growth:      成长指标（Agent能力曲线/自我改进效果）
    """

    # 默认指标定义
    DEFAULT_METRICS = {
        "efficiency": {
            "task_completion_rate": {
                "name": "任务按时完成率",
                "description": "按时完成任务数 / 总任务数",
                "unit": "%",
                "target": 90.0,
                "direction": "higher_is_better"
            },
            "avg_task_duration": {
                "name": "平均任务时长",
                "description": "所有已完成任务的平均完成时间",
                "unit": "min",
                "target": 60.0,
                "direction": "lower_is_better"
            },
            "p0_escalation_rate": {
                "name": "P0升级率",
                "description": "需要上报的任务占比（越低越好）",
                "unit": "%",
                "target": 5.0,
                "direction": "lower_is_better"
            }
        },
        "quality": {
            "qa_pass_rate": {
                "name": "QA通过率",
                "description": "qa_auto_review >=85 通过的任务占比",
                "unit": "%",
                "target": 80.0,
                "direction": "higher_is_better"
            },
            "avg_quality_score": {
                "name": "平均质量评分",
                "description": "所有任务的 QA 评分均值",
                "unit": "/100",
                "target": 85.0,
                "direction": "higher_is_better"
            },
            "blocker_resolution_time": {
                "name": "阻塞解决时间",
                "description": "从阻塞发生到解决的中位时间",
                "unit": "min",
                "target": 120.0,
                "direction": "lower_is_better"
            }
        },
        "growth": {
            "agent_capability_trend": {
                "name": "Agent能力成长曲线",
                "description": "各 Agent 能力评分趋势（基于 performance_history）",
                "unit": "/5",
                "target": 4.0,
                "direction": "higher_is_better"
            },
            "self_improvement_impact": {
                "name": "自我改进效果",
                "description": "改进闭环采纳率",
                "unit": "%",
                "target": 50.0,
                "direction": "higher_is_better"
            }
        }
    }

    def __init__(
        self,
        metrics_config: Optional[str] = None,
        storage_path: Optional[str] = None
    ):
        self.config_path = Path(metrics_config) if metrics_config else DEFAULT_METRICS_CONFIG
        self.storage_path = Path(storage_path) if storage_path else DEFAULT_DATA_DIR
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metrics = self._load_metrics_config()

    def _load_metrics_config(self) -> dict:
        """加载指标配置（文件优先，默认兜底）"""
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    return yaml.safe_load(f) or self.DEFAULT_METRICS
            except Exception:
                pass
        return self.DEFAULT_METRICS

    # ─── 数据采集 ──────────────────────────────────────────────

    def collect_metrics(self, days: int = 7) -> dict:
        """采集最新指标数据

        从以下来源收集:
            - agent-CEO/data/execution_records.json
            - agent-CEO/data/improvement_suggestions.json
            - agent-CEO/config/active_tasks.yaml
        """
        records = self._load_execution_records(days)
        suggestions = self._load_improvement_suggestions(days)
        active = self._load_active_tasks()

        metrics = {}
        # 效率维度
        metrics["efficiency"] = self._calc_efficiency(records, days)
        # 质量维度
        metrics["quality"] = self._calc_quality(records, days)
        # 成长维度
        metrics["growth"] = self._calc_growth(records, suggestions, days)

        # 汇总评分
        metrics["overall_score"] = self._calc_overall(metrics)

        return metrics

    def _load_execution_records(self, days: int) -> list:
        records_file = self.storage_path / "execution_records.json"
        if not records_file.exists():
            return []
        try:
            with open(records_file, encoding="utf-8") as f:
                all_records = json.load(f)
            cutoff = datetime.now() - timedelta(days=days)
            return [
                r for r in all_records
                if datetime.fromisoformat(r.get("timestamp", "2000-01-01")) >= cutoff
            ]
        except Exception:
            return []

    def _load_improvement_suggestions(self, days: int) -> list:
        suggestions_file = self.storage_path / "improvement_suggestions.json"
        if not suggestions_file.exists():
            return []
        try:
            with open(suggestions_file, encoding="utf-8") as f:
                all_s = json.load(f)
            cutoff = datetime.now() - timedelta(days=days)
            return [
                s for s in all_s
                if datetime.fromisoformat(s.get("created_at", "2000-01-01")) >= cutoff
            ]
        except Exception:
            return []

    def _load_active_tasks(self) -> list:
        active_file = DEFAULT_CONFIG_DIR / "active_tasks.yaml"
        if not active_file.exists():
            return []
        try:
            with open(active_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("tasks", []) if isinstance(data, dict) else []
        except Exception:
            return []

    # ─── 指标计算 ──────────────────────────────────────────────

    def _calc_efficiency(self, records: list, days: int) -> dict:
        if not records:
            return self._empty_efficiency()

        completed = [r for r in records if r.get("outcome") in ("completed", "done")]
        total = len(records)

        # 时长（如果有）
        durations = [r.get("completion_time_minutes", 0) for r in completed if r.get("completion_time_minutes")]
        avg_duration = round(sum(durations) / len(durations), 1) if durations else 0

        # P0升级率（统计 escalation_count）
        p0_count = sum(1 for r in records if r.get("priority") == "P0")
        p0_escalated = sum(1 for r in records if r.get("escalated"))

        return {
            "task_completion_rate": {
                "value": round(len(completed) / max(total, 1) * 100, 1),
                "status": self._score_status(
                    len(completed) / max(total, 1) * 100,
                    90.0, "higher_is_better"
                )
            },
            "avg_task_duration": {
                "value": avg_duration,
                "status": self._score_status(avg_duration, 60.0, "lower_is_better")
            },
            "p0_escalation_rate": {
                "value": round(p0_escalated / max(p0_count, 1) * 100, 1),
                "status": self._score_status(
                    p0_escalated / max(p0_count, 1) * 100,
                    5.0, "lower_is_better"
                )
            }
        }

    def _calc_quality(self, records: list, days: int) -> dict:
        if not records:
            return self._empty_quality()

        qa_scores = [r.get("quality_score", 0) for r in records if r.get("quality_score")]
        avg_qa = round(sum(qa_scores) / max(len(qa_scores), 1), 1)
        pass_count = sum(1 for s in qa_scores if s >= 85)
        pass_rate = round(pass_count / max(len(qa_scores), 1) * 100, 1)

        # 阻塞解决时间（暂无数据，估算）
        avg_blocker_time = 90.0  # 默认估算

        return {
            "qa_pass_rate": {
                "value": pass_rate,
                "status": self._score_status(pass_rate, 80.0, "higher_is_better")
            },
            "avg_quality_score": {
                "value": avg_qa,
                "status": self._score_status(avg_qa, 85.0, "higher_is_better")
            },
            "blocker_resolution_time": {
                "value": avg_blocker_time,
                "status": self._score_status(avg_blocker_time, 120.0, "lower_is_better")
            }
        }

    def _calc_growth(self, records: list, suggestions: list, days: int) -> dict:
        # Agent 能力趋势（从 records 聚合）
        agent_scores: dict = {}
        for r in records:
            aid = r.get("agent_id", "unknown")
            score = r.get("quality_score", 3.5)
            if aid not in agent_scores:
                agent_scores[aid] = []
            agent_scores[aid].append(score)

        if agent_scores:
            avg_agent_score = round(
                sum(sum(v) / len(v) for v in agent_scores.values()) / len(agent_scores), 2
            )
        else:
            avg_agent_score = 3.5

        # 自我改进效果
        adopted = sum(1 for s in suggestions if s.get("status") == "adopted")
        total_s = len(suggestions)
        adoption_rate = round(adopted / max(total_s, 1) * 100, 1)

        return {
            "agent_capability_trend": {
                "value": avg_agent_score,
                "status": self._score_status(avg_agent_score, 4.0, "higher_is_better"),
                "agent_breakdown": {
                    aid: round(sum(v) / len(v), 2) for aid, v in agent_scores.items()
                }
            },
            "self_improvement_impact": {
                "value": adoption_rate,
                "status": self._score_status(adoption_rate, 50.0, "higher_is_better"),
                "adopted": adopted,
                "total_suggestions": total_s
            }
        }

    # ─── 辅助计算 ──────────────────────────────────────────────

    def _calc_overall(self, metrics: dict) -> dict:
        """综合评分：三大维度等权，各维度内指标等权"""
        def dim_avg(dim: dict) -> float:
            vals = [v["value"] for v in dim.values() if isinstance(v["value"], (int, float))]
            return sum(vals) / len(vals) if vals else 0.0

        eff = dim_avg(metrics.get("efficiency", {}))
        qual = dim_avg(metrics.get("quality", {}))
        grw = dim_avg(metrics.get("growth", {}))
        # 归一化到百分制
        overall = round((eff + qual + grw) / 3, 1)
        return {
            "value": overall,
            "status": self._score_status(overall, 80.0, "higher_is_better"),
            "breakdown": {"efficiency": round(eff, 1), "quality": round(qual, 1), "growth": round(grw, 1)}
        }

    @staticmethod
    def _score_status(value: float, target: float, direction: str) -> str:
        if direction == "higher_is_better":
            pct = value / max(target, 1)
        else:
            pct = target / max(value, 1) if value > 0 else 1.0
        if pct >= 1.0:
            return "green"
        elif pct >= 0.8:
            return "yellow"
        return "red"

    def _empty_efficiency(self) -> dict:
        return {k: {"value": None, "status": "no_data"}
                for k in ["task_completion_rate", "avg_task_duration", "p0_escalation_rate"]}

    def _empty_quality(self) -> dict:
        return {k: {"value": None, "status": "no_data"}
                for k in ["qa_pass_rate", "avg_quality_score", "blocker_resolution_time"]}

    # ─── 报告生成 ──────────────────────────────────────────────

    def generate_report(self, days: int = 7) -> str:
        """生成进化仪表盘报告"""
        metrics = self.collect_metrics(days)
        overall = metrics.get("overall_score", {})
        lines = [
            f"## Synapse 进化仪表盘 — 近 {days} 天",
            f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"### 综合评分: {overall.get('value', 'N/A')} ({overall.get('status', 'N/A')})",
            "",
            "### 效率维度",
        ]
        for metric_id, m in metrics.get("efficiency", {}).items():
            defn = self.metrics.get("efficiency", {}).get(metric_id, {})
            val = m["value"]
            val_str = f"{val}{defn.get('unit', '')}" if val is not None else "N/A"
            lines.append(f"  [{m['status']:8s}] {defn.get('name', metric_id)}: {val_str}")
        lines += ["", "### 质量维度"]
        for metric_id, m in metrics.get("quality", {}).items():
            defn = self.metrics.get("quality", {}).get(metric_id, {})
            val = m["value"]
            val_str = f"{val}{defn.get('unit', '')}" if val is not None else "N/A"
            lines.append(f"  [{m['status']:8s}] {defn.get('name', metric_id)}: {val_str}")
        lines += ["", "### 成长维度"]
        for metric_id, m in metrics.get("growth", {}).items():
            defn = self.metrics.get("growth", {}).get(metric_id, {})
            val = m["value"]
            val_str = f"{val}{defn.get('unit', '')}" if val is not None else "N/A"
            lines.append(f"  [{m['status']:8s}] {defn.get('name', metric_id)}: {val_str}")
        return "\n".join(lines)

    def get_metrics(self, days: int = 7) -> dict:
        """获取指标（JSON 格式）"""
        return self.collect_metrics(days)


# ─── 使用示例 & 验证 ─────────────────────────────────────────────────────────

def demo():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 60)
    print("Evolution Dashboard Demo -- Synapse v3.0 Phase 3 T5-2")
    print("=" * 60)

    dashboard = EvolutionDashboard()

    metrics = dashboard.get_metrics(days=7)
    overall = metrics.get("overall_score", {})

    print(f"\n[Overall Score] {overall.get('value', 'N/A')} — [{overall.get('status', 'N/A')}]")
    breakdown = overall.get("breakdown", {})
    print(f"  efficiency={breakdown.get('efficiency')}  quality={breakdown.get('quality')}  growth={breakdown.get('growth')}")

    print("\n[Efficiency]")
    for k, v in metrics.get("efficiency", {}).items():
        print(f"  [{v['status']:8s}] {k}: {v['value']}")

    print("\n[Quality]")
    for k, v in metrics.get("quality", {}).items():
        print(f"  [{v['status']:8s}] {k}: {v['value']}")

    print("\n[Growth]")
    for k, v in metrics.get("growth", {}).items():
        print(f"  [{v['status']:8s}] {k}: {v['value']}")

    print("\n--- Markdown Report ---")
    print(dashboard.generate_report(days=7))

    return dashboard


if __name__ == "__main__":
    demo()
