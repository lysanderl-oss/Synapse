# -*- coding: utf-8 -*-
"""
Synapse v3.0 — Agent Capability Router
基于能力向量的余弦相似度匹配，自动路由最优执行者

Phase 2 T2-2: Capability Router 构建
- 任务需求向量 vs Agent 能力向量余弦相似度匹配
- 能力覆盖率 + performance_history 加权评分
- 最低门槛检查，确保每项技能达标

用法:
    from agent_butler.capability_router import CapabilityRouter

    router = CapabilityRouter("obs/01-team-knowledge/HR/personnel")
    task = {"python_development": 4, "code_review": 4, "task_execution": 5}
    results = router.route(task, top_k=3)
"""

import math
import json
import os
import glob
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

# 延迟导入 opc_coo（避免循环依赖）
_cached_coo = None

def _get_coo():
    global _cached_coo
    if _cached_coo is None:
        try:
            from agent_butler.opc_coo import COOAgent
            _cached_coo = COOAgent()
        except Exception:
            return None
    return _cached_coo


# ─── 路由指标追踪 ──────────────────────────────────────────────────────────────

ROUTING_METRICS_FILE = str(Path(__file__).parent / "data" / "routing_metrics.jsonl")


class RoutingMetrics:
    """追踪每次路由决策，用于 A/B 测试和置信度分析"""

    @staticmethod
    def log_routing(
        task_requirements: dict,
        agent_assigned: Optional[str],
        scores: list[dict],
        final_decision: str,
        task_description: str = "",
    ):
        """追加一条路由记录到 metrics 文件"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_description": task_description,
            "agent_assigned": agent_assigned or "none",
            "task_requirements": task_requirements,
            "scores": [
                {
                    "agent_id": s.get("agent_id"),
                    "team": s.get("team"),
                    "final_score": s.get("final_score"),
                    "load_adjusted": s.get("load_adjusted", False),
                }
                for s in scores
            ],
            "final_decision": final_decision,
        }
        try:
            os.makedirs(os.path.dirname(ROUTING_METRICS_FILE), exist_ok=True)
            with open(ROUTING_METRICS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    @staticmethod
    def get_routing_accuracy() -> dict:
        """
        计算"首次分配无需返工比例"
        近似实现：返回 metrics 文件中各 agent 被选中次数的分布
        """
        if not os.path.exists(ROUTING_METRICS_FILE):
            return {"total_decisions": 0, "accuracy_note": "no data yet"}
        try:
            lines = open(ROUTING_METRICS_FILE, encoding="utf-8").readlines()
            records = [json.loads(l) for l in lines if l.strip()]
            if not records:
                return {"total_decisions": 0}
            agent_counts: dict = {}
            for r in records:
                aid = r.get("agent_assigned", "none")
                agent_counts[aid] = agent_counts.get(aid, 0) + 1
            total = len(records)
            return {
                "total_decisions": total,
                "agent_distribution": {
                    k: {"count": v, "ratio": round(v / total, 3)}
                    for k, v in sorted(agent_counts.items(), key=lambda x: -x[1])
                },
            }
        except Exception:
            return {"error": "read failed"}

    @staticmethod
    def get_top_confidence_agents(top_n: int = 3) -> list[dict]:
        """
        返回历史数据中置信度最高的 Top-N Agent
        置信度 = 该 agent 在所有决策中的选中比例 × 其平均 final_score
        """
        if not os.path.exists(ROUTING_METRICS_FILE):
            return []
        try:
            lines = open(ROUTING_METRICS_FILE, encoding="utf-8").readlines()
            records = [json.loads(l) for l in lines if l.strip()]
            agent_scores: dict = {}
            agent_counts: dict = {}
            for r in records:
                aid = r.get("agent_assigned", "none")
                scores = r.get("scores", [])
                agent_counts[aid] = agent_counts.get(aid, 0) + 1
                top_score = max((s.get("final_score", 0) for s in scores), default=0)
                if aid not in agent_scores:
                    agent_scores[aid] = []
                agent_scores[aid].append(top_score)

            total = len(records)
            results = []
            for aid in agent_scores:
                avg_score = sum(agent_scores[aid]) / len(agent_scores[aid])
                ratio = agent_counts[aid] / total
                confidence = round(ratio * avg_score, 4)
                results.append({
                    "agent_id": aid,
                    "confidence_score": confidence,
                    "selection_count": agent_counts[aid],
                    "avg_final_score": round(avg_score, 3),
                    "selection_ratio": round(ratio, 3),
                })
            results.sort(key=lambda x: x["confidence_score"], reverse=True)
            return results[:top_n]
        except Exception:
            return []

# 默认路径 — 与 hr_base.py 保持一致
DEFAULT_PERSONNEL_DIR = Path(
    os.environ.get(
        "OBS_KB_ROOT",
        Path(__file__).parent.parent / "obs"
    )
) / "01-team-knowledge" / "HR" / "personnel"

# 默认配置文件路径
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "router_config.yaml"


class CapabilityRouter:
    """基于能力向量的 Agent 路由引擎

    核心算法:
        match_score = cosine_similarity(task_requirements, agent_skill_levels)
                    + coverage_weight
                    + performance_bonus
    """

    def __init__(
        self,
        personnel_dir: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        self.personnel_dir = Path(personnel_dir or DEFAULT_PERSONNEL_DIR)
        self.config_path = Path(config_path or DEFAULT_CONFIG_PATH)
        self.agents_cache: dict = {}
        self._config: Optional[dict] = None

    # ─── 配置加载 ──────────────────────────────────────────────

    @property
    def config(self) -> dict:
        """延迟加载路由参数配置"""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> dict:
        """从 router_config.yaml 加载路由参数"""
        if self.config_path.exists():
            with open(self.config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        # 硬编码默认值（配置文件不存在时）
        return {
            "weights": {
                "cosine_similarity": 0.40,
                "coverage": 0.30,
                "quality_bonus_range": 0.10,
                "completion_bonus_range": 0.30
            },
            "thresholds": {
                "min_score": 0.30,
                "min_quality_score": 3.0,
                "min_completion_rate": 0.80
            }
        }

    # ─── Agent 加载 ──────────────────────────────────────────────

    def load_all_agents(self, force: bool = False) -> dict:
        """加载所有含 skill_levels 的 Agent 能力卡片

        Args:
            force: True = 强制重新扫描，False = 返回缓存

        Returns:
            {agent_id: card_dict}
        """
        if not force and self.agents_cache:
            return self.agents_cache

        agents: dict = {}
        pattern = str(self.personnel_dir / "**" / "*.yaml")

        for yaml_file in glob.glob(pattern, recursive=True):
            try:
                with open(yaml_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if data:
                    # 兼容两种键名：优先 skill_levels，fallback 到 capabilities
                    if "capabilities" in data and "skill_levels" not in data:
                        data["skill_levels"] = data.pop("capabilities")
                    # 只有 skill_levels 为 dict 时才加载（排除 None / list / 其他类型）
                    sl = data.get("skill_levels")
                    if isinstance(sl, dict):
                        agent_id = data.get("specialist_id", str(yaml_file))
                        agents[agent_id] = data
            except Exception:
                continue

        self.agents_cache = agents
        return agents

    def get_agent(self, agent_id: str) -> Optional[dict]:
        """根据 agent_id 查询单个 Agent"""
        agents = self.load_all_agents()
        return agents.get(agent_id)

    # ─── 核心算法 ──────────────────────────────────────────────

    @staticmethod
    def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
        """计算两个技能向量的余弦相似度

        公式:
            cosθ = (A·B) / (||A|| × ||B||)

        Returns:
            0.0 ~ 1.0，余弦相似度（两个向量都是非负值）
        """
        common_keys = set(vec_a.keys()) & set(vec_b.keys())
        if not common_keys:
            return 0.0

        dot_product = sum(vec_a[k] * vec_b[k] for k in common_keys)
        norm_a = math.sqrt(sum(vec_a[k] ** 2 for k in vec_a.keys()))
        norm_b = math.sqrt(sum(vec_b[k] ** 2 for k in vec_b.keys()))

        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def score_agent(self, agent: dict, task_requirements: dict) -> dict:
        """评估单个 Agent 对任务的匹配度

        评分构成:
            1. base_score (40%)    — 余弦相似度
            2. coverage (30%)     — 任务技能覆盖率
            3. quality_bonus      — 质量评分附加分 ±0.05
            4. completion_bonus   — 完成率附加分 ±0.05

        Returns:
            {
                "agent_id": ...,
                "base_score": 0.0~1.0,
                "coverage": 0.0~1.0,
                "meets_minimum": bool,
                "final_score": 0.0~1.0,
                "quality_bonus": float,
                "completion_bonus": float,
                "skill_gaps": {skill: required_level}  # 不达标的技能
            }
        """
        skill_levels = agent.get("skill_levels", {})
        w = self.config.get("weights", {})

        # 1. 基础匹配分
        base_score = self.cosine_similarity(task_requirements, skill_levels)

        # 2. 技能覆盖率
        if task_requirements:
            coverage = (
                len(set(task_requirements) & set(skill_levels))
                / len(task_requirements)
            )
        else:
            coverage = 1.0

        # 3. 最低能力门槛检查
        skill_gaps: dict = {}
        for skill, level in task_requirements.items():
            actual = skill_levels.get(skill, 0)
            if actual < level:
                skill_gaps[skill] = {"required": level, "actual": actual}

        meets_minimum = len(skill_gaps) == 0

        # 4. performance_history 加权
        perf = agent.get("performance_history", {})
        quality_score = perf.get("avg_quality_score") or 3.5
        completion_rate = perf.get("avg_completion_rate") or 0.9

        # 质量附加分: 以 3.5 为中性基线，±0.5 范围
        quality_bonus = (quality_score - 3.5) * w.get("quality_bonus_range", 0.10)

        # 完成率附加分: 以 90% 为中性基线，±10% 范围
        completion_bonus = (
            (completion_rate - 0.9) * w.get("completion_bonus_range", 0.30)
        )

        # 5. 最终综合得分
        final_score = (
            base_score * w.get("cosine_similarity", 0.40)
            + coverage * w.get("coverage", 0.30)
            + quality_bonus
            + completion_bonus
        )

        return {
            "agent_id": agent.get("specialist_id") or agent.get("agent_id") or "unknown",
            "team": agent.get("team", "unknown"),
            "name": agent.get("name", "unknown"),
            "base_score": round(base_score, 3),
            "coverage": round(coverage, 3),
            "meets_minimum": meets_minimum,
            "final_score": round(final_score, 3),
            "quality_bonus": round(quality_bonus, 3),
            "completion_bonus": round(completion_bonus, 3),
            "skill_gaps": skill_gaps,
            "performance_quality": quality_score,
            "performance_completion": completion_rate
        }

    # ─── 路由接口 ──────────────────────────────────────────────

    # ─── 团队负载感知 ──────────────────────────────────────────────────────────

    LOAD_THRESHOLD_DEGRADE = 0.80   # 负载>80% → 降权50%
    LOAD_THRESHOLD_EXCLUDE = 1.00   # 负载=100% → 直接排除

    def _get_team_load_prefilter(self) -> dict[str, float]:
        """
        调用 opc_coo.get_team_load() 获取各团队当前负载，
        返回 {team_id: load_factor} 映射。

        负载>80% → 降权50%
        负载=100% → 排除
        """
        coo = _get_coo()
        if coo is None:
            return {}
        try:
            team_loads = coo.get_team_load()
            return {tid: info["load_factor"] for tid, info in team_loads.items()}
        except Exception:
            return {}

    def _apply_load_adjustment(self, score: dict, load_factors: dict[str, float]) -> dict:
        """
        对单个 Agent 评分应用负载调整。

        - 负载 80%~100%：final_score 降权 50%
        - 负载 = 100%：标记为 excluded（供外部过滤）
        """
        team = score.get("team", "unknown")
        load_factor = load_factors.get(team, 0.0)
        score["load_factor"] = load_factor
        score["load_adjusted"] = False

        if load_factor >= self.LOAD_THRESHOLD_EXCLUDE:
            # 100% 负载 → 排除（final_score 置零，标记 excluded）
            score["final_score"] = 0.0
            score["load_excluded"] = True
        elif load_factor >= self.LOAD_THRESHOLD_DEGRADE:
            # 80%~100% 负载 → 降权 50%
            original = score["final_score"]
            score["final_score"] = round(original * 0.5, 3)
            score["load_adjusted"] = True
            score["load_degraded"] = True

        return score

    def route(
        self,
        task_requirements: dict,
        top_k: int = 3,
        min_score: Optional[float] = None,
        task_description: str = ""
    ) -> list:
        """路由最优 Agent（可多选）

        Args:
            task_requirements: {skill: required_level, ...}
            top_k: 返回前 N 个候选
            min_score: 最低分数阈值（None=使用配置值）
            task_description: 任务描述（供指标记录）

        Returns:
            按 final_score 降序排列的 Agent 评分列表
        """
        # 1. 获取团队负载
        load_factors = self._get_team_load_prefilter()
        excluded_teams = {t for t, f in load_factors.items() if f >= self.LOAD_THRESHOLD_EXCLUDE}
        degraded_teams = {t for t, f in load_factors.items() if self.LOAD_THRESHOLD_DEGRADE <= f < self.LOAD_THRESHOLD_EXCLUDE}

        if load_factors:
            high_load = {t: f for t, f in load_factors.items() if f >= self.LOAD_THRESHOLD_DEGRADE}
            if high_load:
                import logging
                logging.warning(
                    f"[CapabilityRouter] Team load warning: "
                    f"degraded={degraded_teams}, excluded={excluded_teams}, load_factors={high_load}"
                )

        agents = self.load_all_agents()
        thresholds = self.config.get("thresholds", {})
        min_score = min_score or thresholds.get("min_score", 0.30)

        scores: list = []
        for agent_id, agent in agents.items():
            if "skill_levels" not in agent:
                continue

            score = self.score_agent(agent, task_requirements)

            # 排除100%负载团队
            team = score.get("team", "unknown")
            if team in excluded_teams:
                continue

            # 应用负载降权
            score = self._apply_load_adjustment(score, load_factors)

            # 必须满足最低门槛且分数达标
            if score["meets_minimum"] and score["final_score"] >= min_score:
                scores.append(score)

        scores.sort(key=lambda x: x["final_score"], reverse=True)
        top_agents = scores[:top_k]

        # 记录路由指标
        RoutingMetrics.log_routing(
            task_requirements=task_requirements,
            agent_assigned=top_agents[0]["agent_id"] if top_agents else None,
            scores=scores,
            final_decision=top_agents[0]["agent_id"] if top_agents else "no_match",
            task_description=task_description,
        )

        return top_agents

    def recommend(self, task_requirements: dict, task_description: str = "") -> dict:
        """推荐最优 Agent（便捷方法，含负载感知）"""
        results = self.route(task_requirements, top_k=1, task_description=task_description)
        if results:
            return results[0]
        return {
            "error": "no_suitable_agent",
            "requirements": task_requirements
        }

    # ─── 辅助方法 ──────────────────────────────────────────────

    def explain_score(self, agent_id: str, task_requirements: dict) -> str:
        """生成评分解释（用于日志/调试）"""
        agents = self.load_all_agents()
        agent = agents.get(agent_id)
        if not agent:
            return f"Agent '{agent_id}' not found in personnel library."

        score = self.score_agent(agent, task_requirements)
        lines = [
            f"=== Capability Score for: {agent_id} ===",
            f"  Task: {task_requirements}",
            f"  Base Score (cosine similarity): {score['base_score']}",
            f"  Coverage: {score['coverage']}",
            f"  Meets Minimum: {score['meets_minimum']}",
            f"  Quality Bonus: {score['quality_bonus']:+0.3f} "
            f"(quality={score['performance_quality']})",
            f"  Completion Bonus: {score['completion_bonus']:+0.3f} "
            f"(rate={score['performance_completion']})",
            f"  FINAL SCORE: {score['final_score']}",
        ]
        if score["skill_gaps"]:
            lines.append(f"  Skill Gaps: {score['skill_gaps']}")
        return "\n".join(lines)

    def list_all_skills(self) -> dict:
        """列出所有 Agent 支持的全部技能维度（用于任务设计参考）"""
        agents = self.load_all_agents()
        all_skills: dict = {}
        for agent_id, agent in agents.items():
            for skill in agent.get("skill_levels", {}):
                if skill not in all_skills:
                    all_skills[skill] = {"max_level": 0, "agents": []}
                level = agent["skill_levels"][skill]
                if level > all_skills[skill]["max_level"]:
                    all_skills[skill]["max_level"] = level
                all_skills[skill]["agents"].append((agent_id, level))

        # 按最大等级排序
        return dict(
            sorted(all_skills.items(), key=lambda x: x[1]["max_level"], reverse=True)
        )


# ─── 使用示例 & 验证 ─────────────────────────────────────────────────────────

def _init_routing_metrics():
    """初始化路由指标文件，写入测试记录证明框架已激活"""
    os.makedirs(os.path.dirname(ROUTING_METRICS_FILE), exist_ok=True)
    test_record = {
        "timestamp": datetime.now().isoformat(),
        "task_description": "__ROUTING_METRICS_FRAMEWORK_INIT__",
        "agent_assigned": "framework_initialized",
        "task_requirements": {},
        "scores": [],
        "final_decision": "init",
    }
    try:
        with open(ROUTING_METRICS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(test_record, ensure_ascii=False) + "\n")
        print(f"[RoutingMetrics] Framework initialized at {ROUTING_METRICS_FILE}")
    except Exception as e:
        print(f"[RoutingMetrics] Init failed: {e}")


def demo():
    """演示路由功能"""
    print("=" * 60)
    print("Capability Router Demo — Synapse v3.0 Phase 2 T2-2")
    print("=" * 60)

    _init_routing_metrics()
    router = CapabilityRouter()

    # Demo Task 1: Harness 配置工程任务
    task1 = {
        "task_execution": 4,
        "python_development": 4,
        "automation_scripting": 4
    }
    results1 = router.route(task1, top_k=3)
    print(f"\n[Task 1] {task1}")
    print(f"Top {len(results1)} agents:")
    for r in results1:
        print(f"  {r['agent_id']:20s} [{r['team']:12s}]  "
              f"score={r['final_score']:.3f}  "
              f"cosine={r['base_score']:.3f}  "
              f"cov={r['coverage']:.3f}")

    # Demo Task 2: QA 质量审查任务
    task2 = {
        "quality_audit": 4,
        "yaml_validation": 4,
        "task_execution": 4
    }
    results2 = router.route(task2, top_k=3)
    print(f"\n[Task 2] {task2}")
    print(f"Top {len(results2)} agents:")
    for r in results2:
        print(f"  {r['agent_id']:20s} [{r['team']:12s}]  "
              f"score={r['final_score']:.3f}  "
              f"cosine={r['base_score']:.3f}  "
              f"cov={r['coverage']:.3f}")

    # Demo Task 3: Python 后端开发任务
    task3 = {
        "python_development": 4,
        "code_review": 4,
        "system_integration": 3,
        "task_execution": 4
    }
    results3 = router.route(task3, top_k=3)
    print(f"\n[Task 3] {task3}")
    print(f"Top {len(results3)} agents:")
    for r in results3:
        print(f"  {r['agent_id']:20s} [{r['team']:12s}]  "
              f"score={r['final_score']:.3f}  "
              f"cosine={r['base_score']:.3f}  "
              f"cov={r['coverage']:.3f}")

    # 列出所有技能维度
    print("\n[All Skill Dimensions]")
    skills = router.list_all_skills()
    for skill, info in list(skills.items())[:10]:
        agents_str = ", ".join(
            f"{a}({l})" for a, l in sorted(info["agents"], key=lambda x: -x[1])[:3]
        )
        print(f"  {skill:30s} max={info['max_level']}  {agents_str}")

    return {"task1": results1, "task2": results2, "task3": results3}


if __name__ == "__main__":
    demo()
