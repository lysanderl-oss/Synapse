---
id: pipeline-product-governance
type: core
status: published
lang: zh
version: 1.0
published_at: 2026-04-26
updated_at: 2026-04-26
author: harness_engineer + execution_auditor + knowledge_engineer
review_by: [Lysander, decision_advisor]
audience: [team_partner, technical_builder]
stale_after: 2026-10-26
---

# 管线产品（Pipeline Product）治理元规则

## BLUF

总裁 2026-04-26 决策：lysander.bond 进入"管线产品"治理框架。所有未来变更基于版本基线管理，三层版本（MAJOR/MINOR/PATCH）对应不同审批层级（L4/L3/L2），每版本必须 UAT + 度量快照。

---

## 1. 元规则定义

### 1.1 什么是"管线产品"？

"管线产品"（Pipeline Product）是指：
- **持续演进**而非一次性交付的产品（lysander.bond 网站属此类）
- 变更**版本化、可回滚、可度量**
- 每次发布都形成**基线**（baseline），后续变更基于此基线增量
- 流经**审批门禁**（review gate）—— 不同层级变更走不同审批

与"管线产品"对立的是"项目"模式（一次交付完即结束）。lysander.bond 是长期运营的对外品牌阵地，必须以管线模式管理。

### 1.2 三层版本约定（Semantic Versioning）

| 层级 | 模式 | 例子 | 审批层级 | UAT 要求 |
|------|------|------|----------|----------|
| **MAJOR** | `v2.0+` | 架构重写 / 品牌转向 / 商业模式变更 | **L4 总裁审批** | 三轮 UAT（产品 + 质量 + 战略） |
| **MINOR** | `v1.2`, `v1.3` | 战略内容 / IA 调整 / 新版块 / 双语扩展 | **L3 Lysander 决策** | 双轮 UAT（产品 + 质量） |
| **PATCH** | `v1.1.1` | Bug 修复 / 文案润色 / 链接修正 / SEO 调整 | **L2 Lysander 自主** | 仅质量验证 |

### 1.3 变更分类标签（每个 commit/PR 必须带一个）

- `strategic` — 影响主线故事、品牌、商业模式或战略内容
- `feature` — 新页面 / 版块 / 能力
- `fix` — Bug 修复 / 回归修复
- `chore` — 工具 / 构建 / 部署维护
- `docs` — 文档 / 治理 / 元规则
- `i18n` — 翻译 / locale 路由 / hreflang

### 1.4 审批门禁（Review Gates）

**MAJOR 发布门禁（总裁审批）：**
1. 产品 UAT（3 个用户角色 journey 走查）
2. 质量 UAT（HTTP / i18n / SEO / 性能 / 回归）
3. 战略评审（智囊团：strategy_advisor + execution_auditor + decision_advisor）
4. 总裁 L4 批准
5. 版本锁定 + git tag + CHANGELOG 条目

**MINOR 发布门禁（Lysander 决策）：**
1. 产品 UAT
2. 质量 UAT
3. Lysander 审查（双 UAT 通过 ≥85/100 自动批准）
4. 版本锁定 + git tag + CHANGELOG 条目
5. **总裁简报**（发布后摘要）

**PATCH 发布门禁（Lysander 自主）：**
1. 质量验证（HTTP 回归 + UAT 抽查）
2. 版本号递增 + CHANGELOG 条目
3. 无需简报，除非是 P0 修复

### 1.5 度量基线（每版本必须记录）

```yaml
version: vX.Y.Z
released_at: ISO date
http_health:
  total_pages_checked: N
  pass_rate: ...
seo:
  hreflang_coverage: ...
  sitemap_url_count: ...
  canonical_coverage: ...
i18n:
  bilingual_pages: ...
  ssot_drift_count: 0  # 必须为 0
content:
  blog_count: N
  bilingual_blog_pct: ...
governance:
  license_present: yes/no
  ssot_synced: yes/no
```

存于 `pipeline-metrics/v{X.Y.Z}.yaml`。

### 1.6 分支策略

- `main` — 当前生产基线
- `release/v{X.Y.Z}` — 候选发布分支（可选，MAJOR 用）
- `hotfix/*` — PATCH 分支（基于 main）
- `feature/*` — MINOR 功能分支

### 1.7 回滚路径

每个版本 tag 都是回滚目标：
```bash
git checkout v1.0-bilingual  # 回滚到战略改造前
```

生产回滚流程：
1. 识别回归（UAT 或发布后监控）
2. Lysander 决定回滚目标
3. `git checkout <prior-tag>` + 强制部署
4. 全员通报回滚原因
5. 事后复盘报告

---

## 2. 已建立的基线

| 版本 | 日期 | 类型 | 简述 |
|------|------|------|------|
| **v1.0-bilingual** | 2026-04-25 | MINOR | 全站 100% 中英双语化达成（5 主页 + 8 Forge + 7 Academy + 34 Blog × 双语） |
| **v1.1.0-strategic-overhaul** | 2026-04-26 | MINOR | 战略改造（Janus 去除 + 品牌统一 + Academy SaaS 删除 + BSL-1.1 LICENSE + 元规则修复 + Pipeline 框架建立） |

---

## 3. RACI

| 动作 | R（Responsible） | A（Accountable） | C（Consulted） | I（Informed） |
|------|------------------|------------------|----------------|---------------|
| 提议 MAJOR | strategy_advisor + Lysander | 总裁 | 评审团 | 全团队 |
| 提议 MINOR | product_manager + Lysander | Lysander | UAT 团队 | 总裁简报 |
| 提议 PATCH | ai_systems_dev | Lysander | integration_qa | 内部 |
| 执行 UAT（产品） | product_manager | Lysander | content_strategist | — |
| 执行 UAT（质量） | integration_qa | Lysander | ai_systems_dev | — |
| 战略评审 | strategy_advisor | Lysander | decision_advisor + execution_auditor | 总裁 |
| 度量基线收集 | integration_qa | Lysander | — | — |
| 回滚决策 | Lysander | 总裁（MAJOR）/ Lysander（MINOR/PATCH） | execution_auditor | 全团队 |

---

## 4. 与现有 Harness 规则关系

- **fact-SSOT 元规则**：度量基线中的 `ssot_drift_count: 0` 强制约束，与 fact-SSOT 联动防御数字漂移
- **双语博客 SOP**：MINOR/MAJOR 必须保证 i18n 度量项 100% 双语率
- **SSOT 同步管线**：`synapse-stats.yaml` 等 SSOT 在每版本验证同步
- **CEO Guard / 执行链**：MAJOR/MINOR 变更走标准执行链 0.5 → ① → ② → ③ → ④

---

## 5. 违规处理

未经版本锁定直接 push 到 main 触发线上变更 → 视为违反元规则。

处理路径：
1. **告警**：execution_auditor 检测到 main 分支有未关联 tag 的非 PATCH 级变更
2. **复盘**：Lysander 召集变更责任人复盘，判定违规级别（轻 / 重 / 严重）
3. **补救**：
   - 轻度：补打 tag + 补 CHANGELOG + 补度量基线
   - 重度：Hotfix 锁版 + 临时回滚至上一基线 + 重走 UAT
   - 严重：触发 P0 治理事件 → 总裁通报 → 全团队复盘

---

## 6. 维护与演进

- **3 个月一次**审查本元规则（next: 2026-07-26）
- 元规则本身的变更视为 **MAJOR 级治理变更**，需总裁批准
- 每次新版本发布后自动检查本规则是否需要扩展（执行审计师责任）

---

## 引用

- `lysander-bond/PIPELINE.md` — 英文版治理文档（仓库内）
- `lysander-bond/CHANGELOG.md` — 版本变更历史
- `lysander-bond/pipeline-metrics/` — 度量基线快照目录
- `obs/04-decision-knowledge/2026-04-26-strategic-overhaul-approval-package.md` — 触发本规则建立的总裁决策包
