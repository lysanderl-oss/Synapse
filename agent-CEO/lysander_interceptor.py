"""
Lysander 承接拦截器
确保所有用户诉求先经过 Lysander 承接，再进入执行环节

P0 强制机制：无论 Auto Mode 还是手动模式，
用户输入必须先经过此拦截器，再分发到执行链。
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import uuid
import os


@dataclass
class InterceptedRequest:
    """被拦截的用户诉求"""
    request_id: str
    timestamp: str
    original_input: str
    lysander_restatement: str = ""
    goal_alignment: bool = False
    decision_level: str = "L3"   # 默认 L3（需评估后确定）
    needs_dispatch: bool = True
    dispatch_table: Optional[list] = None
    lysander_notes: str = ""
    status: str = "acknowledged"  # "acknowledged" / "dispatched" / "completed"


class LysanderInterceptor:
    """
    Lysander 承接拦截器

    所有用户诉求的单一入口。确保：
    1. 诉求被 Lysander 完整接收
    2. Lysander 复述并确认理解
    3. 决策级别被正确判断
    4. 派单表被正确输出
    """

    def __init__(self, storage_path: str = "agent-CEO/data/intercept_log.yaml"):
        self.storage_path = storage_path
        self.log: list = []
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                import yaml as _yaml
                with open(self.storage_path, encoding="utf-8") as f:
                    self.log = _yaml.safe_load(f) or []
            except Exception:
                self.log = []

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        import yaml as _yaml
        with open(self.storage_path, "w", encoding="utf-8") as f:
            _yaml.dump(self.log, f, allow_unicode=True, default_flow_style=False)

    def intercept(self, user_input: str) -> InterceptedRequest:
        """
        拦截用户诉求，返回包含 Lysander 承接信息的结构。

        注意：此函数由 Lysander CEO 调用，
        用户看到的输出是 Lysander 的复述和派单表。
        """
        req = InterceptedRequest(
            request_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            original_input=user_input,
        )

        self.log.append(asdict(req))
        self._save()

        return req

    def acknowledge(self, request_id: str, restatement: str,
                    goal_alignment: bool, decision_level: str,
                    needs_dispatch: bool, dispatch_table: list = None,
                    notes: str = "") -> bool:
        """
        Lysander 完成承接后调用此方法更新状态。

        返回：是否更新成功
        """
        for entry in self.log:
            if entry.get("request_id") == request_id:
                entry["lysander_restatement"] = restatement
                entry["goal_alignment"] = goal_alignment
                entry["decision_level"] = decision_level
                entry["needs_dispatch"] = needs_dispatch
                entry["dispatch_table"] = dispatch_table
                entry["lysander_notes"] = notes
                entry["acknowledged_at"] = datetime.now().isoformat()
                entry["status"] = "dispatched" if needs_dispatch else "completed"
                self._save()
                return True
        return False

    def complete(self, request_id: str, outcome: str = "") -> bool:
        """任务完成后标记"""
        for entry in self.log:
            if entry.get("request_id") == request_id:
                entry["status"] = "completed"
                entry["completed_at"] = datetime.now().isoformat()
                entry["outcome"] = outcome
                self._save()
                return True
        return False

    def get_pending(self) -> list:
        """获取待承接的诉求"""
        return [e for e in self.log if e.get("status") == "acknowledged"]

    def get_active(self) -> list:
        """获取进行中的诉求"""
        return [e for e in self.log if e.get("status") == "dispatched"]

    def get_completed(self, limit: int = 20) -> list:
        """获取最近完成的历史记录"""
        completed = [e for e in self.log if e.get("status") == "completed"]
        return completed[-limit:]

    def audit_p0_violations(self) -> list:
        """
        审计 P0 违规：
        - 在未完成【0.5】承接的情况下直接派单或执行
        返回违规记录列表。
        """
        violations = []
        for entry in self.log:
            if entry.get("status") == "dispatched" and not entry.get("lysander_restatement"):
                violations.append({
                    "request_id": entry.get("request_id"),
                    "timestamp": entry.get("timestamp"),
                    "original_input": entry.get("original_input", "")[:100],
                    "violation": "派单/执行发生在承接完成之前（无 Lysander 复述记录）"
                })
        return violations
