---
title: Synapse Digital Twin Collaboration Platform
product_id: synapse_platform
status: active
version: v0.2.1
created: 2026-04-28
approved_by: 总裁刘子杨
decision_ref: D-2026-04-28-002
governance: independent_pmc
---

# Synapse Digital Twin Collaboration Platform

**产品代号**：synapse-platform  
**状态**：Active（独立产品线）  
**当前版本**：v0.2.1  
**立项日期**：2026-04-28  
**治理决策**：D-2026-04-28-002  

---

## 一、产品定位

Synapse Digital Twin Collaboration Platform 是一个 **AI 驱动的数字孪生协作平台**，采用 Multi-Agent 架构，以 Slack 作为主交互入口，通过智能 Agent 团队（pm_zh、ops、research、content）协同处理组织协作需求。

**核心价值主张**：
- 将 Slack 消息转化为结构化任务（IntakeClassifier + Case FSM）
- 多专业 Agent 协同响应，减少人工中间层
- 端到端可观测，从消息接收到回复全链路追踪

**技术架构**：
```
Slack DM → IntakeClassifier → Case FSM → PMAgent → Claude Sonnet 4.5 → 周报回复
```

---

## 二、治理模式

**独立 PMC（Product Management Committee）**

- synapse-platform PMC 与 Synapse-Mini 主产品委员会**平行独立**，不汇报、不受主委员会管辖
- PMC 创立日期：2026-04-28（总裁批准）
- PMC 章程路径：`C:/Users/lysanderl_janusd/Projects/synapse-platform/docs/product/pmc-charter.md`
- 日常决策（L1/L2/L3）由 Lysander CEO 在 PMC 框架内处理
- L4 决策（合同、>100万预算、存续级）上报总裁 刘子杨

**PMC 常设成员**：

| 角色 | 身份 | 决策权限 |
|------|------|----------|
| 总裁 刘子杨 | 最终决策者（L4） | 否决权；L4 决策终审 |
| Lysander CEO | 日常管理者（L3） | L1/L2/L3 决策权，PMC 主席 |
| 技术架构师 | 架构评审（L2） | 架构方案建议权 |
| PMO 代表 | 交付管理（L2） | 交付计划建议权 |
| QA 代表 | 质量门禁执行（L2） | 发布阻断权 |

---

## 三、技术治理文档

**技术文档根目录**：`C:/Users/lysanderl_janusd/Projects/synapse-platform/docs/product/`

| 文档 | 路径 | 说明 |
|------|------|------|
| PMC 章程 v1.0 | `docs/product/pmc-charter.md` | 治理结构、决策矩阵、质量门禁 |
| 产品管线策略 | `docs/product/product-pipeline-strategy.md` | 版本路线图与功能优先级 |

**代码仓库**：`C:/Users/lysanderl_janusd/Projects/synapse-platform`

---

## 四、已验证能力（v0.2.1）

端到端验证通过（2026-04-28 首次完整链路验证）：

```
Slack DM 消息接收
    ↓
IntakeClassifier（意图识别与分类）
    ↓
Case FSM（结构化案例状态机创建）
    ↓
PMAgent（项目管理 Agent 路由）
    ↓
Claude Sonnet 4.5 API 调用
    ↓
周报生成 → Slack DM 回复
```

**验证指标**：
- Slack 消息响应链路全通
- Case 创建与状态流转正常
- Claude API 集成稳定
- 周报格式符合预期

---

## 五、产品线负责人

**Lysander CEO**（代理总裁授权）

- 代理依据：总裁 刘子杨 2026-04-28 批准独立治理，授权 Lysander 主持 PMC
- 授权范围：L1/L2/L3 日常产品决策，L4 事项上报总裁

---

## 六、版本记录

| 版本 | 状态 | 关键里程碑 |
|------|------|-----------|
| v0.1.0 | 已发布 | 基础框架搭建，Slack Bolt + Agent 骨架 |
| v0.2.0 | 已发布 | IntakeClassifier + Case FSM + PMAgent 集成 |
| v0.2.1 | 当前版本 ✅ | 首个端到端验证通过（Slack DM → Claude API 全链路） |
| v0.3.0 | **下一里程碑 P0** | RBAC（角色权限控制）+ CI/CD pipeline 上线 |

---

## 七、下一里程碑：v0.3.0（P0）

**目标**：
1. **RBAC**：引入角色权限控制，区分管理员/成员/只读权限
2. **CI/CD**：完整自动化测试 + 部署流水线，达到质量门禁标准

**决策级别**：L2（PMC 周例会决议 → Lysander 签发）

---

## 八、与 Synapse-Mini 主体系的关系

| 维度 | 关系说明 |
|------|---------|
| 治理 | 独立 PMC，不受主委员会管辖 |
| 技术 | 可选择性复用 Synapse Core Multi-Agent 框架 |
| 决策 | 独立决策链，L4 共同上报总裁 |
| 需求池 | 独立管理（`synapse-platform/` 仓库内），不进入主 requirements_pool.yaml |

---

**编制**：knowledge_engineer · **生效**：2026-04-28 · **下次审查**：v0.3.0 发布时或 PMC 要求时
