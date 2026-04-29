# PMC 产品管线治理前置制度

> 批准：D-2026-04-29-001（总裁 刘子杨，2026-04-29）
> 适用范围：所有产品管线（lysander.bond / PMO Auto / Synapse Platform / Content Marketing）
> 触发场景：涉及产品管线变更的任务，【0.5】承接阶段读取此文件

## 核心原则

**"What & Why 由 PMC 定义，How & When 由执行团队决定"**

PMC 是"门控"而非"微管理"——通过审查后，执行团队有充分自主权。

---

## PMC 触发规则

### 必须触发 PMC（执行前先输出 Product Brief）

| # | 触发条件 | 示例 |
|---|---------|------|
| 1 | 新产品线启动 / 新 GHA 管线创建 | 新建 pipeline-daily-sync.yml |
| 2 | 现有功能行为变更 | 修改情报日报生成逻辑 |
| 3 | 数据 schema 变更 | 修改 Content Collections frontmatter 字段 |
| 4 | 自动化管线逻辑变更 | 修改 intel-daily.yml 核心步骤 |
| 5 | 对外发布的内容策略调整 | 修改博客双语策略 |

### 豁免触发（直接执行，无需 PMC）

| # | 豁免条件 | 示例 |
|---|---------|------|
| 1 | Bug 修复 | 修复 Astro 6 render API |
| 2 | 样式微调 | 调整颜色/字体 |
| 3 | 配置参数调整 | 修改 cron 时间 |
| 4 | 内部工具优化 | 优化脚本性能 |
| 5 | 日志格式变更 | 修改 Slack 通知文案 |

---

## PMC 三角色

| 角色 | Synapse Agent | 职责 |
|------|--------------|------|
| 产品 Owner | Lysander CEO | 最终决策权，代理总裁执行 L3 产品决策 |
| 策略顾问 | strategy_advisor | Why & What 的专业分析，行业对标 |
| 技术顾问 | harness_engineer / ai_systems_dev | How 的可行性确认，风险评估 |

---

## Product Brief 模板（Synapse 版）

每次触发 PMC 时，Lysander 在【0.5】承接阶段输出此简报：

```
## Product Brief — [功能/变更名称]
**产品线**：lysander.bond / PMO Auto / Synapse Platform / Content Marketing
**诉求来源**：总裁 / 数据驱动 / 市场情报
**问题陈述**：（解决什么具体问题）
**成功标准**：（可量化的验收指标，≥1条）
**范围边界**：
  - In Scope：（3条以内）
  - Out of Scope：（3条以内）
**风险与回滚**：（如何撤销；不可逆操作须标注）
**决策级别**：L1 / L2 / L3 / L4
**PMC 确认**：Lysander（代理）/ 总裁（L4 时必须）
```

---

## 融入【0.5】承接流程

在 Lysander 执行【0.5】承接时：

```
1. 复述目标
2. 判断：任务是否涉及产品管线变更？
   │
   ├─ YES（触发条件之一）→ 输出 Product Brief → PMC 确认（5分钟超时自动放行）→ 继续
   │
   └─ NO（豁免条件）→ 直接进入分级与派单
3. 对齐确认
4. 分级 L1-L4
5. 判断派单
6. 输出派单表
```

**超时自动放行规则**：Product Brief 输出后 5 分钟内无异议，Lysander 自动视为 PMC 通过，继续执行。

---

## 产品档案路由

涉及产品管线任务时，【0.5】承接阶段还需读取对应产品档案：

| 关键词 | 读取档案 |
|--------|---------|
| lysander.bond / 情报 / 博客 / 网站 | `obs/02-product-knowledge/Synapse/product-profile.md` |
| 内容管线 / 博客管线 / 情报管线 | `obs/02-product-knowledge/Content-Marketing/product-profile.md` |
| PMO Auto / WF-XX / Monday | `obs/02-product-knowledge/PMO-Auto/product-profile.md` |
| Synapse Platform / synapse-platform | `obs/02-product-knowledge/Synapse/product-profile.md` |
