"""
Synapse v3.0 — 执行链合规审计模块
dispatch_auditor.py

功能：
1. 生成过去N小时的执行链合规报告
2. 检测违规模式（直接执行/贴标签冒充/先斩后奏/伪派单）
3. 供SessionStart hook调用，自动送达总裁
4. 生成每周审计报告并保存到OBS知识库

使用方法：
  python -X utf8 dispatch_auditor.py --summary   # SessionStart hook用
  python -X utf8 dispatch_auditor.py              # 完整报告
  python -X utf8 dispatch_auditor.py --weekly      # 每周审计报告
  python -X utf8 dispatch_auditor.py --unreported  # 检查新增违规
"""

import re
import os
import sys
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict, field

# ── 路径配置 ──────────────────────────────────────────────────────────────

_SYNAPSE_ROOT = Path(__file__).parent.parent  # 自动解析到 Synapse-Mini
AUDIT_LOG = _SYNAPSE_ROOT / "logs" / "ceo-guard-audit.log"
AUDIT_JSONL = _SYNAPSE_ROOT / "audit" / "ceo_guard.jsonl"
INTERCEPT_LOG = _SYNAPSE_ROOT / "agent-CEO" / "data" / "intercept_log.yaml"
VIOLATION_COUNT_FILE = _SYNAPSE_ROOT / "logs" / "ceo-guard-violation-count.tmp"
LAST_REPORT_TAG = _SYNAPSE_ROOT / "logs" / "last_audit_report_tag.json"

# OBS知识库路径（每周报告保存位置）
OBS_WEEKLY_DIR = _SYNAPSE_ROOT / "obs" / "01-team-knowledge" / "HR" / "weekly-audit"

# 合规工具（主对话允许）
_COMPLIANT_TOOLS = {"Read", "Skill", "Agent", "Glob", "Grep", "Monitor", "TaskStop"}


# ── 数据模型 ────────────────────────────────────────────────────────────────

@dataclass
class ViolationEntry:
    """单条违规记录"""
    timestamp: str
    tool: str
    summary: str
    pattern: str  # shell_direct / edit_direct / write_direct / no_dispatch_log
    session_id: str = ""


@dataclass
class DispatchReport:
    """结构化合规报告"""
    generated_at: str = ""
    period_hours: int = 24
    period_start: str = ""
    period_end: str = ""

    total_tool_calls: int = 0
    violation_count: int = 0
    sessions_with_violations: int = 0
    total_sessions: int = 0

    violations: List[ViolationEntry] = field(default_factory=list)
    compliant_sessions: List[str] = field(default_factory=list)

    # 分组统计
    bash_direct_count: int = 0
    edit_direct_count: int = 0
    write_direct_count: int = 0
    no_dispatch_log_count: int = 0

    # 判定
    is_compliant: bool = True
    risk_level: str = "LOW"  # LOW / MEDIUM / HIGH / CRITICAL
    message: str = ""

    # 附加信息
    intercept_log_found: bool = False
    last_report_timestamp: Optional[str] = None
    unreported_count: int = 0


# ── 核心函数 ───────────────────────────────────────────────────────────────

def generate_violation_report(hours: int = 24, log_path: Optional[str] = None) -> str:
    """生成过去N小时的执行链合规报告（CLI用Markdown格式）"""
    log_file = Path(log_path) if log_path else AUDIT_LOG

    if not log_file.exists():
        return _build_no_log_report(hours)

    cutoff = datetime.now() - timedelta(hours=hours)
    entries = []

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                m = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
                if not m:
                    continue
                ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                if ts < cutoff:
                    continue
                entries.append(line.strip())
    except Exception as e:
        return _build_error_report(str(e))

    if not entries:
        return _build_clean_report(hours)

    pre_bash = [e for e in entries if "PRE" in e and "tool=Bash" in e]
    pre_edit = [e for e in entries if "PRE" in e and "tool=Edit" in e]
    pre_write = [e for e in entries if "PRE" in e and "tool=Write" in e]
    post_entries = [e for e in entries if "POST" in e]

    total_tools = len(entries)
    risk_tools = len(pre_bash) + len(pre_edit) + len(pre_write)

    report_lines = []
    report_lines.append("## CEO-GUARD Compliance Report")
    report_lines.append("")
    report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')} (Dubai Time)")
    report_lines.append(f"**Period**: Last {hours} hours")
    report_lines.append(f"**Audit Log**: `{log_file}`")
    report_lines.append("")
    report_lines.append("### Summary")
    report_lines.append("")
    report_lines.append(f"| Metric | Value |")
    report_lines.append(f"|--------|-------|")
    report_lines.append(f"| Total tool calls | {total_tools} |")
    report_lines.append(f"| High-risk calls (Bash/Edit/Write) | {risk_tools} |")
    report_lines.append(f"| POST confirmations | {len(post_entries)} |")
    report_lines.append("")

    if risk_tools == 0:
        report_lines.append("**Status**: COMPLIANT - No violations in last {hours} hours")
        report_lines.append("")
        report_lines.append("> CEO execution guard active. All Bash/Edit/Write calls went through dispatch authorization.")
    else:
        report_lines.append("**Status**: WARNING - High-risk tool direct calls detected")
        report_lines.append("")

    if pre_bash:
        report_lines.append("#### Bash Calls")
        for e in pre_bash[:20]:
            m = re.search(r"\[(.*?)\].*summary=\"(.*?)\"", e)
            if m:
                report_lines.append(f"- `[{m.group(1)}]` {m.group(2)}")
            else:
                report_lines.append(f"- {e}")
        report_lines.append("")

    if pre_edit:
        report_lines.append("#### Edit Calls")
        for e in pre_edit[:20]:
            m = re.search(r"\[(.*?)\].*summary=\"(.*?)\"", e)
            if m:
                report_lines.append(f"- `[{m.group(1)}]` {m.group(2)}")
        report_lines.append("")

    if pre_write:
        report_lines.append("#### Write Calls")
        for e in pre_write[:20]:
            m = re.search(r"\[(.*?)\].*summary=\"(.*?)\"", e)
            if m:
                report_lines.append(f"- `[{m.group(1)}]` {m.group(2)}")
        report_lines.append("")

    report_lines.append("### Constraint Reference")
    report_lines.append("")
    report_lines.append("| Tool | Lysander Main | Sub-Agent |")
    report_lines.append("|------|--------------|-----------|")
    report_lines.append("| Bash/Edit/Write | BLOCKED (need dispatch) | OK |")
    report_lines.append("| Read/Skill/Agent/Glob/Grep | OK | OK |")
    report_lines.append("")
    report_lines.append("---\n*Auto-generated by dispatch_auditor.py - CEO-GUARD Compliance Audit*\n")

    return "\n".join(report_lines)


def generate_violation_summary(hours: int = 24) -> str:
    """生成违规摘要（短格式，用于SessionStart hook输出，ASCII-safe）"""
    log_file = AUDIT_LOG

    if not log_file.exists():
        return "CEO-GUARD: No audit log (first use, confirm hooks active)"

    cutoff = datetime.now() - timedelta(hours=hours)

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if "PRE" in l and
                     ("tool=Bash" in l or "tool=Edit" in l or "tool=Write" in l)]

        recent = []
        for line in lines:
            m = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
            if m:
                ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                if ts >= cutoff:
                    recent.append(line)

    except Exception:
        return "CEO-GUARD: Audit log read error"

    count = len(recent)

    if count == 0:
        return f"CEO-GUARD: No violations in last {hours}h"
    else:
        return f"CEO-GUARD: WARNING - {count} high-risk tool direct call(s) detected"


def generate_dispatch_violation_report(period_hours: int = 24) -> DispatchReport:
    """生成结构化合规报告（内部使用）

    Returns:
        DispatchReport 数据对象，包含所有分析结果
    """
    report = DispatchReport(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        period_hours=period_hours,
        period_start=(datetime.now() - timedelta(hours=period_hours)).strftime("%Y-%m-%d %H:%M:%S"),
        period_end=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    log_file = AUDIT_LOG

    # 检查上次报告时间戳
    if LAST_REPORT_TAG.exists():
        try:
            tag_data = json.loads(LAST_REPORT_TAG.read_text(encoding="utf-8"))
            report.last_report_timestamp = tag_data.get("last_report_at", None)
        except Exception:
            pass

    if not log_file.exists():
        report.message = "Audit log not found"
        report.is_compliant = False
        report.risk_level = "UNKNOWN"
        return report

    cutoff = datetime.now() - timedelta(hours=period_hours)

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            all_lines = [l.strip() for l in f]
    except Exception as e:
        report.message = f"Failed to read audit log: {e}"
        report.is_compliant = False
        report.risk_level = "ERROR"
        return report

    # 解析所有条目
    for line in all_lines:
        m = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
        if not m:
            continue
        ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        if ts < cutoff:
            continue

        report.total_tool_calls += 1

        if "PRE" in line and "tool=Bash" in line:
            report.bash_direct_count += 1
            sm = re.search(r'summary="([^"]*)"', line)
            report.violations.append(ViolationEntry(
                timestamp=m.group(1),
                tool="Bash",
                summary=sm.group(1) if sm else "(no summary)",
                pattern="shell_direct"
            ))
        elif "PRE" in line and "tool=Edit" in line:
            report.edit_direct_count += 1
            sm = re.search(r'summary="([^"]*)"', line)
            report.violations.append(ViolationEntry(
                timestamp=m.group(1),
                tool="Edit",
                summary=sm.group(1) if sm else "(no summary)",
                pattern="edit_direct"
            ))
        elif "PRE" in line and "tool=Write" in line:
            report.write_direct_count += 1
            sm = re.search(r'summary="([^"]*)"', line)
            report.violations.append(ViolationEntry(
                timestamp=m.group(1),
                tool="Write",
                summary=sm.group(1) if sm else "(no summary)",
                pattern="write_direct"
            ))

    report.violation_count = len(report.violations)
    report.is_compliant = (report.violation_count == 0)
    report.sessions_with_violations = len(set(v.session_id for v in report.violations if v.session_id))

    # 检查intercept_log
    if INTERCEPT_LOG.exists():
        report.intercept_log_found = True

    # 检查未报告新增违规
    if report.last_report_timestamp and report.last_report_timestamp != "":
        try:
            last_ts = datetime.strptime(report.last_report_timestamp, "%Y-%m-%d %H:%M:%S")
            report.unreported_count = sum(
                1 for v in report.violations
                if datetime.strptime(v.timestamp, "%Y-%m-%d %H:%M:%S") > last_ts
            )
        except Exception:
            pass

    # 判定风险级别
    if report.violation_count == 0:
        report.risk_level = "LOW"
        report.message = f"No violations in last {period_hours}h"
    elif report.violation_count <= 2:
        report.risk_level = "MEDIUM"
        report.message = f"{report.violation_count} violation(s) detected - check report"
    elif report.violation_count <= 5:
        report.risk_level = "HIGH"
        report.message = f"{report.violation_count} violations - immediate review required"
    else:
        report.risk_level = "CRITICAL"
        report.message = f"{report.violation_count} violations - CEO escalation required"

    return report


def check_unreported_violations() -> Dict:
    """检查上次报告后新增违规

    Returns:
        dict with keys: new_count, new_violations, last_report_at, status
    """
    result = {
        "new_count": 0,
        "new_violations": [],
        "last_report_at": None,
        "status": "unknown"
    }

    if not LAST_REPORT_TAG.exists():
        result["status"] = "no_previous_report"
        return result

    try:
        tag_data = json.loads(LAST_REPORT_TAG.read_text(encoding="utf-8"))
        last_ts_str = tag_data.get("last_report_at", None)
        if not last_ts_str:
            result["status"] = "missing_timestamp"
            return result

        result["last_report_at"] = last_ts_str
        last_ts = datetime.strptime(last_ts_str, "%Y-%m-%d %H:%M:%S")

        # 读取audit log找新增违规
        if not AUDIT_LOG.exists():
            result["status"] = "no_audit_log"
            return result

        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                m = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
                if not m:
                    continue
                ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                if ts <= last_ts:
                    continue
                if "PRE" in line and ("tool=Bash" in line or "tool=Edit" in line or "tool=Write" in line):
                    sm = re.search(r'summary="([^"]*)"', line)
                    result["new_violations"].append({
                        "timestamp": m.group(1),
                        "tool": "Bash" if "tool=Bash" in line else ("Edit" if "tool=Edit" in line else "Write"),
                        "summary": sm.group(1) if sm else "(no summary)"
                    })
                    result["new_count"] += 1

        result["status"] = "checked"
        return result

    except Exception as e:
        result["status"] = f"error: {e}"
        return result


def render_report_text(report: DispatchReport) -> str:
    """将结构化报告渲染为可读文本（用于终端/hook输出，ASCII-safe）"""
    lines = []
    lines.append("=" * 56)
    lines.append(" CEO-GUARD Compliance Report")
    lines.append("=" * 56)
    lines.append(f" Generated : {report.generated_at}")
    lines.append(f" Period    : Last {report.period_hours}h ({report.period_start} -> {report.period_end})")
    lines.append(f" Status    : {'[OK] Compliant' if report.is_compliant else '[!!] Violation detected'}")
    lines.append(f" Risk      : {report.risk_level}")
    lines.append("")
    lines.append("--- Counts ---")
    lines.append(f"  Total tool calls    : {report.total_tool_calls}")
    lines.append(f"  Bash direct        : {report.bash_direct_count}")
    lines.append(f"  Edit direct        : {report.edit_direct_count}")
    lines.append(f"  Write direct       : {report.write_direct_count}")
    lines.append(f"  Violations         : {report.violation_count}")

    if report.violation_count > 0:
        lines.append("")
        lines.append("--- Violations ---")
        for v in report.violations[:10]:
            lines.append(f"  [{v.timestamp}] {v.tool}: {v.summary[:60]}")
        if len(report.violations) > 10:
            lines.append(f"  ... and {len(report.violations) - 10} more")

    lines.append("")
    lines.append(f" Message: {report.message}")
    lines.append("=" * 56)
    return "\n".join(lines)


def render_session_start_reminder() -> str:
    """返回SessionStart提醒文本（如果无违规返回空字符串）

    优先用 check_unreported_violations() 检测新增违规，
    无上次记录时降级使用 generate_violation_summary()。
    """
    result = check_unreported_violations()

    if result["status"] == "no_previous_report":
        # 首次运行，返回简洁确认
        return ""

    if result["status"] not in ("checked", "no_previous_report"):
        # 出错了，返回警告
        return f"CEO-GUARD: Audit status unknown ({result['status']})"

    if result["new_count"] > 0:
        return (f"CEO-GUARD: WARNING - {result['new_count']} new violation(s) "
                f"since last report ({result.get('last_report_at', 'unknown')})")

    return ""


def get_violation_session_counts() -> Dict:
    """读取违规计数（供外部调用）

    Returns:
        dict with counts by session
    """
    result = {
        "total_violations": 0,
        "sessions": {},
        "last_24h_count": 0
    }

    if not AUDIT_LOG.exists():
        return result

    cutoff = datetime.now() - timedelta(hours=24)
    session_counts: Dict[str, int] = {}

    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                if "PRE" not in line:
                    continue
                if not ("tool=Bash" in line or "tool=Edit" in line or "tool=Write" in line):
                    continue

                m = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
                if not m:
                    continue

                ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                result["total_violations"] += 1

                if ts >= cutoff:
                    result["last_24h_count"] += 1

                # 从session标签提取session_id（如果有）
                sm = re.search(r'session[_\-]?id["\s:=]+([^\s"\']+)', line, re.IGNORECASE)
                if sm:
                    sid = sm.group(1)[:16]
                    session_counts[sid] = session_counts.get(sid, 0) + 1

        result["sessions"] = session_counts
        return result

    except Exception as e:
        result["error"] = str(e)
        return result


def _get_facts_audit_summary() -> str:
    """Run scripts/audit_facts.py and capture last 2KB of output for weekly report.

    Failure-tolerant: if the script is missing or errors, returns a marker line
    so the weekly report still generates.
    """
    import subprocess
    facts_script = _SYNAPSE_ROOT / "scripts" / "audit_facts.py"
    if not facts_script.exists():
        return f"[fact-audit] script not found: {facts_script}"
    try:
        result = subprocess.run(
            [sys.executable, str(facts_script)],
            capture_output=True, text=True,
            cwd=str(_SYNAPSE_ROOT), timeout=120,
            encoding="utf-8", errors="replace"
        )
        out = result.stdout or ""
        err = result.stderr or ""
        combined = out + ("\n--- stderr ---\n" + err if err.strip() else "")
        if not combined.strip():
            return f"[fact-audit] no output (exit={result.returncode})"
        # Trim to last 2000 chars to avoid bloating the weekly report
        return combined[-2000:].strip()
    except subprocess.TimeoutExpired:
        return "[fact-audit] timed out after 120s"
    except Exception as e:
        return f"[fact-audit] error: {type(e).__name__}: {e}"


def generate_weekly_audit_report() -> Dict:
    """生成每周审计报告并保存到OBS知识库

    Returns:
        dict with keys: success, report_path, summary
    """
    result = {
        "success": False,
        "report_path": "",
        "summary": ""
    }

    # 创建OBS目录（如果不存在）
    OBS_WEEKLY_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    # 计算本周一
    week_start = now - timedelta(days=now.weekday())
    week_label = week_start.strftime("%Y-W%W")

    report_file = OBS_WEEKLY_DIR / f"week-audit-{week_label}.md"

    # 生成过去7天的报告
    cutoff = now - timedelta(days=7)

    violations = []
    sessions = {}
    total_calls = 0

    if AUDIT_LOG.exists():
        try:
            with open(AUDIT_LOG, "r", encoding="utf-8") as f:
                for line in f:
                    m = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
                    if not m:
                        continue
                    ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                    if ts < cutoff:
                        continue

                    if "PRE" not in line:
                        total_calls += 1
                        continue

                    if not ("tool=Bash" in line or "tool=Edit" in line or "tool=Write" in line):
                        total_calls += 1
                        continue

                    sm = re.search(r'summary="([^"]*)"', line)
                    tool = "Bash" if "tool=Bash" in line else ("Edit" if "tool=Edit" in line else "Write")
                    violations.append({
                        "timestamp": m.group(1),
                        "tool": tool,
                        "summary": sm.group(1) if sm else ""
                    })
                    total_calls += 1
        except Exception as e:
            result["summary"] = f"Error reading audit log: {e}"
            return result

    violation_count = len(violations)
    unique_sessions = len(set(v.get("timestamp", "")[:10] for v in violations))

    # 生成Markdown报告
    md_lines = []
    md_lines.append(f"# Weekly Audit Report — {week_label}")
    md_lines.append("")
    md_lines.append(f"**Generated**: {now.strftime('%Y-%m-%d %H:%M')} (Dubai Time)")
    md_lines.append(f"**Period**: {cutoff.strftime('%Y-%m-%d')} → {now.strftime('%Y-%m-%d')}")
    md_lines.append("")
    md_lines.append("## Executive Summary")
    md_lines.append("")
    md_lines.append(f"| Metric | Value |")
    md_lines.append(f"|--------|-------|")
    md_lines.append(f"| Period | {week_label} |")
    md_lines.append(f"| Total tool calls | {total_calls} |")
    md_lines.append(f"| Violations detected | {violation_count} |")
    md_lines.append(f"| Unique sessions with violations | {unique_sessions} |")
    md_lines.append("")

    if violation_count == 0:
        md_lines.append("**Status**: FULL COMPLIANCE — No violations this week.")
        md_lines.append("")
        md_lines.append("All Bash/Edit/Write calls in Lysander main dialogue went through proper dispatch authorization.")
    else:
        md_lines.append(f"**Status**: ATTENTION REQUIRED — {violation_count} violation(s) detected.")
        md_lines.append("")
        md_lines.append("### Violation Breakdown")
        md_lines.append("")
        bash_v = [v for v in violations if v["tool"] == "Bash"]
        edit_v = [v for v in violations if v["tool"] == "Edit"]
        write_v = [v for v in violations if v["tool"] == "Write"]
        md_lines.append(f"- Bash direct calls: {len(bash_v)}")
        md_lines.append(f"- Edit direct calls: {len(edit_v)}")
        md_lines.append(f"- Write direct calls: {len(write_v)}")
        md_lines.append("")
        md_lines.append("### Violation Details")
        md_lines.append("")
        for v in violations:
            md_lines.append(f"- `[{v['timestamp']}]` [{v['tool']}] {v['summary'][:80]}")
        md_lines.append("")

    md_lines.append("## Audit Mechanism")
    md_lines.append("")
    md_lines.append("- **Audit log**: `logs/ceo-guard-audit.log`")
    md_lines.append("- **Violation patterns**: direct Bash/Edit/Write in Lysander main dialogue")
    md_lines.append("- **Compliance rule**: All execution operations must go through Agent/Skill dispatch to team members")
    md_lines.append("")

    # ── Fact-SSOT Drift section (audit_facts.py) ─────────────────────────
    md_lines.append("## Fact-SSOT Drift")
    md_lines.append("")
    md_lines.append("Cross-checks fact references in obs/ + CLAUDE.md against canonical SSOT.")
    md_lines.append("Baseline: ~184 drift items (2026-04 snapshot). Track week-over-week trend.")
    md_lines.append("")
    md_lines.append("```")
    md_lines.append(_get_facts_audit_summary())
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("*Auto-generated by dispatch_auditor.py - CEO-GUARD Weekly Audit*")

    content = "\n".join(md_lines)

    try:
        report_file.write_text(content, encoding="utf-8")
        result["success"] = True
        result["report_path"] = str(report_file)

        # 更新last_report_tag
        try:
            LAST_REPORT_TAG.write_text(
                json.dumps({"last_report_at": now.strftime("%Y-%m-%d %H:%M:%S")}, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass

        result["summary"] = (
            f"Week {week_label}: {violation_count} violation(s), {total_calls} tool calls, "
            f"{unique_sessions} session(s) affected"
        )
        return result

    except Exception as e:
        result["summary"] = f"Failed to write report: {e}"
        return result


# ── 内部辅助函数 ─────────────────────────────────────────────────────────

def _build_no_log_report(hours: int) -> str:
    return (
        f"## CEO-GUARD Compliance Report\n\n"
        f"**Period**: Last {hours} hours\n\n"
        "> Audit log not found (`logs/ceo-guard-audit.log`).\n"
        "> Possible reasons:\n"
        "> 1. Hooks not triggered yet (first use)\n"
        "> 2. Incorrect log path\n\n"
        "> **Verify**: Run any Bash command in Claude Code and check if log is generated\n\n"
        "---\n*Auto-generated by dispatch_auditor.py*\n"
    )


def _build_error_report(error: str) -> str:
    return (
        "## CEO-GUARD Compliance Report - Read Error\n\n"
        f"Error: {error}\n\n"
        "---\n*Auto-generated by dispatch_auditor.py*\n"
    )


def _build_clean_report(hours: int) -> str:
    return (
        f"## CEO-GUARD Compliance Report\n\n"
        f"**Period**: Last {hours} hours\n\n"
        f"**Status**: No violations recorded - Execution chain compliant\n\n"
        "> CEO execution guard active. All Bash/Edit/Write calls went through dispatch authorization.\n\n"
        "---\n*Auto-generated by dispatch_auditor.py - CEO-GUARD Compliance Audit*\n"
    )


# ── CLI入口 ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    hours = 24

    # 解析参数
    if "--weekly" in sys.argv:
        # 生成每周报告
        result = generate_weekly_audit_report()
        if result["success"]:
            print(f"Weekly audit report generated: {result['report_path']}")
            print(f"Summary: {result['summary']}")
        else:
            print(f"Failed: {result['summary']}")
        sys.exit(0 if result["success"] else 1)

    elif "--summary" in sys.argv:
        # 短格式输出（用于hook）
        print(generate_violation_summary(hours))
        sys.exit(0)

    elif "--unreported" in sys.argv:
        # 检查新增违规
        result = check_unreported_violations()
        if result["status"] == "checked":
            print(f"New violations since last report: {result['new_count']}")
            for v in result["new_violations"]:
                print(f"  [{v['timestamp']}] {v['tool']}: {v['summary'][:60]}")
        else:
            print(f"Status: {result['status']}")
        sys.exit(0)

    elif "--text" in sys.argv:
        # 结构化文本报告
        report = generate_dispatch_violation_report(hours)
        print(render_report_text(report))
        sys.exit(0)

    elif len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except ValueError:
            pass

    # 默认：完整Markdown报告
    print(generate_violation_report(hours))