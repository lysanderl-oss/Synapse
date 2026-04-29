---
id: pmo-auto-monday-product-profile
type: living
status: published
lang: zh
version: 2.0.0
profile_version: "1.0.0"
published_at: "2026-04-29"
updated_at: "2026-04-29"
author: knowledge_engineer
review_by: [synapse_product_owner, integration_qa]
audience: [team_partner]
product: PMO Auto Monday
owner: synapse_product_owner
governance: synapse_main_pmc
committee: [synapse_product_owner, harness_engineer, ai_systems_dev, integration_qa]
---

# PMO Auto Monday — 产品档案

> **委员会使用说明**：当 Lysander 或任何 Agent 接到 PMO Auto Monday 相关任务时，
> 应首先读取此文件获取产品上下文，再开始分析和执行。

## 产品定位

PMO Auto Monday 是 **PMO Auto 的 Monday.com 版本**，与 PMO Auto（Asana 版）平行存在，
两者共用同一业务逻辑（项目初始化 → WBS 生成 → 状态通知），但接入不同的项目管理平台后端。

| 维度 | PMO Auto（Asana 版） | PMO Auto Monday（本产品） |
|------|--------------------|-----------------------|
| 后端平台 | Asana | Monday.com |
| n8n 实例 | n8n.lysander.bond（生产主） | n8n.janusd.io（janusd 副本） |
| 项目注册 | Notion Registry DB | Monday Registry Board |
| 项目文档 | Notion Hub 页面 | Monday WorkDoc（Phase 3） |
| WBS 层级 | Asana Task + Subtask | Monday Board/Group/Item/Subitem + Link Board |
| 关系 | 平行，互不依赖 | 平行，互不依赖 |

> **重要**：PMO Auto Monday 是 Monday.com 后端的**平行产品线**，不是 PMO Auto（Asana 版）的替代品或分支，
> 两条产品线独立演进，不共享运行态数据。

## 当前版本：v2.0.0（Phase 2 GA，2026-04-29）

- **Phase 2 完成日期**：2026-04-29
- **Phase 2 交付内容**：
  - WF-01~09 全部适配完成（03/04/05/06 归档，01/02/08/09 active）
  - pmo-api Monday 路由全部上线：`/run-wbs-monday`、`/webhooks/monday`、`/webhooks/monday/register`、`/webhooks/monday/coverage`
  - WF-01 credential 修复（Notion account `zfnc6V4iDxGmuaf7` + Anthropic account `sv7ExR3w2Pn6J5Zl`），最近 3 次执行全 success
  - M2-A/B/D/F/H PASS，安全验证 95/100
  - Monday Registry Board: 3 items，WBS Board 生成验证通过

## 系统拓扑

| 组件 | 地址 / ID | 说明 |
|------|-----------|------|
| n8n | https://n8n.janusd.io | 工作流引擎（janusd 副本实例） |
| pmo-api | https://pmo-api.lysander.bond | FastAPI 后端（共用，Monday 路由已上线） |
| Monday Registry Board | Board ID: `5095424024` · https://janusd-company.monday.com/boards/5095424024 | 项目注册表，替代 Notion Registry |
| Monday Workspace | Workspace ID: `6203977` | janusd-company.monday.com 主空间 |
| EN Project Registry | Notion DB: `61e17074-706d-4e17-855d-f34b15d6a75c` | 英文项目注册数据源（wbs_to_monday.py 读取） |
| EN WBS Task Database | Notion DB: `922aa4bd-73e5-48d4-aca8-4d7504ce6652` | 英文 WBS 工序数据源（wbs_to_monday.py 读取） |

## 核心链路

```
Monday Registry Board（项目录入）
    │ Init Status = Pending
    ▼
n8n.janusd.io WF-01（项目初始化）
    │
    ▼
pmo-api /run-wbs-monday
  → wbs_to_monday.py
  → Monday Board（PMO_<Code>_WBS）
  → Group（L1 Phase）× N
  → Item（L2 Deliverable）× N
  → Subitem（L3 Work Package）× N
  → Link Board（L4 Task，Phase 3 验证中）
    │
    ▼
pmo-api /create_project_workdoc（Phase 3 实现）
  → Monday WorkDoc（嵌入 WBS Board 视图）
    │
    ▼
Monday Registry Board 回写（board_id + workdoc_url）
    │
    ▼
n8n.janusd.io → Slack 通知（项目初始化完成）
```

## Phase 状态表

| Phase | 内容 | 状态 | 完成时间 |
|-------|------|------|---------|
| Phase 1 | 架构方案 + Registry Board + EN 数据源 + 规格定义 | ✅ 完成 | 2026-04-28 |
| Phase 2 | WF 全适配 + pmo-api 路由上线 + E2E 验收（P0 PASS） | ✅ 完成 | 2026-04-29 |
| Phase 3 | L4 Link Board 验证 + WorkDoc 真实实现 + 双轨期切换 | 🟡 进行中 | — |

## 工作流清单

| WF | 功能 | 状态 |
|----|------|------|
| WF-01 | 项目初始化（Notion EN Registry → Claude 章程 → Monday WBS Board → 回填 Notion） | ✅ active，3次连续 success |
| WF-02 | 任务更新通知 [Monday-ready] | ✅ active |
| WF-03 | [ARCHIVED-Phase3] | ✅ inactive（归档） |
| WF-04 | [ARCHIVED-Phase3] | ✅ inactive（归档） |
| WF-05 | [ARCHIVED-Phase3] | ✅ inactive（归档） |
| WF-06 | [ARCHIVED-Phase3] | ✅ inactive（归档） |
| WF-07 | 会议纪要→Monday 任务 | 🟡 inactive（待 Notion 字段配置） |
| WF-08 | Monday Webhook 完成通知 → Slack | ✅ active |
| WF-09 | Unified Notification [Monday-ready] | ✅ active |

## pmo-api 端点

| 端点 | 方法 | 功能 | 实装状态 |
|------|------|------|---------|
| `/run-wbs-monday` | POST | WBS 生成写入 Monday Board | ✅ 已上线 |
| `/webhooks/monday` | POST | 接收 Monday Webhook，验证 + 转发 | ✅ 已上线 |
| `/webhooks/monday/register` | POST | 向 Monday 注册 Board Webhook | ✅ 已上线 |
| `/webhooks/monday/coverage` | GET | 活跃 Board Webhook 覆盖率检查 | ✅ 已上线 |
| `/create_project_workdoc` | POST | 创建 Monday WorkDoc（标准模板） | 🟡 Phase 3 |
| `/check-monday-status` | GET | 查询 Board 完成状态（兜底） | 🟡 Phase 3 |

## 关键组件

| 组件 | 状态 | 说明 |
|------|------|------|
| MondayClient | ✅ 已实装 | monday_client.py，485 行 |
| wbs_to_monday.py | ✅ 已实装 | 942 行，L1/L2/L3/L4 完整支持 |
| MondayWebhookValidator | ✅ 已实装 | IP 白名单 14 个 CIDR + 时间戳验证 |

## 关键凭证（类型和用途，不含敏感值）

| 凭证 | n8n ID | 用途 |
|------|--------|------|
| Monday API | `l0D3HFmT0ubg5Ewb` | WF-07/08 Monday 操作 |
| Notion account | `zfnc6V4iDxGmuaf7` | WF-01 Notion 读写（7节点） |
| Anthropic account | `sv7ExR3w2Pn6J5Zl` | WF-01 Claude 章程生成 |

## Phase 2 验收结果

| 编号 | 描述 | 结果 |
|------|------|------|
| M2-A | /run-wbs-monday 端到端：Monday Board 中 L1/L2/L3 结构正确创建 | ✅ PASS |
| M2-B | 状态通知链路：Item Done → Webhook → Slack < 30s | ✅ PASS |
| M2-D | 安全验证通过：IP 白名单 + 时间戳验证，安全测试报告 95/100 | ✅ PASS |
| M2-F | Registry Board 数据完整（3 items，WBS Board 生成验证通过） | ✅ PASS |
| M2-H | n8n.janusd.io 新 WF active，WF-03/04/05/06 已归档 | ✅ PASS |
| M2-C | L4 Link Board 可视，Mirror Column 正确 | 🟡 Phase 3 |
| M2-E | WorkDoc 自动生成，URL 回写 Registry Board | 🟡 Phase 3 |
| M2-G | Asana 只读降级（双轨期通过后执行） | DEFERRED |

## 关键约束（必读）

1. **PRINCIPLE-M01 (P0)**：PMO Auto Monday 使用 `n8n.janusd.io` 独立实例，不得混用 `n8n.lysander.bond`（生产主实例）。两实例完全独立，凭证不共享。
2. **PRINCIPLE-M02 (P1)**：Monday Webhook 无 HMAC 签名，安全性依赖 IP 白名单（`MONDAY_IP_WHITELIST`）+ HTTPS + 时间戳验证（±300s）。每次 `monday_webhook_validator.py` 上线后必须确认 IP 白名单为最新官方列表。

## Phase 3 计划

| 项目 | 优先级 | 描述 |
|------|--------|------|
| M2-C L4 Link Board 验证 | P1 | 补充含 L4 节点测试数据，验证 board_relation + Mirror Column |
| M2-E WorkDoc 真实实现 | P1 | Registry Board 加 doc 列，调用 create_workdoc() |
| 双轨期（72h） | P0 | Monday + Asana 并行运行，无回归验证 |
| WF-07 激活 | P2 | Notion EN Registry 加 Monday项目链接 字段 |
| Docker 镜像重建 | P1 | 将 pmo-api 代码变更固化进 Docker 镜像（当前用 docker cp 注入） |
| Asana 只读降级（M2-G） | P2 | 双轨期通过后执行 |

## 快速恢复

| 资源 | 值 |
|------|----|
| Registry Board ID | `5095424024` |
| Registry Board URL | https://janusd-company.monday.com/boards/5095424024 |
| Workspace ID | `6203977` |
| n8n 实例 | https://n8n.janusd.io |
| pmo-api 基础 URL | https://pmo-api.lysander.bond |
| EN Project Registry (Notion) | `61e17074-706d-4e17-855d-f34b15d6a75c` |
| EN WBS Task DB (Notion) | `922aa4bd-73e5-48d4-aca8-4d7504ce6652` |
| 架构文档 | `obs/02-project-knowledge/pmo-monday-auto-architecture-2026.md` |
| VERSION-monday | `pmo-auto/VERSION-monday` |

## 委员会

遇到 PMO Auto Monday 相关任务时，Lysander 应将任务派送给以下委员会成员：

| 角色 | 职责 |
|------|------|
| **synapse_product_owner** | 需求评估、优先级决策、产品方向 |
| **harness_engineer** | 架构设计、WF 改造方案、Board 结构规格 |
| **ai_systems_dev** | pmo-api Monday 路由开发、MondayClient 实装 |
| **integration_qa** | E2E 测试、安全验证、链路验收（M2-A~H 验收标准） |

## 关联文档

- 技术架构方案：[../../02-project-knowledge/pmo-monday-auto-architecture-2026.md](../../02-project-knowledge/pmo-monday-auto-architecture-2026.md)
- PMO Auto（Asana 版）产品档案：[../PMO-Auto/product-profile.md](../PMO-Auto/product-profile.md)
- 产品管线总览：[../_index.md](../_index.md)
