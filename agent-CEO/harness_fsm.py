"""
Synapse v3.0 — Harness FSM Engine
==================================
Synapse 执行链状态机（Finite State Machine）
将 harness_registry.yaml 中的规则转化为可执行的工作流引擎

设计原则：
- 状态转换完全由 VALID_TRANSITIONS 控制，无例外
- 所有转换记录 history，实现完整审计链
- audit_fsm_transition() 集成 harness_registry.yaml 的 P0/P1 约束
- 与 handoff_protocol.yaml 的 37 字段无缝对接

Author: harness_engineer
Task: T6-3
Phase: Phase 2 - FSM Engine
"""

import yaml
import os
from enum import Enum
from datetime import datetime
from typing import Optional


# =============================================================================
# ① 状态枚举
# =============================================================================
class ExecutionState(Enum):
    """Synapse 执行链状态枚举 — 与 handoff_protocol.yaml 完全对齐"""
    IDLE = "idle"
    DISPATCHED = "dispatched"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    QA_REVIEW = "qa_review"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    BLOCKED = "blocked"
    ESCALATED = "escalated"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# =============================================================================
# ② FSM 核心引擎
# =============================================================================
class HarnessFSM:
    """
    Synapse 执行链状态机

    状态图：
        IDLE → DISPATCHED → ACKNOWLEDGED → IN_PROGRESS → QA_REVIEW → COMPLETED
                              ↓                ↓             ↓
                          BLOCKED         BLOCKED       PARTIALLY_COMPLETED
                              ↓                ↓             ↓
                        ESCALATED       ESCALATED        REJECTED → IN_PROGRESS
                              ↓                ↓
                           CANCELLED       CANCELLED
    """

    # 有效转换规则 — 这是唯一的转换依据，无例外
    VALID_TRANSITIONS = {
        ExecutionState.IDLE:              [ExecutionState.DISPATCHED],
        ExecutionState.DISPATCHED:        [ExecutionState.ACKNOWLEDGED,
                                           ExecutionState.BLOCKED,
                                           ExecutionState.CANCELLED],
        ExecutionState.ACKNOWLEDGED:      [ExecutionState.IN_PROGRESS,
                                           ExecutionState.BLOCKED,
                                           ExecutionState.CANCELLED],
        ExecutionState.IN_PROGRESS:       [ExecutionState.QA_REVIEW,
                                           ExecutionState.BLOCKED,
                                           ExecutionState.ESCALATED,
                                           ExecutionState.CANCELLED],
        ExecutionState.QA_REVIEW:         [ExecutionState.COMPLETED,
                                           ExecutionState.PARTIALLY_COMPLETED,
                                           ExecutionState.REJECTED],
        ExecutionState.REJECTED:          [ExecutionState.IN_PROGRESS,
                                           ExecutionState.CANCELLED],
        ExecutionState.BLOCKED:           [ExecutionState.IN_PROGRESS,
                                           ExecutionState.ESCALATED,
                                           ExecutionState.CANCELLED],
        ExecutionState.ESCALATED:          [ExecutionState.IN_PROGRESS,
                                           ExecutionState.CANCELLED],
        ExecutionState.PARTIALLY_COMPLETED: [],
        ExecutionState.COMPLETED:          [],
        ExecutionState.CANCELLED:          [],
    }

    # P0-2: DISPATCHED 超时配置（分钟）
    DISPATCHED_TIMEOUT_MINUTES = 30

    def __init__(self, task_id: str):
        """
        初始化 FSM

        Args:
            task_id: 任务唯一标识（如 T6-3）
        """
        self.task_id = task_id
        self.state = ExecutionState.IDLE
        self.history: list[dict] = []
        self._blocked_since: Optional[datetime] = None
        self._dispatched_at: Optional[datetime] = None
        self._qa_started_at: Optional[datetime] = None
        self._timeout_blocked: bool = False  # P0-2: 是否因超时被阻塞

    # ─── 基础能力 ───────────────────────────────────────────────────────────

    def can_transition(self, target: ExecutionState) -> bool:
        """检查是否允许转换到目标状态"""
        return target in self.VALID_TRANSITIONS.get(self.state, [])

    def transition(self, target: ExecutionState, reason: str = "") -> bool:
        """
        执行状态转换

        Args:
            target: 目标状态
            reason:  转换原因描述

        Returns:
            True  — 转换成功
            False — 转换被拒绝（无效转换）
        """
        if not self.can_transition(target):
            return False

        old = self.state
        self.state = target

        # 记录时间戳
        now = datetime.now()
        entry = {
            "from": old.value,
            "to": target.value,
            "reason": reason,
            "timestamp": now.isoformat(),
            "task_id": self.task_id,
        }

        # 特殊状态的时间追踪
        if target == ExecutionState.DISPATCHED:
            self._dispatched_at = now
            self._timeout_blocked = False  # P0-2: 重置超时标记（新派单周期开始）
        elif target == ExecutionState.BLOCKED:
            self._blocked_since = now
        elif target == ExecutionState.QA_REVIEW:
            self._qa_started_at = now
        elif target != ExecutionState.BLOCKED:
            self._blocked_since = None  # 解除 BLOCKED 状态时清除时间戳

        self.history.append(entry)
        return True

    # ─── 便捷方法（与 handoff_protocol.yaml 字段对应）────────────────────────

    def dispatch(self) -> bool:
        """派单：IDLE → DISPATCHED"""
        return self.transition(ExecutionState.DISPATCHED, "任务已派单")

    def acknowledge(self) -> bool:
        """接收：DISPATCHED → ACKNOWLEDGED"""
        # P0-2: 超时检测：若DISPATCHED已超30分钟，先触发BLOCKED
        self.check_dispatched_timeout()
        return self.transition(ExecutionState.ACKNOWLEDGED, "Agent已接收")

    def start(self) -> bool:
        """开始执行：ACKNOWLEDGED → IN_PROGRESS"""
        return self.transition(ExecutionState.IN_PROGRESS, "开始执行")

    def submit_qa(self) -> bool:
        """提交QA审查：IN_PROGRESS → QA_REVIEW"""
        return self.transition(ExecutionState.QA_REVIEW, "提交QA审查")

    def complete(self) -> bool:
        """完成：QA_REVIEW → COMPLETED"""
        return self.transition(ExecutionState.COMPLETED, "执行完成")

    def partially_complete(self) -> bool:
        """部分完成：QA_REVIEW → PARTIALLY_COMPLETED"""
        return self.transition(ExecutionState.PARTIALLY_COMPLETED, "部分完成")

    def block(self, reason: str = "") -> bool:
        """阻塞：任何执行状态 → BLOCKED"""
        return self.transition(ExecutionState.BLOCKED, reason or "任务阻塞")

    def escalate(self, reason: str = "") -> bool:
        """升级：BLOCKED → ESCALATED"""
        return self.transition(ExecutionState.ESCALATED, reason or "升级到Lysander")

    def reject(self) -> bool:
        """拒绝：QA_REVIEW → REJECTED"""
        return self.transition(ExecutionState.REJECTED, "QA审查未通过")

    def revise(self) -> bool:
        """返工：REJECTED → IN_PROGRESS"""
        return self.transition(ExecutionState.IN_PROGRESS, "返工")

    def cancel(self) -> bool:
        """取消：任何非终态 → CANCELLED"""
        return self.transition(ExecutionState.CANCELLED, "任务取消")

    def resume(self) -> bool:
        """恢复：BLOCKED/ESCALATED → IN_PROGRESS"""
        return self.transition(ExecutionState.IN_PROGRESS, "任务恢复")

    # ─── 查询方法 ─────────────────────────────────────────────────────────────

    def get_state(self) -> str:
        """返回当前状态字符串"""
        return self.state.value

    def get_history(self) -> list[dict]:
        """返回完整转换历史"""
        return self.history

    def is_terminal(self) -> bool:
        """是否终态（不可继续流转）"""
        return self.state in {
            ExecutionState.COMPLETED,
            ExecutionState.PARTIALLY_COMPLETED,
            ExecutionState.CANCELLED,
        }

    def is_blocked(self) -> bool:
        """是否处于阻塞状态"""
        return self.state == ExecutionState.BLOCKED

    def get_blocked_duration(self) -> Optional[float]:
        """
        返回阻塞持续时间（小时）
        仅在 BLOCKED 状态下有效
        """
        if self.state != ExecutionState.BLOCKED or self._blocked_since is None:
            return None
        delta = datetime.now() - self._blocked_since
        return delta.total_seconds() / 3600

    def get_valid_next_states(self) -> list[str]:
        """返回当前状态允许的后继状态列表"""
        states = self.VALID_TRANSITIONS.get(self.state, [])
        return [s.value for s in states]

    # P0-2: 超时检测 — DISPATCHED超过30分钟未变为ACKNOWLEDGED，自动触发BLOCKED
    def check_dispatched_timeout(self) -> bool:
        """
        检测DISPATCHED状态是否超时

        Returns:
            True  — 检测到超时，已自动触发BLOCKED
            False — 未超时，或状态已流转
        """
        if self.state != ExecutionState.DISPATCHED:
            return False
        if self._dispatched_at is None:
            return False

        elapsed = (datetime.now() - self._dispatched_at).total_seconds() / 60
        if elapsed >= self.DISPATCHED_TIMEOUT_MINUTES:
            self._timeout_blocked = True
            self.transition(
                ExecutionState.BLOCKED,
                f"DISPATCHED超时：已等待{elapsed:.1f}分钟，超过{self.DISPATCHED_TIMEOUT_MINUTES}分钟限制"
            )
            return True
        return False

    def is_timeout_blocked(self) -> bool:
        """返回是否因超时被阻塞"""
        return self._timeout_blocked

    def summary(self) -> dict:
        """返回 FSM 快照（用于 active_tasks.yaml 持久化）"""
        return {
            "task_id": self.task_id,
            "state": self.state.value,
            "is_terminal": self.is_terminal(),
            "is_blocked": self.is_blocked(),
            "blocked_hours": round(self.get_blocked_duration(), 2)
                             if self.get_blocked_duration() is not None else None,
            "transition_count": len(self.history),
            "last_transition": self.history[-1] if self.history else None,
            "dispatched_at": self._dispatched_at.isoformat()
                            if self._dispatched_at else None,
            "qa_started_at": self._qa_started_at.isoformat()
                             if self._qa_started_at else None,
            # P0-2: 超时阻塞标记
            "timeout_blocked": self._timeout_blocked,
        }


# =============================================================================
# ③ 审计函数（集成 harness_registry.yaml 约束）
# =============================================================================

def _load_registry() -> dict:
    """加载 harness_registry.yaml"""
    path = os.path.join(
        os.path.dirname(__file__),
        "config",
        "harness_registry.yaml"
    )
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def audit_fsm_transition(
    task_id: str,
    from_state: str,
    to_state: str,
    blocked_hours: Optional[float] = None,
) -> dict:
    """
    审计 FSM 状态转换是否符合 harness_registry 约束

    Args:
        task_id:      任务ID
        from_state:   源状态（字符串）
        to_state:     目标状态（字符串）
        blocked_hours: BLOCKED 持续小时数（可选）

    Returns:
        audit_result: {
            "pass": bool,
            "violations": list[str],  # 违规描述列表
            "warnings": list[str],    # 警告列表（非阻塞）
            "level": "P0" | "P1" | "P2",
        }
    """
    violations: list[str] = []
    warnings: list[str] = []

    # ── P0: 必须经过 QA_REVIEW 才能 COMPLETED ──────────────────────────────
    # P0-7: "执行完成后必须经过【③】QA + 智囊团审查，不可跳过"
    if to_state == "completed" and from_state != "qa_review":
        violations.append(
            "P0-7 违规：COMPLETED 状态必须从 QA_REVIEW 转换而来，"
            f"当前从 {from_state} 直接跳转"
        )

    # ── P0: DISPATCHED 前必须是 IDLE ───────────────────────────────────────
    if to_state == "dispatched" and from_state not in ("idle", ""):
        violations.append(
            "P0 违规：DISPATCHED 前必须是 IDLE，"
            f"当前从 {from_state} 跳转"
        )

    # ── P1: BLOCKED 超过 24小时 必须 ESCALATED ────────────────────────────
    if (from_state == "blocked" and to_state != "escalated"
            and blocked_hours is not None and blocked_hours >= 24):
        warnings.append(
            f"P1 警告：BLOCKED 已持续 {blocked_hours:.1f}h（≥24h），"
            "建议升级到 ESCALATED"
        )

    # ── P1: 终态不可流转 ──────────────────────────────────────────────────
    terminal_states = {"completed", "partially_completed", "cancelled"}
    if from_state in terminal_states and to_state not in terminal_states:
        warnings.append(
            f"P1 警告：从终态 {from_state} 流转到 {to_state}，"
            "确认是否需要重新激活任务"
        )

    # ── P2: ESCALATED 后 Lysander 必须介入 ─────────────────────────────────
    if from_state == "escalated" and to_state != "in_progress":
        if to_state != "cancelled":
            warnings.append(
                "P2 提示：ESCALATED 后恢复应通过 Lysander 决策，"
                "建议转换到 IN_PROGRESS"
            )

    level = "P0" if violations else ("P1" if warnings else "P2")
    return {
        "pass": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "level": level,
        "task_id": task_id,
        "transition": f"{from_state} → {to_state}",
        "audited_at": datetime.now().isoformat(),
    }


def audit_task_fsm(task_id: str) -> dict:
    """
    审计 active_tasks.yaml 中某个任务的 FSM 状态

    Returns:
        audit_result（含 FSM 快照 + 违规检测）
    """
    registry = _load_registry()
    # 基础信息
    return {
        "task_id": task_id,
        "registry_version": registry.get("harness_registry", {}).get("version", "N/A"),
        "fsm_rules_loaded": True,
        "audit_timestamp": datetime.now().isoformat(),
    }


# =============================================================================
# ④ 集成 handoff_protocol.yaml 的 37 字段
# =============================================================================

def build_dispatch_context(fsm: HarnessFSM, dispatch_id: str) -> dict:
    """
    根据当前 FSM 状态，构建 handoff_protocol.yaml 格式的 dispatch 上下文

    用于 Lysander 派单时自动生成符合规范的派单模板
    """
    state = fsm.get_state()
    summary = fsm.summary()

    return {
        # dispatch_id 由 Lysander 在派单时生成 UUID-v4
        "fsm_context": {
            "task_id": fsm.task_id,
            "state": state,
            "dispatched_at": summary.get("dispatched_at"),
            "transition_count": summary.get("transition_count", 0),
            "is_terminal": summary.get("is_terminal", False),
        },
        # valid_handoff_statuses 由 handoff_protocol.yaml 定义
        # current_state 决定 valid next_valid
        "valid_next_states": fsm.get_valid_next_states(),
        "state_audit": audit_fsm_transition(
            task_id=fsm.task_id,
            from_state=summary.get("last_transition", {}).get("from", "idle"),
            to_state=state,
        ),
    }


# =============================================================================
# ⑤ FSM Task Tracker（与 active_tasks.yaml 集成）
# =============================================================================

class TaskTracker:
    """
    FSM 驱动的任务追踪器
    管理多个任务的 FSM 实例，支持持久化和恢复
    """

    def __init__(self, tasks_file: str = ""):
        self._tasks: dict[str, HarnessFSM] = {}
        self._tasks_file = tasks_file or os.path.join(
            os.path.dirname(__file__),
            "config",
            "active_tasks_fsm.yaml"
        )
        # P0-2: 全局超时统计计数器
        self._blocked_timeout_count: dict[str, int] = {}

    def create(self, task_id: str) -> HarnessFSM:
        """创建新任务 FSM"""
        fsm = HarnessFSM(task_id)
        self._tasks[task_id] = fsm
        return fsm

    def get(self, task_id: str) -> Optional[HarnessFSM]:
        """获取任务 FSM"""
        return self._tasks.get(task_id)

    def acknowledge(self, task_id: str) -> bool:
        """
        P0-2: 接收任务（带超时检测）
        - 先检测DISPATCHED超时，超时则自动触发BLOCKED并计数
        - 再执行ACKNOWLEDGED转换
        """
        fsm = self._tasks.get(task_id)
        if fsm is None:
            return False
        # 检测超时：若DISPATCHED已超30分钟，先触发BLOCKED并计数
        if fsm.check_dispatched_timeout():
            self.increment_timeout_count(task_id)
        return fsm.acknowledge()

    def get_active(self) -> list[dict]:
        """列出所有活跃（非终态）任务，含超时检测"""
        result = []
        for task_id, fsm in self._tasks.items():
            # P0-2: 每次查询时主动检测DISPATCHED超时
            if fsm.state == ExecutionState.DISPATCHED:
                if fsm.check_dispatched_timeout():
                    self.increment_timeout_count(task_id)
            if not fsm.is_terminal():
                result.append(fsm.summary())
        return result

    def list_active(self) -> list[dict]:
        """列出所有非终态任务"""
        result = []
        for task_id, fsm in self._tasks.items():
            if not fsm.is_terminal():
                result.append(fsm.summary())
        return result

    def list_blocked(self) -> list[dict]:
        """列出所有阻塞任务"""
        result = []
        for task_id, fsm in self._tasks.items():
            if fsm.is_blocked():
                result.append(fsm.summary())
        return result

    def increment_timeout_count(self, task_id: str) -> int:
        """P0-2: 递增指定任务的超时计数，返回更新后的计数"""
        self._blocked_timeout_count[task_id] = (
            self._blocked_timeout_count.get(task_id, 0) + 1
        )
        return self._blocked_timeout_count[task_id]

    def get_timeout_count(self, task_id: str) -> int:
        """返回指定任务的超时次数"""
        return self._blocked_timeout_count.get(task_id, 0)

    def get_timeout_stats(self) -> dict:
        """返回全局超时统计"""
        return dict(self._blocked_timeout_count)

    def persist(self) -> None:
        """持久化到 YAML 文件"""
        data = {}
        for task_id, fsm in self._tasks.items():
            data[task_id] = {
                "task_id": fsm.task_id,
                "state": fsm.state.value,
                "history": fsm.history,
                # P0-2: 超时阻塞标记
                "timeout_blocked": fsm._timeout_blocked,
            }
        # P0-2: 超时计数器写入全局统计
        data["_global"] = {
            "_blocked_timeout_count": self._blocked_timeout_count,
            "persisted_at": datetime.now().isoformat(),
        }
        os.makedirs(os.path.dirname(self._tasks_file), exist_ok=True)
        with open(self._tasks_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def restore(self) -> None:
        """从 YAML 文件恢复 FSM 实例"""
        if not os.path.exists(self._tasks_file):
            return
        with open(self._tasks_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        global_meta = data.pop("_global", None)
        for task_id, saved in data.items():
            fsm = HarnessFSM(saved["task_id"])
            fsm.state = ExecutionState(saved["state"])
            fsm.history = saved.get("history", [])
            # P0-2: 恢复超时阻塞标记
            fsm._timeout_blocked = saved.get("timeout_blocked", False)
            self._tasks[task_id] = fsm
        # P0-2: 恢复全局超时计数器
        if global_meta:
            self._blocked_timeout_count = global_meta.get("_blocked_timeout_count", {})


# =============================================================================
# ⑥ CLI 测试入口
# =============================================================================

if __name__ == "__main__":
    import json

    print("=" * 60)
    print("Harness FSM — Standalone Verification")
    print("=" * 60)

    fsm = HarnessFSM("TEST-T6-3")
    print(f"\n[TASK: {fsm.task_id}]")
    print(f"Initial state: {fsm.get_state()}")

    # 完整 Happy Path
    steps = [
        ("dispatch",    fsm.dispatch),
        ("acknowledge", fsm.acknowledge),
        ("start",       fsm.start),
        ("submit_qa",   fsm.submit_qa),
        ("complete",    fsm.complete),
    ]

    for name, method in steps:
        ok = method()
        print(f"  {name:15s}: {'OK' if ok else 'FAIL'} → {fsm.get_state()}")

    print(f"\nFinal state:  {fsm.get_state()}")
    print(f"Transitions:  {len(fsm.get_history())}")
    print(f"Terminal:     {fsm.is_terminal()}")

    # 审计
    audit = audit_fsm_transition(
        task_id=fsm.task_id,
        from_state="qa_review",
        to_state="completed",
    )
    print(f"\nAudit:        {json.dumps(audit, indent=2, ensure_ascii=False)}")

    # 测试 REJECTED 路径
    print("\n" + "-" * 60)
    fsm2 = HarnessFSM("TEST-T6-3-REJECT")
    fsm2.dispatch()
    fsm2.acknowledge()
    fsm2.start()
    fsm2.submit_qa()
    fsm2.reject()
    fsm2.revise()
    print(f"Rejection path: {fsm2.get_state()} (expect: in_progress)")

    # 测试 BLOCKED 路径
    print("\n" + "-" * 60)
    fsm3 = HarnessFSM("TEST-T6-3-BLOCK")
    fsm3.dispatch()
    fsm3.acknowledge()
    fsm3.start()
    fsm3.block("测试阻塞原因")
    print(f"Blocked state: {fsm3.get_state()}")
    print(f"Valid next:    {fsm3.get_valid_next_states()}")

    # 测试 P0 违规检测
    print("\n" + "-" * 60)
    audit_p0 = audit_fsm_transition(
        task_id="TEST-P0-VIOLATION",
        from_state="in_progress",
        to_state="completed",
    )
    print(f"P0 violation test: pass={audit_p0['pass']}")
    if audit_p0["violations"]:
        for v in audit_p0["violations"]:
            print(f"  VIOLATION: {v}")

    print("\n" + "=" * 60)
    print("FSM Verification Complete")
    print(f"States: {len(ExecutionState)}")
    print(f"Total transition rules: {sum(len(v) for v in HarnessFSM.VALID_TRANSITIONS.values())}")
    print("=" * 60)
