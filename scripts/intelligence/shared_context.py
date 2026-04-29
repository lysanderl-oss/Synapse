"""
共享上下文和工具函数 — Q2 情报管线 Week 1

职责：
    1. 统一路径常量（REPO_ROOT / prompts / templates / reports）
    2. 加载 prompt / CLAUDE.md / active_tasks.yaml 等上下文文件
    3. 封装 Claude API 调用（含 prompt caching + task_budget + 指数退避）
    4. Slack 通知（复用 n8n webhook，不新增 channel）

依赖：
    - anthropic>=0.40（官方 Python SDK）
    - jinja2>=3
    - pyyaml
    - requests

环境变量：
    - ANTHROPIC_API_KEY   (必需，GitHub Secrets 注入)
    - SLACK_WEBHOOK_N8N   (可选，Slack 通知用)
    - NOTION_TOKEN        (可选，Registry 读取)
    - N8N_API_KEY         (可选，n8n 触发)

注意：不得 commit 任何 API Key；仅从 os.environ 读取。
"""
from __future__ import annotations

import os
import time
import json
from pathlib import Path
from typing import Any, Callable, Optional, Union

try:
    from anthropic import Anthropic
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "anthropic SDK 未安装。请 `pip install anthropic>=0.40`"
    ) from exc


# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------

# scripts/intelligence/shared_context.py → REPO_ROOT = Synapse-Mini/
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

PROMPTS_DIR: Path = REPO_ROOT / "agent-CEO" / "prompts"
TEMPLATES_DIR: Path = REPO_ROOT / "agent-CEO" / "templates"
REPORTS_DIR: Path = REPO_ROOT / "obs" / "06-daily-reports"
ACTIVE_TASKS_YAML: Path = REPO_ROOT / "agent-CEO" / "config" / "active_tasks.yaml"
ORGANIZATION_YAML: Path = REPO_ROOT / "agent-CEO" / "config" / "organization.yaml"
CLAUDE_MD: Path = REPO_ROOT / "CLAUDE.md"


# ---------------------------------------------------------------------------
# Claude API 默认配置
# ---------------------------------------------------------------------------

# Per 任务说明：按 prompt 复杂度选模型（sonnet 默认、opus 留待复杂场景）
DEFAULT_MODEL: str = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
OPUS_MODEL: str = os.environ.get("ANTHROPIC_MODEL_OPUS", "claude-opus-4-6")

DEFAULT_MAX_TOKENS: int = 8000
DEFAULT_TASK_BUDGET: int = 50_000  # INTEL-20260419-004 原生 task budgets

# Beta header — task budgets feature flag
TASK_BUDGETS_BETA: str = "task-budgets-2026-03-13"

# CLAUDE.md 注入截断（防止单次 system 过长；真正大段靠 prompt caching 省 token）
CLAUDE_MD_MAX_CHARS: int = 12_000


# ---------------------------------------------------------------------------
# 文件读取辅助
# ---------------------------------------------------------------------------

def load_prompt(name: str) -> str:
    """Load prompt from ``agent-CEO/prompts/{name}.md``.

    Args:
        name: Prompt 文件名（不带 .md 扩展）。

    Returns:
        Prompt 文本内容（UTF-8）。

    Raises:
        FileNotFoundError: 对应 prompt 文件不存在。
    """
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def load_claude_md(truncate: bool = True) -> str:
    """加载 CLAUDE.md，可选按 ``CLAUDE_MD_MAX_CHARS`` 截断。"""
    text = CLAUDE_MD.read_text(encoding="utf-8")
    if truncate and len(text) > CLAUDE_MD_MAX_CHARS:
        return text[:CLAUDE_MD_MAX_CHARS] + "\n\n…（已截断，完整版见 CLAUDE.md）"
    return text


def load_active_tasks() -> str:
    """加载 active_tasks.yaml 全文（UTF-8）。"""
    return ACTIVE_TASKS_YAML.read_text(encoding="utf-8")


def load_organization_yaml() -> str:
    """加载 organization.yaml 全文（UTF-8）。"""
    if ORGANIZATION_YAML.exists():
        return ORGANIZATION_YAML.read_text(encoding="utf-8")
    return ""


def load_recent_commits(hours: int = 24) -> str:
    """调用 git log 获取近 N 小时 commit 摘要（失败返回空串）。"""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "log", f"--since={hours} hours ago", "--oneline"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
        )
        return result.stdout.strip()
    except Exception as exc:  # pragma: no cover
        print(f"[load_recent_commits] git log failed: {exc}")
        return ""


# ---------------------------------------------------------------------------
# Anthropic Client
# ---------------------------------------------------------------------------

def get_client() -> Anthropic:
    """构造 Anthropic 客户端（从环境变量读 key）。

    Raises:
        RuntimeError: ``ANTHROPIC_API_KEY`` 未设置。
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY missing — set via GitHub Secrets "
            "(Settings → Secrets and variables → Actions)"
        )
    return Anthropic(api_key=api_key)


def _build_system_blocks(
    system: str, cache_system: bool
) -> Union[str, list[dict[str, Any]]]:
    """构造 system 消息（启用 prompt caching 时用 block 形式）。"""
    if not cache_system:
        return system
    # prompt caching: cache_control ephemeral → 5 分钟 TTL
    return [
        {
            "type": "text",
            "text": system,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def call_claude(
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    task_budget: int = DEFAULT_TASK_BUDGET,
    cache_system: bool = True,
    max_retries: int = 3,
) -> str:
    """调用 Claude API（task_budget + prompt caching + 重试）。

    Args:
        system: System prompt 文本（大段 CLAUDE.md/prompt 走 cache）。
        user: 用户消息。
        model: 模型 ID。默认 ``claude-sonnet-4-6``。
        max_tokens: 单次最大输出 token 数。
        task_budget: task_budget 上限，默认 50k（INTEL-20260419-004）。
        cache_system: 是否对 system 启用 prompt caching。
        max_retries: 429/529/5xx 的最大重试次数。

    Returns:
        Claude 响应的文本内容（content[0].text）。

    Raises:
        Exception: 超出重试或 4xx 认证/参数错时向上抛出。
    """
    client = get_client()
    system_blocks = _build_system_blocks(system, cache_system)

    # NOTE: 原计划通过 anthropic-beta: task-budgets-2026-03-13 + extra_body.task_budget
    # 做硬预算控制，但 2026-04-24 首次部署时 API 返回 400
    # "task_budget: Extra inputs are not permitted"（beta 未对本账户开放或已废弃）。
    # 修复策略（Week 1 收尾）：降级为 max_tokens 软控制 + usage 软监控，
    # 超 task_budget 只打 warning 不中断。Week 2 再评估是否重新启用 beta。

    def _do_call() -> str:
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system_blocks,
            "messages": [{"role": "user", "content": user}],
        }
        response = client.messages.create(**kwargs)

        # 打印 token 用量（含 cache 读写）
        usage = getattr(response, "usage", None)
        if usage is not None:
            cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
            cache_create = getattr(usage, "cache_creation_input_tokens", 0) or 0
            print(
                f"[Usage] input={usage.input_tokens} output={usage.output_tokens} "
                f"cache_read={cache_read} cache_create={cache_create}"
            )
            # 成本超 task_budget：warning 但不中断（模型应自降级）
            total_in = (usage.input_tokens or 0) + (usage.output_tokens or 0)
            if total_in > task_budget:
                print(
                    f"[Warning] 任务消耗 {total_in} tokens 超过 task_budget={task_budget}"
                )

        # 抽取 text content
        if not response.content:
            return ""
        first = response.content[0]
        return getattr(first, "text", str(first))

    return retry_with_backoff(_do_call, max_retries=max_retries)


def retry_with_backoff(
    func: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 2.0,
) -> Any:
    """对 ``func()`` 做指数退避重试。

    重试策略：
        - 429 / 529 / 5xx：指数退避 base_delay × 2^attempt
        - 认证/参数错（4xx，非 429）：立即失败，不重试
        - 达到 max_retries：抛出最后一次异常

    Args:
        func: 无参可调用（出错时抛异常）。
        max_retries: 最大重试次数（不含首次）。
        base_delay: 基础延迟（秒）。

    Returns:
        ``func()`` 的返回值。
    """
    last_exc: Optional[BaseException] = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as exc:
            last_exc = exc
            err_str = str(exc)
            status = _extract_status_code(exc, err_str)

            is_retryable = (
                status in {429, 529}
                or (status is not None and 500 <= status < 600)
            )
            if not is_retryable:
                # 4xx（认证/参数）→ 立即失败
                print(f"[Retry] non-retryable error ({status}): {exc}")
                raise

            if attempt >= max_retries:
                print(f"[Retry] max_retries={max_retries} 已耗尽")
                raise

            # 5xx 最多 1 次按任务约束，这里合并处理：
            # 指数退避（429/529/5xx 共用，5xx 实际通常 1-2 次后放弃）
            delay = base_delay * (2 ** attempt)
            print(
                f"[Retry] attempt {attempt + 1}/{max_retries} after {delay:.1f}s "
                f"(status={status}, err={err_str[:120]})"
            )
            time.sleep(delay)

    # 理论不可达（break 条件都抛了）
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("retry_with_backoff: unexpected exit")


def _extract_status_code(exc: BaseException, err_str: str) -> Optional[int]:
    """从 Anthropic 异常中提取 HTTP status code（尽力而为）。"""
    # anthropic SDK 的 APIStatusError / APIError 通常带 .status_code
    code = getattr(exc, "status_code", None)
    if isinstance(code, int):
        return code
    # fallback：字符串扫描
    for token in ("429", "529", "500", "502", "503", "504", "400", "401", "403"):
        if token in err_str:
            return int(token)
    return None


# ---------------------------------------------------------------------------
# Slack 通知（复用 n8n webhook）
# ---------------------------------------------------------------------------

def notify_slack(
    webhook_url: Optional[str],
    title: str = "",
    body: str = "",
    source: str = "unknown",
    priority: str = "info",
    recipient: Optional[str] = None,
) -> bool:
    """发送 Slack 通知（通过 WF-09 Unified Notification (atit1zW3VYUL54CJ)）。

    WF-09 期望的标准 payload 契约（2026-04-24 REQ-INFRA-004 根因定位）：
      - recipient: 命名键（如 'president' → channel C0AV1JAHZHB #ai-agents-noti）
                   或 Slack User ID（如 U0ASLJZMVDE，总裁 DM，紧急 L4 用）
                   或 channel ID（如 C0XXXXXXX）
                   None → 默认 'president' → channel（P0-A 修复 2026-04-23）
      - title: 消息标题
      - body: 消息正文（支持 markdown，Slack 消息长度限制 3500 字）
      - source: 来源标识（workflow/脚本名，如 intel-daily / intel-action / task-resume）
      - priority: info / warning / critical

    日志策略（Week 2.1 升级）：
        - 所有 print 均 ``flush=True``，确保 GH Actions 日志实时可见
        - 打印 URL 安全摘要（脱敏 webhook token）
        - 区分失败类型：empty URL / Timeout / ConnectionError / 其他
        - 响应体校验 "ok":true（防 HTTP 2xx + Slack API 不 ok 的假阳性）

    Args:
        webhook_url: n8n webhook URL（若 None 读环境变量 ``SLACK_WEBHOOK_N8N``）。
        title: 消息标题（截断到 200 字）。
        body: 消息正文（截断到 3500 字）。
        source: 来源标识。
        priority: info / warning / critical（非法值自动降级为 info）。
        recipient: 命名键 / Slack User ID / channel ID；None → 环境变量 SLACK_DEFAULT_RECIPIENT
                   → 'president'（→ channel #ai-agents-noti）。

    Returns:
        True = HTTP 2xx 且 body 含 "ok":true；False = 任何失败。
    """
    import requests
    from urllib.parse import urlparse

    if webhook_url is None:
        webhook_url = os.environ.get("SLACK_WEBHOOK_N8N")
    if not webhook_url:
        print("[Slack] SKIPPED: webhook_url is empty/None", flush=True)
        return False

    # 默认 recipient（命名键 'president' → WF-09 路由到 #ai-agents-noti channel C0AV1JAHZHB）
    # P0-A 修复（2026-04-23）：原默认 "U0ASLJZMVDE" 走 WF-09 fallback → 总裁 DM
    # 现默认 "president" → 命中 WF-09 命名分支 → channel
    # 调用方仍可显式传 "U0ASLJZMVDE" 强制走 DM（紧急 L4 通知用）
    if recipient is None:
        recipient = os.environ.get("SLACK_DEFAULT_RECIPIENT", "president")

    # URL 安全摘要（脱敏 webhook token）
    try:
        parsed = urlparse(webhook_url)
        url_safe = f"{parsed.scheme}://{parsed.netloc}{parsed.path[:30]}..."
    except Exception:
        url_safe = "<url-redacted>"

    payload: dict[str, Any] = {
        "recipient": recipient,
        "title": (title or "")[:200],
        "body": (body or "")[:3500],
        "source": source or "unknown",
        "priority": priority if priority in ("info", "warning", "critical") else "info",
    }

    print(
        f"[Slack] POST to {url_safe} "
        f"(source={payload['source']}, priority={payload['priority']}, "
        f"body_len={len(payload['body'])})",
        flush=True,
    )

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        http_ok = 200 <= resp.status_code < 300
        body_text = (resp.text or "")[:300].replace("\n", " ")

        # 响应体校验：含 "ok":true
        slack_ok = '"ok":true' in body_text or '"ok": true' in body_text

        if http_ok and slack_ok:
            print(
                f"[Slack] ✅ Delivered: status={resp.status_code}, ok=true",
                flush=True,
            )
            return True
        elif http_ok and not slack_ok:
            print(
                f"[Slack] ⚠️ HTTP 2xx but Slack not ok: body='{body_text}'",
                flush=True,
            )
            return False
        else:
            print(
                f"[Slack] ❌ HTTP {resp.status_code}: body='{body_text}'",
                flush=True,
            )
            return False
    except requests.Timeout:
        print("[Slack] ❌ Timeout after 10s", flush=True)
        return False
    except requests.ConnectionError as exc:
        print(f"[Slack] ❌ Connection error: {exc}", flush=True)
        return False
    except Exception as exc:
        print(
            f"[Slack] ❌ Unexpected error: {type(exc).__name__}: {exc}",
            flush=True,
        )
        return False


def notify_slack_legacy(
    webhook_url: Optional[str],
    message: str,
    channel: Optional[str] = None,
) -> bool:
    """Deprecated: 保留以避免破坏旧签名调用方。请迁移到 notify_slack()。

    旧签名 (webhook_url, message, channel=None) → 转换为标准 WF-09 payload。
    """
    return notify_slack(
        webhook_url=webhook_url,
        title="Legacy Notification",
        body=message,
        source="legacy",
        priority="info",
        recipient=channel,
    )


# ---------------------------------------------------------------------------
# JSON 解析辅助（Claude 响应常 fence 包裹）
# ---------------------------------------------------------------------------

def extract_json_block(text: str) -> Optional[dict[str, Any]]:
    """从 Claude 响应中提取第一个 ```json ... ``` 块（容错）。

    Returns:
        解析后的 dict；未找到或解析失败返回 None。
    """
    import re
    # 1) 带 language tag 的 fence
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # 2) 裸 fence
    m = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # 3) 首个 { ... } 扫描
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None


def extract_html_block(text: str) -> Optional[str]:
    """从 Claude 响应中提取 ``<!DOCTYPE html> ... </html>`` 整块（可选）。"""
    import re
    m = re.search(
        r"(<!DOCTYPE html.*?</html>)", text, re.DOTALL | re.IGNORECASE
    )
    return m.group(1) if m else None
