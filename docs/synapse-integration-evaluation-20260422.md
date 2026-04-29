# Synapse 体系整合评估报告

**日期**：2026-04-22  
**评估范围**：ai-team-system（当前版）→ Synapse-Mini（优化版）整合分析  
**执行团队**：Graphify智囊团（strategist + decision_advisor + execution_auditor）

---

## 一、两版本核心差异速览

| 维度 | ai-team-system（当前版） | Synapse-Mini（优化版） | 优势方 |
|------|------------------------|----------------------|--------|
| CLAUDE.md 行数 | 543行 | 392行（-27%） | Mini |
| CEO Guard | 建议式（Advisory） | 技术封锁（Blocking）+ 5个测试用例 | Mini |
| 自定义 Skills | 20个 | 8个（5 SPE + 3 gstack） | 当前版 |
| 核心 Python 模块 | 8个（基础） | 15个（状态机/路由/进化/CFO/COO） | Mini |
| 派单机制 | 强制（含格式规范） | 强制（同等规范） | 持平 |
| 自动化 Agent Prompts | 5个专属 Prompt 文件 | 无 | 当前版 |
| SPE 个人效率模块 | 完整（含OKR追踪） | 基础 capture/plan-day | 当前版 |
| PBS 简报体系 | 完整（PDG 团队 + 3x/天） | 无 | 当前版 |
| Product Ops 团队 | ✅ | 无 | 当前版 |
| OBS 知识库 | 成熟（含实际内容） | 结构模板（空） | 当前版 |
| 文档体系 | README.md | QUICKSTART/SETUP/COLLEAGUE_GUIDE | Mini |
| 进化架构 | 无明确 Phase 规划 | Phase 1/2/3 + 熵增预算 | Mini |
| 分发/模板系统 | 无 | build-distribution.py + templates/ | Mini |
| OPC（CFO/COO Agent） | 无 | opc_cfo.py + opc_coo.py | Mini |
| 执行链状态机 | 无 | harness_fsm.py | Mini |

---

## 二、整合价值矩阵（当前版 → Synapse-Mini）

### 🔴 必须整合（高价值 · 通用性强）

| 内容 | 来源路径 | 整合到 Mini 的位置 | 理由 |
|------|---------|-----------------|------|
| 12个缺失 Skills | `.claude/skills/` | `skills/` | synapse/graphify/qa-gate/retro/knowledge/intel/weekly-review/daily-blog/hr-audit/video-tutorial/dev-plan/dev-secure 均为成熟命令 |
| SPE 完整模块 | CLAUDE.md SPE 章节 + personal_tasks.yaml + spe_intelligence.yaml | CLAUDE.md + agent-CEO/config/ | Mini 的 capture/plan-day 只是 SPE 的子集，缺少 OKR 追踪、行为观察、决策日志 |
| PBS 简报体系 | CLAUDE.md PBS 章节 + PDG 团队配置 | CLAUDE.md + obs/HR/personnel/pdg/ | executive_briefer + style_calibrator 是已验证的高价值模块，3x/天简报是总裁核心服务 |
| 5个自动化 Agent Prompts | agent-butler/config/*.md | agent-CEO/config/ | 情报日报/行动/任务恢复/日历同步/复盘博客 — 自动化闭环的核心驱动，Mini 完全缺失 |
| Product Ops 团队 | organization.yaml 中 product_ops 节 | agent-CEO/config/organization.yaml | synapse_product_owner + requirements_analyst 负责 Synapse 产品化 |
| generate-article.py | scripts/generate-article.py | scripts/ | HTML 自动生成是 daily-blog/retro 技能的执行依赖 |
| briefing_style_guide.yaml | agent-butler/config/ | agent-CEO/config/ | 配合 style_calibrator 的运行时配置 |

### 🟡 建议整合（中等价值 · 需适配）

| 内容 | 来源路径 | 整合建议 | 备注 |
|------|---------|---------|------|
| test_runner 验证框架 | agent-butler/test_runner/ | agent-CEO/test_runner/ | 需适配新路径 |
| n8n_integration.yaml | agent-butler/config/n8n_integration.yaml | agent-CEO/config/ | 整合时需参数化 URL |
| OBS 6大目录结构 | obs/ 目录体系 | obs/ | 补充 session-snapshots / daily-reports 两个目录 |
| PDG 团队 HR 卡片 | obs/HR/personnel/pdg/ | 同路径迁移 | executive_briefer.md + style_calibrator.md |
| 主动驱动协作模式 | CLAUDE.md 归档跟进章节 | CLAUDE.md | 防止任务归档后被遗忘 |

### 🟢 不建议整合（公司专属 · 降低通用性）

| 内容 | 原因 |
|------|------|
| Janus 项目交付团队 | 建筑数字化/BIM/IoT 是 Janusd 公司专属业务 |
| Stock 股票项目团队 | 趋势智选/A股交易系统是个人项目 |
| active_tasks.yaml 历史任务 | 总裁专属项目记录，不适合打包进模板 |
| Growth 团队专属配置 | 面向 Janusd 特定 GTM 场景 |
| obs/ 中的实际内容文件 | 决策日志、会话快照、博客文章均为私有内容 |

---

## 三、整合优先级与执行序列

```
第一优先（即刻价值，无风险）：
  ├── 12个 Skills 迁移到 skills/ 目录
  ├── 5个自动化 Agent Prompts → agent-CEO/config/
  └── generate-article.py → scripts/

第二优先（完整模块，需插入 CLAUDE.md）：
  ├── SPE 完整模块（章节 + 配置文件）
  ├── PBS 简报体系（章节 + PDG 团队配置）
  └── 主动驱动协作章节

第三优先（需适配后整合）：
  ├── test_runner 框架（路径适配）
  ├── n8n_integration.yaml（URL 参数化）
  └── OBS 目录结构补充（session-snapshots / daily-reports）
```

---

## 四、整合后预期提升

| 指标 | 整合前 | 整合后 |
|------|--------|--------|
| Skills 命令数 | 8 | 20 |
| 日常自动化覆盖 | 无 | 6am/8am/10am/8pm 四链路 |
| 个人效率模块 | 基础 | SPE 完整（OKR + 日历 + 行为观察） |
| 总裁服务层 | 无 | PBS 3x/天简报 |
| 产品化管理能力 | 无 | Product Ops 双角色 |
| QA 门禁能力 | qa_engineer | qa-gate Skill + test_runner 框架 |

---

## 五、结论与推荐方案

**评估结论**：两版本属于"强弱互补"关系。Mini 的技术架构更扎实（状态机/拦截器/CFO/进化仪表板），当前版的运营内容更丰富（Skills/SPE/PBS/Prompts）。

**推荐方案**：选择性单向整合 — 将当前版的运营层内容移植入 Mini，保留 Mini 的技术架构不变。

**理由**：
- Mini 的 CEO Guard 技术封锁比当前版更严格，应作为基准
- Mini 的 Python 模块体系（harness_fsm / capability_router / evolution_dashboard）是架构升级，不应被降级
- 当前版的 Skills 和 Prompts 是经过实战验证的运营资产，直接移植风险极低

---

*报告生成：Graphify智囊团 | 审查：Lysander CEO | 2026-04-22*
