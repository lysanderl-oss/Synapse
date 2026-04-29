---
id: synapse-product-profile
product: Synapse 体系
version: 1.0.0
profile_version: "3.0"
type: living
status: published
lang: zh
published_at: "2026-04-28"
updated_at: "2026-04-29"
author: knowledge_engineer
review_by: [harness_engineer, execution_auditor]
audience: [team_partner, knowledge_engineer]
owner: harness_engineer
committee: [harness_engineer, knowledge_engineer, execution_auditor, ai_systems_dev]
---

# Synapse 体系 — 产品档案

> **委员会使用说明**：当 Lysander 或任何 Agent 接到 Synapse 体系相关任务时，
> 应首先读取此文件获取产品上下文，再开始分析和执行。

## 委员会快速入职摘要（Agent 调用时快速消化）

**系统一句话**：Synapse 是 Synapse-PJ 的 AI 协作运营体系，由 OBS 知识层 + Harness 控制层 + Multi-Agent 执行层组成，通过 Claude Code 的 Agent 工具驱动 58-69 名专业 Agent 协作运营。

**当前状态**：v1.0.0 运行中，标准执行链 v2.0 生效，CEO Guard P0 约束激活。

**3 个最重要的约束**：
1. **CEO 执行禁区 (P0)**：Lysander 主对话禁止直接调用 Bash/Edit/Write/WebSearch/WebFetch，必须通过 Agent 工具派单执行
2. **【0.5】承接强制**：任何用户新诉求必须经 Lysander 承接（复述目标→分级→派单），不得直接派单绕过
3. **CLAUDE.md 行数上限 350 行**：超出需先删减再添加；新增路由规则走 `.claude/harness/` 独立文件

**快速定位资源**：
- Harness 配置：`C:\Users\lysanderl_janusd\Synapse-Mini\CLAUDE.md`
- 参考模块目录：`C:\Users\lysanderl_janusd\Synapse-Mini\.claude\harness\`
- 版本：`C:\Users\lysanderl_janusd\Synapse-Mini\VERSION`

## 关联产品线：lysander.bond

| 产品 | 当前版本 | 状态 | 最后部署 |
|------|----------|------|----------|
| lysander.bond | v1.2.0-intelligence-hub | live | 2026-04-29 |
| Intelligence Hub | v1.2.0 | live | 2026-04-29 |
| Post-deploy 健康检查 | active | active | 2026-04-29 |

**管线质量保障（2026-04-29 起）**：
每次 push 到 lysander-bond main → Cloudflare 部署 → 5分钟后自动健康检查 5 个 URL → 失败发 Slack。

## 系统组成

| 层次 | 组件 | 说明 |
|------|------|------|
| 知识层 (OBS) | `obs/` Obsidian 知识库 | 团队知识/产品知识/决策/流程/情报 |
| 控制层 (Harness) | `CLAUDE.md` + `.claude/harness/` | 执行链、约束、路由规则、HR 管理 |
| 执行层 (Agents) | 58-69 名专业 Agent | 13 核心团队，通过 Agent 工具调用 |
| 决策层 | 四级决策 L1-L4 | L1 自动 / L2 专家 / L3 Lysander / L4 总裁 |
| 自动化层 | n8n Harness WF | 定时触发、情报管线、Slack 通知 |

## 核心工作流

```
用户输入 → 【开场】Lysander 身份确认
        → 【0.5】承接与目标确认（复述→分级→派单表）
        → 【①】智囊团分级（S/M/L）→ 方案
        → 【②】执行团队执行（Harness Ops/Butler/RD/OBS 等）
        → 【③】QA + 智囊团审查（质量门禁 ≥85/100）
        → 【④】结果交付总裁
```

**Harness 自动化节奏（Dubai 时区）**：
- 6:00 — 任务恢复，跨会话 active_tasks.yaml 读取
- 8:00 — 情报日报生成并推送 Slack
- 10:00 — 情报行动执行（OBJ 关键词扫描→评估→执行）

## 核心文件清单

| 文件 | 作用 |
|------|------|
| `CLAUDE.md` | Harness 主配置，角色/执行链/约束 |
| `.claude/harness/execution-chain-stage-0.5.md` | 【0.5】承接 6 步详细流程 |
| `.claude/harness/product-routing.md` | 产品管线路由规则 |
| `.claude/harness/hr-management.md` | Agent HR 管理制度 |
| `.claude/harness/credentials-usage.md` | 凭证管理规范 |
| `.claude/harness/dispatch-template-detailed.md` | 派单模板详细说明 |
| `.claude/harness/cross-session-state.md` | 跨会话状态管理协议 |
| `agent-CEO/config/organization.yaml` | 团队配置 |
| `agent-CEO/config/active_tasks.yaml` | 跨会话任务状态 |
| `obs/01-team-knowledge/HR/personnel/` | 69 名 Agent 人员卡片 |

## 系统拓扑

| 组件 | 路径 / 说明 |
|------|------------|
| Harness 主配置 | `CLAUDE.md`（上限 350 行） |
| 参考模块 | `.claude/harness/*.md`（已迁出规则） |
| 命令扩展 | `.claude/commands/*.md` |
| 人员卡片库 | `obs/01-team-knowledge/HR/personnel/`（69 张） |
| 决策归档 | `obs/04-decision-knowledge/decision-log/`（D-编号） |
| 每周审计 | `obs/01-team-knowledge/HR/weekly-audit/` |
| 情报日报 | `obs/06-daily-reports/` |

## 关键约束（PRINCIPLE 列表）

| 级别 | 约束 | 说明 |
|------|------|------|
| P0 | CEO 执行禁区 | Lysander 主对话禁止直接执行 Bash/Edit/Write/WebSearch/WebFetch |
| P0 | 【0.5】承接强制 | 不得绕过承接环节直接派单 |
| P0 | CLAUDE.md 行数 ≤ 350 | 超出需先删减 |
| P0 | 周维度审查 | 每周日 23:00 Dubai 执行 6 维度审查，结果入 `obs/01-team-knowledge/HR/weekly-audit/` |
| P0 | 决策归档 | L3+ 决策必须以 D-编号归档到 `obs/04-decision-knowledge/decision-log/` |
| P1 | 工具白名单 | 主对话只允许 Read/Skill/Agent/Glob/Grep |
| P1 | 规则时间戳 | 每个新增规则须标注 `# [ADDED: YYYY-MM-DD]`，超 180 天未重申进废弃候选 |

## 委员会成员

遇到 Synapse 体系相关任务时，Lysander 应将任务派送给：

| 角色 | 职责 |
|------|------|
| **harness_engineer** | CLAUDE.md 规则配置、执行链变更、P0/P1 规则维护 |
| **knowledge_engineer** | OBS 知识库维护、product-profile 维护、文档架构 |
| **execution_auditor** | 执行链合规审查、熵增审计、派单合规检查 |
| **ai_systems_dev** | Agent 能力开发、工具集成、hr_base.py 维护 |

## 快速恢复（体系异常时）

**执行链断裂**：读取 `CLAUDE.md` 确认 P0 约束，检查 `.claude/harness/` 各模块完整性。

**跨会话恢复**：读取 `agent-CEO/config/active_tasks.yaml`，恢复进行中任务。

**CEO Guard 审计**：日志路径 `logs/ceo-guard-audit.log`；测试场景 `.claude/harness/ceo-guard-tests.md`。

## 关联文档

- 体系主配置：`CLAUDE.md`
- 版本历史：`VERSION` + `CHANGELOG.md`
- 升级协议：`.claude/harness/upgrade-protocol.md`
- 体系介绍页：`synapse_v3_intro.html`

## lysander.bond 产品管线状态

| 产品 | 版本 | 状态 | 最后部署 |
|------|------|------|----------|
| lysander.bond | v1.2.0-intelligence-hub | live | 2026-04-29 |
| Content Marketing 管线 | v2.0 GA | live | 2026-04-29 |
| PMC 治理前置制度 | v1.0 | active | 2026-04-29 |
| 每日 2:00 AM 管线同步 | v1.0 | active | 2026-04-29 |

**每日 2:00 AM 自动同步范围**（D-2026-04-29-001）：
- pipeline-metrics/latest.yaml 全局内容计数刷新
- PIPELINE.md Section 7 版本状态自动同步
- Slack 成功/失败通知

## 已知陷阱（Pitfall Registry）

| # | 陷阱 | 影响 | 参考 |
|---|------|------|------|
| 1 | Astro 6 `render()` API | `post.render()` 已废弃，必须用 `render(post)` | `obs/03-process-knowledge/astro-content-layer-pitfalls.md` |
| 2 | astro.config.mjs redirect 覆盖实际路由 | redirects 优先级高于 src/pages/ 文件 | 同上 |
| 3 | 博客管线生成 .astro 文件 | 触发 esbuild 崩溃，必须输出 Content Collections .md | `obs/02-product-knowledge/Content-Marketing/product-profile.md` |
