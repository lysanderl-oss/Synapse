---
id: ssot-i18n-integrated-review
type: core
status: published
lang: zh
version: "1.0"
published_at: 2026-04-24
author: strategy_advisor + execution_auditor
review_by: [decision_advisor, harness_engineer, ai_systems_dev, content_strategist]
audience: [team_partner, president]
stale_after: 2026-10-24
---

# 方案 ⑤：智囊团综合评审 + 总裁审批版

## BLUF

**4 个团队方案整体一致度 78%**，3 项实质分歧已由智囊团裁决：
① **SSOT 采方案 C**（Build-time Extract 脚本）
② **URL 采全站统一**（/ 中文默认 + /en/ 英文前缀）
③ **学院采混合定位**（课程 + 认证徽章 + 内嵌手册索引）
**综合工程量 30U + 内容治理 8U + 学院重构 15U = 53U，5 阶段执行。**
**建议总裁批准启动，3 个战略决策点需总裁拍板。**

---

# Part A：智囊团评审

## 一、共识矩阵（6 项，无争议）

| # | 事项 | 共识 | 来源方案 |
|---|------|------|---------|
| 1 | 必须建立 SSOT | 一致同意 | ①②③④ 全体 |
| 2 | 学院现状不可持续（7 页聚合） | 一致同意 | ①④ |
| 3 | 英文版必须上线，但不全量 | 一致同意 | ①②④ |
| 4 | 博客不全量翻译（33 篇太多） | 一致同意 | ④ |
| 5 | 错链接必须立刻修复 | 一致同意 | ① |
| 6 | frontmatter 是版本治理基础 | 一致同意 | ②③ |

## 二、分歧矩阵（3 项）

### 2.1 分歧 A：SSOT 技术方案

| 方案 | 支持方 | 论点 |
|------|-------|------|
| B. Git Submodule | 无 | （已在 ② 排除） |
| **C. Build-time Extract** | ai_systems_dev, harness_engineer | Astro 原生适配、工程量 8U、build 时组装、契约清晰 |
| D. npm Package | product_manager（弱偏好） | 版本锁最强，但工程量 15U 过重 |

**裁决**：**采方案 C**。
- 理由：与 Astro Content Collections 原生集成，编辑者工作流无侵入（仍在 synapse-core 写 markdown）
- 契约清晰：`_manifest.yaml` 白名单即公开 API 边界
- 工程量最低风险组（8U）
- D 方案价值在未来多站共享时再启用，当前 overkill

### 2.2 分歧 B：URL i18n 策略

| 方案 | 支持方 | 论点 |
|------|-------|------|
| 单页 hreflang（无 URL 前缀） | content_strategist（弱偏好） | 中文用户 URL 不变，迁移无痛 |
| **全站统一 / 默认中文 + /en/** | ai_systems_dev, product_manager | 品牌一致、hreflang 解决 SEO、Astro 原生支持 |

**裁决**：**采全站统一 /en/ 前缀**。
- 理由：品牌一致性（国际访客看到 /en/ 有清晰锚点）
- hreflang 解决 SEO 双语冲突
- 迁移代价低（Astro i18n 内置支持）
- 中文路径不变（仍是 /），存量流量无损

### 2.3 分歧 C：学院定位

| 方案 | 支持方 | 论点 |
|------|-------|------|
| 纯课程站 | content_strategist | 聚焦学习，不做商业 |
| 课程 + SCP 销售 | product_manager | 认证即销售漏斗 |
| **课程 + 完成徽章 + 下载中心**（混合） | 智囊团整合 | 学习 + 能力沉淀 + 个性化交付 |

**裁决**：**采混合定位**。
- 理由：商业闭环（课程→徽章→SCP 升级路径清晰）
- 与 Forge 区分（Forge 是 what + buy，Academy 是 how + learn + prove）
- 首期不做正式认证，仅徽章（见总裁决策 ②）

### 2.4 分歧 D：协同整合（新增）

**分歧描述**：技术迁移（② Collections 重建）与内容迁移（④ 14 篇精选）是否解耦？

**裁决**：**一体化执行，不解耦**。
- 理由：Collections 重建时顺手补 frontmatter 最经济
- 14 篇精选内容的 source_commit 需在同一批 commit 锁定
- 分开做会出现"先迁结构后补元数据"的双倍工作

## 三、跨方案风险 Top 5

| # | 风险 | 触发方案 | 等级 | 缓解 |
|---|------|---------|------|------|
| 1 | synapse-core 公开时机延后，阻塞所有方案 | ①②③ | 高 | 总裁决策 ① 已批准立即 push |
| 2 | Extract 脚本 build 失败阻塞发布 | ② | 中 | 失败回退到上一次成功 extract 的缓存；CI 双路构建（带 extract / 不带 extract）对比 |
| 3 | frontmatter 标准过严导致作者抵触 | ③ | 中 | 模板自动填 80%；12 字段必填缩到 6 字段必填 + 6 字段选填 |
| 4 | 翻译 out-of-sync 积压失控 | ④ | 中 | 每日 translation_status 推送；每周 content_strategist 硬消化 3 条 |
| 5 | 学院重构期停博客引流下滑 | ④ | 低 | 保留情报日报自动化 + Forge SEO 爬坡补偿 |

## 四、跨方案依赖链

```
总裁 ① synapse-core 公开
    ↓
synapse-core/docs/public/ 边界（方案 ③）
    ↓
_manifest.yaml 白名单（方案 ③）
    ↓
Extract 脚本（方案 ②）
    ↓
synapse-web Content Collections 重建（方案 ②）
    ↓
14 篇精选内容补 frontmatter（方案 ③④）
    ↓
学院重构上线（方案 ①④）
    ↓
全站 /en/ 英文版上线（方案 ②④）
    ↓
博客双语迁移（方案 ④）
```

---

# Part B：总裁审批版

## 五、BLUF（给总裁 3 行）

1. Synapse 内容资产正在失控（学院 7 页聚合 + 33 篇博客无治理 + 英文版 0），**不治理必然烂掉**。
2. 4 团队协同出 4 方案，智囊团裁决 3 分歧，**综合方案 53U 工程量，5 阶段执行**，止血阶段可当夜启动。
3. **3 个决策需总裁拍板**：synapse-core 公开时机、学院认证启动方式、总裁个人 IP 是否参与。

## 六、综合方案要点

| 维度 | 方案 |
|------|------|
| **SSOT 路径** | synapse-core/docs/public/ 为公开 API 边界，_manifest.yaml 白名单，build-time Extract 脚本同步到 synapse-web |
| **URL 策略** | / 中文默认 + /en/ 英文前缀，全站统一，hreflang 声明 |
| **学院定位** | 课程 + 完成徽章 + 个性化下载中心，与 Forge 按"what-buy / how-learn"分工 |
| **双语优先级** | P0：站点骨架 + Forge 全 + Academy 首页 + onboarding + 商业页；P1：5 博客再创作 + harness-101 + multi-agent-ops；P2：9 博客翻译 + 2 门进阶课；P3：19 博客保留中文 |
| **内容版本治理** | 5 层分层 + 12 字段 frontmatter + glossary.yaml + _translations.yaml + 6 个治理脚本 |

## 七、5 阶段交付计划

| 阶段 | 目标 | 关键交付物 |
|------|------|-----------|
| **阶段 1：止血** | 错链接修复 + synapse-core 公开 + 边界定义 | Forge /synapse/get-started 修复、Academy /academy/get-synapse 修复、synapse-core public 分支、docs/public/ 目录结构、_manifest.yaml v0 |
| **阶段 2：SSOT 地基** | Extract 脚本 + frontmatter 标准 + glossary | sync_from_core.mjs、frontmatter_lint.py、glossary.yaml 首批 7 条 |
| **阶段 3：学院重构 + Forge 同源** | 学院 5 门课 + onboarding 双版本同源 | Academy IA 重建、5 门课首版中文、onboarding-steps.yaml、Forge/Academy 渲染双版本 |
| **阶段 4：全站 i18n 架构** | /en/ 路由 + P0 英文内容上线 | Astro i18n 配置、hreflang、Forge 全英文、Academy 首页 + onboarding 英文 |
| **阶段 5：博客双语迁移** | 14 篇精选双语 + 19 篇归档 | 5 篇 P1 再创作 + 9 篇 P2 翻译 + 19 篇 P3 归档标记 |

## 八、资源配置

| 团队 | 阶段 1 | 阶段 2 | 阶段 3 | 阶段 4 | 阶段 5 |
|------|--------|--------|--------|--------|--------|
| Harness Ops | 主力 | 主力 | 支持 | 支持 | 支持 |
| RD | 支持 | 主力 | 支持 | 主力 | 支持 |
| Content Ops | 支持 | 支持 | 主力 | 主力 | 主力 |
| OBS | 支持 | 主力 | 支持 | 支持 | 支持 |
| Butler | — | — | 支持 | 支持 | — |

## 九、6 项成功指标

| # | 指标 | 目标值 | 测量 |
|---|------|-------|------|
| 1 | 错链接数 | 0 | Lighthouse 周扫 |
| 2 | synapse-web build 可重复性 | 100% | CI 连续 10 次一致 hash |
| 3 | frontmatter 合规率 | ≥ 95% | frontmatter_lint 报告 |
| 4 | 学院完课率 | ≥ 40%（onboarding） | Academy 后台 |
| 5 | 英文版 P0 资产覆盖 | 100% | 人工清单核验 |
| 6 | 翻译 out-of-sync 积压 | ≤ 5 条 | translation_status 日扫 |

## 十、5 条风险矩阵（总裁视角）

| # | 风险 | 等级 | 总裁关注点 |
|---|------|------|-----------|
| 1 | synapse-core 公开后敏感信息泄露 | 中 | 决策 ① 前需脱敏扫描 |
| 2 | 学院重构期流量下滑 | 低 | 情报日报 + Forge SEO 补偿，可接受 |
| 3 | 英文版质量不达标影响品牌 | 中 | 双审 ≥85/100 门槛 + 总裁抽审 |
| 4 | 5 阶段跨团队协同失控 | 中 | Lysander 每阶段简报总裁 |
| 5 | 某阶段超期阻塞后续 | 低 | 阶段间解耦设计，允许阶段 5 延后 |

## 十一、3 个总裁决策点

> **更新 2026-04-24 深夜**：总裁修正决策 ② 从 A → B（全站 100% 双语，含所有 33 篇博客），详见 `06-president-decisions.md` 决策修正段。原 P3 "19 篇保留中文" 策略改为"摘要式英文版"。

### 决策 ①：synapse-core 公开时机

| 选项 | 含义 | Lysander 建议 |
|------|------|--------------|
| **A. 立即 push 公开** | 解除阶段 1 阻塞，当夜启动 | ✅ **推荐** |
| B. 脱敏审查后公开 | 阶段 1 延后 1-3 天 | 若总裁有合规顾虑选此 |
| C. 延迟到阶段 2 | 阶段 1-2 并行做私有版 | 最保守，工程量 +20% |

### 决策 ②：学院认证启动方式

| 选项 | 含义 | Lysander 建议 |
|------|------|--------------|
| **A. 仅完成徽章** | 完课即发徽章，无考试 | ✅ **推荐**（首期） |
| B. 正式 SCP 认证 | 含考试 + 证书，商业价值高 | 未来再启动，L4 独立上报 |
| C. 不做认证 | 纯学习站 | 放弃商业闭环，不推荐 |

### 决策 ③：总裁个人 IP 参与学院课程

| 选项 | 含义 | Lysander 建议 |
|------|------|--------------|
| **A. 出镜 1 门（harness-101 或 onboarding）** | 建立"创始人视角"品牌锚 | ✅ **推荐** |
| B. 不出镜，纯 Multi-Agents 交付 | 强调"不依赖个人 IP" | 若总裁偏可复制性选此 |
| C. 延后到阶段 5 后再决定 | 先做好课程结构 | 保守选项 |

## 十二、执行授权请求

**请求总裁**：
1. 对 3 个决策点给出 A/B/C 选择
2. 批准启动阶段 1（当夜可执行）
3. 授权 Lysander 组织阶段 1-5 全程
4. 后续 L1/L2/L3 决策由 Lysander + 智囊团 + 专家评审闭环
5. 每阶段完成时简报总裁（不打扰中间过程）
6. 未来认证商业化如启动，需独立 L4 上报

**预期简报节奏**：
- 阶段 1 完成：当夜到次日简报
- 阶段 2-5 完成：各阶段 1 次简报
- 异常情况（阻塞、超期、预算超支）：实时上报

---

**智囊团签字**：
- strategy_advisor（战略一致性）
- execution_auditor（执行可行性）
- decision_advisor（决策风险）

**方案作者签字**：
- product_manager（方案 ①）
- ai_systems_dev（方案 ②）
- knowledge_engineer + harness_engineer（方案 ③）
- content_strategist（方案 ④）

**归档日期**：2026-04-24
