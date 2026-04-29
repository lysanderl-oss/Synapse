# -*- coding: utf-8 -*-
"""
Synapse v3.0 — OPC COO Agent
首席运营官（COO）：任务调度、资源协调、跨团队沟通

Phase 3 T3-2: OPC COO Agent 原型
用法:
    from agent_butler.opc_coo import COOAgent
    coo = COOAgent()
    schedule = coo.schedule_task({"task": "deploy", "teams": ["rd", "butler"]})
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

CONFIG_DIR = Path(__file__).parent / "config"
PERSONNEL_DIR = Path(__file__).parent.parent / "obs" / "01-team-knowledge" / "HR" / "personnel" / "opc"


class COOAgent:
    """OPC 首席运营官 Agent

    职责:
        任务调度：基于任务类型和团队负载分配执行者
        资源协调：跨团队依赖管理和资源冲突解决
        沟通协调：任务状态同步、阻塞上报、结果汇总

    状态:
        - active_tasks: 当前执行中的任务
        - team_loads: 各团队当前负载
        - blocked_queue: 阻塞任务队列
    """

    def __init__(self):
        self.active_tasks: dict = {}
        self.team_loads: dict = {}
        self.blocked_queue: list = []
        self._load_team_configs()

    def get_team_load(self) -> dict:
        """获取各团队当前负载率（供 CapabilityRouter 调用）

        Returns:
            {team_id: {"load_factor": float, "active_tasks": int, "max_capacity": int}}
        """
        result = {}
        for team_id, load in self.team_loads.items():
            factor = load["active_tasks"] / max(load["max_capacity"], 1)
            result[team_id] = {
                "load_factor": round(factor, 3),
                "active_tasks": load["active_tasks"],
                "max_capacity": load["max_capacity"],
            }
        return result

    def _load_team_configs(self):
        """从 organization.yaml 加载团队配置"""
        config_file = CONFIG_DIR / "organization.yaml"
        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                teams = data.get("teams", {})
                for team_id, team_data in teams.items():
                    members = team_data.get("members", [])
                    self.team_loads[team_id] = {
                        "member_count": len(members),
                        "active_tasks": 0,
                        "max_capacity": len(members) * 3  # 每个成员约3个并发
                    }
            except Exception:
                pass

    # ─── 任务调度 ──────────────────────────────────────────────

    def schedule_task(self, task_request: dict) -> dict:
        """调度任务到最优团队/执行者

        Args:
            task_request: {
                task_id: str,
                task_type: str,
                description: str,
                teams: list[str],          # 允许的团队列表
                priority: str,             # P0/P1/P2/P3
                deadline: str,             # ISO 日期
                dependencies: list[str],   # 依赖任务ID
            }

        Returns:
            {
                task_id: str,
                assigned_team: str,
                assigned_agent: str,
                estimated_start: str,
                load_factor: float,         # 0.0-1.0 负载率
                conflict: list[str],        # 资源冲突警告
            }
        """
        task_id = task_request.get("task_id", f"task-{datetime.now().strftime('%H%M%S')}")
        priority = task_request.get("priority", "P2")
        teams = task_request.get("teams", list(self.team_loads.keys()))

        # 找到负载最低的团队
        best_team = None
        best_load = float("inf")
        for team_id in teams:
            if team_id in self.team_loads:
                load = self.team_loads[team_id]
                if load["active_tasks"] < load["max_capacity"]:
                    factor = load["active_tasks"] / max(load["max_capacity"], 1)
                    if factor < best_load:
                        best_load = factor
                        best_team = team_id

        if best_team:
            self.team_loads[best_team]["active_tasks"] += 1
            self.active_tasks[task_id] = {
                "team": best_team,
                "priority": priority,
                "started_at": datetime.now().isoformat(),
                "status": "in_progress"
            }

        return {
            "task_id": task_id,
            "assigned_team": best_team or "unassigned",
            "assigned_agent": self._get_team_lead(best_team),
            "estimated_start": datetime.now().isoformat(),
            "load_factor": round(best_load, 2) if best_load != float("inf") else 1.0,
            "conflict": self._check_conflicts(task_request)
        }

    def complete_task(self, task_id: str):
        """标记任务完成，释放资源"""
        if task_id in self.active_tasks:
            team = self.active_tasks[task_id]["team"]
            if team in self.team_loads:
                self.team_loads[team]["active_tasks"] = max(
                    0, self.team_loads[team]["active_tasks"] - 1
                )
            del self.active_tasks[task_id]

    def report_blocked(self, task_id: str, reason: str, blocked_by: Optional[str] = None):
        """上报阻塞"""
        self.blocked_queue.append({
            "task_id": task_id,
            "reason": reason,
            "blocked_by": blocked_by,
            "reported_at": datetime.now().isoformat()
        })

    # ─── 跨团队协调 ──────────────────────────────────────────────

    def coordinate_cross_team(
        self,
        task_id: str,
        team_sequence: list[str]
    ) -> dict:
        """协调多团队顺序执行

        Args:
            task_id: 任务ID
            team_sequence: 团队执行顺序，如 ["rd", "butler", "qa"]

        Returns:
            handoff_plan: {team: {next_team, start_condition, deadline}, ...}
        """
        plan = {}
        for i, team in enumerate(team_sequence):
            next_team = team_sequence[i + 1] if i + 1 < len(team_sequence) else None
            plan[team] = {
                "next_team": next_team,
                "start_condition": "任务开始" if i == 0 else f"前团队 {team_sequence[i-1]} 交付完成",
                "handoff_deadline": f"T+{i*2}h",  # 每团队约2小时
            }
        return plan

    def resolve_conflict(self, conflict_type: str, task_ids: list[str]) -> dict:
        """解决资源冲突"""
        resolution = {
            "conflict_type": conflict_type,
            "affected_tasks": task_ids,
            "resolution": None,
            "decided_at": datetime.now().isoformat()
        }

        if conflict_type == "team_overload":
            # 优先级排序，延迟低优先级任务
            task_loads = [(tid, self.active_tasks.get(tid, {}).get("priority", "P3"))
                          for tid in task_ids]
            task_loads.sort(key=lambda x: {"P0": 0, "P1": 1, "P2": 2, "P3": 3}[x[1]])
            resolution["resolution"] = f"延迟低优先级: {[t[0] for t in task_loads[1:]]}"
        elif conflict_type == "dependency_cycle":
            resolution["resolution"] = "上报 Lysander 处理依赖循环"
        else:
            resolution["resolution"] = "人工介入"

        return resolution

    # ─── 状态报告 ──────────────────────────────────────────────

    def get_dashboard(self) -> dict:
        """COO 运营仪表盘"""
        total_active = len(self.active_tasks)
        blocked_count = len(self.blocked_queue)
        team_status = {}
        for team_id, load in self.team_loads.items():
            factor = load["active_tasks"] / max(load["max_capacity"], 1)
            team_status[team_id] = {
                "active_tasks": load["active_tasks"],
                "max_capacity": load["max_capacity"],
                "load_factor": round(factor, 2),
                "status": "healthy" if factor < 0.7 else "busy" if factor < 1.0 else "overloaded"
            }
        return {
            "total_active_tasks": total_active,
            "blocked_tasks": blocked_count,
            "blocked_queue": self.blocked_queue[-5:],  # 最近5个
            "team_status": team_status,
            "coo_status": "operational"
        }

    # ─── 内部工具 ──────────────────────────────────────────────

    def _get_team_lead(self, team_id: str) -> str:
        """获取团队负责人"""
        lead_map = {
            "harness_ops": "harness_engineer",
            "butler": "butler_pmo",
            "rd": "rd_tech_lead",
            "graphify": "graphify_strategist",
            "obs": "obs_architect",
            "content_ops": "content_strategist",
            "growth": "growth_insights",
        }
        return lead_map.get(team_id, team_id)

    def _check_conflicts(self, task_request: dict) -> list[str]:
        """检查资源冲突"""
        conflicts = []
        teams = task_request.get("teams", [])
        for team in teams:
            if team in self.team_loads:
                load = self.team_loads[team]
                if load["active_tasks"] >= load["max_capacity"]:
                    conflicts.append(f"{team}: overloaded({load['active_tasks']}/{load['max_capacity']})")
        return conflicts


# ─── 使用示例 & 验证 ─────────────────────────────────────────────────────────

def demo():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 60)
    print("OPC COO Agent Demo -- Synapse v3.0 Phase 3 T3-2")
    print("=" * 60)

    coo = COOAgent()

    # Dashboard
    dash = coo.get_dashboard()
    print(f"\n[COO Dashboard]")
    print(f"  Active tasks: {dash['total_active_tasks']}")
    print(f"  Blocked: {dash['blocked_tasks']}")
    print(f"  Teams: {', '.join(dash['team_status'].keys())}")

    # 任务调度
    task1 = coo.schedule_task({
        "task_id": "T-deploy-001",
        "task_type": "deployment",
        "description": "生产环境部署",
        "teams": ["rd", "butler"],
        "priority": "P1"
    })
    print(f"\n[Schedule] T-deploy-001")
    print(f"  Team: {task1['assigned_team']}  Agent: {task1['assigned_agent']}")
    print(f"  Load: {task1['load_factor']:.0%}  Conflict: {task1['conflict']}")

    # 跨团队协调
    handoff = coo.coordinate_cross_team(
        "T-cross-001",
        ["rd", "butler", "qa"]
    )
    print(f"\n[Cross-Team Handoff] T-cross-001")
    for team, info in handoff.items():
        print(f"  {team}: next={info['next_team']} condition={info['start_condition']}")

    # 冲突解决
    resolved = coo.resolve_conflict(
        "team_overload",
        ["T-1", "T-2", "T-3"]
    )
    print(f"\n[Conflict Resolution]")
    print(f"  Type: {resolved['conflict_type']}")
    print(f"  Resolution: {resolved['resolution']}")

    return coo


if __name__ == "__main__":
    demo()
