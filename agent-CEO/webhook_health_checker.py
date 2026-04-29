"""
webhook_health_checker.py — n8n Webhook 健康检查自动化
Synapse v3.0 — P1-5 任务交付物
==============================================================
功能：
  - 单个 webhook 健康检查（GET + HMAC-SHA256 签名）
  - 批量检查所有已配置 endpoint
  - UNHEALTHY 状态持续 3 次触发 Slack 告警
  - 日志持久化（logs/webhook_health/）
==============================================================
用法：
  python agent-CEO/webhook_health_checker.py        # 批量检查
  from agent_CEO.webhook_health_checker import WebhookHealthChecker
  checker = WebhookHealthChecker()
  status, ms, err = checker.check_webhook_health("intelligence-action", "https://...")
"""

import os
import time
import json
import hmac
import hashlib
import logging
import requests
import yaml
from datetime import datetime, timezone
from pathlib import Path

# ── 路径配置 ──────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent.parent.resolve()          # Synapse-Mini/
CONFIG_DIR    = BASE_DIR / "agent-CEO" / "config"
LOG_DIR       = BASE_DIR / "agent-CEO" / "logs" / "webhook_health"
STATE_FILE    = LOG_DIR / "failure_state.json"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# ── 日志配置 ──────────────────────────────────────────────
logger = logging.getLogger("webhook_health_checker")
logger.setLevel(logging.INFO)
_handler = logging.FileHandler(LOG_DIR / f"health_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(_handler)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(console)


# ── 状态持久化（failure_count） ─────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii_entry=False, indent=2), encoding="utf-8")


# ── HMAC 签名 ─────────────────────────────────────────────
def build_signature(payload_bytes: bytes, hmac_secret: str, timestamp: str) -> str:
    """生成 X-Synapse-Signature: syn1:<hmac_sha256(timestamp + "." + payload)>"""
    msg = f"{timestamp}.".encode() + payload_bytes
    sig = hmac.new(hmac_secret.encode(), msg, hashlib.sha256).hexdigest()
    return f"syn1:{sig}"


class WebhookHealthChecker:
    """
    n8n Webhook 健康检查器

    主要方法：
      check_webhook_health(name, url) -> (status, response_time_ms, last_error)
      batch_check()                   -> list[dict]  (所有 endpoint 检查结果)
    """

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = str(CONFIG_DIR / "webhook_health_config.yaml")
        self.config = self._load_config(config_path)
        self.security = self._load_security()
        self._n8n_webhook_url = None   # 延迟加载：按需从 n8n_integration.yaml 读取

    # ── 配置加载 ─────────────────────────────────────────
    def _load_config(self, path: str) -> dict:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_security(self) -> dict:
        n8n_cfg = CONFIG_DIR / "n8n_integration.yaml"
        with open(n8n_cfg, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("webhook_security", {})

    def _get_n8n_webhook_url(self) -> str | None:
        """
        从 n8n_integration.yaml 读取统一的告警 webhook URL。
        按以下优先级查找：
          1. notifications.slack.webhook_url
          2. notifications.slack.unified_webhook_url
          3. execution_chain_triggers.action_completed.webhook_url（action-notify）
        找不到则返回 None，触发降级日志。
        """
        if self._n8n_webhook_url is not None:
            return self._n8n_webhook_url

        n8n_cfg = CONFIG_DIR / "n8n_integration.yaml"
        try:
            with open(n8n_cfg, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # 优先级1：notifications.slack 下是否有统一 webhook
            notif = data.get("notifications", {})
            slack_cfg = notif.get("slack", {})
            url = slack_cfg.get("webhook_url") or slack_cfg.get("unified_webhook_url")
            if url:
                self._n8n_webhook_url = url.strip()
                return self._n8n_webhook_url

            # 优先级2：action_completed 的 action-notify webhook
            triggers = data.get("execution_chain_triggers", {})
            action_done = triggers.get("action_completed", {})
            url = action_done.get("webhook_url")
            if url:
                self._n8n_webhook_url = url.strip()
                return self._n8n_webhook_url

        except Exception as e:
            logger.warning(f"读取 n8n_integration.yaml 失败: {e}")

        self._n8n_webhook_url = None
        return None

    def _write_local_alert_log(self, message: str) -> None:
        """
        降级方案：无 n8n webhook URL 时，将告警消息追加写入本地告警日志。
        日志路径：logs/webhook_health/alert_log.txt
        """
        log_path = LOG_DIR / "alert_log.txt"
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
            logger.warning(f"[降级日志] 告警已写入本地: {log_path}")
        except Exception as e:
            logger.error(f"[降级日志] 写入失败: {e}")


    # ── 核心检查方法 ─────────────────────────────────────
    def check_webhook_health(self, webhook_name: str, webhook_url: str) -> tuple:
        """
        检查单个 webhook 健康状态。

        Returns:
            (status: str, response_time_ms: float, last_error: str|None)
            status: "HEALTHY" | "UNHEALTHY" | "TIMEOUT" | "NETWORK_ERROR"
        """
        timestamp = str(int(time.time()))
        body = b""   # GET 请求 body 为空

        # 构造 HMAC 签名 header（n8n_integration.yaml 中定义的 key）
        hmac_secret = self.security.get("hmac_secret", "")
        if hmac_secret:
            sig = build_signature(body, hmac_secret, timestamp)
            headers = {
                self.security.get("sign_header", "X-Synapse-Signature"): sig,
                self.security.get("timestamp_header", "X-Synapse-Timestamp"): timestamp,
                "User-Agent": "Synapse-HealthChecker/v3.0",
            }
        else:
            headers = {"User-Agent": "Synapse-HealthChecker/v3.0"}

        timeout = self.config.get("timeout_seconds", 5)
        start = time.perf_counter()
        try:
            response = requests.get(webhook_url, headers=headers, timeout=timeout)
            elapsed_ms = (time.perf_counter() - start) * 1000

            if response.status_code == 200:
                logger.info(f"✅ [{webhook_name}] 200 OK — {elapsed_ms:.0f}ms")
                return ("HEALTHY", round(elapsed_ms, 1), None)

            elif response.status_code == 404:
                # n8n 未激活 webhook 返回 404（需手动触发一次）
                logger.warning(f"⚠️  [{webhook_name}] 404 未激活 — {elapsed_ms:.0f}ms")
                return ("UNHEALTHY", round(elapsed_ms, 1), "404: webhook 未激活（从未被调用过）")

            elif response.status_code == 402:
                # n8n 需要认证，webhook 存在但需要凭证
                logger.warning(f"⚠️  [{webhook_name}] 402 需要认证 — {elapsed_ms:.0f}ms")
                return ("UNHEALTHY", round(elapsed_ms, 1), "402: webhook 需要认证")

            else:
                logger.warning(f"⚠️  [{webhook_name}] HTTP {response.status_code} — {elapsed_ms:.0f}ms")
                return ("UNHEALTHY", round(elapsed_ms, 1), f"HTTP {response.status_code}")

        except requests.Timeout:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(f"⏱️  [{webhook_name}] 超时（>{timeout}s）")
            return ("TIMEOUT", round(elapsed_ms, 1), f"请求超时（>{timeout}s）")

        except requests.RequestException as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(f"❌ [{webhook_name}] 网络错误: {e}")
            return ("NETWORK_ERROR", round(elapsed_ms, 1), str(e))

    # ── 批量检查 + Slack 告警 ─────────────────────────────
    def batch_check(self) -> list[dict]:
        """
        检查所有 monitored_endpoints，返回结果列表。
        连续 3 次 UNHEALTHY 触发 Slack 告警。
        """
        results = []
        endpoints = self.config.get("monitored_endpoints", [])

        logger.info(f"═══ 批量健康检查开始 — {len(endpoints)} 个 endpoint ═══")

        for ep in endpoints:
            name = ep.get("name", "unknown")
            url  = ep.get("url", "")
            if not url:
                continue

            status, ms, err = self.check_webhook_health(name, url)
            record = {"name": name, "url": url, "status": status,
                      "response_time_ms": ms, "last_error": err,
                      "checked_at": datetime.now(timezone.utc).isoformat()}
            results.append(record)

            # 更新 failure_count
            state = load_state()
            if status == "HEALTHY":
                state[name] = 0   # 重置计数
            else:
                state[name] = state.get(name, 0) + 1

            failure_count = state[name]
            save_state(state)

            # 告警阈值判断
            threshold = self.config.get("alert_threshold", 3)
            if failure_count >= threshold:
                self._trigger_slack_alert(name, url, status, err, failure_count)

        # 汇总日志
        healthy = sum(1 for r in results if r["status"] == "HEALTHY")
        logger.info(f"═══ 批量检查完成 — ✅{healthy}/{len(results)} 健康 ═══")

        # 保存本次结果
        report_path = LOG_DIR / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.write_text(json.dumps(results, ensure_ascii_entry=False, indent=2), encoding="utf-8")
        logger.info(f"报告已保存: {report_path}")

        return results

    # ── Slack 告警 ─────────────────────────────────────────
    def _trigger_slack_alert(self, webhook_name: str, url: str,
                              status: str, error: str, failure_count: int) -> None:
        """
        通过 n8n webhook 统一入口触发 Slack Bot 告警。
        复用 n8n_integration.yaml 中已配置的 Slack Bot Credentials。
        无 n8n webhook URL 时降级写入本地告警日志。
        """
        n8n_webhook_url = self._get_n8n_webhook_url()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emoji = "🚨" if failure_count >= 3 else "⚠️"
        msg_lines = [
            f"{emoji} *Synapse Webhook 健康告警*",
            f"> webhook名称: `{webhook_name}`",
            f"> 当前状态: `{status}`",
            f"> 连续失败: `{failure_count}` 次",
            f"> 错误信息: `{error}`",
            f"> URL: <{url}|{webhook_name}>",
            f"> 告警时间: `{timestamp}`",
            "",
            "_自动触发: n8n Webhook Health Checker_",
        ]
        message = "\n".join(msg_lines)

        if n8n_webhook_url:
            try:
                resp = requests.post(
                    n8n_webhook_url,
                    json={
                        "alert_type": "webhook_health",
                        "message": message,
                        "webhook_name": webhook_name,
                        "url": url,
                        "status": status,
                        "error": error,
                        "failure_count": failure_count,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    logger.info(f"n8n 告警已发送（Slack Bot）: {webhook_name}")
                else:
                    logger.warning(f"n8n 告警发送失败({resp.status_code}): {webhook_name}，降级写入本地日志")
                    self._write_local_alert_log(message)
            except Exception as e:
                logger.error(f"n8n 告警异常: {e}，降级写入本地日志")
                self._write_local_alert_log(message)
        else:
            # 无 n8n webhook URL，降级写入本地日志供人工巡查
            fallback_msg = (
                f"[ALERT-FALLBACK] {emoji} {webhook_name} 连续 {failure_count} 次失败 "
                f"（未找到 n8n webhook URL）— 请检查: {url}"
            )
            logger.warning(fallback_msg)
            self._write_local_alert_log(message)


# ── CLI 入口 ──────────────────────────────────────────────
if __name__ == "__main__":
    checker = WebhookHealthChecker()
    results = checker.batch_check()

    # 打印摘要到 stdout
    for r in results:
        icon = {"HEALTHY": "✅", "UNHEALTHY": "⚠️", "TIMEOUT": "⏱️", "NETWORK_ERROR": "❌"}.get(r["status"], "?")
        err_str = f" | {r['last_error']}" if r["last_error"] else ""
        print(f"{icon} {r['name']:<35} {r['status']:<12} {r['response_time_ms']:>7.0f}ms{err_str}")