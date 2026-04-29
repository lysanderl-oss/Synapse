---
title: Marketing — 品牌叙事与市场定位
product_id: marketing
status: published
profile_version: 1.0.0
created: 2026-04-29
updated: 2026-04-29
approved_by: 总裁刘子杨
decision_ref: D-2026-04-29-001
governance: synapse_main_pmc
routing_active: true
supersedes: [content_marketing, janus_digital, enterprise_governance]
---

# Marketing — 品牌叙事与市场定位

**产品代号**：marketing  
**状态**：Published  
**Profile 版本**：1.0.0  
**生效日期**：2026-04-29  
**整合来源**：Content Marketing + Janus Digital + Enterprise Governance

---

## 一、产品定位

Marketing 是 Synapse-PJ 的**品牌叙事与市场定位伞形产品线**，统一管理三类市场资产：

| 子方向 | 内容 | 来源 |
|--------|------|------|
| **品牌内容** | 博客管线（v2.0 GA）、情报管线（v1.2.0 GA）、双语策略 | 原 Content Marketing |
| **产品定位叙事** | Janus Digital 市场定位、竞品分析、Q2 路线图、投资人叙事框架 | 原 Janus Digital |
| **市场教育材料** | Enterprise Governance 白皮书、DeepMind/Gartner 框架对标、治理咨询叙事 | 原 Enterprise Governance |

**核心逻辑**：三个子方向当前阶段的主要工作均为市场叙事建构，共享相同的执行团队，统一治理降低管理摩擦。

---

## 二、关键约束（PRINCIPLE）

| # | 约束 | 说明 |
|---|------|------|
| M-P1 | **内容发布走 lysander.bond 管线** | 所有品牌内容的对外发布必须经过 lysander.bond GHA 管线，不直接操作站点文件 |
| M-P2 | **叙事一致性优先** | 三个子方向的对外叙事必须统一（Synapse 治理架构为技术信用背书），由 graphify_strategist 负责跨方向叙事对齐 |
| M-P3 | **白皮书/研究内容须 QA 审查** | 所有对外发布的白皮书、竞品分析必须经 integration_qa 事实核查，不发布未经核查的数据 |

---

## 三、子方向演进路径（产品化毕业触发条件）

### Janus Digital 产品化触发条件
当以下任一条件满足时，Janus Digital 自动触发从 Marketing 拆出为独立产品线：
- [ ] 第一个付费客户合同谈判启动
- [ ] Q2 路线图完成并获总裁批准，明确产品 SKU 和定价
- [ ] 有独立的技术交付物（代码仓库或可部署服务）需要独立版本管理

### Enterprise Governance 产品化触发条件
当以下任一条件满足时，Enterprise Governance 自动触发从 Marketing 拆出为独立产品线：
- [ ] 白皮书 v1.0 完成并开始用于客户沟通
- [ ] 第一个企业治理咨询项目启动
- [ ] 形成可重复交付的评估工具或框架产品

**拆出工作量预估**：约 2-4 小时（新建 product-profile + 更新路由表），可逆操作。

---

## 四、当前里程碑

### 品牌内容子方向
| 里程碑 | 状态 |
|--------|------|
| 博客管线 v2.0 GA | ✅ 完成（2026-04-28） |
| 情报管线 v1.2.0 GA（Intelligence Hub）| ✅ 完成（2026-04-28） |
| 双语策略全站覆盖 | ✅ 完成（2026-04-26） |
| pipeline-daily-sync 每日自动刷新 | ✅ 完成（2026-04-29） |

### 产品定位叙事子方向（原 Janus Digital）
| 里程碑 | 状态 |
|--------|------|
| 立项（REQ-JD-001）| ✅ 完成（2026-04-24） |
| 竞品差异化分析 | ✅ 完成（INTEL-20260427-002） |
| Q2 Agent 产品路线图 | 🟡 进行中（graphify_strategist） |
| 投资人叙事框架 | 🟡 进行中（INTEL-20260427-006） |

### 市场教育材料子方向（原 Enterprise Governance）
| 里程碑 | 状态 |
|--------|------|
| 立项（REQ-EG-001）| ✅ 完成（2026-04-24） |
| DeepMind 框架映射 + 白皮书草稿 v1 | 🟡 **进行中，本周交付**（INTEL-20260428-005） |
| Stanford HAI 对照研究 | 🟡 进行中（INTEL-20260427-004） |
| 服务定价与交付标准 | ⬜ 未启动 |

---

## 五、委员会成员

| 角色 | Synapse Agent | 职责 |
|------|--------------|------|
| 产品 Owner | Lysander CEO | 产品方向决策（L3） |
| 品牌内容 | content_strategist | 博客策略、内容质量 |
| 市场定位 | graphify_strategist | 竞品分析、客户叙事、跨方向叙事一致性 |
| 财务策略 | financial_analyst | 定价模型、融资策略 |
| 治理叙事 | enterprise_architect | 白皮书、Gartner/DeepMind 框架对标 |
| 知识沉淀 | knowledge_engineer | OBS 归档、文档标准化 |
| 发布质量 | integration_qa | QA 门禁、事实核查 |
| 技术支持 | harness_engineer | 管线配置、GHA 维护 |

---

## 六、快速恢复

- 博客管线脚本：`scripts/auto-publish-blog.py`
- 情报发布脚本：`scripts/intelligence/publish_to_bond.py`
- 竞品分析报告：`obs/01-team-knowledge/HR/intelligence-actions/INTEL-20260427-002-*.md`
- 白皮书任务：`active_tasks.yaml` → INTEL-20260428-005
- 历史档案：`obs/02-product-knowledge/Content-Marketing/`（archived）、`obs/02-product-knowledge/Janus-Digital/`（archived）、`obs/02-product-knowledge/Enterprise-Governance/`（archived）

---

**编制**：knowledge_engineer · **生效**：2026-04-29 · **下次审查**：任一子方向触发产品化毕业条件时
