# Synapse v3.0 体系组织架构

> 更新时间：2026-04-22
> 三阶段进化完成状态：Phase 1 完成 / Phase 2 完成 / Phase 3 进行中
> 核心版本：v3.0.0

---

## 一、决策体系（四级制）

```
L1 自动执行
  决策者：系统自动
  触发条件：task_type in (query, routine, status, check, list)
  适用场景：例行操作、标准流程、信息查询
  执行方式：自动执行，无需人工干预
  典型任务：状态查询、配置读取、文件列表、版本检查

L2 专家评审
  决策者：智囊团 + 领域专家
  触发条件：complexity in (M, L) and not routine
  适用场景：专业问题需要专家分析、新领域探索
  执行流程：
    1. execution_auditor 识别所需专家领域
    2. Lysander 召集相关专家（可跨团队）
    3. 专家们各自从专业角度分析
    4. decision_advisor 综合各方意见形成建议
    5. Lysander 审核建议，做出最终决策
  上报条件：scope=cross_team OR priority in (P0,P1) OR risk_level in (high, critical) → 升级 L3

L3 Lysander 决策
  决策者：Lysander CEO（AI管理者，总裁刘子杨的AI分身）
  触发条件：跨团队 / P0-P1优先级 / 高风险战略级任务
  决策范围：
    - 基于专家建议做管理决策
    - 跨团队协调和资源分配
    - 方案取舍和多方案比选
  约束：不上报总裁，Lysander 有充分专家支撑
  上报条件：legal=True OR financial=True OR company_critical=True → 升级 L4

L4 总裁决策
  决策者：总裁 刘子杨（最高决策者，公司实际拥有者）
  触发条件（仅以下4种情况打扰总裁）：
    1. 法律约束：涉及外部合同签署、法律协议
    2. 重大财务：预算投入 > 100万
    3. 公司存续：不可逆且直接影响公司生死存亡的决策
    4. 总裁明确要求汇报的特定事项
  其他所有决策，无论多复杂，均由 Lysander + 智囊团 + 专家评审解决
```

**决策引擎模块**：`agent-butler/decision_engine.py`（DecisionEngine 类，T6-4）

---

## 二、执行团队架构

### 统计总览

| 维度 | 数值 |
|------|------|
| 总团队数 | 13 个（含 2 个可选模块） |
| 活跃 Agent 总数 | **48 个** |
| 可选模块 Agent | 10 个（Janus + Stock） |
| OPC 核心 Agent | 4 个 |

---

### 2.1 Graphify 智囊团（Intelligence）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| graphify_strategist | 战略规划师 | 市场/竞品/OKR分析，战略方案制定 | 战略分析 |
| relation_discovery | 关联发现师 | 知识图谱构建，实体关系挖掘 | 知识图谱 |
| trend_watcher | 趋势观察员 | AI前沿动态监测，信号捕捉 | 趋势情报 |
| decision_advisor | 决策顾问 | 风险评估，决策建议，多方案评审 | 决策支持 |
| execution_auditor | 执行审计师 | 任务分级（S/M/L），执行链合规检查 | 执行链审计 |
| ai_tech_researcher | AI技术研究员 | 前沿技术评估，情报日报生成 | AI研究 |
| evolution_engine | 进化引擎 | 版本升级，Gap分析，体系进化 | 版本管理 |

**团队规模**：7 人 | **Lead**：graphify_strategist
**路由关键词**：战略、分析、OKR、竞争、市场、决策、风险、AI研究、前沿、技术评估、趋势、情报、关联、知识图谱、升级、进化

---

### 2.2 Harness Ops 驾驭运维部（Infrastructure）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| harness_engineer | 驾驭工程师 | CLAUDE.md/Harness配置变更，执行链维护 | 配置管理 |
| ai_systems_dev | AI系统开发 | hr_base.py/脚本/自动化/CEO Guard实现 | 代码开发 |
| knowledge_engineer | 知识工程师 | 方法论文档创建，知识沉淀，流程编写 | 知识萃取 |
| integration_qa | 集成质量师 | QA自动评分（>=85分通过），语法检查 | 质量门禁 |
| harness_entropy_auditor | 熵值审计师 | CLAUDE.md行数监控（上限350行），熵增控制 | 熵值管理 |

**团队规模**：5 人 | **Lead**：harness_engineer
**路由关键词**：Harness、配置、执行链、约束、代码、脚本、自动化、QA、质量、验证、熵值、行数、知识、文档、方法论

---

### 2.3 HR 管理团队（Governance）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| hr_director | HR总监 | 入职审批、人员管理、试用期跟踪 | 人事管理 |
| capability_architect | 能力架构师 | Agent能力审计、A/B/C级质量标准、成长曲线 | 能力评估 |

**团队规模**：2 人 | **Lead**：hr_director
**路由关键词**：HR、入职、审批、人员、试用期、能力审计、A级、能力描述

---

### 2.4 Butler 交付运营团队（Operations）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| butler_delivery | 交付管家 | 里程碑管理，项目交付协调 | 交付管理 |
| butler_training | 培训管家 | 入职培训，课程设计，ADDIE模型 | 培训设计 |
| butler_pmo | PMO管家 | WBS分解，Asana任务管理，active_tasks维护 | 项目管理 |
| butler_iot | IoT管家 | 传感器/MQTT/设备管理 | IoT系统 |
| butler_iot_data | IoT数据分析师 | 时序数据，异常检测 | 数据分析 |
| butler_uat | UAT管家 | 用户验收测试，缺陷管理 | 测试验收 |

**团队规模**：6 人 | **Lead**：butler_pmo
**路由关键词**：交付、里程碑、项目、协调、培训、PMO、WBS、IoT、传感器、UAT、验收

---

### 2.5 RD 研发团队（Engineering）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| rd_tech_lead | 技术负责人 | 架构设计，技术方案选型，ADR | 架构决策 |
| rd_backend | 后端工程师 | Python/FastAPI/API/SQL开发 | 后端开发 |
| rd_frontend | 前端工程师 | React/Vue/UI组件开发 | 前端开发 |
| rd_devops | DevOps工程师 | CI/CD/Docker/部署自动化 | 运维开发 |
| rd_qa | 测试工程师 | pytest/Playwright/STRIDE/覆盖率 | 测试工程 |

**团队规模**：5 人 | **Lead**：rd_tech_lead
**路由关键词**：架构、技术方案、后端、API、SQL、前端、React、Vue、DevOps、CI/CD、Docker、测试

---

### 2.6 OBS 知识管理团队（Knowledge）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| obs_architect | 知识架构师 | OBS知识库架构设计，标签体系，Vault管理 | 知识架构 |
| obs_knowledge_engineer | 知识工程师 | MOC编写，知识萃取，链接维护 | 知识沉淀 |
| obs_search | 知识检索师 | Dataview查询，搜索优化 | 信息检索 |
| obs_quality | 质量审计师 | 准确性审核，去重，健康度检查 | 质量把控 |

**团队规模**：4 人 | **Lead**：obs_architect
**路由关键词**：OBS、知识库、架构、Vault、标签体系、知识沉淀、MOC、检索、搜索、质量、审核

---

### 2.7 Content Ops 内容运营团队（Content）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| content_strategist | 内容策略师 | 内容日历，选题策划，SEO优化 | 内容策略 |
| content_creator | 内容创作者 | 文章撰写，博客创作，长文输出 | 文字创作 |
| content_visual | 视觉设计师 | Figma设计，品牌视觉，图形输出 | 视觉设计 |
| content_publishing | 发布工程师 | CMS/Vercel自动化发布，发布流程 | 发布运维 |
| content_training | 培训设计师 | ADDIE课程设计，Kirkpatrick评估 | 培训设计 |
| content_ai_visual | AI视觉师 | Midjourney绘图，Prompt工程，插画 | AI绘图 |
| content_video_script | 视频编剧 | YouTube剧本，故事板创作 | 内容编剧 |
| content_video_prod | 视频制作 | CapCut剪辑，配音，OBS录制 | 视频制作 |

**团队规模**：8 人 | **Lead**：content_strategist
**路由关键词**：内容策略、内容日历、SEO、写作、文章、博客、视觉、设计、Figma、品牌、发布、CMS、视频脚本、故事板、AI绘图、Midjourney、视频制作

---

### 2.8 PDG 总裁直属小组（Executive）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| executive_briefer | 总裁简报师 | BLUF格式汇报，总裁决策材料准备 | Executive briefing |
| style_calibrator | 风格校准师 | 语气/风格/Style Guide校准 | 风格管理 |

**团队规模**：2 人 | **Lead**：executive_briefer
**路由关键词**：简报、汇报、BLUF、风格、语气、校准、Style Guide

---

### 2.9 Growth 增长团队（Growth）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| growth_insights | 增长洞察师 | 用户研究、PMF/NPS/JTBD洞察 | 增长分析 |
| gtm_strategist | GTM策略师 | 市场策略、竞品分析、发布策略 | 市场GTM |
| sales_enablement | 销售赋能师 | MEDDIC方法论，Battle Card制作 | 销售赋能 |
| community_manager | 社区运营 | GitHub/DevRel/开源社区运营 | 社区运营 |

**团队规模**：4 人 | **Lead**：gtm_strategist
**路由关键词**：用户研究、PMF、NPS、洞察、JTBD、GTM、市场、竞品、销售、赋能、MEDDIC、Battle Card、社区、GitHub、DevRel、开源

---

### 2.10 AI/ML 工程团队（Engineering）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| ai_ml_engineer | AI/ML工程师 | Claude API/RAG/Prompt Caching/LLM优化 | AI工程 |

**团队规模**：1 人 | **Lead**：ai_ml_engineer
**路由关键词**：AI、ML、Claude API、RAG、Prompt Caching、LLM

---

### 2.11 Specialist 领域专家组（Specialist）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| legal_counsel | 法律顾问 | 合同审查、知识产权、合规审查 | 法律咨询 |
| financial_analyst | 财务分析师 | P&L分析、DCF建模、预算评估 | 财务分析 |

**团队规模**：2 人 | **Lead**：legal_counsel
**路由关键词**：法律、合同、合规、IP、知识产权、财务、预算、P&L、DCF、建模

---

### 2.12 OPC Core 核心团队（Executive）

| Agent | 角色 | 核心职责 | 技能维度 |
|-------|------|----------|----------|
| opc_ceo_agent | OPC CEO | 战略决策，体系进化，外部协调 | CEO管理 |
| opc_coo_agent | COO运营官 | 任务调度、资源协调、跨团队沟通、运营仪表盘 | 运营调度 |
| opc_cfo_agent | CFO财务官 | 成本监控、预算控制、ROI分析、财务预警 | 财务管控 |
| opc_cto_agent | CTO技术官 | 技术架构、技术决策、工程标准 | 技术治理 |

**团队规模**：4 人 | **Lead**：opc_ceo_agent
**路由关键词**：OPC、调度、协调、跨团队、CFO、成本、预算、ROI、财务预警

---

### 2.13 可选模块（Optional）

#### Janus 项目交付团队（未启用）

| Agent | 角色 | 职责 |
|-------|------|------|
| janus_pm | 项目经理 | 项目整体管理 |
| janus_de | 开发工程师 | 交付开发 |
| janus_sa | 方案架构师 | 技术方案设计 |
| janus_cde | 云开发工程师 | 云端开发 |
| janus_qa | 测试工程师 | 质量验证 |
| janus_pmo_auto | 自动PMO | 任务自动追踪 |

**启用方式**：在 `synapse.yaml` 的 optional_modules 中取消注释 opt_janus

#### Stock 股票交易系统团队（未启用）

| Agent | 角色 | 职责 |
|-------|------|------|
| stock_analyst | 股票分析师 | 市场分析 |
| stock_quant | 量化工程师 | 量化策略 |
| stock_risk | 风险管理员 | 风险管理 |
| stock_news | 新闻分析师 | 新闻事件 |
| stock_portfolio | 组合管理员 | 组合管理 |

**启用方式**：在 `synapse.yaml` 的 optional_modules 中取消注释 opt_stock

---

## 三、技术组件矩阵

按层级排列，涵盖三阶段产出所有核心模块：

### Meta-Cognition 层（元认知）

| 模块 | 文件 | 类 | 状态 | 说明 |
|------|------|-----|------|------|
| Decision Engine | `agent-butler/decision_engine.py` | DecisionEngine | 活跃 | L1-L4四级决策引擎（Phase 3 T6-4） |
| FSM Engine | `agent-butler/harness_fsm.py` | SynapseFSM | 活跃 | 11状态/19转换规则，状态机驱动（Phase 2 T6-3） |
| Self-Improvement Loop | `agent-butler/self_improvement.py` | SelfImprovementLoop | 活跃 | 执行结果→数据采集→模式识别→改进建议→审批→验证（Phase 3） |

### Decision Core 层（决策核心）

| 模块 | 文件 | 类 | 状态 | 说明 |
|------|------|-----|------|------|
| Capability Tracker | `agent-butler/capability_tracker.py` | CapabilityTracker | 活跃 | Agent能力持续评估，成长曲线（Phase 3 T2-3） |
| Evolution Dashboard | `agent-butler/evolution_dashboard.py` | EvolutionDashboard | 活跃 | 效率/质量/成长三大维度仪表盘（Phase 3 T5-2） |

### Knowledge Graph 层（知识图谱）

| 模块 | 文件 | 类 | 状态 | 说明 |
|------|------|-----|------|------|
| Intelligence Forecaster | `agent-butler/intelligence_forecaster.py` | IntelligenceForecaster | 活跃 | 周期性热点检测，7天关键词外推（Phase 3 T1-4） |
| OPC COO Agent | `agent-butler/opc_coo.py` | COOAgent | 活跃 | 任务调度/资源协调/冲突解决（Phase 3 T3-2） |

### 情报管线（Intelligence Pipeline）

| 模块 | 文件 | 触发时间 | 说明 |
|------|------|----------|------|
| 情报日报Agent | `agent-butler/intelligence_daily.py` | 8:00am Dubai | AI前沿动态搜索→情报日报HTML→git push |
| 情报行动Agent | `agent-butler/intelligence_action.py` | 10:00am Dubai | 日报建议→4专家评估→评审决策→执行→行动报告 |

### 执行网络（Execution Network）

| 模块 | 文件 | 说明 |
|------|------|------|
| HR Base | `agent-butler/hr_base.py` | HR知识库核心，审计评分，决策逻辑 |
| HR Watcher | `agent-butler/hr_watcher.py` | 文件监控，自动触发审计 |
| OPC CFO Agent | `agent-butler/opc_cfo.py` | 财务监控，预算控制，ROI分析 |

### 配置文件体系

| 文件 | 用途 |
|------|------|
| `agent-butler/config/organization.yaml` | 团队角色配置，13团队48 Agent |
| `agent-butler/config/harness_registry.yaml` | 规则注册表，32条约束规则 |
| `agent-butler/config/fsm_states.yaml` | FSM状态配置，11状态定义 |
| `agent-butler/config/active_tasks.yaml` | 跨会话任务状态 |
| `agent-butler/config/active_tasks_fsm.yaml` | FSM任务追踪 |
| `agent-butler/config/evolution_metrics.yaml` | 进化指标配置 |
| `obs/credentials.md` | 凭证管理（加密存储） |

### Self-Improvement 闭环

```
执行结果记录（ExecutionRecord）
    ↓
数据采集（每次任务完成）
    ↓
模式识别（min 5条记录触发分析）
    ├─ Agent 阻塞率排名
    ├─ 任务类型平均质量
    ├─ 7天窗口阻塞率
    └─ Agent 均分质量
    ↓
改进建议生成
    ├─ P0：任务均分<3.5/5 或 7天阻塞>=3
    ├─ P1：Agent阻塞率>=20% 或 均分<3.5/5
    └─ 30天去重窗口
    ↓
审批流程
    ├─ P0 → Lysander CEO
    ├─ P1 → harness_engineer
    └─ P2 → execution_auditor
    ↓
执行落地（4类）
    ├─ Process类 → 更新harness_registry.yaml/CLAUDE.md
    ├─ Team类 → 更新organization.yaml
    ├─ Knowledge类 → 生成新文档
    └─ Tool类 → 更新工具层配置
    ↓
验证 → 融入Harness
```

---

## 四、OPC 核心架构（CFO/COO）

### 4.1 OPC 架构定位

OPC（Operations Center）核心团队是 Synapse v3.0 Phase 3 新增的执行管理层，
为 Lysander CEO 提供专业化的运营和财务支撑。

```
Lysander CEO（最高管理决策层）
    ├── OPC CEO Agent — 战略决策，体系进化
    ├── OPC COO Agent — 运营调度，资源协调（已激活）
    ├── OPC CFO Agent — 财务监控，成本控制（已激活）
    └── OPC CTO Agent — 技术架构，工程标准
```

### 4.2 CFO Agent（首席财务官 Agent）

| 维度 | 内容 |
|------|------|
| **Agent ID** | opc_cfo_agent |
| **文件** | `agent-butler/opc_cfo.py` |
| **人员卡片** | `obs/01-team-knowledge/HR/personnel/opc/cfo_agent.yaml` |
| **汇报线** | 汇报给 Lysander CEO |
| **协作对象** | COO Agent、CTO Agent、Lysander CEO |

**核心能力**：

| 能力 | 描述 | 输出指标 |
|------|------|----------|
| financial_monitoring | 实时监控API消耗和执行成本 | daily_cost/token_usage/api_calls/cost_per_task |
| budget_control | 执行任务预算控制 | max_cost_per_task/daily_budget_limit/alert_threshold |
| roi_analysis | 任务价值 vs 成本投资回报分析 | roi_score/cost_efficiency/value_assessment |
| risk_alerting | 财务风险识别和预警 | over_budget/anomalous_spend/cost_trend_up |

**技能水平**：
- financial_analysis: 5/5
- cost_optimization: 4/5
- data_modeling: 4/5
- risk_management: 4/5

**决策权限**：
- 决策级别：L2（专家评审级，重大决策上报 Lysander）
- 预算自动批准上限：100 美元
- 预警阈值：预算消耗 80% 时触发预警

**财务集成**：
- 成本追踪：Claude API / n8n / GitHub Actions
- 报告输出：日燃烧率 / 周报 / 月报

### 4.3 COO Agent（首席运营官 Agent）

| 维度 | 内容 |
|------|------|
| **Agent ID** | opc_coo_agent |
| **文件** | `agent-butler/opc_coo.py` |
| **人员卡片** | `obs/01-team-knowledge/HR/personnel/opc/coo_agent.yaml` |
| **汇报线** | 汇报给 Lysander CEO |
| **协作对象** | CFO Agent、CTO Agent、Lysander CEO |

**核心能力**：

| 能力 | 描述 | 输出 |
|------|------|------|
| 任务调度 | 基于团队负载（max_capacity = member_count × 3）分配最优执行团队 | 调度分配表（含负载率/冲突警告） |
| 跨团队Handoff | 协调多团队顺序执行，监控交接节点 | Handoff时序图 |
| 资源冲突解决 | team_overload/dependency_cycle按优先级排序 | 冲突解决报告 |
| 运营仪表盘 | 汇总active_tasks/blocked_queue/team_loads | Markdown格式COO Dashboard |

**技能水平**：
- task_scheduling: 5/5
- resource_coordination: 5/5
- cross_team_communication: 5/5
- priority_management: 5/5
- conflict_resolution: 4/5
- operational_reporting: 4/5

**负载管理阈值**：
- healthy: <= 70% capacity
- busy: 70%-100% capacity
- overloaded: > 100% capacity
- 每成员最大并发任务数：3

### 4.4 与现有体系的集成点

```
Lysander CEO（主对话）
    │
    ├── OPC COO Agent
    │   ├── 接收任务 → 检查团队负载 → 分配执行团队
    │   ├── 监控 blocked_queue → 冲突解决 → 上报 Lysander
    │   └── 生成 COO Dashboard → 10:30am Dubai 每日报告
    │       │
    │       └── 输入：active_tasks.yaml / team_loads
    │
    └── OPC CFO Agent
        ├── 监控执行成本 → 超出阈值预警
        ├── ROI分析 → 任务价值评估
        └── 生成财务报告 → 每日/每周/每月
            │
            └── 输入：execution_records.json / task_outcomes.json

Harness Registry（规则注册表）
    └── 48个Agent能力描述 + 路由关键词
        │
        └── OPC体系共享同一 routing_keywords 表

Decision Engine（决策引擎）
    └── L1-L4 四级决策
        ├── L1: OPC内部自动执行（例行监控/报告）
        ├── L2: 专家评审（CFO成本评估/COO运营建议）
        ├── L3: Lysander综合意见决策
        └── L4: 总裁决策（>100万财务/法律约束）

Evolution Dashboard（进化仪表盘）
    └── 效率/质量/成长三大维度
        │
        └── OPC COO Dashboard 提供运营数据
        └── OPC CFO Dashboard 提供财务数据
```

---

## 五、能力路由网络

基于 `harness_registry.yaml` 中 routing_keywords 构建的能力网络：

### 5.1 路由机制

```
用户输入关键词
    ↓
matching routing_keywords
    ↓
选择最优 Agent
    ↓
执行任务 → 记录到 task_outcomes.json
    ↓
Capability Tracker 更新 Agent 评分
```

### 5.2 能力路由示例

**场景1：Harness 配置变更**
```
输入："更新 CLAUDE.md 的执行链规则"
关键词匹配："Harness" + "执行链" + "规则"
路由至：harness_engineer
执行：配置变更 → integration_qa 验证 → QA评分 >=85 → 交付
```

**场景2：财务成本分析**
```
输入："分析本月API消耗和ROI"
关键词匹配："API" + "成本" → opc_cfo_agent
路由至：opc_cfo_agent
执行：financial_monitoring + roi_analysis → 财务报告 → 上报 Lysander
```

**场景3：跨团队任务调度**
```
输入："协调RD和Butler团队完成IoT项目交付"
关键词匹配："协调" + "跨团队" → opc_coo_agent
路由至：opc_coo_agent
执行：检查团队负载 → 分配任务 → handoff时序监控 → 冲突解决 → COO Dashboard
```

**场景4：趋势情报分析**
```
输入："搜索AI前沿动态并生成情报日报"
关键词匹配："AI研究" + "前沿" → ai_tech_researcher
        "趋势" + "情报" → trend_watcher
路由至：ai_tech_researcher + trend_watcher 协作
执行：情报收集 → relation_discovery 关联分析 → graphify_strategist 战略评估 → 日报输出
```

**场景5：内容SEO策略**
```
输入："制定下季度内容日历和SEO策略"
关键词匹配："内容策略" + "SEO" → content_strategist
路由至：content_strategist
执行：市场分析（growth_insights）→ 内容日历制定 → content_creator 创作 → content_publishing 发布
```

### 5.3 团队间能力协同网络

```
Graphify（智囊团）
    graphify_strategist → 提供战略方向
    execution_auditor → 分级任务，触发路由
    trend_watcher → 情报输入
    decision_advisor → 决策建议

Harness Ops
    harness_engineer → 配置管理，规则维护
    integration_qa → 质量门禁
    harness_entropy_auditor → 熵增控制

OPC Core
    opc_coo_agent → 跨团队调度中心（Hub）
    opc_cfo_agent → 财务成本中枢（Hub）
    opc_ceo_agent → 战略整合

执行团队（Butler/RD/OBS/Content/Growth）
    各团队 Lead → 向 OPC COO 汇报负载状态
    各团队 Agent → 按 routing_keywords 被精准调度
```

---

## 六、统计摘要

| 维度 | 数值 |
|------|------|
| **总 Agent 数量**（活跃） | **48 个** |
| **总团队数量**（活跃） | **12 个** |
| **核心模块数量**（含Phase 1/2/3） | **16 个** |
| **OPC Agent 数量** | **4 个**（全员在OPC Core） |
| **可选模块 Agent** | 10 个（Janus 6 + Stock 5，未启用） |
| **P0 约束规则** | 9 条 |
| **P1 约束规则** | 18 条 |
| **P2 约束规则** | 5 条 |
| **FSM 状态数** | 11 个 |
| **FSM 转换规则** | 19 条 |
| **Harness 版本** | v3.0.0 |
| **组织架构版本** | v3.0.0 |

---

## 七、Agent 完整清单

| # | Agent ID | 团队 | 角色 | 状态 |
|---|----------|------|------|------|
| 1 | graphify_strategist | graphify | 战略规划师 | active |
| 2 | relation_discovery | graphify | 关联发现师 | active |
| 3 | trend_watcher | graphify | 趋势观察员 | active |
| 4 | decision_advisor | graphify | 决策顾问 | active |
| 5 | execution_auditor | graphify | 执行审计师 | active |
| 6 | ai_tech_researcher | graphify | AI技术研究员 | active |
| 7 | evolution_engine | graphify | 进化引擎 | active |
| 8 | hr_director | hr | HR总监 | active |
| 9 | capability_architect | hr | 能力架构师 | active |
| 10 | harness_engineer | harness_ops | 驾驭工程师 | active |
| 11 | ai_systems_dev | harness_ops | AI系统开发 | active |
| 12 | knowledge_engineer | harness_ops | 知识工程师 | active |
| 13 | integration_qa | harness_ops | 集成质量师 | active |
| 14 | harness_entropy_auditor | harness_ops | 熵值审计师 | active |
| 15 | butler_delivery | butler | 交付管家 | active |
| 16 | butler_training | butler | 培训管家 | active |
| 17 | butler_pmo | butler | PMO管家 | active |
| 18 | butler_iot | butler | IoT管家 | active |
| 19 | butler_iot_data | butler | IoT数据分析师 | active |
| 20 | butler_uat | butler | UAT管家 | active |
| 21 | rd_tech_lead | rd | 技术负责人 | active |
| 22 | rd_backend | rd | 后端工程师 | active |
| 23 | rd_frontend | rd | 前端工程师 | active |
| 24 | rd_devops | rd | DevOps工程师 | active |
| 25 | rd_qa | rd | 测试工程师 | active |
| 26 | obs_architect | obs | 知识架构师 | active |
| 27 | obs_knowledge_engineer | obs | 知识工程师 | active |
| 28 | obs_search | obs | 知识检索师 | active |
| 29 | obs_quality | obs | 质量审计师 | active |
| 30 | content_strategist | content_ops | 内容策略师 | active |
| 31 | content_creator | content_ops | 内容创作者 | active |
| 32 | content_visual | content_ops | 视觉设计师 | active |
| 33 | content_publishing | content_ops | 发布工程师 | active |
| 34 | content_training | content_ops | 培训设计师 | active |
| 35 | content_ai_visual | content_ops | AI视觉师 | active |
| 36 | content_video_script | content_ops | 视频编剧 | active |
| 37 | content_video_prod | content_ops | 视频制作 | active |
| 38 | executive_briefer | pdg | 总裁简报师 | active |
| 39 | style_calibrator | pdg | 风格校准师 | active |
| 40 | growth_insights | growth | 增长洞察师 | active |
| 41 | gtm_strategist | growth | GTM策略师 | active |
| 42 | sales_enablement | growth | 销售赋能师 | active |
| 43 | community_manager | growth | 社区运营 | active |
| 44 | ai_ml_engineer | ai_ml | AI/ML工程师 | active |
| 45 | legal_counsel | specialist | 法律顾问 | active |
| 46 | financial_analyst | specialist | 财务分析师 | active |
| 47 | opc_ceo_agent | opc_core | OPC CEO | active |
| 48 | opc_coo_agent | opc_core | COO运营官 | active |
| 49 | opc_cfo_agent | opc_core | CFO财务官 | active |
| 50 | opc_cto_agent | opc_core | CTO技术官 | active |

---

> 文档生成：knowledge_engineer
> 数据来源：`agent-butler/config/organization.yaml`、`agent-butler/config/harness_registry.yaml`、
> `obs/01-team-knowledge/HR/personnel/`（所有 Agent 卡片）
> 下次更新：建议每周一结合 Agent 审计自动更新本文件