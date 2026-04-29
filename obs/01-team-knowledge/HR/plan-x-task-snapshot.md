# Plan X — 统一通知架构完整任务快照
> Synapse v3.0 核心基础设施升级
> 创建: 2026-04-23 | 最后更新: 2026-04-23 | 状态: 🔴 待继续

---

## 一、背景与决策（Why）

### 问题起源
2026-04-22 晚间会话中，Strategist/Decision Advisor/Execution Auditor Agent 在执行分析时，**通过本地 Slack MCP 直接调用了 `slack_search_public_and_private` 工具**，意外向 Slack #news-ai-general 频道发送了"Synapse 双目录整合 — 技术整合路径报告"。

### 根因分析
本地 Slack MCP (mcp__77a256e0-d621-4108-987b-9b0193d2cd94__slack_search_public_and_private) 的 channel_id 参数不可控，**任何 Agent 均可在任意会话中直接调用并指定任意频道**（包括 public channels）。

### 决策结论（总裁 2026-04-23 批准）
- **方案**: Plan X — 禁用本地 Slack MCP，所有 Slack 通知统一经 n8n WF-09
- **迁移方式**: 一次性切换到位（不渐进迁移）
- **无 Email 降级层**（总裁明确拒绝）
- **授权**: 总裁已授权全部执行操作

---

## 二、目标架构（Target）

```
当前状态:
  Claude Code Agent → [本地 Slack MCP] → 任意 Slack 频道（失控）
  n8n Workflow      → [直接 Slack API] → Slack C0AJN5PN1G8

Plan X 目标:
  Claude Code Agent → [n8n WF-09 webhook] → Slack（受控路由）
  n8n Workflow      → [n8n WF-09 webhook] → Slack（统一入口）
                    ↑
              所有通知的唯一出口
              HMAC 签名验证
              优先级路由控制
```

### WF-09 统一通知工作流（10 节点设计）

```
[Webhook POST /webhook/notify]
        ↓
[HMAC Signature Validation]
        ↓
[Parse Recipient] → president / @Uxxx / Cxxx
        ↓
[Switch priority] → normal / high / critical
        ↓
[Slack Send Message] ← 使用 Slack Bot Token 凭证 (ID: uWER9LYkLVS3tMqr)
        ↓
[Critical: 2nd Alert to harness_ops]
        ↓
[Write Log]
```

### HMAC 签名规范

```
secret: "MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8"
计算: signature = HMAC-SHA256(recipient + priority + title + body + timestamp)
验证窗口: 300 秒
```

### WF-09 输入 Schema

```json
{
  "recipient": "president | @U0123456789 | C0123456789",
  "priority": "normal | high | critical",
  "title": "通知标题（最多100字符）",
  "body": "通知正文（最多2000字符，mrkdwn格式）",
  "source": "来源标识（如 wf-02-task-change）",
  "signature": "HMAC-SHA256 hex",
  "timestamp": "Unix 时间戳（秒）"
}
```

---

## 三、已完成工作

| 任务 | 文件 | 状态 |
|------|------|------|
| n8n_integration.yaml 更新 | agent-CEO/config/n8n_integration.yaml | ✅ 已 commit |
| settings.local.json 移除 Slack MCP | .claude/settings.local.json | ✅ 已 commit |
| WF-09 设计文档 | obs/01-team-knowledge/HR/unified-notification-wf9-design.md | ✅ 已创建 |
| n8n 迁移状态分析 | obs/01-team-knowledge/HR/n8n-wf-migration-status.md | ✅ 已创建 |

**Git commit**: `5003322 feat: Phase 1+2 — scripts迁移 + Skills迁移 + hook路径修复`

---

## 四、待执行工作（核心）

### 4.1 创建 WF-09（在 n8n Cloud）

**n8n Cloud URL**: https://n8n.lysander.bond

**操作步骤**:
1. 登录 n8n Cloud
2. 新建 Workflow，命名 "WF-09 Unified Notification"
3. 添加 4 个节点（Webhook → HMAC Validate → Parse Recipient → Send Slack Message）
4. Webhook Path: `/webhook/notify`
5. Slack 凭证: 使用已有的 "Slack Bot Token" (ID: uWER9LYkLVS3tMqr)
6. 激活 Workflow（点击 Activate）

**Node 1 - Webhook**:
- Type: webhook
- Path: notify
- Method: POST
- Response Mode: lastNode

**Node 2 - HMAC Validate (Code 节点)**:
```javascript
const crypto = require('crypto');
const secret = 'MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8';
const body = $input.first().json;

const now = Math.floor(Date.now() / 1000);
const ts = parseInt(body.timestamp);
if (isNaN(ts) || Math.abs(now - ts) > 300) throw new Error('Timestamp expired');

const data = body.recipient + body.priority + body.title + body.body + body.timestamp;
const expected = crypto.createHmac('sha256', secret).update(data).digest('hex');

if (body.signature !== expected) throw new Error('Signature mismatch');

return [{json: {validated: true, ...body}}];
```

**Node 3 - Parse Recipient (Code 节点)**:
```javascript
const r = $input.first().json.recipient || '';
let channelId = r;
let channelType = 'channel';

if (r === 'president') {
  channelId = 'C0AJN5PN1G8';  // 总裁通知主频道
} else if (r.startsWith('@U')) {
  channelType = 'user';
} else if (r.startsWith('C')) {
  channelType = 'channel';
}

return [{json: {channelId, channelType, ...$input.first().json}}];
```

**Node 4 - Send Slack Message (n8n-nodes-base.slack)**:
- Credential: uWER9LYkLVS3tMqr (Slack Bot Token)
- Operation: sendMessage
- Channel: `{{ $json.channelId }}`
- Text: `*{ { $json.title } }*\n\n{ { $json.body } }\n\n来源: { { $json.source } } | 优先级: { { $json.priority } }`

### 4.2 测试 WF-09

生成 HMAC 签名并发送测试请求：
```bash
ts=$(date +%s)
python3 -c "
import hmac, hashlib, time
secret = 'MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8'
data = 'C0AJN5PN1G8' + 'high' + 'WF-09测试' + 'Plan X验证测试' + '$ts'
sig = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
print(sig)
" > /tmp/sig.txt

sig=$(cat /tmp/sig.txt)
curl -X POST "https://n8n.lysander.bond/webhook/notify" \
  -H "Content-Type: application/json" \
  -d "{\"recipient\":\"C0AJN5PN1G8\",\"priority\":\"high\",\"title\":\"WF-09测试\",\"body\":\"Plan X验证测试\",\"source\":\"wf-09-test\",\"signature\":\"$sig\",\"timestamp\":\"$ts\"}"
```

验证 Slack 是否收到通知。

### 4.3 迁移 8 个 PMO Workflows

对于每个 workflow，找到 Slack HTTP Request 节点（URL: `https://slack.com/api/chat.postMessage`），替换为：

**URL**: `https://n8n.lysander.bond/webhook/notify`
**Method**: POST
**Headers**:
- Content-Type: application/json
- X-Synapse-Timestamp: (Unix timestamp)
- X-Synapse-Signature: (HMAC signature)
**Body**:
```json
{
  "recipient": "C0AJN5PN1G8",
  "priority": "normal",
  "title": "[原始通知标题]",
  "body": "[原始 mrkdwn 通知内容]",
  "source": "wf-XX-[workflow-name]",
  "signature": "[HMAC签名]",
  "timestamp": "[Unix时间戳]"
}
```

**待迁移 Workflows**:
| Workflow | n8n ID | 当前 Slack 节点 |
|----------|--------|----------------|
| WF-01 项目初始化 | AnR20HucIRaiZPS7 | slack-dm-pm, slack-fallback-channel |
| WF-02 任务变更通知 | IXEFFpLwnlcggK2E | wf02-http-2 |
| WF-03 里程碑提醒 | uftMqCdR1pRz079z | wf03-http-3 |
| WF-04 PMO周报自动化 | 40mJOR8xXtubjGO4 | slack-notify |
| WF-05 逾期任务预警 | rlEylvNQW55UPbAq | slack-alert |
| WF-05 章程确认 | g6wKsdroKNAqHHds | wf05-slack-notify |
| WF-06 任务依赖链通知 | knVJ8Uq2D1UZmpxr | wf06-slack-summary |
| WF-07 会议纪要→Asana任务 | seiXPY0VNzNxQ2L3 | slack-summary |

### 4.4 凭证安全（WF-05 staticData）

WF-05（g6wKsdroKNAqHHds）的 staticData 中有明文 Asana PAT 和 Notion Token：
```json
{
  "asanaPAT": "<redacted: see credentials.mdenc → ASANA_PAT>",
  "notionToken": "<redacted: see credentials.mdenc → NOTION_TOKEN>"
}
```
需要将这些凭证迁移到 n8n Credentials Store 并从 staticData 中移除。
> 注：2026-04-24 REQ-INFRA-001 shipped — 明文 Token 已从本 snapshot 遮盖，原值存于 `obs/credentials.mdenc`。

---

## 五、技术信息汇总

### n8n 关键凭证
- **Slack Bot Token ID**: uWER9LYkLVS3tMqr（所有 workflows 共用）
- **目标 Slack 频道 ID**: C0AJN5PN1G8

### HMAC 配置
- **Secret**: MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8
- **Timestamp 容忍**: 300 秒
- **签名算法**: HMAC-SHA256

### n8n_integration.yaml 关键配置
```yaml
unified_notification:
  webhook_url: "https://n8n.lysander.bond/webhook/notify"
  input_schema:
    recipient: "string — 总裁:president, 用户ID:@UXXXXXXXXX, 频道ID:CXXXXXXXXX"
    priority: "string — normal|high|critical"
    title: "string（最多100字符）"
    body: "string（最多2000字符）"
    source: "string — 来源标识"
    signature: "string — HMAC-SHA256"
```

### 已禁用
- 本地 Slack MCP: `mcp__77a256e0-d621-4108-987b-9b0193d2cd94__slack_search_public_and_private`（已从 settings.local.json 移除）
- calendar_sync_agent 不再 `requires_mcp: [slack]`，改为 `notification_via: unified_notification`

---

## 六、验证标准

### WF-09 创建成功
- [ ] n8n UI 中看到 "WF-09 Unified Notification" workflow
- [ ] Webhook 节点 Path 为 `/webhook/notify`
- [ ] Workflow 状态为 Active

### 端到端测试通过
- [ ] curl 发送测试请求后，Slack 收到通知
- [ ] HMAC 签名正确则通过，错误则拒绝

### Workflow 迁移完成
- [ ] 8 个 PMO workflows 全部改为 POST 到 `/webhook/notify`
- [ ] 原 Slack API 调用节点已替换或禁用
- [ ] 每个 workflow 测试通知发送成功

---

## 七、启动命令（新会话）

```
总裁指令: "执行 Plan X"
→ 读取本文件 (obs/01-team-knowledge/HR/plan-x-task-snapshot.md) 获取完整上下文
→ 登录 n8n Cloud (https://n8n.lysander.bond)
→ 创建 WF-09（按 4.1 步骤）
→ 测试 webhook（按 4.2 步骤）
→ 迁移 8 个 workflows（按 4.3 步骤）
→ 清理 WF-05 staticData（按 4.4 步骤）
→ Git commit 最终状态
```

---

## 八、相关文件索引

| 文件 | 用途 |
|------|------|
| `obs/01-team-knowledge/HR/unified-notification-wf9-design.md` | WF-09 完整设计（n8n UI 操作指南） |
| `obs/01-team-knowledge/HR/n8n-wf-migration-status.md` | 8 个 workflow 的节点配置详情 |
| `agent-CEO/config/n8n_integration.yaml` | Synapse n8n 集成配置（含 HMAC secret） |
| `.claude/settings.local.json` | Slack MCP 已禁用（已更新） |

---

**决策授权记录**: 总裁 刘子杨 2026-04-23 批准，执行方式：一次性切换到位，无渐进迁移，无 email 降级层。