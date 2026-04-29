"""
心跳监控脚本 — Q2 情报管线
每日 Dubai 11:00（UTC 07:00）运行，检查前一天的情报产出完整性。

避免情报管线再次像 2026-04-21 那样静默停摆 3 天无人发现。

健康判定：
    - intelligence-daily.html 存在 + 大小 > 100 字节
    - action-report.md 存在 + 大小 > 100 字节

失败 → exit 1（GH Actions 标记红）+ Slack 告警（复用 WF-09 Unified Notification (atit1zW3VYUL54CJ)）。
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "obs" / "06-daily-reports"


def check_heartbeat(days_back: int = 1) -> dict:
    """检查前 days_back 天的产出文件。

    Args:
        days_back: 回溯天数（默认 1 天 = 昨天）。

    Returns:
        {
            "target_date": "YYYY-MM-DD",
            "check_at": ISO timestamp,
            "missing": [...],
            "present": [...],
            "healthy": bool,
        }
    """
    now = datetime.now(timezone.utc)
    target_date = (now - timedelta(days=days_back)).strftime("%Y-%m-%d")

    expected = {
        "intelligence_daily": REPORTS_DIR / f"{target_date}-intelligence-daily.html",
        "action_report": REPORTS_DIR / f"{target_date}-action-report.md",
    }

    result = {
        "target_date": target_date,
        "check_at": now.isoformat(),
        "missing": [],
        "present": [],
    }

    for name, path in expected.items():
        if path.exists() and path.stat().st_size > 100:
            result["present"].append(name)
        else:
            result["missing"].append(name)

    result["healthy"] = len(result["missing"]) == 0
    return result


def _notify_slack_minimal(webhook_url: str, message: str, healthy: bool = True) -> bool:
    """轻量 Slack 通知（仅依赖 requests，不触发 shared_context 的 anthropic 顶层导入）。

    复用 Synapse 统一 notification 通道（WF-09 Unified Notification (atit1zW3VYUL54CJ)）。

    WF-09 payload contract（Parse Recipient 节点）：
        - recipient: 'president' → 总裁 DM (U0ASLJZMVDE)
        - title:     消息标题（Slack *bold*）
        - body:      正文
        - source:    来源标识（出现在 footer）
        - priority:  P0/P1/P2/P3
        - signature/timestamp: 可选 HMAC 验证（未提供则跳过）
    """
    import requests
    title = "情报管线心跳告警" if not healthy else "情报管线心跳"
    priority = "P1" if not healthy else "P3"
    payload = {
        "recipient": "president",
        "title": title,
        "body": message[:1800],
        "source": "heartbeat-check",
        "priority": priority,
    }
    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
        )
        body_text = resp.text or ""
        # 同时要求 Slack API 层面 ok:true（避免 HTTP 200 但 Slack API 失败的假阳性）
        http_ok = 200 <= resp.status_code < 300
        slack_ok = '"ok":true' in body_text.lower().replace(' ', '')
        ok = http_ok and slack_ok
        preview = body_text[:200]
        print(
            f"[Slack] status={resp.status_code} http_ok={http_ok} slack_ok={slack_ok} body_preview={preview!r}",
            flush=True,
        )
        return ok
    except requests.exceptions.Timeout:
        print("[Slack] Timeout", flush=True)
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"[Slack] ConnectionError: {e}", flush=True)
        return False
    except Exception as e:
        print(f"[Slack] Error: {e}", flush=True)
        return False


def main():
    import json
    result = check_heartbeat(days_back=1)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)

    # Slack 通知（直接用 requests，不引入 shared_context 以避免 anthropic 依赖）
    webhook = os.environ.get("SLACK_WEBHOOK_N8N")
    if result["healthy"]:
        msg = (
            f"[心跳] {result['target_date']} 情报管线健康："
            f"intelligence_daily + action_report 均生成"
        )
    else:
        missing = ", ".join(result["missing"])
        msg = (
            f"[心跳告警] {result['target_date']} 缺失：{missing}"
            f"（可能情报管线停摆）"
        )

    if webhook:
        success = _notify_slack_minimal(webhook, msg, healthy=result["healthy"])
        print(f"[Notify] Slack {'OK' if success else 'FAILED'}", flush=True)
    else:
        print("[Notify] SLACK_WEBHOOK_N8N not set; skipped", flush=True)

    # 如不健康，exit 非零以让 GH Actions 标记失败
    sys.exit(0 if result["healthy"] else 1)


if __name__ == "__main__":
    main()
