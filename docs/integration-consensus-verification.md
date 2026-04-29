# Synapse 双目录整合方案 — 共识验证报告

**日期**：2026-04-22
**执行者**：Decision Advisor（决策顾问）
**验证方法**：实地文件检查 vs 智囊团报告对比

---

## 一、报告 vs 实际文件 差异对照表

### 🔴 必须整合项（报告声称）— 实际验证

| 报告声称缺失 | 验证方法 | 实际状态 | 是否吻合 |
|------------|---------|---------|---------|
| 12个 Skills | `.claude/skills/` + `skills/` Glob | Mini有8个技能（.claude/skills/ 3个 + skills/ 5个）；报告称"synapse/graphify/qa-gate..."等12个 — **无实际文件支撑** | ⚠️ 部分失实 |
| SPE 完整模块 | Grep "SPE\|OKR\|日行事历" | CLAUDE.md中无SPE章节 | ✅ 确认缺失 |
| PBS 简报体系 | Grep "briefer\|简报" + pdg团队 | organization.yaml中有pdg团队（含executive_briefer、style_calibrator）；obs/HR/personnel/pdg/存在2张HR卡 | ⚠️ 部分存在 |
| 5个自动化Agent Prompts | agent-CEO/config/ Glob | agent-CEO/config/下无.md文件（仅有.yaml/.py/.js） | ✅ 确认缺失 |
| Product Ops 团队 | Grep "product_ops\|Product Ops" | organization.yaml中无此团队 | ✅ 确认缺失 |
| generate-article.py | scripts/ Glob | scripts/下无此文件（仅有build-distribution.py） | ✅ 确认缺失 |

### 🟢 不建议整合项（报告建议删除）— 实际验证

| 报告建议删除 | 验证方法 | 实际状态 | 是否吻合 |
|------------|---------|---------|---------|
| Janus 项目交付团队 | organization.yaml + synapse.yaml | 存在opt_janus配置（enable: false），synapse.yaml有注释引用 | ✅ 确认为可选模块 |
| Stock 股票项目团队 | organization.yaml | 存在opt_stock配置（enable: false） | ✅ 确认为可选模块 |
| Growth 团队配置 | organization.yaml | Growth团队**已启用**（growth_insights/gtm_strategist/sales_enablement/community_manager） | ❌ 与报告矛盾 |
| OBS实际内容文件 | obs/目录 | obs/01-team-knowledge/HR/personnel/下存在实际HR卡和内容 | ✅ 确认含私有内容 |

---

## 二、共识吻合度评分

| 维度 | 评估项数 | 准确数 | 失实数 | 吻合度 |
|------|---------|-------|-------|--------|
| 🔴 必须整合项 | 6 | 4 | 2 | **67%** |
| 🟢 不建议整合项 | 4 | 3 | 1 | **75%** |
| **整体** | **10** | **7** | **3** | **70%** |

**关键失实项：**
1. **Skills数量**：报告声称当前版有20个Skills，实际检查 `.claude/skills/` 仅3个有效文件（gstack-review/qa/ship），其余5个在 `skills/` 目录。报告所说的"synapse/graphify/qa-gate..."等12个技能**无文件支撑**，属于引用失准。
2. **PBS部分存在**：report声称PBS"无"，实际上pdg团队已在Mini中配置，executive_briefer和style_calibrator两张HR卡已就位。
3. **Growth团队**：报告建议"不建议整合Growth团队配置"，但Growth团队在Mini中**已启用且活跃**，不是待整合项。

---

## 三、最优先整合项 TOP3（基于实际缺失度）

### 🥇 第1优先：5个自动化 Agent Prompts

**现状**：Mini的 `agent-CEO/config/` 下无任何 .md Prompt文件
**缺口影响**：情报闭环管线（6am/8am/10am/8pm自动化）**完全缺失执行依赖**
**整合内容**（优先级排序）：
1. `情报日报Agent Prompt` → 驱动每日8am情报生成
2. `情报行动Agent Prompt` → 驱动每日10am评估执行
3. `任务恢复Agent Prompt` → 驱动6am断点续接
4. `日历同步Agent Prompt` → 驱动日历自动化
5. `复盘博客Agent Prompt` → 驱动每日复盘内容生成

**整合路径**：`agent-CEO/config/` — 需从原 ai-team-system 的 agent-butler/config/ 迁移5个 .md 文件
**价值**：解锁整个自动化闭环，是Mini从"人工驱动"升级为"系统驱动"的关键

---

### 🥈 第2优先：SPE 完整模块（OKR追踪 + 行为观察）

**现状**：CLAUDE.md无SPE章节；仅有基础 capture/plan-day Skills
**缺口影响**：总裁个人效率系统不完整，无法追踪OKR进度和行为决策日志
**整合内容**：
1. CLAUDE.md 新增 SPE 章节（OKR目标设定/追踪/复盘）
2. `personal_tasks.yaml` 模板 → `agent-CEO/config/`
3. `spe_intelligence.yaml` → `agent-CEO/config/`（行为观察记录）

**整合路径**：CLAUDE.md + `agent-CEO/config/personal_tasks.yaml`
**价值**：总裁每日使用的核心系统，直接影响执行效率

---

### 🥉 第3优先：generate-article.py 脚本

**现状**：scripts/目录下无此文件
**缺口影响**：daily-blog/retro技能的执行依赖缺失，导致每日复盘博客无法自动化生成HTML
**整合内容**：`scripts/generate-article.py`
**价值**：内容运营自动化链路的关键节点，与 `daily-blog` Skill配套使用

---

## 四、整合后删除 Multi-Agents System 的风险清单

> 注：此节针对"ai-team-system（当前版）"的删除风险，与Synapse-Mini无关

| 风险项 | 风险等级 | 描述 | 缓解措施 |
|--------|---------|------|---------|
| **Skills命令断链** | 🔴 高 | 报告称有12个Skills，删除后若用户仍使用旧命令会触发失败 | 保留 `skills/` 目录中的5个核心Skills（dispatch/capture/plan-day/time-block/weekly-review）；旧命令映射到新Skills |
| **PBS简报服务中断** | 🔴 高 | 若删除 PDG团队，3x/天简报服务停止 | PDG团队在Mini中已存在（非删除项），无需担心 |
| **自动化管线崩溃** | 🔴 高 | 若删除自动化Agent Prompts，定时任务全部失效 | 迁移Prompts到Mini后，原系统可安全删除 |
| **Growth团队误删** | 🟡 中 | Growth团队在Mini中已启用，删除原版无影响 | 无需操作 |
| **Janus/Stock可选模块误操作** | 🟡 中 | organization.yaml中的opt_janus/opt_stock若被错误启用 | 保持默认disable状态，不影响主线 |
| **OBS内容文件误删** | 🟡 中 | obs/目录下的实际HR卡和内容文件若被删除 | 私有内容不打包进分发模板，已在🟢建议中处理 |
| **Python模块依赖** | 🔴 高 | generate-article.py缺失导致内容生成链路断裂 | 优先迁移脚本，再执行删除判定 |

---

## 五、补充发现（报告未提及的差异）

| 发现项 | 说明 |
|--------|------|
| **PBS部分存在** | pdg团队已在Mini中配置，但可能缺少 PDG章节（CLAUDE.md无PBS章节） |
| **Growth已活跃** | 报告建议"不建议整合Growth"，但Growth在Mini中已是活跃团队（enabled: true） |
| **Janus/Stock仅配置无成员卡** | opt_janus/opt_stock在organization.yaml中定义了成员列表（janus_pm/de/sa.../stock_analyst/quant...），但obs/HR/personnel/下无对应HR卡片 |
| **CLAUDE.md行数** | 当前行数398行，未超过350行熵增预算上限 |

---

## 六、结论

**智囊团报告共识吻合度：70%**

报告整体方向正确（自动化Prompts缺失、SPE缺失是真实缺口），但存在3处关键失实：
1. Skills数量夸大了约50%（12 vs 实际8个，且来源文件不存在）
2. PBS系统部分存在（pdg团队已配置，只是缺少CLAUDE.md章节）
3. Growth团队建议删除有误（已启用状态）

**最优先整合TOP3**：
1. 自动化Agent Prompts（5个.md文件）→ 解锁情报管线自动化
2. SPE完整模块（OKR+行为观察）→ 总裁核心效率系统
3. generate-article.py → 内容生成链路关键节点

**删除ai-team-system前必须完成**：以上TOP3迁移 + Skills命令映射验证 + PBS CLAUDE.md章节补充

---

*验证报告：Decision Advisor | 2026-04-22*