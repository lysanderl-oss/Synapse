---
id: product-knowledge-index
type: living
status: published
lang: zh
version: 1.0.0
published_at: "2026-04-27"
updated_at: "2026-04-27"
author: knowledge_engineer
review_by: [synapse_product_owner]
audience: [team_partner]
title: 产品管线总览
maintainer: knowledge_engineer
---

# 产品管线总览

产品管理委员会知识库入口。当 Lysander 接到与某产品线相关的任务时，
首先读取对应产品的 `product-profile.md` 获取产品上下文。

## 在线产品线

| 产品 | 状态 | 当前版本 | 产品档案 |
|------|------|---------|---------|
| PMO Auto | GA | v2.6.0 | [PMO-Auto/product-profile.md](PMO-Auto/product-profile.md) |
| Synapse 体系 | Active | v3.x | [Synapse/product-profile.md](Synapse/product-profile.md)（待完善）|

> **注**：本目录同时包含历史积累的产品治理文档：
> - [product_lines/](product_lines/) — 多产品线总章（委员会章程体系）
> - [product_committee_charter.md](product_committee_charter.md) — 委员会章程 v2.0（2026-04-24 总裁批准）
> - [requirements_pool.yaml](requirements_pool.yaml) — 需求池（按产品线分区）

## 委员会工作规则

1. **任务触发**：Lysander 收到与某产品线相关需求时，派单给对应产品委员会
2. **上下文获取**：委员会读取 product-profile.md 获取产品状态
3. **协作执行**：委员会提供分析、建议，协助 Lysander 制定方案
4. **知识更新**：每次重要变更后，委员会更新 product-profile.md 和 releases/

## 相关治理文档

- 多产品线总章：[product_lines/index.md](product_lines/index.md)
- 产品委员会章程 v2.0：[product_committee_charter.md](product_committee_charter.md)
- PMO Auto 迭代治理规范：[pmo-auto-product-governance.md](pmo-auto-product-governance.md)
- PRD PMO Auto：[prd-pmo-auto.md](prd-pmo-auto.md)
