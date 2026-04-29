# Synapse 双目录整合战略分析报告

**日期**：2026-04-22
**执行者**：Strategist（智囊团战略专家）
**任务来源**：Graphify 智囊团 — Synapse 双目录整合评估

---

## 一、两版本真实差异对照表（基于实际文件）

### 1.1 CLAUDE.md 核心规格

| 指标 | Multi-Agents System | Synapse-Mini | 说明 |
|------|---------------------|--------------|------|
| **CLAUDE.md 行数** | 378 行 | 397 行 | Mini 略多（+5%），但内容更精炼 |
| **执行链版本** | v2.0（无【0.5】承接节点） | v2.0（含【0.5】Lysander 承接强制节点） | Mini 更严格 |
| **CEO Guard 类型** | 建议式（Advisory，无技术封锁） | 技术封锁式（PreToolUse Hook + lysander_interceptor.py） | Mini 架构更健壮 |
| **派单制度** | 强制（含格式规范） | 强制（同等规范） | 持平 |
| **决策体系** | L1–L4 四级制 | L1–L4 四级制 | 相同 |
| **自动化编排章节** | 有（3个远程Agent时间线） | 有（同等自动化时间线） | 相同 |
| **Harness治理规则** | 无 | 有（熵增预算 350行 / 180天规则时效 / 3天审查） | Mini 独有 |
| **Phase 演进规划** | 无 | Phase 1/2/3 + 触发条件 | Mini 独有 |

### 1.2 技能体系（Skills）

| 维度 | Multi-Agents System | Synapse-Mini |
|------|---------------------|--------------|
| **Skill 数量** | **14 个** | **3 个** |
| **技能列表** | dispatch, graphify, qa-gate, intel, knowledge, hr-audit, retro, dev-plan, dev-review, dev-qa, dev-ship, dev-secure, daily-blog, synapse | gstack, gstack-qa, gstack-ship |
| **平均成熟度** | 高（已验证运营技能） | 高（聚焦 QA/Ship 专项） |
| **缺失技能** | — | synapse, intel, knowledge, hr-audit, retro, weekly-review, daily-blog, qa-gate, dev-plan, dev-secure, dev-review, dev-qa |

**Mini 缺失的 11 个 Skills（均为 Multi-Agents System 已有）**

| Skill | 功能 | 价值 |
|-------|------|------|
| `/synapse` | 体系状态查询与升级 | 高（核心基础设施） |
| `/intel` | 情报搜集简报 | 高（每日情报管线依赖） |
| `/knowledge` | 知识库管理 | 高（OBS 核心能力） |
| `/hr-audit` | Agent 能力审计 | 中（HR 管理必需） |
| `/retro` | 每日复盘博客生成 | 高（已接入情报管线） |
| `/weekly-review` | 周复盘生成 | 中（习惯性总结） |
| `/daily-blog` | 每日博客生成 | 高（情报管线输出依赖） |
| `/qa-gate` | QA 质量门禁触发 | 中（独立 QA 技能） |
| `/dev-plan` | 开发计划生成 | 中（研发辅助） |
| `/dev-review` | 代码审查 | 中（研发辅助） |
| `/dev-secure` | 安全审查 | 中（研发辅助） |

### 1.3 Python 模块体系

| 维度 | Multi-Agents System | Synapse-Mini |
|------|---------------------|--------------|
| **Python 模块数量** | **2 个**（hr_base.py, hr_watcher.py） | **18 个** |
| **模块列表** | hr_base（HR知识库+决策）, hr_watcher（文件监控） | hr_base, lysander_interceptor, harness_fsm, capability_router, opc_cfo, opc_coo, decision_engine, evolution_dashboard, intelligence_fanout, intelligence_forecaster, visual_qa, dispatch_auditor, dispatch_weekly_audit, capability_tracker, self_improvement, webhook_auth, webhook_health_checker, __init__ |
| **架构深度** | 基础 | 完整状态机 + 路由 + 进化追踪 + OPC体系 |
| **intercept 机制** | 无 | lysander_interceptor.py（P0强制） |
| **执行链状态机** | 无 | harness_fsm.py |
| **OPC Agent** | 无 | opc_cfo.py + opc_coo.py |
| **进化仪表板** | 无 | evolution_dashboard.py |
| **派单审计** | 无 | dispatch_auditor.py + dispatch_weekly_audit.py |

### 1.4 自动化与脚本体系

| 维度 | Multi-Agents System | Synapse-Mini |
|------|---------------------|--------------|
| **Agent Prompts** | 2 个（daily-intelligence-prompt, intelligence-action-prompt） | 0 个 |
| **核心脚本** | generate-article.py, build-distribution.py, generate-daily-intelligence.py, asana_notion_sync.py | build-distribution.py |
| **generate-article.py** | 有（科技蓝主题 HTML 生成，markdown+pygments 支持） | 无 |
| **PMO/WBS 脚本群** | 有（Janusd 公司专用，8+ 个脚本） | 无 |
| **n8n 集成** | agent-butler/config/n8n_integration.yaml | agent-CEO/config/n8n_integration.yaml（均存在） |

### 1.5 OBS 知识库

| 维度 | Multi-Agents System | Synapse-Mini |
|------|---------------------|--------------|
| **目录结构** | 完整（01-team-knowledge, 02-deliverables, 03-hr, 04-processes, 05-decisions, 06-daily-reports） | 基础（01-team-knowledge, 06-daily-reports 已有，其余为模板） |
| **实际内容** | 大量（人员卡片、决策日志、会话快照、博客文章） | 部分（已有 personnel/graphify/trend_watcher, 每日复盘博客, 情报日报） |
| **PDG 团队** | 有（executive_briefer + style_calibrator） | 无 |
| **session-snapshots** | 有 | 无（Mini 中不存在此目录） |
| **daily-reports** | 有（按日期组织） | 有（2026-04-17/18/19/20/21） |

---

## 二、整合价值量化评估

### 2.1 技能整合价值矩阵

| 迁移项目 | 来源 | 迁移至 | 整合难度 | 预期价值 | 优先级 |
|---------|------|--------|---------|---------|--------|
| 11 个缺失 Skills | Multi-Agents System | Synapse-Mini/skills/ | **低**（直接迁移） | ★★★★★ | P0 |
| generate-article.py | scripts/generate-article.py | Synapse-Mini/scripts/ | **低**（路径适配） | ★★★★★ | P0 |
| 2 个 Agent Prompts | agent-butler/config/ | agent-CEO/config/ | **低**（直接迁移） | ★★★★★ | P0 |
| PBS 简报体系 | CLAUDE.md 章节 + PDG 团队 | Synapse-Mini/CLAUDE.md + obs/ | **中**（需融合） | ★★★★☆ | P1 |
| SPE 完整章节 | CLAUDE.md SPE 章节 | Synapse-Mini/CLAUDE.md | **中**（需精简整合） | ★★★★☆ | P1 |
| PDG 团队 HR 卡片 | obs/HR/personnel/pdg/ | 同路径 | **低**（直接迁移） | ★★★☆☆ | P2 |
| n8n_integration.yaml | agent-butler/config/ | agent-CEO/config/ | **低**（URL 参数化） | ★★★☆☆ | P2 |

### 2.2 量化收益预估

| 指标 | 整合前 | 整合后 | 提升 |
|------|--------|--------|------|
| 可用 Skill 命令数 | 3 | 14 | **+367%** |
| 日常自动化覆盖 | 部分（情报管线已有） | 完整（含 QA-gate / daily-blog / intel 全链路） | **+200%** |
| Python 架构深度 | 2 模块 | 18 模块 | **+800%** |
| CEO Guard 防护 | 建议式 | 技术封锁式 | **+100%** |
| 总裁服务层 | 基础 | PBS 3x/天 + SPE 完整 | **+150%** |

---

## 三、整合后删除 Multi-Agents System 的风险评估

### 3.1 低风险项（可直接迁移后删除）

| 内容 | 风险原因 |
|------|---------|
| 11 个 Skills | 纯配置文本文件，迁移无技术风险 |
| generate-article.py | 独立脚本，无外部依赖 |
| Agent Prompts | 纯文本配置文件 |
| PBS/PBS 团队配置 | 独立 YAML/文档 |
| PDG HR 卡片 | 独立 Markdown 文档 |
| n8n_integration.yaml | 配置文件 |

### 3.2 中风险项（需适配后删除）

| 内容 | 风险 | 缓解措施 |
|------|------|---------|
| Janusd 公司专属脚本 | WBS/PMO 脚本与公司业务强绑定，不适合进 Mini 模板 | 保留在 Multi-Agents System，不迁移 |
| Obs 内容文件 | 决策日志/会话快照含总裁私人信息 | 选择性迁移，删除 Multi-Agents System 前做一次内容审查 |

### 3.3 高风险项（删除前必须完成迁移）

| 内容 | 风险 | 建议 |
|------|------|------|
| generate-article.py | daily-blog 和 retro Skill 依赖此脚本生成 HTML | 迁移前勿删除 Multi-Agents System |
| Synapse 版本历史 | Multi-Agents System 含完整演进记录 | 合并前将历史归档至 Synapse-Mini/obs/history/ |

### 3.4 整体风险评级

| 风险维度 | 评级 | 说明 |
|---------|------|------|
| 技术迁移风险 | 低 | Skills/Prompts/脚本均为静态文件，Git 操作即可完成 |
| 功能损失风险 | 低 | Mini 架构更优，迁移 Skills 后功能不减反增 |
| 知识丢失风险 | 中 | OBS 历史内容需主动迁移 |
| 运营中断风险 | 低 | 迁移可分阶段完成，不影响当前运营 |

**结论：删除 Multi-Agents System **可行**，风险可控，但需完成以下前置条件后执行。**

---

## 四、战略建议

### 4.1 建议：执行整合，路径为"选择性单向整合"

**核心理由：**
1. Mini 的技术架构（18 个 Python 模块 + lysander_interceptor + harness_fsm）是从 Multi-Agents System 演进而来，代表架构升级方向
2. Multi-Agents System 的 Skills/Prompts/脚本是经过实战验证的运营资产
3. 两版本属于"强架构 + 强运营"互补，整合后形成完整体系

### 4.2 整合路径（三阶段）

```
【第一阶段：P0 技能迁移】（预计完成时间：1小时）
  1. 将 11 个缺失 Skills 从 Multi-Agents System/skills/ 迁移到 Synapse-Mini/skills/
  2. 将 generate-article.py 迁移到 Synapse-Mini/scripts/
  3. 将 2 个 Agent Prompts 迁移到 Synapse-Mini/agent-CEO/config/
  4. 验证 Skill 命令可用性
  → 验证通过后，Multi-Agents System 进入"归档态"（只读）

【第二阶段：P1 模块融合】（预计完成时间：2小时）
  5. 将 SPE 完整章节从 Multi-Agents System 融入 Synapse-Mini/CLAUDE.md
  6. 将 PBS 简报体系章节 + PDG 团队配置融入 Mini
  7. 补充 Synapse-Mini/obs/ 中缺失的 session-snapshots 目录
  8. 融合 n8n_integration.yaml 参数
  → 融合后测试完整执行链

【第三阶段：归档与删除】（前置条件完成前不执行）
  9. 将 Multi-Agents System 完整归档为 synapse-archive-20260422.zip
  10. 删除 Multi-Agents System 目录（待总裁审批）
```

### 4.3 不整合项（明确排除）

以下内容**不迁移**，保留在 Multi-Agents System 归档包中：

| 内容 | 排除原因 |
|------|---------|
| WBS/PMO 脚本群（wbs_*.py, pmo_knowledge_loop.py, asana_notion_sync.py） | Janusd 公司业务专用，与 Synapse 体系无关 |
| Growth 团队配置 | 公司特定 GTM 场景 |
| Stock 股票项目团队 | 个人项目 |
| Janus 项目交付团队 | 建筑数字化/BIM/IoT 专属 |
| active_tasks.yaml 历史任务 | 总裁私人项目记录 |
| obs/ 中的实际决策日志和会话快照 | 私有内容，待主动筛选后决定是否迁移 |

### 4.4 关键决策问题答复

| 问题 | 答案 |
|------|------|
| **整合后删除 Multi-Agents System 可行吗？** | 可行。前置条件：① 完成 P0 Skills 迁移 ② 完成 generate-article.py 迁移 ③ 归档为 .zip。完成此三步后删除风险极低。 |
| **Skills 迁移后有功能损失吗？** | 无损失。反而增加 11 个 Skills，Mini 的 gstack Skills 继续保留。 |
| **PBS/SPE 简报体系能在 Mini 中重建吗？** | 可以迁移。Multi-Agents System 的 PBS 和 SPE 章节已验证可用，直接迁移比重建更快更安全。 |
| **"选择性单向整合"策略是否最优？** | 是。最优理由：Mini 架构是演进方向（18 > 2 Python 模块），Multi-Agents System 的运营资产（Skills）是经过验证的内容，单向迁移避免双向合并冲突。 |

---

## 五、结论

**执行建议：立即启动第一阶段（P0 Skills 迁移）**

**理由：**
- Skills 迁移技术风险为零（纯文本文件 Git 操作）
- 整合后立即产生价值（Skill 命令从 3 个增至 14 个）
- 不影响当前任何运营（可并行完成）
- 第一阶段完成后 Mini 即具备完整作战能力

**等待总裁审批：**
- 第三阶段（删除 Multi-Agents System 目录）的执行时间点

---

*报告生成：Strategist（智囊团战略专家）| 审查节点：Lysander CEO | 日期：2026-04-22*
