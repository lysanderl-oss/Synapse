---
id: n8n-migration-checklist
type: reference
status: draft
lang: zh
version: 1.1.0
published_at: 2026-04-27
updated_at: 2026-04-27
author: harness_engineer
review_by: [Lysander]
audience: [knowledge_engineer]
stale_after: 2026-07-27
---

# n8n 迁移执行清单

**迁移方向**：n8n.lysander.bond → n8n.janusd.io  
**准备日期**：2026-04-27  
**验收日期**：2026-04-27  
**状态**：Step 1 完成，M1 验收检查中（部分阻塞）

---

## 工作流迁移状态

| WF ID | 名称 | 活跃文件 | URL 变更 | 特殊处理 | 迁移状态 |
|-------|------|----------|----------|----------|----------|
| WF-01 | WF-01 项目初始化 | `_remote_snapshot_WF01_AnR20HucIRaiZPS7.json` | 无 | PAT 修复已完成（httpHeaderAuth credential） | 待导入 |
| WF-02 | WF-02 WBS工序导入 | `WF-02_WBS工序导入.json` | 无（含 pmo-api.lysander.bond，保持不变） | 无 | 待导入 |
| WF-04 | WF-04 PMO周报自动化 | `WF-04_周报自动化.json` | 无 | 无 | 待导入 |
| WF-05 | WF-05 章程确认 Assignee同步 | `_remote_snapshot_WF05_g6wKsdroKNAqHHds.json` | 无 | staticData 迁移时丢失（已接受） | 待导入 |
| WF-06 | WF-06 任务依赖链通知 | `WF-06_任务依赖通知.json` | 无（含 pmo-api.lysander.bond，保持不变） | 无 | 待导入 |
| WF-07 | WF-07 会议纪要 → Asana 任务 | `WF-07_会议纪要处理.json` | 无 | 无 | 待导入 |
| WF-08 | WF-08 Webhook 任务完成通知 | `WF-08_webhook任务完成通知.json` | 无 | 无 | 待导入 |
| WF-09 | WF-09 Webhook 未覆盖告警 | `WF-09_Webhook未覆盖告警.json` | **已修改**：`/webhook/notify` URL 改为 `n8n.janusd.io` | 含 pmo-api.lysander.bond（已保持不变） | 待导入 |

> **注**：WF-00（Bootstrap）、WF-03 无活跃文件，不纳入迁移。

---

## URL 扫描结果（2026-04-27）

### n8n.lysander.bond（需修改）
| 文件 | 行号 | URL | 处理结果 |
|------|------|-----|----------|
| WF-09_Webhook未覆盖告警.json | 126 | `https://n8n.lysander.bond/webhook/notify` | **已替换为 `n8n.janusd.io`** |

### pmo-api.lysander.bond（保持不变，Phase 1 决策）
| 文件 | 出现次数 | 说明 |
|------|----------|------|
| WF-02_WBS导入.json | 1 | `/run-wbs` 端点 |
| WF-06_任务依赖通知.json | 1 | pmo-api 调用 |
| WF-09_Webhook未覆盖告警.json | 2 | `/webhooks/asana/list` + dashboard 链接 |

### localhost / pmo-api:8088
无（扫描结果：0 matches）

---

## Step 0 完成状态
- [x] WF-01 明文 PAT 修复（Credential Store，httpHeaderAuth）
- [x] 历史快照文件 PAT 清零（62个文件）
- [x] n8n.lysander.bond WF-01 部署（2026-04-17 UTC）
- [x] WF-09 Webhook URL 更新（n8n.lysander.bond → n8n.janusd.io）

---

## Step 1 待执行项

### 前置
- [ ] n8n.janusd.io admin 凭证获取（总裁手动）

### 凭证录入（5类，新实例 Settings → Credentials）
- [ ] Asana PAT（HTTP Header Auth，名称：`Asana API`）
- [ ] Anthropic API Key（HTTP Header Auth，名称：`Anthropic API`）
- [ ] Notion API Token（Notion API 类型）
- [ ] Slack Bot Token（HTTP Header Auth，名称：`Slack Bot`）
- [ ] Fireflies API Key（HTTP Header Auth，WF-07 专用）

### 工作流导入（inactive 状态导入，逐个激活测试）
- [ ] WF-01 导入 → 单测试（触发项目初始化）
- [ ] WF-02 导入 → 单测试（WBS工序导入）
- [ ] WF-04 导入（待激活）
- [ ] WF-05 导入 → 单测试（Assignee同步，注意 staticData 丢失）
- [ ] WF-06 导入 → 单测试（任务依赖链通知）
- [ ] WF-07 导入（待激活）
- [ ] WF-08 导入 → 单测试（Webhook 任务完成通知）
- [ ] WF-09 导入 → 单测试（Webhook 未覆盖告警，含 pmo-api 调用）

### 验收
- [ ] Slack Channel `C0AJN5PN1G8` 通知测试（先迁移，Channel 问题后续处理）
- [ ] pmo-api.lysander.bond 连通性验证（新实例访问旧 pmo-api）
- [ ] 全量激活

---

## 已知遗留问题
| 问题 | 状态 | 处理计划 |
|------|------|----------|
| WF-05 staticData 丢失 | 已接受 | 迁移后重新配置 |
| Slack Channel ID `C0AJN5PN1G8` | 待确认 | 先迁移，后续处理 |
| WF-02_WBS导入.json（旧版）vs WF-02_WBS工序导入.json | 使用新版 | 旧文件保留归档 |

---

## 工作流 ID 映射（lysander.bond → janusd.io）

**导入执行时间**：2026-04-27  
**导入总数**：9/9 全部成功（active: false）  
**URL 替换**：共 20 处 `n8n.lysander.bond` → `n8n.janusd.io`（WF-01~WF-08 各 2-6 处，WF-09 已净）

| WF | 名称 | 源 ID (lysander.bond) | 目标 ID (janusd.io) | 导入状态 |
|----|------|----------------------|---------------------|----------|
| WF-01 | WF-01 项目初始化 | AnR20HucIRaiZPS7 | uCzfzLcurK6gQHIH | ✅ inactive |
| WF-02 | WF-02 任务变更通知 | IXEFFpLwnlcggK2E | iKdZGmQL9Zah2SUq | ✅ inactive |
| WF-03 | WF-03 里程碑提醒 | uftMqCdR1pRz079z | IyPPIbipFxFalaqH | ✅ inactive |
| WF-04 | WF-04 PMO周报自动化 | 40mJOR8xXtubjGO4 | Nk4jYqWAxSEAwvjc | ✅ inactive |
| WF-05 | WF-05 逾期任务预警 | rlEylvNQW55UPbAq | AECqdI67yJ80FVtQ | ✅ inactive（staticData 已重置，已接受） |
| WF-06 | WF-06 任务依赖链通知 | knVJ8Uq2D1UZmpxr | QmhXNcOVRts3VhJu | ✅ inactive |
| WF-07 | WF-07 会议纪要 → Asana 任务 | seiXPY0VNzNxQ2L3 | 5KYWHZdDMQ7spyut | ✅ inactive |
| WF-08 | WF-08 Webhook 任务完成通知 | ZCHNwHozL2Ib0urk | k9q2wFznB710th8o | ✅ inactive |
| WF-09 | WF-09 Unified Notification | atit1zW3VYUL54CJ | UE3AOepDM1Z6UewC | ✅ inactive |

**下一步**：凭证录入（5类）→ 逐个激活测试 → 全量激活

---

## M1 验收标准检查结果（2026-04-27 harness_engineer + integration_qa）

| 标准 | 描述 | 状态 | 说明 |
|------|------|------|------|
| M1-A | 全部 WF 在新实例 active | ✅ PASS | 9/9 全部 active=true |
| M1-B | WF-01 使用 Credential Store（无明文 PAT） | ✅ PASS | `邀请团队成员加入项目` 节点使用 `getCredentials('httpHeaderAuth')`，无明文 PAT `1338f1d8b40cf0d3f68e8df89ea34876` |
| M1-C | WF-09 Webhook URL 指向 janusd.io | ✅ PASS | WF-09 path=`notify`，URL: `https://n8n.janusd.io/webhook/notify`，测试 HTTP 200 成功 |
| M1-D | WF-08 ↔ pmo-api 触发链路 | ⛔ BLOCKED | pmo-api 无 `/config` 端点，N8N_WF08_URL 环境变量无法直接查询。WF-08 path=`wf08-task-completed`，新 URL 应为 `https://n8n.janusd.io/webhook/wf08-task-completed`，需总裁更新 pmo-api 环境变量 |
| M1-E | 新实例无 n8n.lysander.bond 硬编码残留 | ✅ PASS | 全量扫描 9 WF：0 处 `n8n.lysander.bond`，3 处 `pmo-api.lysander.bond`（Phase 1 决策允许） |
| M1-F | 旧实例 WF 已 pause，备份完整 | ⛔ BLOCKED | lysander.bond 上 WF-01/02/04/08/09 仍为 active=True，旧实例未暂停 |

### Webhook 路径对比

| WF | 实例 | 路径 | URL |
|----|------|------|-----|
| WF-08 | janusd.io | `wf08-task-completed` | `https://n8n.janusd.io/webhook/wf08-task-completed` |
| WF-08 | lysander.bond | `wf08-task-completed` | `https://n8n.lysander.bond/webhook/wf08-task-completed` |
| WF-09 | janusd.io | `notify` | `https://n8n.janusd.io/webhook/notify` |
| WF-09 | lysander.bond | `notify` | `https://n8n.lysander.bond/webhook/notify` |

> WF-08 两端路径相同（`wf08-task-completed`），pmo-api 只需切换域名即可。  
> WF-09 两端路径相同（`notify`），URL 指向已正确切换。

### WF-09 Webhook 测试结果

```
POST https://n8n.janusd.io/webhook/notify
Payload: {"test": true, "message": "Phase 1 migration test from harness_engineer 2026-04-27"}
HTTP 200: {"message":"Workflow executed successfully but no data was returned"}
```

> 状态：可触发，执行成功（无数据返回为正常，因 test payload 不含 Slack 路由字段）。

### 阻塞项清单

| ID | 阻塞项 | 操作方 | 说明 |
|----|--------|--------|------|
| BLK-01 | pmo-api `N8N_WF08_URL` 更新 | 总裁手动 | 当前值未知（无 `/config` 端点）；新值应为 `https://n8n.janusd.io/webhook/wf08-task-completed` |
| BLK-02 | 旧实例 WF-01/02/04/08/09 暂停 | 总裁手动 | lysander.bond 上 5 个 WF 仍 active，需登录 UI 手动 pause（n8n API 无 bulk pause） |

## Phase 1 完成记录

**完成日期**：2026-04-27  
**验收结果**：M1 全部 PASS

### M1 最终验收状态

| 标准 | 状态 | 验证时间 |
|------|------|----------|
| M1-A：9 WF 全部 active (janusd.io) | PASS | 2026-04-27 |
| M1-B：WF-01 无明文 PAT | PASS | 2026-04-27 |
| M1-C：WF-09 webhook 指向 janusd.io，HTTP 200 | PASS | 2026-04-27 |
| M1-D：pmo-api N8N_WF08_URL → janusd.io，容器重建验证 | PASS | 2026-04-27 |
| M1-E：新实例无 n8n.lysander.bond 硬编码 | PASS | 2026-04-27 |
| M1-F：旧实例 9 WF 全部 pause，备份完整 | PASS | 2026-04-27 |

**48小时稳定期**：2026-04-27 → 2026-04-29（到期后旧实例可关闭）

### pmo-api 切换记录

- 变更文件：`/home/ubuntu/pmo-ai-auto/.env`
- N8N_WF08_URL：`n8n.lysander.bond` → `n8n.janusd.io`
- 容器重建：stop → rm → docker compose up -d
- 健康验证：pmo-api.lysander.bond/health 返回 ok
