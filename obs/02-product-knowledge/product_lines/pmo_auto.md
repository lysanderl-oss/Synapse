# PMO Auto — 项目管理自动化产品

**立项日期**：V1.x 系列长期迭代，V2.0 于 2026-04-23 正式 GA
**成熟度**：生产运行（当前版本 pmo-auto-2.0.3）
**产品线常委**：synapse_product_owner
**汇报链**：synapse_product_owner → Lysander CEO → 总裁（L4 大版本验收）
**战略依据**：从作坊式研发 → 双轨制（产品轨 + 工程轨），V1.7.0 遗留 15 条源码审计差异清零

## 产品线定义

PMO Auto 是基于 n8n 的项目管理自动化产品线，实现项目从创建到任务完成通知的**全链路自动化编排**。以 Asana 为项目前端、Notion 为注册表、Slack 为通知通道，通过 WF-01 ~ WF-08 工作流串联 L1 项目 → L4 子任务的全生命周期。

区别于传统 PMO 工具，PMO Auto **不做新前端、不做重平台**，专注"编排 + 治理 + 实时通知"三位一体的自动化落地能力，Webhook 已从 2 项目灰度扩展到 36 活跃项目全量覆盖。

## 版本轨迹

| Tag | 发布日期 | 关联需求 | 变更摘要 |
|-----|---------|---------|---------|
| `pmo-auto-2.0.0-ga` | 2026-04-23 | REQ-001 / 005 / 009 | V2.0 正式发布，TC-A01~A06 全部 PASS |
| `pmo-auto-2.0.1` | 2026-04-24 | REQ-010 | SSL 补丁 — pmo-api.lysander.bond HTTPS 上线 |
| `pmo-auto-2.0.3` | 2026-04-24 | REQ-012-D-01 | WF-05 OOM 修复 — n8n runner 堆内存 4096MB |

**注**：v2.0.2 跳号保留给 REQ-012-TC-01 方法论升级（无代码变更，未独立打 tag）。

## 核心工作流

| 工作流 | 职责 |
|--------|-----|
| WF-01 | Notion Registry → Asana 项目初始化 + Hub 页面生成 |
| WF-02 | WBS 轮询触发（`团队信息维护=已维护` filter）|
| WF-03 | WBS Sections 创建（L1/L2）|
| WF-04 | WBS Tasks 创建（L3 + 依赖）|
| WF-05 | Assignee 分配（含 L4 子任务 + 通知）|
| WF-06 | 兜底轮询完成通知 |
| WF-07 | 预留 |
| WF-08 | Webhook 实时完成通知（替代 WF-06 轮询的主要路径）|

## 核心能力

1. **全量活跃项目 Webhook 覆盖**：73 活跃订阅（36 项目 × 2 事件类型）
2. **实时任务完成通知**：Asana 任务完成 → WF-08 → Slack DM（延迟 < 5 秒）
3. **WBS 全层级自动导入**：L1 项目 → L2 阶段 → L3 工序 → L4 子任务
4. **凭证集中管理**：n8n Credentials Store（httpHeaderAuth），使用 `requestWithAuthentication`，杜绝硬编码
5. **子域名独立对外**：pmo-api.lysander.bond（Let's Encrypt SSL，有效期至 2026-07-23）
6. **双轨制治理**：产品轨（需求池 + PRD）+ 工程轨（n8n 工作流 + FastAPI 服务），5 质量门禁不可绕过

## 与其他产品线的关系

- **Synapse Core**：PMO Auto 构建在 Core 的 Harness / Agent 架构之上；PMO 方法论升级（REQ-012-TC-01）反哺 Core 的 QA 门禁规则
- **Janus Digital**：未来可作为 Janus Digital Agent 产品的参考实施案例
- **Enterprise Governance**：PMO Auto 双轨制 + 5 质量门禁机制是企业交付方案的参考案例
- **Content Marketing**：PMO Auto 开发历程可写入内容矩阵（B 类问题日志 + C 类方法论）

## 需求池分区

`product: pmo_auto`

## 当前生产运行事实（2026-04-24）

| 状态 | 需求 |
|------|------|
| **Shipped** | REQ-001 / 005 / 009 / 010 / 012-D-01 / 012-TC-01 |
| **In progress** | — |
| **Deferred 至 v2.1** | REQ-002 / 003 / 004 |
| **Wontfix** | REQ-011（n8n Variables 迁移，总裁决定不升级付费套餐）|
| **Scheduled** | REQ-012-WBS-QA-001（WBS 全面验证，2026-04-28 启动）|

## 治理机制

- **日常功能评审**：synapse_product_owner + Lysander（L3）
- **技术方案**：harness_engineer + n8n_ops（L2）
- **Bug 修复**：integration_qa 自动（L1）
- **大版本发布**：总裁验收（L4）

## 下一步

1. REQ-012 WBS 全面验证（2026-04-28 启动，integration_qa 执行）
2. V2.1 backlog 规划（REQ-002 / 003 / 004 重新评估）
3. V2.0 GA 经验积累至方法论（反哺 Synapse Core QA 门禁规则）

---

**关联文件**：
- PRD: `obs/02-product-knowledge/prd-pmo-auto.md`
- V2.0 GA 验收报告: `obs/06-daily-reports/2026-04-23-pmo-v200-acceptance-report-ga.md`
- V2.0.3 WF-05 修复事件: `obs/06-daily-reports/2026-04-24-wf05-crash-incident.md`
- 版本文件: `pmo-auto/VERSION`
