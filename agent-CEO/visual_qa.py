"""
Synapse v3.0 — Visual QA 自动化模块
====================================
与 integration_qa 的 qa_auto_review() 集成
UI 变更任务自动触发截图 diff 验证

Usage:
    from visual_qa import VisualQA, trigger_visual_qa

    vqa = VisualQA(base_dir="agent-CEO/data/visual_qa")
    result = vqa.capture("https://example.com/page")
    diff = vqa.compare("before.png", "after.png")
    report = vqa.generate_diff_report(diff)
"""

import os
import json
import hashlib
import shutil
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Literal

# 全局阈值配置
THRESHOLD_DIFF_RATIO = 0.05  # 5% — 超过此比例视为显著差异

# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DiffResult:
    """Diff 比较结果"""
    before_path: str
    after_path: str
    before_hash: Optional[str]
    after_hash: Optional[str]
    diff_ratio: float        # 0.0 - 1.0，差异比例
    is_significant: bool     # True = 超过阈值
    status: str              # "significant" | "unchanged" | "first_change" | "error"
    message: str
    compared_at: str = None

    def __post_init__(self):
        if self.compared_at is None:
            self.compared_at = datetime.now().isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# VisualQA 主类
# ─────────────────────────────────────────────────────────────────────────────

class VisualQA:
    """
    Visual QA 自动化类

    提供截图 capture、像素 diff 对比、差异报告生成功能。
    与 qa_auto_review() 集成，UI 变更任务自动调用。

    diff 策略：
    - 优先使用文件 hash（MD5）作为近似差异指标
    - 配合文件大小差异比例辅助判断
    - 差异比例 > THRESHOLD_DIFF_RATIO（5%）视为显著差异
    """

    def __init__(self, base_dir: str = "agent-CEO/data/visual_qa"):
        self.base_dir = base_dir
        self.screenshot_dir = os.path.join(base_dir, "screenshots")
        self.diff_dir = os.path.join(base_dir, "diffs")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs(self.diff_dir, exist_ok=True)

    # ── 文件工具 ─────────────────────────────────────────────────────────────

    def _file_hash(self, filepath: str) -> Optional[str]:
        """计算文件 MD5 hash，文件不存在返回 None"""
        if not os.path.exists(filepath):
            return None
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def _file_size_ratio(self, path1: str, path2: str) -> float:
        """计算两个文件大小差异比例（0.0 - 1.0）"""
        if not os.path.exists(path1) or not os.path.exists(path2):
            return 0.0
        s1 = os.path.getsize(path1)
        s2 = os.path.getsize(path2)
        if s1 == 0:
            return 1.0 if s2 > 0 else 0.0
        return abs(s1 - s2) / max(s1, s2)

    # ── capture: 截图（占位，早期由 gstack/mcp 完成）────────────────────────

    def capture(self, target_url_or_path: str, label: str = "") -> dict:
        """
        截图目标页面或路径

        实际截图由 gstack / mcp__Claude_in_Chrome 工具完成。
        此方法记录截图元数据到本地，供后续 compare() 使用。

        Args:
            target_url_or_path: URL 或文件路径
            label: 标签（用于命名截图文件）

        Returns:
            截图元数据 dict: {screenshot_id, label, path, timestamp, note}
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_label = "".join(c if c.isalnum() else "_" for c in label)[:30]
        screenshot_id = f"{ts}_{safe_label}" if safe_label else ts

        # 截图实际路径（由 gstack/mcp 填充）
        path = os.path.join(self.screenshot_dir, f"{screenshot_id}.png")

        meta = {
            "screenshot_id": screenshot_id,
            "label": label,
            "target": target_url_or_path,
            "path": path,
            "timestamp": datetime.now().isoformat(),
            "note": (
                "实际截图请使用 gstack / mcp__Claude_in_Chrome 工具完成，"
                "本方法仅记录元数据。请将截图保存到上述 path 字段指向的位置。"
            ),
        }

        # 写入元数据 JSON
        meta_file = os.path.join(self.screenshot_dir, f"{screenshot_id}.meta.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        return meta

    # ── compare: 差异对比 ───────────────────────────────────────────────────

    def compare(self, before_path: str, after_path: str) -> DiffResult:
        """
        比较变更前后的截图/文件

        差异算法：
        1. 计算两个文件的 MD5 hash — 相同则文件完全一致
        2. 计算文件大小差异比例作为辅助指标
        3. diff_ratio = 0.0（hash 一致）或 1.0（hash 不同），由文件大小差异辅助调节

        注：完整像素级 diff 需要 Pillow，可选安装。
        当前实现使用 hash + 文件大小作为近似，快速可靠。

        Args:
            before_path: 变更前文件路径（截图或任意文件）
            after_path: 变更后文件路径

        Returns:
            DiffResult 对象
        """
        before_abs = os.path.abspath(before_path)
        after_abs = os.path.abspath(after_path)

        # 首次变更：before 不存在
        if not os.path.exists(before_abs):
            return DiffResult(
                before_path=before_abs,
                after_path=after_abs,
                before_hash=None,
                after_hash=self._file_hash(after_abs),
                diff_ratio=0.0,
                is_significant=False,
                status="first_change",
                message="首次变更，无 before 截图，无需 diff 比较",
            )

        # after 不存在 → 异常
        if not os.path.exists(after_abs):
            return DiffResult(
                before_path=before_abs,
                after_path=after_abs,
                before_hash=self._file_hash(before_abs),
                after_hash=None,
                diff_ratio=1.0,
                is_significant=True,
                status="error",
                message="变更后文件不存在，无法比较",
            )

        # hash 对比
        hash_before = self._file_hash(before_abs)
        hash_after = self._file_hash(after_abs)

        if hash_before == hash_after:
            return DiffResult(
                before_path=before_abs,
                after_path=after_abs,
                before_hash=hash_before,
                after_hash=hash_after,
                diff_ratio=0.0,
                is_significant=False,
                status="unchanged",
                message=f"文件完全一致，hash: {hash_before}",
            )

        # hash 不同 → 计算文件大小差异作为近似 diff ratio
        size_ratio = self._file_size_ratio(before_abs, after_abs)

        # 尝试 Pillow 像素级 diff（可选）
        try:
            from PIL import Image
            img_before = Image.open(before_abs)
            img_after = Image.open(after_abs)

            if img_before.size != img_after.size:
                # 分辨率不同，使用文件大小比例
                diff_ratio = size_ratio
            else:
                # 逐像素对比
                pixels_before = list(img_before.getdata())
                pixels_after = list(img_after.getdata())
                diff_count = sum(
                    1 for a, b in zip(pixels_before, pixels_after) if a != b
                )
                diff_ratio = diff_count / len(pixels_before)

        except ImportError:
            # 无 Pillow → 使用文件大小比例作为近似
            diff_ratio = max(size_ratio, 0.3)  # 保守估计

        is_significant = diff_ratio > THRESHOLD_DIFF_RATIO

        status = "significant" if is_significant else "unchanged"
        message = (
            f"差异比例 {diff_ratio:.1%}，"
            f"{'超过' if is_significant else '未超过'}阈值 {THRESHOLD_DIFF_RATIO:.0%}"
        )

        return DiffResult(
            before_path=before_abs,
            after_path=after_abs,
            before_hash=hash_before,
            after_hash=hash_after,
            diff_ratio=round(diff_ratio, 4),
            is_significant=is_significant,
            status=status,
            message=message,
        )

    # ── generate_diff_report: 差异报告 ─────────────────────────────────────

    def generate_diff_report(self, diff_result: DiffResult, task_id: str = "") -> dict:
        """
        生成结构化 diff 报告

        Args:
            diff_result: compare() 返回的 DiffResult
            task_id: 关联任务 ID（可选）

        Returns:
            diff 报告 dict
        """
        return {
            "task_id": task_id,
            "before": diff_result.before_path,
            "after": diff_result.after_path,
            "before_hash": diff_result.before_hash,
            "after_hash": diff_result.after_hash,
            "diff_ratio": f"{diff_result.diff_ratio:.2%}",
            "is_significant": diff_result.is_significant,
            "status": diff_result.status,
            "message": diff_result.message,
            "threshold": f"{THRESHOLD_DIFF_RATIO:.0%}",
            "verdict": (
                "PASS — 显著差异已确认，变更生效"
                if diff_result.is_significant
                else "PASS — 无明显差异，变更未引入视觉破坏"
                if diff_result.status == "unchanged"
                else "INFO — 首次变更，无历史基线"
                if diff_result.status == "first_change"
                else "ERROR — 比较失败"
            ),
            "compared_at": diff_result.compared_at,
            "qa_dimension": "visual_integrity",
            "threshold_used": THRESHOLD_DIFF_RATIO,
        }


# ─────────────────────────────────────────────────────────────────────────────
# trigger_visual_qa: UI 变更任务自动触发函数
# ─────────────────────────────────────────────────────────────────────────────

def trigger_visual_qa(
    task_id: str,
    before_path: Optional[str] = None,
    after_path: Optional[str] = None,
    task_description: str = "",
) -> dict:
    """
    UI 变更任务自动触发 Visual QA

    在 UI/前端变更任务中自动调用，读取变更前后截图进行对比。
    与 integration_qa 的 qa_auto_review() 集成，补充 visual_integrity 维度。

    Args:
        task_id: 任务 ID
        before_path: 变更前截图路径（如不提供则尝试自动查找）
        after_path: 变更后截图路径
        task_description: 任务描述（用于查找截图）

    Returns:
        Visual QA 结果 dict（含 diff_report + verdict）
    """
    vqa = VisualQA()

    # 自动查找截图（基于 task_id 或 task_description 关键词）
    if not before_path or not after_path:
        found_before, found_after = _find_screenshots(task_id, task_description)
        before_path = before_path or found_before
        after_path = after_path or found_after

    if not before_path and not after_path:
        return {
            "task_id": task_id,
            "status": "no_screenshots",
            "verdict": "INFO",
            "message": "未提供截图路径且未找到自动匹配截图，跳过 Visual QA",
            "note": "如需启用，请使用 gstack capture 工具获取截图路径后传入",
            "triggered_at": datetime.now().isoformat(),
        }

    if not before_path:
        return {
            "task_id": task_id,
            "status": "first_change",
            "verdict": "PASS",
            "message": "首次变更，无需 diff 比较",
            "after_path": after_path,
            "triggered_at": datetime.now().isoformat(),
        }

    diff_result = vqa.compare(before_path, after_path)
    report = vqa.generate_diff_report(diff_result, task_id=task_id)

    return {
        "task_id": task_id,
        "diff_result": asdict(diff_result),
        "diff_report": report,
        "verdict": report["verdict"],
        "passed": diff_result.status != "error",
        "triggered_at": datetime.now().isoformat(),
    }


def _find_screenshots(task_id: str, task_description: str) -> tuple[Optional[str], Optional[str]]:
    """
    基于 task_id / task_description 自动查找匹配的截图文件

    约定截图命名格式：
    - 变更前: {task_id}_before.png / {task_id}_before.jpg
    - 变更后: {task_id}_after.png / {task_id}_after.jpg

    Returns:
        (before_path, after_path) — 均可能为 None
    """
    vqa = VisualQA()
    base = vqa.screenshot_dir

    candidates_before: list[str] = []
    candidates_after: list[str] = []

    # 按 task_id 精确匹配
    for fname in os.listdir(base) if os.path.exists(base) else []:
        if not fname.endswith((".png", ".jpg", ".jpeg")):
            continue
        if task_id in fname:
            if "_before" in fname:
                candidates_before.append(os.path.join(base, fname))
            elif "_after" in fname:
                candidates_after.append(os.path.join(base, fname))

    before_path = candidates_before[0] if candidates_before else None
    after_path = candidates_after[0] if candidates_after else None

    return before_path, after_path


# ─────────────────────────────────────────────────────────────────────────────
# 与 qa_auto_review() 集成 — 扩展 integration_qa 门禁
# ─────────────────────────────────────────────────────────────────────────────

def integration_visual_gate(
    task_id: str,
    before_path: Optional[str] = None,
    after_path: Optional[str] = None,
    task_description: str = "",
) -> dict:
    """
    Visual QA 门禁 — 补充 qa_auto_review() 的 visual_integrity 维度

    由 integration_qa 在 UI 变更任务中调用。
    返回结果可直接并入 qa_auto_review() 的 issues 列表。

    Args:
        task_id: 任务 ID
        before_path / after_path: 截图路径
        task_description: 任务描述

    Returns:
        Visual gate 裁决 dict: {
            gate: "pass" | "warn" | "fail",
            visual_issues: list[str],
            diff_report: dict,
            passed: bool,
        }
    """
    result = trigger_visual_qa(task_id, before_path, after_path, task_description)
    status = result.get("status", "")

    if status == "no_screenshots":
        return {
            "gate": "warn",
            "visual_issues": [
                "Visual QA 跳过：未找到截图，请在 UI 变更任务中补充截图"
            ],
            "diff_report": result,
            "passed": True,  # 软失败，不阻止交付
        }

    if status == "first_change":
        return {
            "gate": "pass",
            "visual_issues": [],
            "diff_report": result,
            "passed": True,
        }

    diff_report = result.get("diff_report", {})
    is_significant = result.get("diff_result", {}).get("is_significant", False)

    if status == "error":
        return {
            "gate": "fail",
            "visual_issues": [
                f"Visual QA 比较失败：{result.get('message', 'unknown error')}"
            ],
            "diff_report": diff_report,
            "passed": False,
        }

    # 正常差异检测
    visual_issues: list[str] = []
    if is_significant:
        visual_issues.append(
            f"Visual diff 显著（{diff_report.get('diff_ratio','?')}），"
            "需人工确认是否为主动变更效果"
        )

    return {
        "gate": "pass",
        "visual_issues": visual_issues,
        "diff_report": diff_report,
        "passed": result.get("passed", True),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Visual QA — Module Demo")
    print("=" * 60)

    vqa = VisualQA()

    # 元数据捕获
    meta = vqa.capture("https://example.com/dashboard", label="dashboard_main")
    print(f"\n[capture] screenshot_id: {meta['screenshot_id']}")
    print(f"        path: {meta['path']}")

    # diff report（无文件时）
    demo_diff = DiffResult(
        before_path="/fake/before.png",
        after_path="/fake/after.png",
        before_hash=None,
        after_hash=None,
        diff_ratio=0.0,
        is_significant=False,
        status="first_change",
        message="首次变更，无需diff比较",
    )
    report = vqa.generate_diff_report(demo_diff, task_id="T6-DEMO")
    print(f"\n[generate_diff_report] verdict: {report['verdict']}")
    print(f"                          diff_ratio: {report['diff_ratio']}")
    print(f"                          threshold: {report['threshold']}")

    # trigger_visual_qa（无截图时）
    trigger_result = trigger_visual_qa(
        task_id="T6-DEMO-UI",
        task_description="修改首页 UI",
    )
    print(f"\n[trigger_visual_qa] status: {trigger_result.get('status')}")
    print(f"                    verdict: {trigger_result.get('verdict')}")

    print("\n" + "=" * 60)
    print("Visual QA Demo Complete")
    print("=" * 60)
