"""
dispatch_weekly_audit.py

每周定时任务脚本 — 调用 dispatch_auditor.generate_weekly_audit_report()
保存每周审计报告到 OBS 知识库。

用法（无参数）：
  python -X utf8 dispatch_weekly_audit.py

用法（指定路径）：
  python -X utf8 dispatch_weekly_audit.py --output ./obs/01-team-knowledge/HR/weekly-audit

触发方式（n8n cron 或 Windows Task Scheduler）：
  每周一 09:00 Dubai Time
  命令: python -X utf8 "C:/Users/lysanderl_janusd/Synapse-Mini/agent-CEO/dispatch_weekly_audit.py"

输出：
  - 生成 obs/01-team-knowledge/HR/weekly-audit/week-audit-YYYY-WXX.md
  - 打印报告路径到 stdout
"""

import sys
import os
from pathlib import Path

# 确保 UTF-8 输出（Windows 默认 cp1252 会导致中文/emoji乱码）
# main dialogue 中的 print() 同样需要 -X utf8 标志才能避免编码错误
# 此脚本作为独立 cron 进程，确保编码正确
if sys.stdout.encoding != "utf-8":
    os.environ["PYTHONIOENCODING"] = "utf-8"

_SYNAPSE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_SYNAPSE_ROOT / "agent-CEO"))

from dispatch_auditor import generate_weekly_audit_report


def main():
    output_dir_arg = None

    # 解析可选参数 --output <dir>
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if len(sys.argv) > idx + 1:
            output_dir_arg = sys.argv[idx + 1]

    # 如有指定输出目录，覆盖 OBS_WEEKLY_DIR
    # （generate_weekly_audit_report 内部使用 OBS_WEEKLY_DIR，
    #  若需要外部指定，可通过环境变量 OBS_WEEKLY_AUDIT_DIR 传递）
    if output_dir_arg:
        os.environ["OBS_WEEKLY_AUDIT_DIR"] = str(Path(output_dir_arg).resolve())

    print("=" * 56)
    print(" CEO-GUARD Weekly Audit")
    print("=" * 56)
    print(f" Root: {_SYNAPSE_ROOT}")
    print(f" Time: (Dubai Time)")
    print("")

    result = generate_weekly_audit_report()

    if result["success"]:
        print(f" SUCCESS")
        print(f" Report : {result['report_path']}")
        print(f" Summary: {result['summary']}")
        print("=" * 56)
        return 0
    else:
        print(f" FAILED: {result['summary']}")
        print("=" * 56)
        return 1


if __name__ == "__main__":
    sys.exit(main())