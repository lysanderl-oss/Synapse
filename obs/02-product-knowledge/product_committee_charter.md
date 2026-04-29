---
title: Synapse 产品委员会章程 V2
version: v2.0
status: active
created: 2026-04-22
upgraded: 2026-04-24
drafted_by: knowledge_engineer
reviewed_by: strategy_advisor
approved_date: 2026-04-24
approved_by: 总裁刘子杨
supersedes: product_committee_charter.md（V1，2026-04-22）
---

# Synapse 产品委员会章程 V2

**生效日期**：2026-04-24
**版本**：v2.0（正式版）
**授权**：总裁刘子杨批准（2026-04-24）
**主席**：Lysander CEO

> V2 章程于 2026-04-24 经总裁批准正式生效，取代 2026-04-22 建立的 V1 章程。
> V1 章程在 Git 历史中保留，不再作为当前生效版本。

---

## 一、修订背景

V1 章程（2026-04-22 立）仅覆盖 PMO Auto 单一产品线，随 Synapse-PJ 业务扩展，已出现以下治理缺口：

1. **Janus Digital 企业 Agent 产品线**进入酝酿期，无产品治理通道
2. **Gartner 治理对标企业方案**战略方向未纳入委员会
3. **lysander-bond 内容营销**无产品负责人角色
4. 战略层评估（strategy_advisor）指出：**现行章程只覆盖 PMO**，建议扩容至多产品线治理架构

**V2 核心扩容：** 引入产品线常委制 + 需求池分区 + product_ops 扩编。

---

## 二、组织架构升级

### 2.1 常委扩容 — 产品线常委制

在 V1 "常委"结构基础上，为每条产品线设立"产品线常委"席位（每条产品线 1 名产品负责人）。

| 角色 | 成员 | 职责 |
|------|------|------|
| 主席 | Lysander CEO | 主持会议，L3 决策，跨产品线资源分配 |
| 执行秘书 | synapse_product_owner | 议程准备，决议执行，跨产品线路线图协调 |
| 战略常委 | strategy_advisor | 战略对齐评审 |
| 执行审计常委 | execution_auditor | 执行链审计 |
| 质量常委 | integration_qa | 质量门禁总览 |
| **产品线常委（Synapse 内核）** | synapse_core_owner（待任命） | Harness/OBS/Agents 架构演进 |
| **产品线常委（PMO Auto）** | pmo_auto_owner（待任命，暂由 synapse_product_owner 兼任） | PMO 产品迭代 |
| **产品线常委（内容营销）** | content_strategist（新增岗位，见第五节） | lysander-bond 内容战略 |
| **产品线常委（Janus Digital）** | enterprise_architect（新增岗位，见第五节） | 企业 Agent 产品化 |
| **产品线常委（企业治理）** | enterprise_architect（跨线兼任） | Gartner 治理对标方案 |
| 列席（轮值） | 各产品线业务代表 | 一线反馈 |

### 2.2 当前产品线清单（5 条）

| 产品线编码 | 名称 | 状态 |
|-----------|------|------|
| `synapse_core` | Synapse 内核（Harness / OBS / Agents） | 持续迭代 |
| `pmo_auto` | PMO Auto（自动化项目管理） | 已 GA（v2.0） |
| `content_marketing` | lysander-bond 内容营销 | 运营中 |
| `janus_digital` | Janus Digital 企业 Agent 产品线 | 酝酿中 |
| `enterprise_governance` | Gartner 治理对标企业方案 | 酝酿中 |

---

## 三、需求池分区设计

V1 使用单一 `requirements_pool.yaml` 汇总所有需求。V2 按产品线分区，每条需求必须标注 `product:` 字段。

### 3.1 分区字段规范

每条需求条目新增必填字段：

```yaml
REQ-XXX:
  product: synapse_core | pmo_auto | content_marketing | janus_digital | enterprise_governance
  title: "..."
  rice_score: { reach, impact, confidence, effort }
  ...
```

### 3.2 分区视图

- `requirements_pool.yaml` 保持为主池
- 运行期按 `product:` 字段聚合视图（由 requirements_analyst 维护）
- 跨产品线依赖的需求必须额外标注 `depends_on_products: [product_a, product_b]`

---

## 四、决策矩阵扩展

### 4.1 单产品线内部决策

| 事项 | 级别 | 决策者 |
|------|------|--------|
| 单产品线功能评审 | L3 | 产品线常委 + Lysander |
| 单产品线优先级排序 | L3 | 产品线常委 + synapse_product_owner |
| 单产品线 Bug 修复 | L1 | integration_qa（自动） |
| 单产品线大版本发布 | L4 | 总裁验收 |

### 4.2 跨产品线决策（V2 新增）

| 事项 | 级别 | 决策者 |
|------|------|--------|
| 跨产品线资源分配 | L3 | Lysander（综合各产品线常委意见） |
| 跨产品线架构对齐（API/数据模型） | L3 | synapse_product_owner + 相关产品线常委 |
| 产品线新增/废止 | L4 | 总裁 |
| 战略方向（年度路线图） | L4 | 总裁 |
| 商业化/融资决策 | L4 | 总裁（financial_analyst 提供建议） |

---

## 五、product_ops 扩编建议

V2 引入 3 个新岗位以支撑多产品线治理：

### 5.1 content_strategist — 内容战略专员
- **职责：** lysander-bond 内容战略规划、内容日历管理、内容 KPI 对齐
- **汇报：** synapse_product_owner
- **产品线归属：** content_marketing

### 5.2 enterprise_architect — 企业方案架构师
- **职责：** Janus Digital 企业 Agent 产品化、Gartner 治理对标方案设计、企业客户场景建模
- **汇报：** synapse_product_owner
- **产品线归属：** janus_digital + enterprise_governance（跨线）

### 5.3 financial_analyst — 商业化/融资顾问
- **职责：** 产品商业化路径分析、融资场景评估、ROI 建模
- **汇报：** Lysander CEO（L4 决策建议）
- **来源建议：** 可从 graphify 团队借调

---

## 六、保留 V1 核心机制

以下 V1 机制**完整保留**，不因 V2 扩容而改变：

### 6.1 5 质量门禁（不可跳过）
1. PRD 评审：产品线常委 + synapse_product_owner + Lysander + 工程可行性确认
2. 启动会：WBS 拆解 + Sprint 规划
3. Alpha：集成测试通过（integration_qa）
4. Beta：E2E 测试通过（qa_engineer）
5. 发布评审：总裁大版本验收

### 6.2 总裁参与边界
总裁刘子杨仅参与以下场景：
- 季度战略对齐
- 大版本验收（L4）
- 产品线新增/废止（L4）
- 商业化/融资决策（L4）
- 法律/合同等外部事项（L4）

其他所有决策由 Lysander + 产品委员会 + 专家评审解决。

---

## 七、评审与生效流程

1. **草案公示：** 本章程 V2 草案由 knowledge_engineer 撰写（2026-04-23），strategy_advisor 预审
2. **异步评审：** 2026-04-23 总裁查阅决议备忘录
3. **总裁批准：** 2026-04-24 总裁在 Lysander 对话中明确批准："lysander 整体方案批准，请组织执行"
4. **生效：** 2026-04-24 本文件升级为 `product_committee_charter.md`（V2 正式版），V1 在 Git 历史中归档

---

## 八、生效后的联动执行项

本章程 V2 生效同时触发以下执行项：

1. requirements_analyst 撤销 REQ-011（V1 范式下的需求条目）
2. synapse_product_owner 建立 `janus_digital` / `enterprise_governance` 需求池分区
3. capability_architect 创建 3 个新岗位档案（content_strategist / enterprise_architect / financial_analyst）
4. harness_engineer 更新 `agent-CEO/config/organization.yaml`
5. integration_qa 对 REQ-012（WBS 验证）排期

---

## 九、未决事项（待后续委员会推进）

1. 各产品线常委人选待 HR 审核（capability_architect）
2. `content_strategist` / `enterprise_architect` / `financial_analyst` 三个新岗位卡片待 HR 起草
3. `requirements_pool.yaml` 分区迁移方案待 requirements_analyst 制定

---

**章程状态：** active（v2.0 正式版）
**批准日期：** 2026-04-24
**批准人：** 总裁刘子杨
**下次审查：** 产品线新增/废止时，或总裁要求时
