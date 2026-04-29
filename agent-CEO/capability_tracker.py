# -*- coding: utf-8 -*-
"""
Synapse v3.0 — Capability Tracker
Agent 能力持续评估，跟踪成长曲线

Phase 3 T2-3: 能力持续评估系统
用法:
    from agent_butler.capability_tracker import CapabilityTracker
    tracker = CapabilityTracker()
    tracker.record_task_outcome("ai_systems_dev", "T6-4", {
        "quality_score": 4.5, "duration_minutes": 15, "blockers": []
    })
    trend = tracker.get_capability_trend("ai_systems_dev")
"""

import json
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

DEFAULT_DATA_DIR = Path(__file__).parent / "data" / "capability"


class CapabilityTracker:
    """能力持续评估，跟踪 Agent 成长曲线

    核心功能:
        record_task_outcome: 记录每次任务执行结果，持续更新能力评分
        get_capability_trend: 获取 Agent 能力趋势（7d/30d）
        get_skill_gap: 识别能力缺口，对比目标能力画像
        get_team_health: 团队整体能力健康度
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else DEFAULT_DATA_DIR
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.records_file = self.storage_path / "task_outcomes.json"
        self._records: Optional[list] = None

    # ─── 数据持久化 ──────────────────────────────────────────────

    @property
    def records(self) -> list:
        if self._records is None:
            self._records = self._load_records()
        return self._records

    def _load_records(self) -> list:
        if self.records_file.exists():
            try:
                with open(self.records_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_records(self):
        try:
            with open(self.records_file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ─── 核心方法 ──────────────────────────────────────────────

    def record_task_outcome(
        self,
        agent_id: str,
        task_id: str,
        outcome: dict
    ):
        """记录每次任务执行结果，持续更新能力评分

        Args:
            agent_id: Agent ID
            task_id: 任务标识
            outcome: {
                quality_score: float,       # 0-5 质量评分
                duration_minutes: int,      # 完成耗时（分钟）
                blockers: list[str],        # 阻塞原因列表
                task_type: str,             # 任务类型
                skills_used: list[str],     # 使用的技能
                timestamp: str,             # ISO 8601 时间戳（可选，默认当前）
            }
        """
        record = {
            "agent_id": agent_id,
            "task_id": task_id,
            "quality_score": outcome.get("quality_score", 3.5),
            "duration_minutes": outcome.get("duration_minutes", 0),
            "blockers": outcome.get("blockers", []),
            "task_type": outcome.get("task_type", "unknown"),
            "skills_used": outcome.get("skills_used", []),
            "timestamp": outcome.get("timestamp") or datetime.now().isoformat(),
        }
        self.records.append(record)
        self._save_records()

    def get_capability_trend(self, agent_id: str, days: int = 30) -> dict:
        """获取 Agent 能力趋势

        Returns:
            {
                "agent_id": str,
                "period_days": int,
                "task_count": int,
                "quality_avg": float,
                "quality_trend": "improving" | "stable" | "declining",
                "blocker_rate": float,
                "trend_data": [(date, quality_avg), ...],
                "skills_performance": {skill: avg_quality}
            }
        """
        cutoff = datetime.now() - timedelta(days=days)
        records = [
            r for r in self.records
            if r["agent_id"] == agent_id
            and datetime.fromisoformat(r["timestamp"]) >= cutoff
        ]

        if not records:
            return {
                "agent_id": agent_id,
                "period_days": days,
                "task_count": 0,
                "quality_avg": None,
                "quality_trend": "no_data",
                "blocker_rate": None,
                "trend_data": [],
                "skills_performance": {}
            }

        task_count = len(records)
        quality_scores = [r["quality_score"] for r in records]
        quality_avg = round(sum(quality_scores) / len(quality_scores), 2)
        blocked = sum(1 for r in records if r["blockers"])
        blocker_rate = round(blocked / task_count, 3)

        # 计算趋势（前半段 vs 後半段）
        trend = self._calc_trend(records)

        # 按日期聚合
        date_buckets: dict = {}
        for r in records:
            date = r["timestamp"][:10]
            if date not in date_buckets:
                date_buckets[date] = []
            date_buckets[date].append(r["quality_score"])
        trend_data = sorted([
            (d, round(sum(v) / len(v), 2)) for d, v in date_buckets.items()
        ])

        # 技能表现
        skills_perf: dict = {}
        for r in records:
            for skill in r.get("skills_used", []):
                if skill not in skills_perf:
                    skills_perf[skill] = []
                skills_perf[skill].append(r["quality_score"])
        skills_performance = {
            s: round(sum(v) / len(v), 2) for s, v in skills_perf.items()
        }

        return {
            "agent_id": agent_id,
            "period_days": days,
            "task_count": task_count,
            "quality_avg": quality_avg,
            "quality_trend": trend,
            "blocker_rate": blocker_rate,
            "trend_data": trend_data,
            "skills_performance": skills_performance
        }

    def get_skill_gap(self, agent_id: str, target_profile: dict) -> list:
        """识别能力缺口

        Args:
            agent_id: Agent ID
            target_profile: {skill: required_level, ...}  (1-5)

        Returns:
            [{skill, required, actual, gap, status}, ...]
            status: "meets" | "close" | "gap" | "missing"
        """
        # 从 records 推断当前能力（取最近使用的技能评分）
        trend = self.get_capability_trend(agent_id, days=30)
        current_skills = trend.get("skills_performance", {})

        gaps = []
        for skill, required in target_profile.items():
            actual_raw = current_skills.get(skill)
            # 用 quality_avg 作为兜底
            actual = actual_raw if actual_raw is not None else trend.get("quality_avg", 3.0)
            gap = required - actual
            if actual_raw is None:
                status = "missing"
            elif gap <= 0:
                status = "meets"
            elif gap <= 1:
                status = "close"
            else:
                status = "gap"
            gaps.append({
                "skill": skill,
                "required": required,
                "actual": round(actual, 2),
                "gap": round(gap, 2),
                "status": status
            })
        return gaps

    def get_team_health(self, days: int = 30) -> dict:
        """团队整体能力健康度"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            r for r in self.records
            if datetime.fromisoformat(r["timestamp"]) >= cutoff
        ]
        if not recent:
            return {"task_count": 0, "health": "no_data"}

        agent_ids = set(r["agent_id"] for r in recent)
        quality_avg = round(sum(r["quality_score"] for r in recent) / len(recent), 2)
        blocker_rate = round(
            sum(1 for r in recent if r["blockers"]) / len(recent), 3
        )
        health = "healthy" if quality_avg >= 3.5 and blocker_rate < 0.2 \
            else "warning" if quality_avg >= 3.0 \
            else "critical"

        return {
            "period_days": days,
            "task_count": len(recent),
            "agent_count": len(agent_ids),
            "quality_avg": quality_avg,
            "blocker_rate": blocker_rate,
            "health": health,
            "agent_summaries": {
                aid: self.get_capability_trend(aid, days)
                for aid in sorted(agent_ids)
            }
        }

    # ─── 内部工具 ──────────────────────────────────────────────

    @staticmethod
    def _calc_trend(records: list) -> str:
        """基于前半段 vs 後半段均值判断趋势"""
        if len(records) < 4:
            return "stable"
        half = len(records) // 2
        first_half = [r["quality_score"] for r in records[:half]]
        second_half = [r["quality_score"] for r in records[half:]]
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        delta = second_avg - first_avg
        if delta > 0.3:
            return "improving"
        elif delta < -0.3:
            return "declining"
        return "stable"


# ─── 使用示例 & 验证 ─────────────────────────────────────────────────────────

def demo():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 60)
    print("Capability Tracker Demo -- Synapse v3.0 Phase 3 T2-3")
    print("=" * 60)

    tracker = CapabilityTracker()

    # Simulated historical data
    import random
    agents = ["ai_systems_dev", "harness_engineer", "integration_qa"]
    for agent_id in agents:
        for i in range(6):
            tracker.record_task_outcome(
                agent_id=agent_id,
                task_id=f"T{30 - i * 5}-{i}",
                outcome={
                    "quality_score": round(random.uniform(3.5, 4.8), 1),
                    "duration_minutes": random.randint(10, 60),
                    "blockers": ["api_config"] if random.random() < 0.2 else [],
                    "task_type": "python_development",
                    "skills_used": ["python_development", "task_execution"],
                    "timestamp": (
                        datetime.now() - timedelta(days=30 - i * 5)
                    ).isoformat()
                }
            )

    # 趋势分析
    for agent_id in agents:
        trend = tracker.get_capability_trend(agent_id, days=30)
        print(f"\n[{agent_id}] ({trend['task_count']} tasks, {trend['period_days']}d)")
        print(f"  quality_avg={trend['quality_avg']}  trend={trend['quality_trend']}")
        print(f"  blocker_rate={trend['blocker_rate']}")

    # 技能缺口
    target = {"python_development": 4, "hook_development": 4, "task_execution": 5}
    gaps = tracker.get_skill_gap("ai_systems_dev", target)
    print(f"\n[ai_systems_dev] Skill Gap vs target:")
    for g in gaps:
        print(f"  {g['skill']}: required={g['required']} actual={g['actual']} "
              f"gap={g['gap']} [{g['status']}]")

    # 团队健康度
    health = tracker.get_team_health(days=30)
    print(f"\n[Team Health] {health['period_days']}d")
    print(f"  tasks={health['task_count']} agents={health['agent_count']} "
          f"quality={health['quality_avg']} blocker={health['blocker_rate']} "
          f"health={health['health']}")

    return tracker


if __name__ == "__main__":
    demo()
