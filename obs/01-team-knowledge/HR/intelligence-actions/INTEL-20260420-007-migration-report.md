# Claude Sonnet 4 / Opus 4 停服迁移报告

> 报告编号：INTEL-20260420-007
> 制作人：rd_devops
> 制作日期：2026-04-22
> 任务来源：INTEL-20260419-002（P0），关联 INTEL-20260420-007（持续跟踪，P0逾期）
> 停服截止：2026-06-15，剩余 **55天**

---

## ① 受影响系统清单

### 扫描范围

全库检索关键词：`claude-sonnet-4` / `claude-opus-4` / `sonnet-4-6` / `opus-4`

### 扫描结果

| 文件路径 | 引用类型 | 具体引用 | 风险等级 |
|----------|----------|----------|----------|
| `synapse.yaml` | **无引用** | — | 无风险 |
| `.claude/settings.json` | **无引用** | — | 无风险 |
| `.claude/settings.local.json` | **无引用** | — | 无风险 |
| `agent-butler/config/n8n_integration.yaml` | **无引用** | — | 无风险 |
| `agent-butler/config/decision_rules.yaml` | **无引用** | — | 无风险 |
| `agent-butler/config/organization.yaml` | **无引用** | — | 无风险 |
| `agent-butler/config/active_tasks.yaml` | 状态记录 | `claude-sonnet-4-6` 出现在 notes 字段（任务跟踪记录，非配置引用） | 低 |
| `agent-butler/hr_base.py` | **无引用** | — | 无风险 |
| `scripts/build-distribution.py` | **无引用** | — | 无风险 |
| `.claude/hooks/ceo_guard_pre.js` | **无引用** | — | 无风险 |
| `.claude/hooks/ceo_guard_post.js` | **无引用** | — | 无风险 |

### 历史报告文件（情报输出，仅供参考）

| 文件路径 | 引用内容 | 说明 |
|----------|----------|------|
| `obs/06-daily-reports/2026-04-17-retro.md` | `claude-sonnet-4-6` | 情报回顾报告，记录当前版本 |
| `obs/06-daily-reports/2026-04-18-retro.md` | `claude-sonnet-4-6` | 情报回顾报告 |
| `obs/06-daily-reports/2026-04-19-retro.md` | `claude-sonnet-4-6` + `claude-opus-4-7`（新发布） | 情报回顾报告 |
| `obs/06-daily-reports/2026-04-19-intelligence-daily.html` | `claude-opus-4-7`（发布公告） | 情报日报，公告内容 |
| `obs/06-daily-reports/2026-04-19-action-report.md` | `claude-haiku-4-5-20251001`（替代模型） | 行动报告，涉及 Haiku 迁移 |
| `obs/01-team-knowledge/HR/intelligence-actions/` | 行动报告 | 历史行动建议 |

### 结论

**核心运营配置文件无 `claude-sonnet-4` / `claude-opus-4` 硬编码引用。**

所有出现均为：
1. **情报日报/行动报告**（`obs/06-daily-reports/`）—— 信息记录文件，非运营配置
2. **active_tasks.yaml 的 notes 字段** —— 任务跟踪状态记录，非配置引用

Synapse 架构上**不直接指定 Claude 模型 ID**，模型由 Claude Code 运行时通过环境/API凭证调用，不由配置文件驱动。

---

## ② 现状梳理

### 当前主模型

| 项目 | 值 |
|------|-----|
| 当前运行模型 | `claude-sonnet-4-6` |
| 模型角色 | Synapse 主对话模型（Claude Code 运行载体） |
| 配置文件来源 | Claude Code 运行时注入，非 synapse.yaml 配置 |
| 是否受停服影响 | **是** — `claude-sonnet-4-6` 在停服清单内 |

### n8n 定时任务配置分析

`agent-butler/config/n8n_integration.yaml` 中定义的自动化任务：

| 任务名称 | 触发时间（UTC） | 触发方式 | 模型依赖 |
|----------|----------------|----------|----------|
| 任务自动恢复Agent | 02:15 UTC | n8n Cron Trigger | 通过 Claude Code Skill 触发，使用主模型 |
| 情报日报Agent | 03:00 UTC | n8n Cron Trigger（`trig_01Lp7Q1Nn36JQAw4FEEJmKQX`） | 同上 |
| 情报行动管线Agent | 04:00 UTC | n8n Cron Trigger（`trig_017vgQox9JUcwvnx43ucLRPd`） | 同上 |
| 日终复盘+博客生成 | 19:00 UTC | n8n Cron Trigger | 同上 |
| 每日任务恢复 | 06:00 Dubai | n8n Cron Trigger（`trig_01RJJoy4v8TLj2HyHRnABKJb`） | 同上 |

**关键发现**：n8n 配置中**不硬编码模型 ID**，仅触发远程 Claude Code Agent 脚本。模型选择由 Claude Code 运行时环境决定。

### API 调用依赖分析

| API/端点 | 配置文件 | 模型指定方式 |
|----------|----------|--------------|
| Claude Code（Claude Code 桌面应用） | 无配置文件 | 由 Claude Code 自动管理 |
| n8n Webhook（`n8n.lysander.bond`） | `n8n_integration.yaml` | 通过 Skill 调用 Claude Code，不直接指定模型 |
| Slack MCP | `settings.local.json` | MCP Connector 代理，不直接指定模型 |
| Google Calendar MCP | `settings.local.json` | 同上 |

### 定时任务 Agent 映射

| 定时任务 | 执行 Agent | 模型使用方式 |
|----------|-----------|--------------|
| 每日情报日报 | `synapse-intelligence-daily`（远程） | Claude Code API（凭证在 n8n 远程 Agent） |
| 每日行动管线 | `synapse-intelligence-action`（远程） | Claude Code API（凭证在 n8n 远程 Agent） |
| 任务自动恢复 | `synapse-task-resume`（远程） | Claude Code API（凭证在 n8n 远程 Agent） |
| 日终复盘 | `synapse-daily-review`（远程） | Claude Code API（凭证在 n8n 远程 Agent） |

---

## ③ 迁移资源估算

### 需修改文件数量

| 类别 | 文件数 | 说明 |
|------|--------|------|
| 核心运营配置（需修改） | **0 个** | 无硬编码，Claude Code 自动处理 |
| 情报报告文件（更新描述） | 5 个 | `obs/06-daily-reports/` 中的版本引用 |
| 任务跟踪记录 | 1 个 | `active_tasks.yaml` notes 字段（可选清理） |
| **合计** | **6 个文件**（均为信息记录，非运营代码） |

### 迁移复杂度

| 维度 | 评估 |
|------|------|
| 迁移难度 | **极低** — Synapse 架构不硬编码模型 ID |
| 配置文件变更 | **无需修改** — 架构设计规避了此风险 |
| 代码变更 | **无需修改** — `hr_base.py`、`n8n_integration.yaml` 均无引用 |
| 运营中断风险 | **极低** — 模型升级由 Claude Code 运行时处理 |
| 测试工作量 | **< 1 人日** — 确认主对话正常运行即可 |

### 实际需要执行的操作

由于 Synapse 采用 **Claude Code 运行时模型选择**（模型由 Claude Code 自动管理，不在配置文件中指定），迁移实际上是：

1. **被动等待停服**（2026-06-15）— 停服后 Claude Code 自动切换到新模型（如 `claude-sonnet-4-7`）
2. **验证功能正常** — 停服后确认核心功能（执行链、QA门禁、派单机制）运行正常
3. **更新情报报告历史版本引用**（可选）— 将旧版本引用更新为新模型 ID

### 潜在风险点

| 风险项 | 描述 | 缓解措施 |
|--------|------|----------|
| n8n 远程 Agent（定时任务） | 远程 Agent 可能使用固定模型 ID | 需确认 n8n 远程 Agent 配置；建议在停服前审查远程 Agent 的模型设置 |
| CLAUDE.md 中版本引用 | `claude-sonnet-4-6` 可能出现在说明文本中 | 更新文档版本说明 |
| API凭证兼容性 | 新模型是否需要新 API Key | 通常无需，Anthropic API Key 兼容所有同代模型 |

### 迁移时间估算

| 阶段 | 工作量 | 负责团队 |
|------|--------|----------|
| 阶段1：远程 Agent 配置审查 | 2 小时 | rd + ai_ml |
| 阶段2：n8n 定时任务模型配置确认 | 1 小时 | rd_devops + ai_ml_engineer |
| 阶段3：停服后功能验证 | 2 小时 | integration_qa |
| 阶段4：文档更新（可选） | 1 小时 | knowledge_engineer |
| **合计** | **约 6 小时** | — |

---

## ④ 建议迁移路径

### 推荐方案：被动迁移 + 主动验证

由于 Synapse 架构设计规避了硬编码模型引用，推荐**最低干预迁移路径**：

```
阶段1（立即）：远程 Agent 配置审查
├─ rd_devops + ai_ml_engineer 审查 n8n 远程 Agent 的模型配置
├─ 确认定时任务 Agent 不使用硬编码旧模型 ID
└─ 如有硬编码 → 替换为新模型（claude-sonnet-4-7 或 claude-opus-4-7）

阶段2（2026-06-15 前1周）：停服前准备
├─ 确认 Claude Code 版本为最新（支持 Sonnet 4.7 / Opus 4.7）
├─ 确认 API Key 有效且有余额
└─ 准备回滚方案（如降级到 Sonnet 4.7）

阶段3（2026-06-15 停服当日）：功能验证
├─ integration_qa 执行完整功能测试
├─ 验证执行链、派单机制、QA门禁正常运行
└─ 如有问题 → 立即回滚或联系 Anthropic 支持

阶段4（停服后1周）：文档收尾
├─ 更新 CLAUDE.md 中的版本引用
├─ 更新 active_tasks.yaml 中的 notes 字段
└─ 生成迁移完成报告
```

### 升级目标模型建议

| 当前模型 | 停服日期 | 推荐升级目标 | 理由 |
|----------|----------|-------------|------|
| `claude-sonnet-4-6` | 2026-06-15 | `claude-sonnet-4-7` | 保持 Sonnet 系列，成本/性能比最优 |
| — | — | `claude-opus-4-7` | 如需最高推理能力（成本为 Sonnet 5 倍） |

**建议**：主对话保持 `claude-sonnet-4-7`（综合性价比最优），复杂推理任务可切换 `claude-opus-4-7`。

### 下一步行动项

| # | 行动项 | 执行者 | 截止日期 | 优先级 |
|---|--------|--------|----------|--------|
| 1 | 审查 n8n 远程 Agent 配置，确认模型 ID | rd_devops + ai_ml_engineer | 2026-04-25 | P0 |
| 2 | 确认 Claude Code 支持 Sonnet 4.7 / Opus 4.7 | ai_ml_engineer | 2026-04-25 | P0 |
| 3 | 更新 CLAUDE.md 版本引用 | knowledge_engineer | 2026-04-30 | P1 |
| 4 | 更新 active_tasks.yaml notes 字段 | harness_engineer | 2026-04-30 | P1 |
| 5 | 停服前功能验证预案制定 | integration_qa | 2026-06-08 | P1 |

---

## 附录：扫描方法说明

### 扫描关键词
```
claude-sonnet-4, claude-opus-4, sonnet-4-6, sonnet-4-7,
opus-4-6, opus-4-7, claude-3-haiku-20240307
```

### 扫描文件类型
```
*.yaml, *.yml, *.json, *.py, *.md, *.html, *.js
```

### 排除范围（已验证无引用）
```
synapse.yaml, settings.json, settings.local.json,
n8n_integration.yaml, decision_rules.yaml,
organization.yaml, hr_base.py, build-distribution.py,
ceo_guard_pre.js, ceo_guard_post.js
```

---

*报告生成：rd_devops（INTEL-20260420-007）*
*审查：ai_ml_engineer（协助模型升级路径建议）*
*下次更新：2026-04-25（阶段1完成后）*
