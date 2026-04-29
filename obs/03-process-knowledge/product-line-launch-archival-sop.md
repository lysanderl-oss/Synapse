---
title: 产品线上线知识归档 SOP
sop_id: SOP-PRODUCT-ARCHIVAL-001
version: v1.0
status: active
decision_ref: L2-2026-04-28-001
approved_by: 总裁刘子杨（2026-04-28）
enforcer: knowledge_engineer
created: 2026-04-28
trigger: 任何新产品线 Phase N 交付完成时
---

# 产品线上线知识归档 SOP

## 背景与根因

**触发事件**：Synapse Digital Twin Collaboration Platform 经过 33.6 小时完整开发，于 2026-04-28 完成端到端验证并上线。但原始设计会话（Edge server network architecture）产出的产品设计，未触发知识归档流程，导致：

- `requirements_pool.yaml` 无该产品线条目
- `active_tasks.yaml` 无追踪任务
- OBS 中仅有治理文档，无需求池记录

**本 SOP 目的**：防止"会话产出了产品设计，但没有触发知识归档"这一流程断点再次发生。

---

## 适用范围

以下场景必须执行本 SOP：

| 触发场景 | 说明 |
|----------|------|
| 新产品线 Phase 0（设计完成） | 脚手架 + 产品文档产出后 |
| 新产品线首次 GA 发布 | 端到端验证通过后 |
| 现有产品线重大版本（MINOR+） | 新增功能域时 |
| 产品线独立治理变更 | PMC 成立或治理模式变更时 |

---

## 必须完成的归档检查清单

### ✅ 核心三项（缺一不可）

- [ ] **requirements_pool.yaml** — `meta.product_lines` 已包含该产品线 ID
- [ ] **requirements_pool.yaml** — `backlog` 中有至少 1 条该产品线的需求条目（含 RICE 评分）
- [ ] **active_tasks.yaml** — 有对应的版本追踪任务（含 `product` 字段、`blocker` 字段、`version_target`）

### ✅ 扩展三项（建议完成）

- [ ] **product_lines/index.md** — 产品线信息表已更新
- [ ] **product_lines/{product_id}.md** — 独立产品档案已创建（含定位、治理、版本记录）
- [ ] **decision-log/** — 如有治理变更，L3+ 决策已归档

---

## 执行角色

| 角色 | 职责 |
|------|------|
| **knowledge_engineer** | 主责：执行归档检查清单，完成文件写入 |
| **Lysander CEO** | 审查：确认三项核心归档完成后，方可关闭该 Phase 交付 |
| **execution_auditor** | 监督：Phase 交付清单中若缺少归档确认，标记为执行链断裂 |

---

## 执行步骤

```
Phase N 交付完成
    ↓
knowledge_engineer 执行归档检查清单（上方 6 项）
    ↓
输出归档确认摘要（每项 ✅/❌ + 文件路径）
    ↓
Lysander 审查确认：三项核心全部 ✅
    ↓
Phase 交付正式关闭
```

---

## 历史补录记录

| 产品线 | 补录日期 | 补录原因 | 执行者 |
|--------|----------|----------|--------|
| synapse_platform | 2026-04-28 | 原设计会话（Edge server session）未触发归档流程 | knowledge_engineer |

---

**编制**：knowledge_engineer · **审批**：总裁刘子杨 · **生效**：2026-04-28
