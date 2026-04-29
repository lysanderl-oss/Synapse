# gstack × Synapse v3.0 融合规范草案

版本：v0.1 草案
起草人：harness_engineer
日期：2026-04-19
状态：待 Lysander CEO 审批 → 待总裁刘子杨验收

---

## 一、命令归属映射表

gstack 共23条命令，按职能域映射到 Synapse 现有团队和专员。

### 1.1 完整映射

| gstack 命令 | 角色描述 | 映射团队 | 主责专员 | 协同专员 | 触发条件 |
|-------------|----------|----------|----------|----------|----------|
| `/office-hours` | 创始人/总裁开放答疑 | pdg | executive_briefer | graphify_strategist | 总裁主动发起或日历触发 |
| `/plan-eng-review` | 工程规划评审 | rd | rd_tech_lead | rd_backend / rd_frontend | M/L级研发任务启动前 |
| `/build` | 功能实现构建 | rd | rd_backend / rd_frontend | rd_devops | 规划评审通过后 |
| `/review` | 代码审查 | rd | rd_tech_lead | rd_backend / rd_frontend | 每次 PR 提交强制触发 |
| `/qa` | 质量验证 | rd | rd_qa | integration_qa | 代码审查通过后强制触发 |
| `/ship` | 发布上线 | rd | rd_devops | rd_qa | QA全部通过后 |
| `/retro` | 迭代复盘 | butler | butler_pmo | execution_auditor | 每次发布后 / 周回顾 |
| `/cso` | 安全主管评审 | specialist | legal_counsel (兼) / rd_qa | rd_backend | L级任务强制，M级可选 |
| `/founder` | 创始人视角决策 | pdg | executive_briefer | graphify_strategist | L4决策上报前准备 |
| `/ceo` | CEO战略对齐 | graphify | graphify_strategist | Lysander CEO | L3决策场景 |
| `/cto` | 技术战略评审 | rd | rd_tech_lead | graphify_strategist | 技术选型/架构变更 |
| `/pm` | 产品经理规划 | butler | butler_pmo | growth_gtm_strategist | 需求分析/路线图 |
| `/eng-manager` | 工程经理协调 | rd | rd_tech_lead | butler_pmo | 跨模块任务协调 |
| `/qa-lead` | QA主管流程管控 | rd | rd_qa | integration_qa | QA流程设计/改进 |
| `/security` | 安全专项审查 | specialist | legal_counsel (兼) / rd_qa | rd_backend | 上线前安全扫描 |
| `/design-review` | 设计评审 | rd | rd_frontend | content_ops | UI/UX 交付前 |
| `/data` | 数据分析洞察 | specialist | financial_analyst / graphify_strategist | obs_knowledge_engineer | 数据驱动决策 |
| `/marketing` | 市场策略 | growth | gtm_strategist | content_strategist | GTM/发布推广 |
| `/gtm` | Go-to-Market 规划 | growth | gtm_strategist | graphify_strategist | 新产品/功能发布 |
| `/legal` | 法律合规审查 | specialist | legal_counsel | Lysander CEO | 合同/IP/合规 |
| `/finance` | 财务评估 | specialist | financial_analyst | Lysander CEO | 预算/P&L决策 |
| `/docs` | 文档沉淀 | obs | obs_knowledge_engineer | rd_tech_lead | 每次交付后 |
| `/standup` | 日站会同步 | butler | butler_pmo | execution_auditor | 每日自动触发 |

### 1.2 安全覆盖缺口说明

> **缺口识别**：Synapse 当前无专属 `security_engineer` Agent。`/cso` 和 `/security` 命令目前由 `rd_qa`（STRIDE威胁建模能力）+ `legal_counsel`（合规视角）联合覆盖。
>
> **建议**：在 P1 阶段（试点后）向 hr_director 提交 `security_engineer` 入职申请，专项覆盖渗透测试/SAST/DAST能力域。

---

## 二、SKILL.md × agent_card 统一方案

### 2.1 现状对比

| 维度 | gstack SKILL.md | Synapse agent_card_template.yaml |
|------|-----------------|----------------------------------|
| 定义格式 | Markdown 自由文本，强调角色心智模型和方法论 | YAML 结构化，强调能力量化和路由关键词 |
| 能力描述层级 | 无强制分级，描述风格多样 | A/B/C 三级，A级有量化指标要求 |
| 路由机制 | 通过命令名直接调用 `/skill-name` | 通过 `summon_keywords` 关键词路由 |
| HR 审批 | 无 | hr_director 入职审批 + capability_architect 评审 |
| 重叠检测 | 无 | Jaccard 相似度 <30% 约束 |

### 2.2 推荐方案：扩展字段融合（不创建独立格式）

**决策**：在现有 `agent_card_template.yaml` 中增加可选的 `gstack_skills` 扩展字段，而非创建独立 skill card 格式。

**理由**：
- 保持单一数据源原则，避免维护两套 Agent 定义
- YAML 结构化格式天然兼容 SKILL.md 的内容要素
- 不破坏现有 HR 审批流程和 capability_architect 评审机制

**扩展字段规范**（在 agent_card_template.yaml 末尾追加）：

```yaml
# GSTACK SKILLS EXTENSION (可选，仅当 Agent 承接 gstack 命令时填写)
gstack_skills:
  commands:                    # 此 Agent 主责的 gstack 命令列表
    - command: "/plan-eng-review"
      trigger: "M级及以上研发任务启动"
      deliverables:
        - "技术规划文档"
        - "工程评审会议纪要"
        - "风险清单"
      methodology: "SQALE 技术债评估 + ADR 文档化 + 架构风险矩阵"
  skill_philosophy: |          # 角色心智模型（对应 SKILL.md 的自由文本部分，≤200字）
    [角色定位描述]
  collaboration_triggers:      # 触发协同的条件
    - when: "[条件]"
      summon: "[协同专员 specialist_id]"
```

### 2.3 迁移路径

```
现有 Agent Card         +    gstack SKILL.md 内容
(rd_tech_lead.yaml)          (/plan-eng-review, /cto, /review)
        ↓                              ↓
        └─────────── 合并 ──────────→ 扩展后的 rd_tech_lead.yaml
                                      (增加 gstack_skills 字段)
```

**执行顺序**：
1. harness_engineer 起草字段规范（本文档）
2. capability_architect 验证字段与现有 HR Schema 的兼容性
3. obs_knowledge_engineer 更新 agent_card_template.yaml
4. rd 团队5名专员逐一补充 gstack_skills 字段
5. integration_qa 验证路由一致性（gstack 命令 → agent_card 专员 → 无歧义）

---

## 三、执行链整合方案

### 3.1 整合原则

gstack 命令作为 Synapse 标准执行链的**内嵌子流程**，而非独立并行流程。
- gstack 命令不替代 Synapse 任务分级和派单机制
- gstack 命令在"执行"环节内部作为标准化操作步骤触发
- 所有触发记录必须写入派单表，不得隐式执行

### 3.2 M级研发任务整合链

```
[Synapse 标准链]                    [gstack 内嵌点]

目标接收
    ↓
任务分级（M级判定）
    ↓
团队派单（rd 团队）
    ↓
执行环节
    ├─ Step 1: rd_tech_lead 执行 /plan-eng-review
    │          ↳ 输出：技术规划文档 + 工程评审确认
    │          ↳ 门禁：规划文档通过后才能进入 build
    ├─ Step 2: rd_backend / rd_frontend 执行 /build
    │          ↳ 输出：代码实现 + 单元测试
    ├─ Step 3: rd_tech_lead 执行 /review（代码审查）
    │          ↳ 门禁：至少1名 Lead 审批 + CI 全绿
    └─ Step 4: rd_qa 执行 /qa
               ↳ 门禁：测试覆盖率 ≥80% + 零STRIDE高危
    ↓
QA审查（Synapse integration_qa，>=85分）
    ↓
rd_devops 执行 /ship
    ↓
结果交付
    ↓
butler_pmo 执行 /retro（必须，不可跳过）
    ↓
obs_knowledge_engineer 执行 /docs（知识沉淀）
```

### 3.3 L级研发任务额外步骤

在 M级链基础上，L级任务强制增加：

```
任务分级（L级判定）
    ↓
智囊团深度分析（graphify_strategist + rd_tech_lead 执行 /cto）
    ↓
安全评审（rd_qa + legal_counsel 执行 /cso + /security）
    ↓
[继续 M级执行链...]
    ↓
发布前：rd_devops 执行 /ship（需 Lysander 审批确认）
    ↓
growth_gtm_strategist 执行 /gtm（如涉及外部发布）
```

### 3.4 强制门禁规则

| 门禁点 | 触发命令 | 通过条件 | 不通过处理 |
|--------|----------|----------|------------|
| build 前 | `/plan-eng-review` | 技术规划文档已输出 | 退回规划，不得进入 build |
| QA前 | `/review` | Lead 审批 + CI 全绿 | PR 退回修改 |
| Synapse QA前 | `/qa` | 覆盖率 ≥80% + 零高危漏洞 | 退回 rd_qa 修复 |
| ship 前 | Synapse QA | ≥85分 | 退回修订 |
| 交付前 | `/retro` | 复盘文档已产出 | 阻止关闭任务 |

---

## 四、CLAUDE.md 路由表建议更新

### 4.1 新增路由条目

在现有路由表末尾追加以下行（不修改现有条目）：

```markdown
| /plan-eng-review/工程评审/技术规划评审 | rd | rd_tech_lead |
| /build/功能构建/代码实现 | rd | rd_backend / rd_frontend |
| /review/代码审查/PR审查 | rd | rd_tech_lead |
| /qa/质量验证/测试验收 | rd | rd_qa |
| /ship/发布/上线/部署发布 | rd | rd_devops |
| /retro/迭代复盘/sprint复盘 | butler | butler_pmo |
| /cso/安全评审/CSO | specialist + rd | legal_counsel + rd_qa |
| /office-hours/答疑/总裁答疑 | pdg | executive_briefer |
| /standup/站会/日同步 | butler | butler_pmo |
| /gtm/Go-to-Market/发布推广 | growth | gtm_strategist |
| /docs/文档沉淀/技术文档 | obs | obs_knowledge_engineer |
| /design-review/设计评审/UI评审 | rd | rd_frontend |
| gstack/命令/slash命令 | harness_ops | harness_engineer |
```

### 4.2 熵值影响评估

| 项目 | 当前值 | 增加后 |
|------|--------|--------|
| CLAUDE.md 行数（估算） | ~285行 | +13行 ≈ 298行 |
| 熵值状态 | 接近警告线 | **触及警告线（>285），未超硬性上限300** |

> **重要提示**：路由表更新须配合 CLAUDE.md 其他内容压缩，确保总行数不超过300行硬性上限。建议 harness_entropy_auditor 在实施前执行熵值检查，并由 harness_engineer 执行必要的行数压缩。

---

## 五、试点建议（P0阶段）

### 5.1 试点范围

选择 **1个 M级研发任务** 作为完整融合链试点，建议条件：
- 涉及 rd_backend + rd_frontend 双专员协同
- 有明确的 API 接口交付物（便于 /review 门禁验证）
- 工期适中（不过于简单也不过于复杂）

### 5.2 试点验证清单

```
[ ] gstack 命令触发记录写入派单表（无隐式执行）
[ ] /plan-eng-review 输出技术规划文档（ADR格式）
[ ] /review 由 rd_tech_lead 执行，非 rd_backend 自审
[ ] /qa 覆盖率报告附于交付物
[ ] /ship 前 Synapse QA ≥85分
[ ] /retro 复盘文档在任务关闭前产出
[ ] /docs 知识沉淀写入 obs 知识库
[ ] 全程无 Lysander CEO 直接执行工具行为
```

### 5.3 试点成功标准

- 执行链完整性：execution_auditor 检查无派单记录缺失
- QA 评分：integration_qa ≥85分
- 复盘产出：butler_pmo /retro 文档质量评分 ≥80分
- 总裁验收：刘子杨总裁对交付物无重大意见

---

## 六、待决策事项（需 Lysander/总裁审批）

### 6.1 需 Lysander CEO 决策（L3）

| # | 议题 | 背景 | 建议选项 |
|---|------|------|----------|
| D1 | agent_card_template.yaml 是否增加 gstack_skills 字段 | 本规范第二节方案 | **A：增加扩展字段（推荐）** / B：独立 skill_card 格式 |
| D2 | /cso 安全命令的长期覆盖方案 | 当前无专属 security_engineer | **A：rd_qa + legal_counsel 联合覆盖（短期）** / B：新增 security_engineer（长期） |
| D3 | gstack 命令是否纳入 SPE 个人生产力引擎指令表 | 23条命令与现有 /plan-day 等可能重叠 | A：全部纳入 / **B：仅纳入与总裁直接交互的命令（推荐）** |
| D4 | CLAUDE.md 熵值超限的处理优先级 | 新增路由后接近300行上限 | A：优先压缩现有内容 / **B：路由表外链到独立文件（推荐）** |

### 6.2 需总裁刘子杨决策（L4）

| # | 议题 | 触发原因 |
|---|------|----------|
| P1 | 是否向外部（如 Garry Tan / YC 社区）公开本融合规范 | 涉及 Synapse-PJ 内部系统架构对外披露 |
| P2 | 是否正式采用 gstack 作为 Synapse 研发工作流标准 | 战略级工具链决策，影响团队工作方式 |

---

## 附录：gstack 命令全景（参考）

基于 gstack 框架公开信息整理，共23条命令涵盖以下职能域：

- **决策层**：`/founder` `/ceo` `/office-hours`
- **技术层**：`/cto` `/eng-manager` `/plan-eng-review` `/build` `/review` `/ship`
- **质量层**：`/qa` `/qa-lead` `/security` `/cso` `/design-review`
- **运营层**：`/pm` `/marketing` `/gtm` `/data` `/docs`
- **法务财务**：`/legal` `/finance`
- **团队节奏**：`/standup` `/retro`

---

*本文档为 v0.1 草案，待 Lysander CEO 审核后提交总裁验收。*
*起草依据：rd 团队5名专员 Agent Card + agent_card_template.yaml + CLAUDE.md 路由表*
*下一步：capability_architect 评审字段扩展方案兼容性*
