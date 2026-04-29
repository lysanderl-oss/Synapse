# 情报管线多租户扩展 — 架构与使用指南

**版本**：v0.1 draft
**适用产品线**：janus_digital / enterprise_governance（主）+ synapse_core（底座）
**当前状态**：单租户生产运行（Synapse-PJ 内部），多租户扩展骨架预留 @ Q2 Week 4 → Q3 灰度

---

## 一、为什么需要多租户

### 1.1 Synapse-PJ 的产品化命题

情报管线的第一批客户场景：
- **中小科技公司 CTO**：希望获得结构化 AI/Agent 情报（每日分析 + 专家评分），用低成本替代自己筛选海量信息
- **投资机构分析师**：希望快速了解 AI 赛道动态，辅助投资决策
- **战略咨询独立顾问**：希望用 AI 助手替代初级分析师，聚焦高价值输出

这些客户不可能让你把他们的数据混在一起跑，更不可能共用一个 Slack 告警 channel。所以**租户隔离是企业软件的基线**，不是加分项。

### 1.2 当前架构的局限

V0.1（Q2 Week 1-3 实施版本）的状态：
- ✅ 云端自动运行（GitHub Actions 调度）
- ✅ 按日产出情报日报 + 行动报告
- ✅ 可观测（心跳监控 + Slack 通知）
- ❌ 只有一个租户（Synapse-PJ）
- ❌ 所有数据混在 synapse-ops 仓库
- ❌ 无法同时服务客户 A 和客户 B

## 二、多租户架构设计（Q3-Q4 目标）

### 2.1 隔离层次（3 种选择）

| 方案 | 隔离粒度 | 运维成本 | 安全性 | 适用 |
|------|:------:|:------:|:------:|:----:|
| **Strong isolation** | 每租户一个 GitHub repo + 独立 secrets | 高 | 极高 | Enterprise 客户（白标 / 私有化）|
| **Config-based isolation** | 单 repo，多 config，目录隔离 | 低 | 中 | Pro / Starter 客户 |
| **Shared with tagging** | 单 repo + 单 config，元数据标租户 | 最低 | 低 | 不推荐（仅 demo）|

**Lysander 推荐**：默认采用 **Config-based isolation** + Enterprise 客户上升到 **Strong isolation**。两档组合覆盖 95% 场景，运维成本可控。

### 2.2 租户配置模型

每个租户一份 `tenants/{tenant_id}/config.yaml`：

```yaml
tenant_id: acme-corp
name: ACME Corporation
tier: pro
owner_email: cto@acme.com
created: 2026-08-15

intelligence:
  topics:
    - AI agents
    - Vertical SaaS
  model: claude-sonnet-4-6
  daily_schedule: "04:00"  # UTC
  language: en  # or zh

output:
  reports_dir: tenants/acme-corp/reports/
  format: html  # or pdf / notion

notifications:
  slack_webhook: <tenant-specific webhook>
  email: cto@acme.com,cfo@acme.com

branding:
  logo_url: https://acme.com/logo.svg
  primary_color: "#0066cc"
  footer: "Powered by Janus Digital"

data_sovereignty:
  export_enabled: true
  retention_days: 365
```

### 2.3 数据隔离

每个租户独立的目录结构：
- `tenants/{tenant_id}/reports/` — 输出目录（日报 / 行动报告）
- `tenants/{tenant_id}/prompts/` — prompt overrides（可选，默认继承 synapse_core）
- `tenants/{tenant_id}/history/` — 历史归档（yaml / json）
- `tenants/{tenant_id}/logs/` — 运行日志（心跳 / API 消耗）

### 2.4 计费与成本归属

通过 Claude API 的 metadata 字段按租户打标：

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[...],
    metadata={"user_id": f"tenant:{tenant_id}"}
)
```

按 `user_id` aggregate 成本 → 月度对账 → 驱动 Stripe 出账单。

## 三、使用场景示意（假设已上线 Q4 商品化）

### 3.1 客户 onboarding 流程

**步骤 1**：客户访问 https://janus.digital，选择 Pro 计划（$899/月）
**步骤 2**：填写偏好（关注领域 / 语言 / 通知方式 / Slack webhook）
**步骤 3**：系统自动：
- 创建 `tenants/acme-corp/config.yaml`
- 生成 tenant-specific API key（若客户要求导出）
- 触发首次情报日报（demo 报告）

**步骤 4**：客户每日 Dubai 08:00（或自选时区）收到情报日报 + 行动报告

### 3.2 客户 dashboard（未来 UI）

类似：
```
ACME Corp 情报管线 Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 近 30 天产出
  - 情报日报：30 份 ✅
  - 行动报告：30 份 ✅
  - 心跳健康率：100%
  - API 消耗：42K tokens（$35 / $80 预算）

📝 最新 3 份报告
  - 2026-08-30 情报日报（12 条情报）[查看 HTML]
  - 2026-08-30 行动报告（4 专家评分）[查看 MD]
  - 2026-08-29 情报日报（10 条）[查看]

⚙️ 配置
  - 语言：英文 / 时区：UTC+4 Dubai
  - 主题：AI agents / Vertical SaaS
  - 通知：Slack / Email
```

### 3.3 数据导出（Data Sovereignty）

客户随时可导出：
- 所有历史情报（YAML / JSON）
- 配置（yaml）
- 管线运行状态

API：`GET /api/tenants/{tenant_id}/export?format=yaml`

## 四、Synapse-PJ 内部使用（当前单租户模式）

Synapse-PJ 作为 V0.1 阶段的**第一个"租户"**（实际上是体系本身）：

- tenant_id: `synapse-pj`
- repo: synapse-ops（单 repo 模式）
- output: `obs/06-daily-reports/*-intelligence-daily.html`
- schedule: Dubai 08:00
- notifications: n8n WF-09 → Slack

**当前你（总裁）每天看到的情报日报 = 自己的"租户 0"**。Q3 Q4 只是把这个模式复制多份，每份隔离。

### 当前架构的"多租户友好"基因

Week 1 设计时已嵌入以下"未来多租户 ready"特性：

1. **凭证通过 GitHub Secrets 注入**（而非硬编码）— 不同租户可用不同 secrets scope
2. **prompt 抽取为版本化文件**（`agent-CEO/prompts/`）— 不同租户可引用不同 prompt variant
3. **配置驱动**（`CLAUDE.md` / `active_tasks.yaml`）— 不同租户可 fork 配置
4. **输出目录可配置**（`scripts/intelligence/shared_context.py` 的 `REPORTS_DIR`）— 不同租户可指向不同目录
5. **模型参数可配置**（`DEFAULT_MODEL` / `DEFAULT_MAX_TOKENS`）— 不同租户可选 Claude/GLM/Qwen

## 五、实施路线（RFC 级粗略）

### Q2 Week 4（预留骨架）
- 抽象 `tenant_id` 概念到代码（默认 = `synapse-pj`）
- 目录结构预留（`tenants/synapse-pj/`）
- config 可选加载机制（兼容当前硬编码路径）

### Q3（2026-07-01 起，灰度）
- 灰度 ≤3 付费客户（免费试用 + 合同签署）
- 独立安全审计（第三方）
- 租户隔离代码实现（config-based）
- 基础 dashboard（极简，只读）

### Q4（2026-10-01 起，商品化）
- Janus Digital SKU 正式商品化
- Tier 1 Starter $299 / Tier 2 Pro $899 / Enterprise $2000+
- SOC 2 合规 + Stripe 支付 + 自助 onboarding

### 尚未实现（需要 Q3 启用）

1. 租户隔离层（独立 prompt / template / config / output）
2. 租户身份认证（谁是客户 A vs 客户 B）
3. 计费与成本归属（按租户统计 API 消耗）
4. 租户 dashboard（客户查看自己的管线状态）
5. 数据主权 API（客户导出/导入历史）
6. 告警路径自定义（客户指定自己的 Slack / Email / Webhook）
7. 品牌白标（报告页头可配置客户 logo）

## 六、关键决策等待总裁批准

1. **Q3 灰度客户是否由总裁邀请 vs Lysander 主动 outreach？**
2. **定价三档是否调整？**（当前：$299 / $899 / $2000+）
3. **第一批灰度客户领域优先级：SaaS CTO / 投资人 / 咨询顾问 — 哪个先？**

（这些决策将在 Q2 结束 + Q3 启动前向总裁正式呈报，本文档仅是介绍性说明。）

## 七、与其他产品线的协同

- **synapse_core**：提供底座（Agent 协同 / CEO Guard / 执行链），多租户扩展复用这套基础设施
- **pmo_auto**：未来可作为客户的 PMO 集成示例（跨产品集成 / 增值服务）
- **content_marketing**：情报管线本身就是 Content 的素材池（内容复用）
- **enterprise_governance**：企业客户情报管线 + 治理方案打包销售（高客单价）

---

## 附录：技术决策记录

- 基础方案选型见：`obs/06-daily-reports/2026-04-24-intelligence-pipeline-roundtable.md`
- Week 1-3 实施：见各 week completion report
- REQ-INFRA-003 需求：`requirements_pool.yaml` 行 390
