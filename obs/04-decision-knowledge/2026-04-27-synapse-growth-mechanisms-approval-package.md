---
title: Synapse 体系审查 + 成长机制综合审批包
type: core
status: pending_approval
decision_level: L4
created: 2026-04-27
author: 智囊团（strategy_advisor + execution_auditor + decision_advisor）
reviewers: [Lysander, 总裁刘子杨]
domain: harness-governance
priority: P0
mechanism_count_after: 8
mechanism_count_before: 5
source_proposals: [agent-A-harness-weekly-review, agent-B-strategic-discovery, agent-C-knowledge-content-feedback]
binding: false
---

# 战略审批包：Synapse 体系审查 + 优化机制

## BLUF（4 行给总裁）

- 三方案已综合评审：当前 14 个机制中 4 真跑/6 纸面/4 空转，P0 规则自身已失效（CLAUDE.md 超线 17%、决策归档率 < 5%、intercept_log 死亡 5 天）
- 推荐战略：**8 机制硬上限** + 周/双周/月分层节奏 + **智囊团独立路径**（绕开 Lysander 自评陷阱）
- 立即可做 PATCH 7 项（Lysander 自主，本周内闭环）；月度三项扩展深审挂载在周审查上，不算独立机制
- **等待总裁对 4 个 L4 决策点裁决**（CLAUDE.md 上限 / 周审查入 P0 / 智囊团独立汇报 / 决策强制归档）

---

## 一、核心共识（三方案一致项）

| # | 共识 | 来源 |
|---|------|------|
| C1 | 当前 Harness 已存在熵增危机（行数超线 + 机制空转 + 自评陷阱） | A+B+C |
| C2 | 必须有"非 Lysander 主导"的独立审查路径，否则陷入自评者陷阱 | B+C |
| C3 | 机制总数必须设上限，否则越建越多反噬执行力 | B（A/C 默认认可） |
| C4 | 决策归档（D-编号）严重不足，是追溯能力的最大短板 | A+C |
| C5 | 立即可做的 PATCH 项不需要新机制，只需要把已有的接通（cron / 孤儿脚本 / 死库） | A+C |
| C6 | 双语博客网站层是当前唯一 100% 对齐的治理标杆，可作为复用模板 | C（A/B 未否认） |
| C7 | 月度低频机制不应作为独立机制，应作为高频机制的"扩展深审" | B（A/C 兼容） |

---

## 二、综合方案要点

### 2.1 8 机制全景图

```
┌─────────────────────────────────────────────────────────────┐
│  日                                                          │
│   ├─ 情报闭环（n8n + Agents → Lysander）           [已有]   │
│   └─ active_tasks 续接（自动恢复）                  [已有]   │
│                                                              │
│  周                                                          │
│   └─ Harness 周审查（harness_engineer + execution_auditor   │
│      → Lysander → 总裁摘要一行）                    [新建]  │
│      （月度第一周附加：Agent 进化 + 情报质量深审）           │
│      （月度最后周附加：决策回溯 + 凭证安全深审）             │
│                                                              │
│  双周                                                        │
│   ├─ OBS 健康度（knowledge_engineer → Lysander）    [新建]  │
│   └─ 战略对齐（智囊团独立 → 总裁，绕 Lysander）     [新建]  │
│                                                              │
│  事件触发                                                    │
│   ├─ 双语博客 SOP（content_strategist）             [已有]   │
│   └─ Pipeline Product 治理（harness_engineer）      [已有]   │
│                                                              │
│  实时                                                        │
│   └─ CEO Guard hook（PreToolUse → 审计日志）        [已有]   │
│                                                              │
│  合计：8 个机制，达到 Agent B 推荐上限                       │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 分层节奏 + 责任链

| 机制 | 频次 | 执行者 | 消费者 | 行动通道 |
|------|------|--------|--------|---------|
| 情报闭环 | 日 8/10am | n8n cron | Lysander | Slack 通知总裁 |
| active_tasks 续接 | 日 6am | 自动恢复 Agent | Lysander | 内部续接 |
| **Harness 周审查** | **周日 23:00** | harness_engineer + execution_auditor | Lysander → 总裁一行 | PATCH/MINOR/L4 三级上报 |
| **OBS 健康度** | **双周一 10:00** | knowledge_engineer | Lysander | OBS 报告 + Lysander 派单修复 |
| **战略对齐** | **双周三 10:00** | 智囊团（独立） | **直达总裁** | 总裁直接裁决，Lysander 收转发 |
| 双语博客 SOP | 事件 | content_strategist | 内部 QA | 发布前 checklist |
| Pipeline Product | 事件 | harness_engineer | Lysander → 总裁 | 设计变更走 L3 |
| CEO Guard hook | 实时 | PreToolUse hook | 审计日志 | 每日审计聚合到周审查 |

### 2.3 立即 PATCH 修复（Lysander 自主，本周内闭环）

| # | PATCH | 优先级 | 负责人 | 完成判据 |
|---|-------|--------|--------|---------|
| P1 | 紧急压缩 CLAUDE.md（超线 17% → 350 内或申请上调） | P0 | harness_engineer | 行数 ≤ 总裁批复值 |
| P2 | dispatch_weekly_audit.py 接通 cron / 删除（孤儿） | P0 | ai_systems_dev | 真跑或归档 |
| P3 | intercept_log 死亡 5 天 → 检测 LysanderInterceptor 调用断点 | P0 | execution_auditor | 当日恢复写入 |
| P4 | decision-log 补归档（13 天 0 新增 → 至少补回 5 个 L3） | P1 | knowledge_engineer | D-编号 ≥ 5 |
| P5 | frontmatter 合规率 47% → 修复 OBS 已有文档批量补 frontmatter | P1 | knowledge_engineer | 合规率 ≥ 80% |
| P6 | 5 闲置目录评估（删 / 启用 / 合并） | P2 | knowledge_engineer | 闲置归零 |
| P7 | 14 机制纸面项清理（保留真跑 4 + 新建 3 + Pipeline Product 1 = 8，其余降级或归档） | P0 | execution_auditor | 机制清单收敛到 8 |

### 2.4 智囊团独立路径设计（关键创新）

**问题**：Agent B 警告"自评者陷阱" — Lysander 主导的审查会自动美化数据。

**方案**：战略对齐审查由 **strategy_advisor + decision_advisor** 双周独立执行：
- 直接对照总裁原始意图（人员卡 + 重大决策记录） vs Lysander 当期实际派单
- 输出"对齐分"：1-5 分 + 偏移项清单
- **绕过 Lysander，直达总裁** 收摘要
- Lysander 收"已发送"通知，可申辩但不能拦截

**保护机制**：避免变成"小报告通道" — 智囊团必须基于事实数据（决策日志 + 派单记录），不接受主观判断。

---

## 三、跨方案冲突 + 裁决

| # | 冲突 | A 立场 | B 立场 | C 立场 | **裁决** | 理由 |
|---|------|--------|--------|--------|----------|------|
| F1 | 周审查维度数 | 6 维度 | ≤ 8 机制（含审查内部） | 反馈+知识+内容 3 维独立 | **6 维度但分级**：D1-D3 周做、D4-D6 隔周做 | 兼顾覆盖度与机制熵 |
| F2 | OBS 审查频次 | 未涉及 | 双周 | 月 | **双周** | 月度太疏，缺口已浮现，Agent C 可在双周内消化 |
| F3 | 内容质量审查频次 | 未涉及 | 不进 Top 5 | 周 | **取消独立机制**，并入双语博客 SOP 事件触发 | 避免频次过密，无变更不审 |
| F4 | 反馈机制是否新建 | 未涉及 | 未推荐 | 周（前置先建反馈通道） | **暂缓**，前置条件未满足，Q3 重评 | C 自身承认前置依赖未就绪 |
| F5 | 月度三项是否独立 | 未明确 | 月独立 | 月独立 | **挂载在周审查的月度扩展位** | 满足 ≤ 8 上限 |

---

## 四、总裁裁决 4 个 L4 决策点

### 决策 ①：CLAUDE.md 350 行预算的现实

**事实**：当前 407 行，超线 17%；Phase 2 原计划收紧至 300 行。

**选项**：
- **A. 严格压缩到 350**（删 5-7 个 P1/P2 规则迁至 `.claude/harness/` 碎片）⭐ **智囊团建议**
- B. 上调上限至 380（承认现实但不放任）
- C. 维持 350 + 推迟 Phase 2 收紧（妥协选项）

**智囊团建议理由**：上限是治理意志的锚点，松动一次就再难收紧。已有 5 个 P1/P2 规则块属于"参考模块"性质（HR 评分细则、凭证使用、升级协议、Visual QA、月度扩展），完全可以迁移而不丢失约束力。

**裁决**：☐ A  ☐ B  ☐ C  ☐ 其他：__________

---

### 决策 ②：周审查机制是否写入 CLAUDE.md "Harness 治理规则" 节作为 P0 规则

**含义**：与"3 天定期审查"同级，写入即不可被 Lysander 自主撤销。

**选项**：
- **A. 写入 P0 节**（与 350 行预算同级硬约束）⭐ **智囊团建议**
- B. 仅写入 SOP 文档，不入 P0 节（柔性规则）
- C. 暂不写入，先观察 4 周（Phase 0 验证期）

**智囊团建议理由**：周审查的核心价值是约束 Lysander 自身，若放在 SOP 文档中 Lysander 可自主推迟，等于无约束。写入 P0 后总裁有撤销权但 Lysander 没有。

**裁决**：☐ A  ☐ B  ☐ C  ☐ 其他：__________

---

### 决策 ③：战略对齐审查由智囊团独立汇报总裁（绕开 Lysander）

**含义**：每双周一次，智囊团基于事实数据独立评估"Lysander 是否在朝总裁意图执行"，绕过 Lysander 直达总裁。

**选项**：
- **A. 同意，智囊团独立 → 总裁** ⭐ **智囊团建议**（避免自评陷阱）
- B. 仍由 Lysander 主导，智囊团辅助（保留单一汇报通道）
- C. 不实施此机制（Lysander 信任度足够）

**智囊团建议理由**：Agent B 的"自评者陷阱"风险是真实的 — 当前 14 机制中 6 纸面、4 空转能存活，正是因为没有非 Lysander 视角的审查。智囊团独立路径不是夺权，是质保。

**风险**：可能演变为"小报告通道"，因此需明确"必须基于事实数据，不接受主观判断"约束。

**裁决**：☐ A  ☐ B  ☐ C  ☐ 其他：__________

---

### 决策 ④：决策归档（D-编号）强制化

**事实**：30 个 L3+ 决策被提及 vs 1 份正式归档（< 5%），13 天 0 新增。这是追溯能力的根基。

**选项**：
- **A. 强制：所有 L3+ 决策必须 D-编号归档**（CI/hook 拦截，未归档无法继续派单）⭐ **智囊团建议**
- B. 鼓励但不强制（保留软规则）
- C. 仅 L4 决策强制（最低限度）

**智囊团建议理由**：决策归档是 Lysander 自我训练的唯一数据源（Agent B 洞察）。无归档 = 无成长 = 智囊团永远是单次咨询而不是积累式智能。CI 拦截是唯一能落地的强制机制。

**裁决**：☐ A  ☐ B  ☐ C  ☐ 其他：__________

---

## 五、Lysander 自主决策（已决，仅通报总裁）

| # | 决策 | 范围 | 状态 |
|---|------|------|------|
| L3-1 | 立即派单 7 项 PATCH（见 §2.3） | Harness Ops 团队 | 待批后启动 |
| L3-2 | 周审查频次：周日 23:00 Dubai | 时间安排 | 已定 |
| L3-3 | OBS 健康度双周一 10:00 / 战略对齐双周三 10:00 | 时间安排 | 已定 |
| L3-4 | 月度三项扩展挂载在 Harness 周审查（不算独立机制） | 机制结构 | 已定 |
| L3-5 | 反馈机制暂缓（前置条件未满足，Q3 重评） | 机制裁剪 | 已定 |
| L3-6 | 内容质量审查并入双语博客 SOP 事件触发 | 机制裁剪 | 已定 |

---

## 六、机制清单总览

| # | 机制 | 频次 | 执行者 | 消费者 | 已有/新建 |
|---|------|------|--------|--------|----------|
| 1 | 情报闭环 | 日 8/10am | n8n + Agents | Lysander → 总裁 | 已有 |
| 2 | active_tasks 续接 | 日 6am | 自动 | Lysander | 已有 |
| 3 | **Harness 周审查** | 周日 23:00 | harness_engineer + execution_auditor | Lysander → 总裁一行 | **新建** |
| 4 | **OBS 健康度** | 双周一 10:00 | knowledge_engineer | Lysander | **新建** |
| 5 | **战略对齐** | 双周三 10:00 | 智囊团（独立） | **直达总裁** | **新建** |
| 6 | 双语博客 SOP | 事件 | content_strategist | 内部 | 已有 |
| 7 | Pipeline Product 治理 | 事件 | harness_engineer | Lysander → 总裁 | 已有 |
| 8 | CEO Guard hook | 实时 | PreToolUse hook | 日志 | 已有 |

**合计 8 个，达上限。再加任何机制必须先撤一个。**

---

## 七、月度扩展（不算独立机制）

挂载在 Harness 周审查上，每月特定周次执行深审：

| 扩展项 | 挂载位置 | 执行者 |
|--------|---------|--------|
| Agent 能力进化深审 | 每月第一周 Harness 审查 | harness_engineer |
| 情报质量深审 | 每月第一周 Harness 审查 | content_strategist |
| 决策回溯（Lysander 自训练） | 每月最后一周 Harness 审查 | 智囊团 |
| 凭证安全巡检 | 每月最后一周 Harness 审查 | harness_engineer |

---

## 八、风险矩阵 + 缓解（5 条）

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| R1 机制熵增反噬（建机制本身是熵） | 中 | 高 | 8 上限硬约束 + 月度扩展挂载不独立 |
| R2 仪式化（连续 2 期无 actionable 即弃） | 高 | 中 | 周审查必须输出 ≥ 1 PATCH 否则记空转 |
| R3 自评者陷阱（Lysander 美化数据） | 高 | 高 | 智囊团独立路径 + 战略对齐绕 Lysander |
| R4 立即可做太多导致总裁审批阻塞本周执行 | 中 | 中 | L3 PATCH 可在总裁批 L4 前并行启动 |
| R5 反馈通道前置不到位 → 反馈机制空跑 | 已规避 | - | F4 裁决：暂缓反馈机制，Q3 重评 |

---

## 九、执行启动条件

**前置（总裁裁决）**：
- ☐ 决策 ① CLAUDE.md 上限
- ☐ 决策 ② 周审查入 P0
- ☐ 决策 ③ 智囊团独立路径
- ☐ 决策 ④ 决策强制归档

**总裁批复后 Lysander 立即动作**：
1. 派单 7 项 PATCH（harness_engineer + ai_systems_dev + knowledge_engineer + execution_auditor 协同）
2. 第一次 Harness 周审查：本周日 23:00 Dubai
3. 第一次 OBS 健康度：下周一 10:00
4. 第一次战略对齐：下周三 10:00（智囊团独立通道首次激活）
5. CLAUDE.md 更新：写入新 P0 节点（如决策 ② 选 A）

---

## 十、附：原始三份方案归档位置

- Agent A（Harness 周审查机制）：见本次会话评审消息中"三份原始方案核心摘要"§A
- Agent B（战略发现）：见本次会话评审消息中"三份原始方案核心摘要"§B
- Agent C（知识 + 内容 + 反馈）：见本次会话评审消息中"三份原始方案核心摘要"§C
- 评审执行者：智囊团合并工（strategy_advisor + execution_auditor + decision_advisor）
- 评审时间：2026-04-27
- 本文档为最终综合审批包，原始三份并入归档

---

**文档签字位**：

- 智囊团评审完成：✓ 2026-04-27
- Lysander 审核：☐
- 总裁批复：☐
