---
id: infra-pmo-api
type: reference
status: published
lang: zh
version: 2.6.0
published_at: "2026-04-28"
updated_at: "2026-04-28"
author: ai_systems_dev
review_by: [synapse_product_owner, integration_qa]
audience: [team_partner, knowledge_engineer]
stale_after: "2027-04-28"
profile_version: "2.6.0"
owner: ai_systems_dev
---

# 基础设施档案：pmo-api

## 实例信息

| 项目 | 值 |
|------|-----|
| API URL | https://pmo-api.lysander.bond |
| 服务器 | ubuntu@43.156.171.107 |
| 部署方式 | Docker Compose（`/home/ubuntu/pmo-auto/`）|
| 数据目录 | `/home/ubuntu/pmo-data/pmo_api.db`（SQLite 持久化）|

## 使用本服务的产品线

- PMO Auto（WF-11 调用 `/run-wbs`，WF-08 接收 Asana Webhook）

## 关键端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 服务健康检查 |
| `/run-wbs` | POST | 触发 WBS 导入（调用 wbs_to_asana.py）|
| `/webhooks/asana/register-team` | POST | 批量注册 Asana Webhook |
| `/webhooks/asana/event` | POST | 接收 Asana 任务完成事件 |

## 关键约束

1. **WBS 防重入**：`wbs_to_asana.py` 检测到项目已有任务（>0）则退出（exit code 1），Notion 状态可能误写为"失败"
2. **callback_url**：`/run-wbs` 支持可选 `callback_url` 字段，当前生产未启用
3. **HMAC 签名**：Asana Webhook 事件需通过签名验证（`X-Synapse-Signature` + `X-Synapse-Timestamp`）

## 本地代码路径

```
C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\pmo_api\
├── main.py          # FastAPI 主应用，含 /run-wbs 和 _run_pipeline
├── db.py            # SQLite 操作
└── routes\
    └── asana_webhook.py  # Webhook 事件处理
```

## 快速恢复

```bash
ssh ubuntu@43.156.171.107 "cd /home/ubuntu/pmo-auto && docker-compose restart"
```
