---
id: bilingual-blog-production-sop
type: core
status: published
lang: zh
version: 1.1
published_at: 2026-04-24
updated_at: 2026-04-24
author: knowledge_engineer
review_by: [content_strategist, execution_auditor]
audience: [content_strategist, knowledge_engineer, team_partner]
stale_after: 2026-10-24
---

# 双语博客生产 SOP（Bilingual Blog Production SOP）

## 决策背景

**2026-04-24 总裁 L4 决策**：今后所有新博客内容生产，必须同时产出**中英双语版本**并在网站发布。

此决策将"双语同发"从可选最佳实践提升为**强制生产标准**，纳入 integration_qa 质量门禁，与 content_strategist KPI 直接挂钩。决策意图：扩大 Synapse-PJ 的国际受众覆盖（lysander-bond 英语读者群 + 中文核心读者群并重），确立"AI 治理纪实"品牌在中英双语市场的叙事主权。

## 适用范围

- ✅ 今后所有新博客（从 2026-04-25 起）
- ✅ 历史博客（33 篇存量）：**同样纳入双语范围**（总裁 2026-04-24 修正决策 ② = B 全站 100% 双语）
  - P1 级（评为"英文价值高"的 5 篇）：full 再创作（1500-2500 字）
  - P2 级（9 篇）：full 翻译 + 润色
  - P3 级（19 篇）：允许"摘要式英文版"（300-500 字精华 + 中文原文链接）以减轻产能压力
  - 无"保留中文不译"分类
- ✅ 跨类别适用：A 类系统拆解 / B 类问题日志 / C 类方法论提炼 / D 类进化记录 四类均需双语
- ⚠ 例外：内部工作日志（非公开发布）不在本 SOP 范围内

## 生产流程（8 步）

### 第 1 步：选题（content_strategist）
- 从内容日历选题池 + 当日情报日报中挑选
- 明确 target 受众（4 Pillars 中的哪一类）
- 初步判断语言首发（中文或英文），另一语言延迟 <2 周
- 选题卡入 `obs/04-content-pipeline/` 对应周目录

### 第 2 步：大纲（content_strategist + 领域专家）
- 写出主语言（中文）大纲
- 标注术语（与 `glossary.yaml` 对齐）
- 通过 Lysander 初步确认（S 级，不上报总裁）
- 大纲阶段即预判英文版改写方向（避免后期返工）

### 第 3 步：主语言草稿（content_creator）
- 按大纲产出 1500-2500 字
- frontmatter 含 `lang: zh`, `translation_of: null`, `hasEnglish: true`, `status: draft`
- 技术细节参考 `harness_engineer` 专业校对（A 类内容强制）

### 第 4 步：视觉素材（content_visual）
- Hero 图 + 1-2 配图（品牌色合规）
- 中英版可共用（除非配图含文字）
- 若配图含文字，需产出中英两版（统一 Figma 源文件管理）

### 第 5 步：翻译 / 再创作（content_creator）
- **原则**：再创作 > 直译
- 标题重写（面向英文受众，不死译）
- 术语查 `glossary.yaml`，保持 canonical 译法
- 行业套词（"revolutionary"、"game-changing"）避免
- 文化专属比喻需替换或加注（例：中文成语 → 英文等价典故）
- 产出：`<slug>.en.md` 或 `/en/blog/<slug>.astro`
- frontmatter 含 `lang: en`, `translation_of: <zh-post-id>`, `status: draft`

### 第 6 步：双审（style_calibrator + integration_qa）
- style_calibrator：风格一致性、tone、术语
- integration_qa：85/100 评分（完整性 / 准确性 / 一致性 / 可维护性 / 合规性）
- 中英版分别评分，均 ≥85 才能发布
- 评分记录写入博客 frontmatter 的 `qa_score_zh` / `qa_score_en` 字段

### 第 7 步：同步发布（content_publishing）
- 中英版同一 commit 入仓
- URL 模式：
  - 中文（默认）：`/blog/<slug>/`
  - 英文：`/en/blog/<slug>/`
- 翻译追踪表（`_translations.yaml`）更新
- hreflang 标签 + sitemap 自动生成
- Visual QA 强制：部署完成后截取中英两版首屏，确认布局未破坏

### 第 8 步：发布后复盘（content_strategist + growth_insights）
- 7 天 PV / 停留时长 / 分享次数数据（分语言统计）
- 30 天回访率
- 中英版表现差异归因（若英文表现显著弱 → 调整再创作策略）
- 入 OBS 归档至 `obs/04-content-pipeline/<year>/<slug>/`

## 质量门禁

| 维度 | 标准 |
|------|------|
| 完整性 | ≥ 20/20 |
| 准确性 | ≥ 20/20 |
| 一致性 | ≥ 17/20（术语查表）|
| 可维护性 | ≥ 17/20 |
| 合规性 | ≥ 17/20 |
| **总分** | **≥ 85/100** |

中英版独立评分，均需达标。任一语言未达 85 → 博客不得发布（见下文回滚规则）。

## 产能约束

- **每周产能**：1-2 篇新博客（中英双语对等）
- **上限**：每周不超过 3 篇新博客，避免 QA 队列积压
- **Escape hatch**：若 content_creator 产能瓶颈，先发中文 + 标 `hasEnglish: false`，在下轮 sprint 补英文；此情形需 Lysander 知情且记入翻译债务清单
- **债务清理**：翻译债务 > 3 篇时，content_strategist 暂停新选题，优先清理
- **存量博客补译额外产能**：每周 1-2 篇存量补译（不计入新博客配额）
- 存量优先级：P1 > P2 > P3，摘要式英文版可并行批量产出以清存量
- 预估：P1+P2 共 14 篇 × 1 篇/周 ≈ 14 周；P3 摘要 19 篇可加速至 4-6 周

## 回滚与延迟规则

- 英文版若 QA 未过（评分 < 85），**不得延迟中文版发布**
- 英文版可标 `status: draft` 延迟至下周，但中文版必须带 `hasEnglish: pending` 元数据
- 未过 QA 的英文版记入"翻译债务"，每周 retro 检查
- 若英文版因翻译成本 / 敏感度原因永久不发 → 提交 Lysander L3 决策豁免，存档理由

## 与其他流程的接口

- **与 content_strategist 内容日历**：新博客必须在周内容日历中明示双语计划
- **与 `glossary.yaml`**：术语变更需同步更新本 SOP 引用
- **与 `audit_content.py`**：周期扫描中 `hasEnglish: pending` 超 14 天未补 → 警告
- **与 SSOT frontmatter 标准**：所有博客必须遵循 12 字段 frontmatter
- **与自动发布流水线**：`scripts/auto-publish-blog.py` 需增加双语校验步骤（未达标阻止 git push）

## 指标

- **双语达成率** = 发布新博客中中英双语都到位的比例（目标 ≥ 90%）
- **翻译延迟** = 英文版发布时间 − 中文版发布时间（目标 ≤ 7 天）
- **双语 QA 通过率** = 首次提交即过 85 分的比例（目标 ≥ 80%）
- **跨语种表现差** = 英文版 PV / 中文版 PV（基线建立后观察）

## 违规处理

- 新博客发布时英文版缺失且未标 `hasEnglish: pending` → integration_qa 拦截
- 连续 2 周双语达成率 < 70% → Lysander 介入调整产能或范围
- 绕过 QA 门禁强发 → 记 P1 违规，计入 content_strategist 季度 KPI 扣分

## 职责分配（RACI）

| 环节 | R (负责) | A (决策) | C (咨询) | I (知会) |
|------|---------|---------|---------|---------|
| 选题 | content_strategist | Lysander | 情报日报 Agent | — |
| 草稿 | content_creator | content_strategist | 领域专家 | knowledge_engineer |
| 翻译 | content_creator | content_strategist | glossary 维护者 | — |
| QA | integration_qa | content_strategist | style_calibrator | Lysander |
| 发布 | content_publishing | content_strategist | — | Lysander |
| 复盘 | content_strategist | Lysander | growth_insights | 总裁（月报） |

## 版本历史

- v1.0（2026-04-24）：knowledge_engineer 初稿，基于总裁 L4 决策。review_by: content_strategist + execution_auditor。
- v1.1（2026-04-24 深夜）：应用总裁修正决策 ②（A → B 全站 100% 双语）。历史 33 篇存量纳入双语范围，P3 由"保留中文"改为"摘要式英文版"。新增存量补译产能条款。
- 下一次审查：2026-07-24（3 个月后），或出现以下任一触发条件时提前重审：
  - 双语达成率连续 2 周 < 70%
  - 翻译债务清单 > 5 篇
  - glossary.yaml 或 SSOT frontmatter 标准重大变更
