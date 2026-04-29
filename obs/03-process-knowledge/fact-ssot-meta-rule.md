---
id: fact-ssot-meta-rule
type: core
status: published
lang: zh
version: 1.0
published_at: 2026-04-26
updated_at: 2026-04-26
author: [harness_engineer, execution_auditor]
review_by: [knowledge_engineer, integration_qa, decision_advisor]
audience: [knowledge_engineer, technical_builder, content_strategist, harness_engineer]
stale_after: 2026-10-26
---

# 事实型数字 SSOT 化（Fact-SSOT Meta-Rule）

> **元规则等级**：Synapse 体系级，等同于 CEO 执行禁区 / 350 行熵增预算
> **触发场景**：任何文档、网页、博客、报告中提到具体的事实型数字
> **强制对象**：所有 Agent、所有 Worker、所有人工作者
> **违规处理**：CI 拦截 + Lysander 复审 + 审计日志记录

---

## 1. 背景与触发事件

### 1.1 触发本规则的事故（2026-04-26）

总裁在审视网站时发现：同一事实——"Synapse 体系内部署的 Agent 数量"——在不同位置出现了三个不同数字：

| 数字 | 出现位置 | 自称什么 |
|------|----------|----------|
| **44** | 主页、Academy、Forge 多数页面、所有早期博客 | "44 位 AI Agent / 10 个团队 / 7 支团队" |
| **46** | `/synapse/team`、`/synapse/capabilities`、proposal.md | "46 位专家 / 11 支团队" |
| **50** | `/services` Mac 终端 mockup、英文 about.astro / index.astro | "50 agents / 10 teams" |

而**真实值**（基于 synapse-core@36ab925 仓库 modules/* 实际计数）：
- **53 个 unique Agent**（54 个 .md 文件 - 1 个跨模块重复 capability_architect）
- **13 个 module（团队）**

三个网站数字**全部错误**。事故根因不是写错了一处文案，而是**根本没有 SSOT**：每个页面在不同时点被冻结，作者凭记忆/印象写数字，从未有过单点权威源。

### 1.2 为什么必须升级为元规则

普通的"文案审核"无法解决此类问题：
- 网站今天有 44/46/50 三个数字，明天加新页面可能又冒出 48
- Agent 数量本身就在演进（38 → 49 → 53 → 未来可能 60+）
- 团队数量也在演进（8 → 11 → 13）
- 价格、版本号、行数预算、模块数同理

**这是结构性问题，不是失误问题**。结构性问题需要结构性约束。

---

## 2. 元规则定义

### 2.1 规则陈述

> **所有"事实型数字"必须从单一权威源（SSOT）取值。
> 文案、页面、博客、报告、Slack 通知、API 响应中
> 不得硬编码任何一个事实型数字。**

### 2.2 什么是"事实型数字"

事实型数字 = 描述系统/产品**当前真实状态**的可计数数值。

**必须 SSOT 化的数字**：
- Agent 数量（如 53、54）
- 团队/模块数量（如 13）
- 版本号（如 v3.0.0）
- 行数预算（如 CLAUDE.md ≤ 350 行）
- 价格（如训练 $500）
- 审计评分阈值（如 ≥ 85/100）
- Token 预算（如 200k context）
- 客户数 / 项目数 / 已交付数

**不需要 SSOT 化的数字**：
- 自然语言中的概数（"几十个"、"几百行"，但要避免与精确数字共用）
- 装饰性 mockup（如终端动画的 fake CPU 占用率）—— 但必须明确标记为 mockup
- 数学/物理常数（π、光速）
- 历史快照（明确标注 "as of YYYY-MM-DD" 的某次审计结果）

### 2.3 适用范围

**必须遵守元规则的产物**：
- `lysander-bond/` 网站（src/pages、src/content/blog、src/components）
- `synapse-core/` 文档（docs/public/、CLAUDE.md、README.md）
- `Synapse-Mini/` 工作仓（obs/、agent-CEO/config/、报告 HTML）
- 所有自动生成的报告（情报日报、行动报告、PMO 周报）
- Slack 通知模板
- 任何对外发布的演示材料

**例外**：
- 用户输入的复述（如"用户说要 50 个"，引用而非陈述）
- 历史档案文档（明确标注 frozen at YYYY-MM-DD）

---

## 3. 实施机制（三层防御）

### 3.1 Layer 1：构建时注入（强制，第一道防线）

**SSOT 文件**：`synapse-core/docs/public/synapse-stats.yaml`

由 `synapse-core/scripts/generate-stats.mjs` 在每次 push 时自动生成，内容：

```yaml
# Auto-generated; DO NOT EDIT
# Source: synapse-core@<commit>
version: <reads VERSION>
generated_at: <ISO-8601>

agents:
  total_unique: <count of unique modules/*/agents/*.md basenames>
  total_files: <count of all .md files under modules/*/agents/>
  by_module:
    core: <int>
    harness_ops: <int>
    # ... per module

modules:
  total: <count of modules/*/ directories>
  list: [<sorted module ids>]

harness:
  claude_md_lines_cap: 350
  agent_card_min_score: 85
  stale_after_days: 180
```

**消费方实现**：
- `lysander-bond/scripts/sync_from_core.mjs` 在 prebuild 时拉取此文件 → `src/data/synapse-core/synapse-stats.yaml`
- Astro 页面通过 `import stats from '../data/synapse-core/synapse-stats.yaml'` 读取
- 模板使用 `{stats.agents.total_unique}` `{stats.modules.total}` 替换硬编码
- 任何提及事实型数字的页面**必须** import stats，**禁止**写死数字

**违规检测**（CI 强制）：
- `lysander-bond/scripts/lint-no-hardcoded-stats.mjs`：扫描 src/ 中所有 .astro / .md / .ts，匹配 `\b(4[0-9]|5[0-9]|6[0-9])\s*(个|位|名|人)?\s*(AI )?[Aa]gent\b`，与 stats 实际值比对，不一致或硬编码则 build 失败。
- 加入 `package.json` scripts 的 prebuild 链：`sync_from_core → generate-stats → lint-no-hardcoded-stats → astro build`

### 3.2 Layer 2：审计扫描（次防线，每周 Cron）

**审计脚本**：`synapse-core/scripts/audit_facts.py`（新增）

每周一 00:00 UTC 运行，扫描三个仓库：
1. 提取所有"数字+Agent/团队/module"模式
2. 与 synapse-stats.yaml 对比
3. 生成 `audit/facts_drift_<date>.jsonl`，列出每条违规
4. 大于 5 条违规 → Slack 告警 → 触发 Lysander 复审任务

### 3.3 Layer 3：Skill / Hook 提示（最弱防线，在源头拦截人工写作）

**触发点**：`content_strategist`、`content_creator`、`technical_writer` 撰写包含数字的内容时

**机制**：
- 写作 Skill 模板加入 checklist 项：
  - [ ] 我引用的 Agent / 团队 / 版本数字是从 synapse-stats.yaml 读取的吗？
  - [ ] 如果是博客等不便构建时注入的场景，我是否在文末标注了 "数据快照：YYYY-MM-DD（synapse-core@<commit>）"？
- `Write` 工具的 PreToolUse hook：检测正则模式 `[0-9]+\s*(个|位|名)?\s*[Aa]gent`，对命中者注入提醒："此数字是否已 SSOT 化？"

---

## 4. 责任 RACI

| 任务 | R（执行） | A（问责） | C（咨询） | I（知会） |
|------|-----------|-----------|-----------|-----------|
| synapse-stats.yaml 生成脚本 | ai_systems_dev | harness_engineer | knowledge_engineer | Lysander |
| sync_from_core.mjs 升级 | ai_systems_dev | harness_engineer | content_strategist | Lysander |
| lint-no-hardcoded-stats.mjs | integration_qa | harness_engineer | ai_systems_dev | Lysander |
| 每周事实漂移审计 | execution_auditor | harness_engineer | integration_qa | Lysander、总裁（仅摘要） |
| 网站现有 44/46/50 全量替换 | content_strategist | harness_engineer | content_creator | Lysander |
| 元规则文档维护 | knowledge_engineer | harness_engineer | execution_auditor | 全 Agent |

---

## 5. 违规处理流程

### 5.1 CI 拦截（自动）
- `lint-no-hardcoded-stats.mjs` 失败 → build 失败 → push 被拒 → 提交者被通知

### 5.2 审计发现（半自动）
- 周审计输出违规清单 → 自动创建 active_tasks 修复任务 → 路由到 content_strategist
- 修复后由 integration_qa 验证 → 关闭任务

### 5.3 总裁直接发现（人工，最严重情况）
- 总裁在网站/报告中发现事实漂移 → Lysander 立即响应：
  1. 全仓库扫描，定位所有错误数字
  2. 派单修复（content_strategist + harness_engineer）
  3. 复盘根因，强化对应 Layer 防线
  4. 写入 root_cause_analysis 报告

---

## 6. 与现有 Harness 规则的关系

| 已有规则 | 关系 |
|----------|------|
| **350 行 CLAUDE.md 熵增预算** | 行数本身就是事实型数字，由本元规则覆盖（行数从 audit_harness 取值，禁止硬编码） |
| **180 天废弃审查** | 时间字段（stale_after）由 frontmatter 单点定义，已是 SSOT，本规则强化执行 |
| **12 字段 frontmatter 规范** | 本元规则的细颗粒前置规则；frontmatter 是文档级 SSOT，本规则是数字级 SSOT |
| **CEO 执行禁区** | 同等优先级元规则，互不冲突 |

---

## 7. 演进与版本

- **v1.0（2026-04-26）** — 初始版本，由 44/46/50 漂移事故触发
- 重大变更需总裁会话中确认（同 P0 规则变更流程）
- 每 6 个月由 harness_engineer 复审一次

---

## 8. 速查表（给所有 Agent 看的 5 行总结）

> 1. 任何具体数字（Agent 数、团队数、版本、价格、行数）→ 从 SSOT 读，不写死。
> 2. SSOT 文件：`synapse-core/docs/public/synapse-stats.yaml`，每次 push 自动重生成。
> 3. 网站 / 博客 / 报告中提到数字 → import stats 引用，或文末标注 "数据快照 YYYY-MM-DD"。
> 4. CI 会扫描硬编码数字 → 命中即 build 失败，没有例外。
> 5. 总裁不应该比 SSOT 先发现数字漂移 —— 那是体系失职。
