# n8n Workflow 迁移状态报告

> 更新时间：2026-04-23
> 数据来源：本地 n8n Cloud 备份 JSON（`C:\Users\lysanderl_janusd\`）
> n8n 实例：`https://n8n.lysander.bond`
> 参考配置：`agent-CEO/config/n8n_integration.yaml` v3.0.0

---

## 一、执行摘要

共发现 **9 个工作流**（本地备份），按 Plan X（统一通知架构 v3.0）审计结果：

| 维度 | 现状 |
|------|------|
| Slack 通知方式 | 全部使用**直接 Slack API** `https://slack.com/api/chat.postMessage`（httpHeaderAuth generic credential），**无一使用** n8n 内置 Slack Node |
| Plan X 合规 | 全部工作流 Slack 通知**未经过** WF-09（`https://n8n.lysander.bond/webhook/notify`），直接调用 Slack Bot Token |
| 本地 Slack MCP | Synapse 配置中禁用了本地 Slack MCP（`agent-CEO/config/n8n_integration.yaml`），但 n8n 工作流的通知方式与 Claude Code MCP 无关 |
| WF-09 状态 | 本地备份中**未找到** WF-09（统一通知工作流），需在 n8n Cloud 确认是否存在 |
| Synapse 触发器 | `trig_01RJJoy4v8TLj2HyHRnABKJb`（任务恢复）、`trig_01Lp7Q1Nn36JQAw4FEEJmKQX`（情报日报）、`trig_017vgQox9JUcwvnx43ucLRPd`（行动管线）在本地备份中**未找到**，这些属于 Synapse 远程定时 Agent，非本地 PMO 工作流 |

---

## 二、工作流清单

### 2.1 PMO 通知类工作流（Janus Digital 内部管理）

| 工作流 | n8n ID | 状态 | 定时 | Slack 通知节点 | 目标频道 | Plan X 合规 |
|--------|--------|------|------|----------------|----------|-------------|
| WF-01 项目初始化 | `AnR20HucIRaiZPS7` | ✅ active | 每5分钟轮询 | `slack-dm-pm` / `slack-fallback-channel` | `C0AJN5PN1G8` + 用户 DM | ❌ 未经过 WF-09 |
| WF-02 任务变更通知 | `IXEFFpLwnlcggK2E` | ✅ active | `*/30 5-14 * * 1-5`（工作日每30分钟） | `wf02-http-2` (Slack变更通知) | `C0AJN5PN1G8` | ❌ 未经过 WF-09 |
| WF-03 里程碑提醒 | `uftMqCdR1pRz079z` | ✅ active | `0 5 * * 1-5`（工作日09:05 SGT） | `wf03-http-3` (Slack里程碑通知) | `C0AJN5PN1G8` | ❌ 未经过 WF-09 |
| WF-04 PMO周报自动化 | `40mJOR8xXtubjGO4` | ✅ active | `0 1 * * 1`（周一09:00 SGT） | `slack-notify` | `C0AJN5PN1G8` | ❌ 未经过 WF-09 |
| WF-05（逾期任务预警） | `rlEylvNQW55UPbAq` | ✅ active | `0 1 * * 1-5`（工作日09:00 SGT） | `slack-alert` | `C0AJN5PN1G8` | ❌ 未经过 WF-09 |
| WF-05（章程确认 Assignee同步） | `g6wKsdroKNAqHHds` | ✅ active | 每5分钟轮询 | `wf05-slack-notify` | `C0AJN5PN1G8` | ❌ 未经过 WF-09 |
| WF-06 任务依赖链通知 | `knVJ8Uq2D1UZmpxr` | ✅ active | 每60分钟 | `wf06-slack-summary` | `C0AJN5PN1G8` + 用户 DM | ❌ 未经过 WF-09 |
| WF-07 会议纪要→Asana任务 | `seiXPY0VNzNxQ2L3` | ✅ active | 每30分钟 | `slack-summary` (Slack通知创建结果) | `C0AJN5PN1G8` | ❌ 未经过 WF-09 |

### 2.2 PMO Notion OAuth 工作流（模板，未激活）

| 工作流 | 用途 | 触发 | 状态 |
|--------|------|------|------|
| WF-01（OAuth版）项目空间初始化 | 新项目初始化 | Webhook `/webhook/wf-01-project-init` | 📋 模板（未导入 n8n Cloud） |
| WF-04（OAuth版）Asana进度同步 | Notion-Asana 双向同步 | 每日 Cron `0 6 * * *` | 📋 模板（未导入 n8n Cloud） |

---

## 三、Slack 通知节点分析

### 3.1 当前通知方式（所有工作流一致）

```
n8n HTTP Request Node
  ├── Method: POST
  ├── URL: https://slack.com/api/chat.postMessage
  ├── Authentication: genericCredentialType / httpHeaderAuth
  ├── Credential Name: "Slack Bot Token"
  ├── Credential ID: uWER9LYkLVS3tMqr（所有工作流共用）
  └── Body (JSON):
      {
        "channel": "C0AJN5PN1G8",
        "text": "...",
        "blocks": [...]
      }
```

**关键发现：**
- **无一使用 n8n 内置 Slack Node**（`n8n-nodes-base.slack`）
- **无一经过 WF-09 统一通知入口**（`https://n8n.lysander.bond/webhook/notify`）
- 所有工作流共用同一个 Slack Bot Token Credential（`uWER9LYkLVS3tMqr`）
- 所有通知发往同一频道 `C0AJN5PN1G8`（Slack）

### 3.2 Plan X 目标架构 vs 现状

```
现状：
  Claude Code → [本地 Slack MCP 已禁用] → （无通知）
  n8n Workflow → [直接调用 Slack API] → Slack C0AJN5PN1G8

Plan X 目标：
  Claude Code → [n8n WF-09 webhook] → Slack C0AJN5PN1G8
  n8n Workflow → [n8n WF-09 webhook] → Slack C0AJN5PN1G8

当前问题：
  n8n 工作流均未经过 WF-09，无法统一控制优先级、路由、HMAC签名
```

---

## 四、敏感信息发现

### 4.1 凭证嵌入 staticData（高风险）

**WF-05（章程确认 Assignee同步）** `g6wKsdroKNAqHHds` staticData 中发现：

```json
{
  "asanaPAT": "<redacted: see credentials.mdenc → ASANA_PAT>",
  "notionToken": "<redacted: see credentials.mdenc → NOTION_TOKEN>"
}
```

> 注：2026-04-24 已将两条明文 Token 迁移至 `obs/credentials.mdenc`（REQ-INFRA-001 shipped）。
> AI Agent 使用方式：`python creds.py get ASANA_PAT -p "<主密码>"` / `... NOTION_TOKEN ...`

**风险：**
- 工作流 JSON 导出文件存储在本地（`C:\Users\lysanderl_janusd\`），未加密
- Asana PAT 包含完整访问令牌
- Notion Integration Token 可写入 Notion 数据库
- 这些凭证应迁移至 n8n Credentials Store，staticData 中移除明文

**建议：**
1. 将 Asana PAT 和 Notion Token 添加至 n8n Credentials Store（命名凭证）
2. 在工作流中引用命名凭证，移除 staticData 中的明文
3. 从本地备份 JSON 文件中删除敏感字段后再备份

---

## 五、迁移建议

### 5.1 短期（立即）

- [ ] **WF-09 统一通知工作流**：在 n8n Cloud 确认 WF-09 是否存在并激活，如不存在需创建
- [ ] **凭证安全**：清理 `g6wKsdroKNAqHHds` staticData 中的明文 Asana PAT 和 Notion Token
- [ ] **健康检查**：在 n8n Cloud 验证所有 webhook URL 可达性（`agent-CEO/config/n8n_integration.yaml` 中的 health_check 段落）

### 5.2 中期（Plan X 合规）

以下工作流 Slack 通知节点需改造为经过 WF-09：

| 工作流 | 当前 Slack Node | 改造方案 |
|--------|----------------|----------|
| WF-01 项目初始化 | `slack-dm-pm` / `slack-fallback-channel` | 先发至 WF-09，再 DM 指定用户 |
| WF-02 任务变更通知 | `wf02-http-2` | 先发至 WF-09 |
| WF-03 里程碑提醒 | `wf03-http-3` | 先发至 WF-09 |
| WF-04 PMO周报自动化 | `slack-notify` | 先发至 WF-09 |
| WF-05（逾期任务预警） | `slack-alert` | 先发至 WF-09 |
| WF-05（章程确认） | `wf05-slack-notify` | 先发至 WF-09 |
| WF-06 任务依赖链通知 | `wf06-slack-summary` | 先发至 WF-09 |
| WF-07 会议纪要 | `slack-summary` | 先发至 WF-09 |

**改造模式（每个工作流）：**

```
当前：
  [任意节点] → httpRequest(Slack API) → Slack

目标：
  [任意节点] → httpRequest(WF-09 webhook) → n8n WF-09 → Slack

WF-09 请求格式（参考 n8n_integration.yaml）：
  POST https://n8n.lysander.bond/webhook/notify
  Headers:
    X-Synapse-Signature: HMAC-SHA256(recipient+priority+title+body+timestamp, hmac_secret)
    X-Synapse-Timestamp: <unix timestamp>
  Body:
    {
      "recipient": "C0AJN5PN1G8",
      "priority": "normal|high|critical",
      "title": "通知标题",
      "body": "通知正文（mrkdwn格式）",
      "source": "wf-02-task-change"
    }
```

### 5.3 长期

- [ ] Synapse 远程定时 Agent（`trig_01RJJoy4v8TLj2HyHRnABKJb` 等）需与 n8n Cloud 确认存在并同步到本地备份
- [ ] PMO Notion OAuth 工作流模板（`n8n_wf_pmo_notion_oauth.json`）需导入 n8n Cloud 并激活

---

## 六、附录

### 6.1 共用凭证

| 凭证名称 | 凭证 ID | 用途 | 安全状态 |
|----------|---------|------|----------|
| Slack Bot Token | `uWER9LYkLVS3tMqr` | 所有工作流 Slack 通知 | ✅ 在 n8n Credentials Store |
| Asana PAT | `t1H98T0ROD4S804H` | 所有工作流 Asana API | ✅ 在 n8n Credentials Store |
| Fireflies API Key | `W1AzqnJVj4M6h3Gf` | WF-07 | ✅ 在 n8n Credentials Store |
| Gemini API | `z149aW3CXelugx97` | WF-07 | ✅ 在 n8n Credentials Store |
| Notion API | `qdn9QguMUFJGJrGb` | WF-07, WF-05 | ✅ 在 n8n Credentials Store |

### 6.2 关键 Channel ID

| 频道 | ID | 用途 |
|------|-----|------|
| `#general`（或主通知频道） | `C0AJN5PN1G8` | 所有工作流通知目标 |

### 6.3 相关文件

- `agent-CEO/config/n8n_integration.yaml` — Synapse n8n 集成配置（v3.0.0）
- `C:\Users\lysanderl_janusd\n8n_wf_*.json` — n8n Cloud 备份文件
- `C:\Users\lysanderl_janusd\n8n_workflows.json` — 完整导出（426.7KB，未读取）
