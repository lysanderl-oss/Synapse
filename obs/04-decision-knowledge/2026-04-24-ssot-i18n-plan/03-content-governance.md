---
id: synapse-content-governance-plan
type: core
status: published
lang: zh
version: "1.0"
published_at: 2026-04-24
author: knowledge_engineer + harness_engineer
review_by: [decision_advisor, execution_auditor]
audience: [team_partner]
stale_after: 2026-10-24
---

# 方案 ③：内容治理方案 — 5 层分层 + SSOT 契约 + 版本追踪

## BLUF

**内容不治理，必然腐烂。**三条核心规则立刻落地：
① **5 层分层**（Core/Living/Reference/Narrative/Private）决定同步策略与发布目标；
② **SSOT 契约**：`synapse-core/docs/public/` 即公开 API 边界，非白名单内容不得对外；
③ **12 字段 frontmatter**（含 `source_commit` / `translation_of` / `stale_after`）为全量内容版本锚点。
**熵增预算**：学院 20 门 / Forge 15 页 / SOP 25 份 / 博客首屏 12 篇 / 术语表 150 条，超出即触发淘汰。

## 一、治理目标：为什么内容需要 HR

### 1.1 三大腐烂模式

| 腐烂模式 | 典型症状 | 损失 |
|---------|---------|------|
| **失真** | 代码已改，文档还写旧接口 | 用户按文档操作失败，信任崩塌 |
| **熵增** | 谁都能加一页，谁都不删 | 学院 7 页变 70 页，找不到重点 |
| **分裂** | 同一个概念 5 个地方各自定义 | Harness 在 A 页叫"控制层"，B 页叫"规则引擎" |

### 1.2 Synapse 的特殊风险

- **双语**：一处改了中文，英文版默默过期
- **Multi-Agents 自动生成**：Agent 产出速度 > 人工审核速度，熵增 10 倍
- **跨仓库 SSOT**：synapse-core 改了，synapse-web 不知道

### 1.3 治理哲学：内容也是 Agent 团队的成员

- 每份内容有 **作者**（specialist_id）、**审阅人**（review_by）、**保质期**（stale_after）
- 过期 → 进入废弃候选（类比 Agent 的"评估-转岗-退役"）
- 新增须过审（类比 Agent 的入职审批）

## 二、5 层内容分层（核心治理模型）

| 层 | 类型 | 生命周期 | 示例 | 同步策略 | 发布目标 |
|----|------|---------|------|---------|---------|
| **Core** | 方法论 / 原则 / 架构 | 半永久 | Harness Engineering、执行链 v2.0、决策体系 | 季度复查，人工审核后 propagate | Forge how-it-works / 学院核心课 |
| **Living** | 活文档 | 持续追加 | changelog、情报日报、路线图 | 自动追加，build 时同步 | Forge changelog / Intelligence |
| **Reference** | 查阅类 | 跟随代码 | API 文档、配置手册、HR 卡片 | 跟随 source_commit 同步 | Docs 站 / 学院查阅 |
| **Narrative** | 叙事类 | 一次创作 | 博客、案例、访谈 | 一次创作 + 版本声明，不改写 | Blog |
| **Private** | 内部类 | 永不对外 | 决策日志、HR 人员卡、retro | **永不同步出 OBS** | 仅 OBS |

### 2.1 分层判断 3 问

新增内容时，作者必须回答：
1. 这份内容半年后还会被引用吗？（是 → Core/Reference，否 → Living/Narrative）
2. 代码改了这份内容要同步改吗？（是 → Reference，否 → Core/Narrative）
3. 包含敏感信息吗？（是 → Private，强制锁 OBS）

### 2.2 分层与 SSOT 路径映射

```
synapse-core/
  docs/
    public/           ← 白名单边界，只允许 Core + Reference + Living
      core/           ← Core 层
      reference/      ← Reference 层
      living/         ← Living 层
      _manifest.yaml  ← 白名单声明（哪些文件可公开）
  obs/                ← Private 层（永不进 public/）
```

## 三、SSOT 契约（公开 API 边界）

### 3.1 契约三原则

1. **白名单显式**：`_manifest.yaml` 列出所有可公开文件，未列出者 extract 脚本拒绝拉取
2. **破坏性变更走 CHANGELOG Breaking 分节**：Core 层文件语义变更必须在 `synapse-core/CHANGELOG.md` 的 `## Breaking` 标记
3. **版本锁**：synapse-web 通过 `synapse.version` 锁定依赖 core 版本，不被动跟进

### 3.2 _manifest.yaml 示例

```yaml
version: "1.0"
last_audit: 2026-04-24
public:
  core:
    - harness-engineering.md
    - execution-chain.md
    - decision-system.md
  reference:
    - api/dispatch.md
    - config/organization.yaml
  living:
    - changelog.md
    - intelligence/latest.md
excluded:  # 显式标记不对外
  - obs/**
  - agent-CEO/config/active_tasks.yaml
  - logs/**
```

### 3.3 破坏性变更流程

```
harness_engineer 提案 → Lysander 批准 L3
    ↓
synapse-core/CHANGELOG.md 加 ## Breaking 条目
    ↓
breaking_changes_alert.py 扫描 → synapse-web 收到告警
    ↓
integration_qa 在 synapse-web 侧评估影响 → 升级或锁版
```

## 四、12 字段 frontmatter 标准

每份 Core / Reference / Living / Narrative 内容必须含：

```yaml
---
id: synapse-harness-engineering          # 全站唯一 ID（kebab-case）
type: core                                # core | living | reference | narrative
status: published                         # draft | review | published | deprecated
lang: zh                                  # zh | en
translation_of: null                      # 若为译文，指向原文 id
version: "2.0"                            # 内容版本
source_commit: abc1234                    # synapse-core 对应 commit（Reference 层必填）
synapse_version: "v0.9"                   # 兼容的 synapse 体系版本
published_at: 2026-04-24
updated_at: 2026-04-24
author: harness_engineer                  # specialist_id
review_by: [decision_advisor]             # 审阅人列表
audience: [team_partner, public]          # 受众
stale_after: 2026-10-24                   # 保质期（到期自动进废弃候选）
---
```

**工具保障**：`frontmatter_lint.py` 在 CI 阶段拒绝缺字段的内容。

## 五、翻译追踪机制

### 5.1 _translations.yaml

每个双语内容目录放一个 `_translations.yaml`：

```yaml
harness-engineering:
  en:
    commit: abc1234       # 英文版最新 commit
    updated_at: 2026-04-24
  zh:
    commit_based_on: abc1234   # 中文翻译基于哪个英文 commit
    commit: def5678             # 中文版最新 commit
    updated_at: 2026-04-24
    status: published
```

### 5.2 翻译状态机

```
untranslated → in-progress → review → published
                                         ↓
                                     out-of-sync ← 英文版 commit 更新
                                         ↓
                                    re-translating → review → published
```

**工具**：`translation_status.py` 每日扫描，产出"out-of-sync"列表给 content_strategist。

## 六、术语表 glossary.yaml（首批 7 条）

```yaml
- id: harness-engineering
  zh: Harness 工程 / 束具工程
  en: Harness Engineering
  definition_zh: Agent = Model + Harness 的工程范式，强调前馈控制、约束系统、结构化流程
  definition_en: Engineering paradigm where Agent = Model + Harness, emphasizing feed-forward control, constraint system, and structured workflow
  preferred: Harness Engineering（品牌术语保留英文）

- id: dispatch
  zh: 派单
  en: dispatch
  definition_zh: Lysander 将任务分配给专业团队 Agent 的强制前置步骤
  definition_en: Mandatory step where Lysander assigns tasks to specialist agents

- id: ceo-guard
  zh: CEO 守卫
  en: CEO Guard
  definition_zh: 阻止 Lysander 主对话直接调用执行类工具的 PreToolUse hook
  definition_en: PreToolUse hook that prevents Lysander main dialog from directly invoking execution tools

- id: agent
  zh: 智能体 / Agent
  en: Agent
  definition_zh: Synapse 体系中的独立执行单元
  definition_en: Independent execution unit in Synapse system
  preferred: Agent（全站保留英文）

- id: execution-chain
  zh: 执行链
  en: execution chain
  definition_zh: Synapse v2.0 定义的标准工作流（开场→承接→分级→执行→QA→交付）
  definition_en: Standard workflow defined by Synapse v2.0

- id: ssot
  zh: 单一真相源
  en: SSOT (Single Source of Truth)
  definition_zh: 内容与配置的唯一权威来源仓库
  definition_en: Single authoritative repository for content and configuration
  preferred: SSOT（品牌术语保留英文）

- id: intelligence-pipeline
  zh: 情报闭环
  en: intelligence pipeline
  definition_zh: 发现→评估→执行→报告的自动化链路
  definition_en: Automated pipeline of discover → evaluate → execute → report
```

**工具**：`check_glossary.py` 扫描文中是否出现未登记术语的多种译法。

## 七、内容运营 SOP（全链路）

```
选题（content_strategist 基于路线图）
    ↓
大纲（作者出大纲，review_by 过目）
    ↓
草稿（作者完成，frontmatter 就位）
    ↓
视觉资产（配图/截图/图表）
    ↓
审核
  ├─ 语言质量：style_calibrator
  ├─ 版本合规：frontmatter_lint + check_glossary
  └─ 战略对齐：review_by 签字
    ↓
发布（Living 层自动，其他层手动）
    ↓
周期复查（按 stale_after 触发）
    ↓
归档 / 废弃 / 重写
```

## 八、熵增预算（各层上限）

| 层 | 上限 | 超出处理 |
|----|------|---------|
| 学院课程 | 20 门 | 合并或下架 |
| Forge 页 | 15 页 | 合并到学院 |
| SOP 文档 | 25 份 | 归档到历史 |
| 博客首屏 | 12 篇（置顶精选） | 旋转，非首屏保留归档 |
| 术语表 | 150 条 | 合并近义 |

**审计节奏**：`audit_content.py` 每 14 天运行一次，超预算告警 → Lysander 指派裁剪。

## 九、工具链（6 个脚本）

| 脚本 | 功能 | 触发 |
|------|------|------|
| `audit_content.py` | 熵增预算 + stale_after 扫描 | 每 14 天 cron |
| `translation_status.py` | out-of-sync 检测 | 每日 cron |
| `sync_from_core.mjs` | synapse-core → synapse-web build-time extract | build 时 |
| `breaking_changes_alert.py` | synapse-core CHANGELOG Breaking 分节告警 | core push 后 webhook |
| `check_glossary.py` | 未登记术语或不一致译法 | pre-commit hook |
| `frontmatter_lint.py` | 12 字段完整性 | pre-commit hook |

## 十、RACI 矩阵

| 事项 | R（负责） | A（批准） | C（咨询） | I（知会） |
|------|---------|---------|---------|---------|
| 新增 Core 内容 | 作者 specialist | Lysander | decision_advisor | 总裁 |
| 翻译任务 | content_strategist | Lysander | style_calibrator | — |
| 破坏性变更 | harness_engineer | Lysander（L3） | integration_qa | 总裁（L4 仅影响外部时） |
| 博客发布 | content_strategist | Lysander | style_calibrator | — |
| 内容废弃 | knowledge_engineer | Lysander | 原作者 | — |
| 周期复查 | knowledge_engineer | — | 原作者 | Lysander |
| 术语表变更 | knowledge_engineer | Lysander | content_strategist | 全体作者 |
| 学院课程 | content_strategist | Lysander | product_manager | 总裁（首发） |

## 十一、5 阶段迁移路线

| 阶段 | 目标 | 工作项 |
|------|------|-------|
| 1. 标准落地 | frontmatter + glossary 上线 | 12 字段模板、glossary.yaml 首批 7 条、frontmatter_lint 接入 pre-commit |
| 2. 资产迁入 | 现有内容补 frontmatter | 所有 Forge 页 + 学院页 + 博客精选 14 篇补字段 |
| 3. 同步器上线 | sync_from_core + _manifest 就绪 | synapse-core/docs/public/ 边界定义、_manifest.yaml 首版、extract 脚本联调 |
| 4. 周期化 | audit + translation_status 自动跑 | cron 接入、告警路由 |
| 5. 扩展 | breaking_changes_alert + 术语表扩到 50 条 | 跨仓库告警、glossary 扩充 |

## 十二、5 条风险

| 风险 | 等级 | 缓解 |
|------|------|------|
| R1. 作者抵触 frontmatter 填写 | 中 | pre-commit hook 强制 + 模板自动填 80% |
| R2. synapse-core 破坏性变更漏告警 | 高 | CHANGELOG Breaking 分节硬性要求 + PR 模板 |
| R3. 翻译 out-of-sync 积压 | 中 | 每日 translation_status 推送 + 每周 content_strategist 消化 |
| R4. 术语表与实际文档漂移 | 中 | check_glossary.py + 每月人工校准 |
| R5. 熵增预算被无视 | 低 | audit_content 告警 → Lysander 强制裁剪 |

## 十三、与其他方案的接口

- **对 ① 产品方案**：学院课程须符合 Core 层治理，单向导出到 synapse-core
- **对 ② 技术方案**：Extract 脚本按 `_manifest.yaml` 白名单工作
- **对 ④ 内容方案**：博客分级、翻译优先级均沿用本方案的分层 + 翻译状态机

## 十四、BLUF 收束

**必须立刻做（阶段 1 内）：**
1. 12 字段 frontmatter 标准 + frontmatter_lint 接入 pre-commit
2. synapse-core/docs/public/ 边界 + _manifest.yaml 首版
3. glossary.yaml 首批 7 条上线

**可延后（阶段 4-5）：**
1. breaking_changes_alert.py 跨仓库告警
2. 术语表扩到 150 条
3. 熵增预算自动裁剪脚本

**不做：**
1. 全文搜索引擎（Algolia 后续再说）
2. 内容协作评论系统（GitHub PR 已足够）

---

**作者**：knowledge_engineer + harness_engineer
**审阅**：decision_advisor, execution_auditor
**归档日期**：2026-04-24
