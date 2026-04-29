# WF-09: 统一通知工作流设计
# Synapse v3.0 — Plan X 实施
# 创建日期: 2026-04-23

## 背景

本地 Slack MCP (mcp__slack_search_public_and_private) 存在 channel_id 不可控风险，
任何 Agent 均可直接调用 Slack MCP 并指定任意 channel（包括 public channels）。
Plan X 决策：禁用本地 Slack MCP，所有 Slack 通知统一经 n8n WF-09。

## 触发方式

POST https://n8n.lysander.bond/webhook/notify
Content-Type: application/json

## 输入 Schema

```json
{
  "recipient": "president | @U0123456789 | C0123456789",
  "priority": "normal | high | critical",
  "title": "string (max 100 chars)",
  "body": "string (max 2000 chars)",
  "source": "string",
  "signature": "HMAC-SHA256 hex",
  "timestamp": "ISO 8601"
}
```

## HMAC 签名计算

```
signature = HMAC-SHA256(
  recipient + priority + title + body + timestamp,
  secret: "MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8"
)
```

## n8n 工作流设计（10 个节点）

### Node 1: Webhook（入口）
- Trigger: POST /webhook/notify
- Output: 完整 JSON body

### Node 2: Signature Validation（签名验证）
- 计算 HMAC-SHA256(recipient + priority + title + body + timestamp, secret)
- 与传入 signature 比对
- 不匹配 → Error Trigger（记录日志后终止）
- 匹配 → 继续

### Node 3: Parse Recipient（解析收件人）
- 分离 recipient 类型：
  - "president" → 总裁固定 DM 频道
  - "@U..." → Slack 用户 ID
  - "C..." → Slack 频道 ID
- 设置 node.xxx.channel_id

### Node 4: Switch（优先级路由）
- normal: 直接发送
- high: 发送 + 记录 health_check
- critical: 发送 + 2nd alert to harness_ops

### Node 5: Slack Search（仅用于频道名搜索）
- 仅当 recipient 不是 ID 格式时（包含字母名）触发
- 搜索 Slack 频道，找到 channel ID
- 设置 node.xxx.target_channel_id

### Node 6: Slack - Send Message（核心发送节点）
- Credentials: n8n Slack OAuth Bot（需要以下 Scope）
  - chat:write — 发送消息
  - channels:read — 读取频道列表（用于 Node 5 搜索）
- Channel: { { $json.channel_id } }
- Message:
  ```
  *{ { $json.title } }*
  { { $json.body } }

  来源: { { $json.source } } | 优先级: { { $json.priority } }
  ```

### Node 7: Second Alert（critical 级别）
- 仅在 priority=critical 时触发
- 额外发送消息到 harness_ops 指定频道
- 内容: "紧急通知已发送至 {recipient}，请关注"

### Node 8: Write Log（记录日志）
- 写入 n8n 执行日志或外部日志服务
- 记录: timestamp, recipient, priority, title, source, status

### Node 9: Error Trigger（签名验证失败）
- 记录失败日志（不暴露内部细节给调用方）
- 静默终止，不返回错误信息（防止签名泄露）

## 安全性

1. HMAC 签名验证 — 防止伪造请求
2. OAuth Bot — 不使用用户 token，避免权限泄露
3. 最小权限原则 — 只需 chat:write 和 channels:read
4. 签名验证失败静默处理 — 不返回详细错误

## 迁移映射（现有 n8n workflows → WF-09）

| 原 Workflow | 原通知方式 | 改为 WF-09 |
|---|---|---|
| WF-2 (action-notify) | slack MCP direct call | POST /webhook/notify, recipient="president", source="action-report" |
| WF-4 (butler-execute) | slack MCP direct call | 同上 |
| WF-5 (expert-review) | slack MCP direct call | 同上 |
| WF-6 (lysander-approve) | slack MCP direct call | 同上 |
| WF-8 (task-status) | slack MCP direct call | 同上 |

## n8n 创建步骤

1. 登录 https://n8n.lysander.bond
2. 新建 Workflow，命名 "Unified Notification (WF-09)"
3. 添加 Webhook 触发节点（POST /webhook/notify）
4. 按设计添加其余节点（Node 1-9）
5. 配置 Slack OAuth Bot Credentials
   - 权限：chat:write, channels:read
6. 激活 Workflow
7. 验证:
   ```
   curl -X POST https://n8n.lysander.bond/webhook/notify \
     -H "Content-Type: application/json" \
     -d '{"recipient":"president","priority":"high","title":"测试","body":"WF-09 验证测试","source":"qa","signature":"...","timestamp":"2026-04-23T00:00:00Z"}'
   ```

## 无 Email 降级

用户明确要求：无需 Email 提醒层。
critical 通知仅在 n8n 内部执行 second alert，不降级到 email。
