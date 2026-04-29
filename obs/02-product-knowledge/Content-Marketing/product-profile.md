---
id: content-marketing-product-profile
product: Content Marketing 内容营销
version: 1.0.0
profile_version: "1.0"
type: living
status: published
lang: zh
published_at: "2026-04-29"
updated_at: "2026-04-29"
author: knowledge_engineer
review_by: [harness_engineer, execution_auditor]
audience: [team_partner, knowledge_engineer]
owner: knowledge_engineer
committee: [knowledge_engineer, harness_engineer, integration_qa, content_strategist]
---

# Content Marketing 内容营销 — 产品档案

> **委员会使用说明**：当 Lysander 或任何 Agent 接到内容营销/博客/情报发布相关任务时，
> 应首先读取此文件获取产品上下文，再开始分析和执行。

## 委员会快速入职摘要

**系统一句话**：Content Marketing 是 Synapse-PJ 的内容生产与发布体系，
驱动 lysander.bond 博客、情报日报、决策归档三条内容管线，实现 AI 团队工作成果的对外可见化。

**当前状态**：博客管线 v2（已 GA），情报管线 v1.2.0（已 GA），双语内容策略生效。

**3 个最重要的约束**：
1. **博客文件格式**：必须输出至 `src/content/blog/zh/` 和 `src/content/blog/en/`（Content Collections .md），**禁止生成 .astro 文件**（会触发 esbuild 崩溃）
2. **情报内容双语**：所有新发布情报路由必须同时提供 ZH 和 EN 版本（EN 可含 disclaimer banner）
3. **Astro 6 API**：动态路由必须使用 `render(post)` 而非 `post.render()`

## 关联 GHA 管线

| 管线 | 触发时间（Dubai） | 目标产出 | 告警 |
|------|-----------------|---------|------|
| `blog-publish.yml` | 每日 22:00 | `src/content/blog/` 新文章 | ✅ 成功+失败 Slack |
| `blog-heartbeat.yml` | 每日 23:00 | 博客健康检查 | ✅ 异常 Slack |
| `intel-daily.yml` | 每日 08:00 | `src/content/intelligence/daily/` | ✅ 成功+失败 Slack（2026-04-29 新增）|
| `intel-action.yml` | 每日 10:00 | `src/content/intelligence/decisions/` + `results/` | ✅ 成功+失败 Slack（2026-04-29 新增）|

## 系统拓扑

| 组件 | 路径 |
|------|------|
| 博客生成脚本 | `scripts/auto-publish-blog.py` |
| 情报发布脚本 | `scripts/intelligence/publish_to_bond.py` |
| 会话提炼脚本 | `scripts/session-to-worklog.py` |
| 质量规范 | `obs/03-process-knowledge/quality-assurance-framework.md` |
| Astro 陷阱文档 | `obs/03-process-knowledge/astro-content-layer-pitfalls.md` |
| 内容输出目标 | `C:\Users\lysanderl_janusd\lysander-bond\src\content\` |

## 核心约束（PRINCIPLE 列表）

| 级别 | 约束 | 说明 |
|------|------|------|
| P0 | 禁止生成 .astro 博客文件 | 只能输出 Content Collections .md，否则 esbuild 崩溃 |
| P0 | 使用 render(post) | Astro 6 breaking change，post.render() 已移除 |
| P1 | 双语同步 | 新增页面必须同时有 ZH + EN 版本 |
| P1 | QA 评分 ≥85 | integration_qa 审查通过后才允许发布 |

## 委员会成员

| 角色 | 职责 |
|------|------|
| **knowledge_engineer** | 内容策略、档案维护、SOP 文档 |
| **harness_engineer** | 管线配置、GHA workflow 维护 |
| **integration_qa** | 发布质量门禁、双语合规检查 |
| **content_strategist** | 博客选题、内容质量、品牌声音 |

## 快速恢复（内容管线异常时）

**博客管线失败**：检查 `obs/04-content-pipeline/_inbox/` 是否有文件；检查 session-to-worklog.py 输出是否非空；参见 `obs/03-process-knowledge/astro-content-layer-pitfalls.md`。

**情报管线失败**：检查 `obs/06-daily-reports/` 是否有当日 HTML；检查 `BOND_WRITE_TOKEN` secret 是否有效。

## 当前版本

| 组件 | 版本 | 状态 |
|------|------|------|
| 博客管线 | v2.0 | GA |
| 情报管线 | v1.2.0 | GA |
| 双语策略 | v1.0 | 生效 |
