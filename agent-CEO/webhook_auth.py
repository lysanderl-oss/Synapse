"""
Webhook HMAC-SHA256 签名验证库
P0-A2 SEC-P0-1 — 所有 n8n webhook 请求必须通过签名验证
[ADDED: 2026-04-22]
"""

import hmac
import hashlib
import time
import os
from typing import Optional

import yaml


def load_config():
    """从 n8n_integration.yaml 加载 webhook 安全配置"""
    config_path = os.path.join(
        os.path.dirname(__file__), "config", "n8n_integration.yaml"
    )
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def verify_signature(
    request_body: bytes,
    signature_header: Optional[str],
    timestamp_header: Optional[str],
) -> bool:
    """
    验证 HMAC-SHA256 签名，重放攻击防护。

    Args:
        request_body: 原始请求体（bytes）
        signature_header: X-Synapse-Signature header 值，格式：sha256=<hex>
        timestamp_header: X-Synapse-Timestamp header 值，Unix 时间戳（字符串）

    Returns:
        True = 验证通过；False = 验证失败（签名错误或重放攻击）
    """
    config = load_config()
    security = config.get("webhook_security", {})

    secret = security.get("hmac_secret", "")
    tolerance = security.get("timestamp_tolerance_seconds", 300)

    # 1. 参数合法性检查
    if not signature_header or not timestamp_header:
        return False

    # 2. Timestamp 验证 — 防止重放攻击
    try:
        timestamp = int(timestamp_header)
    except (ValueError, TypeError):
        return False

    if abs(time.time() - timestamp) > tolerance:
        # 超过容忍窗口，视为重放攻击
        return False

    # 3. 签名验证 — 使用 timing-safe 比较防止时序攻击
    body_str = request_body.decode() if isinstance(request_body, bytes) else request_body
    expected = "sha256=" + hmac.new(
        secret.encode(),
        f"{timestamp}.{body_str}".encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)


def sign_request(body: bytes) -> tuple[str, str]:
    """
    为出站请求生成 HMAC 签名（供调用方使用）。

    Args:
        body: 请求体（bytes）

    Returns:
        (signature_header, timestamp_header) 元组
    """
    config = load_config()
    secret = config["webhook_security"]["hmac_secret"]
    timestamp = str(int(time.time()))

    body_str = body.decode() if isinstance(body, bytes) else body
    signature = "sha256=" + hmac.new(
        secret.encode(),
        f"{timestamp}.{body_str}".encode(),
        hashlib.sha256,
    ).hexdigest()

    return signature, timestamp


def require_auth(func):
    """
    装饰器：为 Flask/FastAPI 等 Web 框架的路由自动验证签名。

    期望路由函数接收以下 kwargs：
        request_body: bytes
        signature_header: str
        timestamp_header: str

    验证失败时抛出 PermissionError。

    Example (Flask):
        @app.route("/webhook/qa-auto-review", methods=["POST"])
        @require_auth
        def handle_webhook(request_body=None, signature_header=None,
                           timestamp_header=None, **kwargs):
            ...
    """
    def wrapper(*args, **kwargs):
        request_body = kwargs.get("request_body", b"")
        signature_header = kwargs.get("signature_header")
        timestamp_header = kwargs.get("timestamp_header")

        if not verify_signature(request_body, signature_header, timestamp_header):
            raise PermissionError("Webhook signature verification failed")
        return func(*args, **kwargs)
    return wrapper
