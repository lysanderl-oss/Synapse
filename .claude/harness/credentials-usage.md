# 凭证管理 — 参考模块
# [ADDED: 2026-04-12]
# 本文件由 CLAUDE.md 提取。按需读取，非会话启动时自动加载。
# 触发场景：需要使用 API Key、Token 等凭证时

## 凭证管理

敏感凭证（API Key、Token、密码）存储在 `obs/credentials.md`，使用 Meld Encrypt 加密。

### AI 调用方式

```bash
# 获取单个凭证（需要用户提供密码）
PYTHONUTF8=1 python creds.py get GITHUB_TOKEN -p "密码"

# 导出全部凭证（供批量使用）
PYTHONUTF8=1 python creds.py export -p "密码"

# 查看所有 Key 名（无需密码）
PYTHONUTF8=1 python creds.py list
```

### n8n Webhook HMAC 密钥

| Key 名 | 来源 | 用途 |
|--------|------|------|
| `n8n_webhook_hmac_secret` | `agent-butler/config/n8n_integration.yaml` → `webhook_security.hmac_secret` | 所有 n8n webhook 的 HMAC-SHA256 签名认证 |
| `n8n_webhook_timestamp_tolerance` | 同上 → `webhook_security.timestamp_tolerance_seconds` | 时间戳容差，默认 300s（5分钟） |

**密钥结构**：
```yaml
webhook_security:
  hmac_secret: "<32字符URL-safe随机密钥>"
  timestamp_tolerance_seconds: 300
  sign_header: "X-Synapse-Signature"
  timestamp_header: "X-Synapse-Timestamp"
```

**认证流程**：n8n workflow 的首个 Code 节点调用 `verify_signature(body, signature, timestamp)`，验证失败返回 401。

**n8n 端配置**：在 n8n Credentials 中创建 `synapse_webhook_auth` 类型，字段：
- `hmac_secret`：填入上方密钥值

**轮换规则**：每 90 天轮换一次，轮换后同步更新 n8n Credentials + `n8n_integration.yaml`。

### 使用规则

1. **需要凭证时**：先用 `list` 确认 Key 名，再向用户请求密码，用 `get` 获取值
2. **密码处理**：用户提供的密码只在当次命令中使用，不存储、不记录
3. **凭证文件**：`obs/credentials.md` 已加入 `.gitignore`，不上传 GitHub

---

## Slack 通知（统一通过 WF-09）
# [ADDED: 2026-04-27]

> ⚠️ **强制要求**：所有 Slack 通知必须通过 WF-09（Unified Notification Workflow），不得直接调用 Slack API 或其他通用 webhook。

### Webhook 端点
- URL: `https://n8n.lysander.bond/webhook/notify`
- Method: POST
- Content-Type: application/json
- 鉴权: HMAC（可选）— 无 signature 字段则跳过校验

### 路由契约
| recipient | Slack Channel | 用途 |
|-----------|---------------|------|
| `president` | `C0AV1JAHZHB` (#ai-agents-noti) | 总裁通知 |
| 其他 | 见 WF-09 设计文档 | ... |

### 推荐调用（Python）
```python
from agent_CEO.shared_context import notify_slack

notify_slack(
    recipient='president',  # 默认值，可省略
    title='会话总结已生成',
    message='...',
    priority='info'  # info | warning | critical
)
```

### 直接 curl 调用
```bash
curl -X POST -H 'Content-Type: application/json' \
  --data '{"recipient":"president","title":"...","message":"..."}' \
  https://n8n.lysander.bond/webhook/notify
```

### 反例（禁止）
- ❌ 直接调用 `slack.com/api/chat.postMessage`
- ❌ 使用历史遗留 webhook（如 Asana 通知 / Harness 错误通知 — 已 deactivated）
- ❌ 在 agent prompt 中含糊说"通过 Slack 发送"，必须明确"通过 WF-09 (`POST /webhook/notify`)"

### 限制
- WF-09 仅支持文本消息，**不支持文件上传**
- 文件分享需要：(a) 上传到外部存储 + 发链接，或 (b) 总裁手动上传

### 关键文档
- 设计：`obs/01-team-knowledge/HR/unified-notification-wf09-design.md`
- 诊断报告：`obs/06-daily-reports/2026-04-25-wf09-routing-diagnosis.md`
- n8n Workflow ID: `atit1zW3VYUL54CJ`

### 失败排查
1. HTTP 200 + `ok:false` → 查 n8n 执行日志
2. HTTP 5xx → n8n 服务故障
3. 任何错误 → 不要降级到其他 webhook，立即 Lysander 上报
