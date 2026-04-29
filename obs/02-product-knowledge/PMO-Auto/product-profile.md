---
id: pmo-auto-product-profile
type: living
status: published
lang: zh
version: 2.6.0
profile_version: "2.6.0"
published_at: "2026-04-27"
updated_at: "2026-04-27"
author: knowledge_engineer
review_by: [synapse_product_owner, integration_qa]
audience: [team_partner]
product: PMO Auto
owner: synapse_product_owner
committee: [synapse_product_owner, pmo_test_engineer, ai_systems_dev, integration_qa]
---

# PMO Auto — 产品档案

> **委员会使用说明**：当 Lysander 或任何 Agent 接到 PMO Auto 相关任务时，
> 应首先读取此文件获取产品上下文，再开始分析和执行。

## 产品概述

PMO Auto 是 Synapse-PJ 的项目管理自动化系统，通过 n8n 工作流 + pmo-api + Notion + Asana
实现项目从注册到 WBS 导入的全流程自动化。

**核心链路**：Notion Registry（注册） → WF-01（项目初始化）→ Asana 项目 + 成员 + Hub 页面
→ WF-11 轮询 → pmo-api /run-wbs → wbs_to_asana.py → Asana WBS 全层级任务

## 当前版本：v2.6.0 (GA)

- **发布日期**：2026-04-27（锁定包：2026-04-28）
- **版本亮点**：BUG-003 WF-12 激活修复，WBS 导入链路全通，E2E 全 PASS
- **验收结论**：TC-A01~A06 + TC-B（Suite B PRD 合规）全部通过
- **详见**：[releases/v2.6.0.md](releases/v2.6.0.md)

## 系统拓扑

| 组件 | 地址 / ID | 说明 |
|------|-----------|------|
| n8n | https://n8n.lysander.bond | 工作流引擎，37个 Workflows（23 激活 / 14 归档）|
| pmo-api | https://pmo-api.lysander.bond | FastAPI 后端，WBS 导入引擎（ubuntu@43.156.171.107）|
| Notion Registry DB | ccb49243-a892-4691-bf0f-6adb3b1e576d | 项目注册表 |
| Notion Hub DB | 34d114fc-81d9-... | 项目 Hub 页面 |
| Asana Team | ProjectProgressTesting — GID: 1213938170960375 | 任务管理前端 |

## 核心工作流清单

| WF | ID | 功能 | 状态 |
|----|-----|------|------|
| WF-01 | AnR20HucIRaiZPS7 | 项目初始化（触发源）— Notion→Asana 项目+成员+Hub | active |
| WF-11 | VaFr43GafxDrPvEE | WBS 导入触发器（每5分钟轮询）| active |
| WF-12 | p8tPxmkhMcQPcRMh | WBS 工序导入（n8n 原生备用路径）| active ⚠️ 必须保持 active |
| WF-08 | ZCHNwHozL2Ib0urk | Asana 任务完成通知（Webhook 实时）| active |
| WF-09 | atit1zW3VYUL54CJ | 统一通知（Slack DM）| active |

> **WBS 导入主路径**：WF-01 设置"WBS导入状态=待导入" → WF-11 轮询 → POST pmo-api /run-wbs
> → wbs_to_asana.py V1.4 → Asana 任务（幂等保护：任务数>0 自动退出）
>
> **WBS 导入备用路径**：WF-11 → WF-12 webhook（JS Code 原生实现，已激活，当前生产主力走 pmo-api Python 路径）

## 关键约束（必读）

1. **PRINCIPLE-002 (P0)**：测试必须使用 `团队信息维护=已维护` 且 PM/DE/SA/CDE 四个邮箱全填的测试数据；缺任何字段会导致成员加入失败，**不算** BUG — 是测试数据不合规
2. **WF-12 必须保持 active**：每次 n8n 重建/迁移/升级后必须确认 WF-12 (p8tPxmkhMcQPcRMh) active=true，否则 WBS 备用路径断裂（BUG-003 根因）
3. **pmo-api callback_url**：当前未配置 callback_url，WBS 导入通过 pmo-api 直接运行 wbs_to_asana.py，不依赖回调
4. **幂等保护**：wbs_to_asana.py 检测 Asana 任务数>0 自动退出；WF-12 有 wf02-idempotency-check 节点；重复触发安全

## 快速恢复

**一键恢复脚本**：

```bash
cd "C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\_LOCKED_v2.6.0_FULL_20260428"
bash restore.sh <N8N_API_KEY>
```

**锁定包内容**：37个 n8n workflow JSON + pmo-api 完整代码 + config.yaml + docker-compose.yml

**恢复后必须确认**：`WF-12 (p8tPxmkhMcQPcRMh) active=true`

详见：[releases/v2.6.0.md](releases/v2.6.0.md) — 恢复指南章节

## 历史版本

见 [version-history.md](version-history.md)

## 委员会快速入职摘要（Agent 调用时快速消化）

**系统一句话**：PMO Auto 通过 n8n WF-01（项目录入）→ WF-11（WBS触发）→ pmo-api（Python脚本）自动创建 Asana 项目 + 成员 + WBS任务，Notion 作为唯一注册源。

**当前状态**：v2.6.0 GA，全链路 E2E 验收通过，所有 P1 Bug 已关闭。

**3个最重要的约束**：
1. PRINCIPLE-002 (P0)：测试数据必须 团队信息维护=已维护 + 四邮箱非空，否则 TC-A01 FAIL
2. WF-12 必须 active：每次 n8n 重建后手动确认（否则 WBS 备用路径 404）
3. 不要重复调用 /run-wbs：wbs_to_asana.py 有防重入保护，但连续触发会导致"失败"状态误报

**快速定位资源**：
- 恢复脚本：`C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\_LOCKED_v2.6.0_FULL_20260428\restore.sh <N8N_API_KEY>`
- 完整产品档案：`obs/02-product-knowledge/PMO-Auto/product-profile.md`

## 委员会

遇到 PMO Auto 相关任务时，Lysander 应将任务派送给以下委员会成员：

| 角色 | 职责 |
|------|------|
| **synapse_product_owner** | 需求评估、优先级决策、产品方向 |
| **pmo_test_engineer** | E2E 测试设计与执行、验收报告 |
| **ai_systems_dev** | n8n workflow 开发、pmo-api 开发 |
| **integration_qa** | 集成测试、链路验证、质量门禁 |

## 关联文档

- PRD：[../prd-pmo-auto.md](../prd-pmo-auto.md)
- 产品线档案（多产品线视角）：[../product_lines/pmo_auto.md](../product_lines/pmo_auto.md)
- 产品迭代治理规范：[../pmo-auto-product-governance.md](../pmo-auto-product-governance.md)
- V2.0 GA 验收报告：`obs/06-daily-reports/2026-04-23-pmo-v200-acceptance-report-ga.md`
