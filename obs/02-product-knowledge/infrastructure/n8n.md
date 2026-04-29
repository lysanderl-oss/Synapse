---
id: infra-n8n
type: reference
status: published
lang: zh
version: 1.0.0
published_at: "2026-04-28"
updated_at: "2026-04-28"
author: ai_systems_dev
review_by: [harness_engineer, integration_qa]
audience: [team_partner, knowledge_engineer]
stale_after: "2027-04-28"
profile_version: "2026-04-28"
owner: ai_systems_dev
---

# 基础设施档案：n8n 工作流引擎

## 实例信息

| 项目 | 值 |
|------|-----|
| 实例 URL | https://n8n.lysander.bond |
| API 端点 | https://n8n.lysander.bond/api/v1/ |
| Webhook 基础 URL | https://n8n.lysander.bond/webhook/ |
| API 认证 | Header: X-N8N-API-KEY |

## 使用本实例的产品线

- PMO Auto（WF-01~WF-14）
- Synapse Harness（Synapse-WF3/4/6/7/8 等系统工作流）

## 关键约束

1. **WF-12 必须保持 active**：每次 n8n 迁移/重建后必须手动确认
2. **Webhook path 不可随意更改**：PMO Auto 的 pmo-api 依赖固定 webhook path（`pmo-wf02-wbs-import`）
3. **Task Runner 模式**：Code Node 内不能使用 `this.getCredentials()`，必须用 HTTP Request 节点

## 常用操作

```bash
# 获取所有工作流
curl -s "https://n8n.lysander.bond/api/v1/workflows?limit=50" -H "X-N8N-API-KEY: {KEY}"

# 激活指定工作流
curl -X POST "https://n8n.lysander.bond/api/v1/workflows/{id}/activate" -H "X-N8N-API-KEY: {KEY}"

# 查看最近执行
curl -s "https://n8n.lysander.bond/api/v1/executions?workflowId={id}&limit=5" -H "X-N8N-API-KEY: {KEY}"
```

## 凭证获取

n8n API Key 通过 `creds.py` 获取（目录：`C:\Users\lysanderl_janusd\Synapse-Mini`）
