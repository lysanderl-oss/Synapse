---
name: Synapse Multi-Agent体系进化方案
description: Synapse体系持续进化战略方案，2026年Q2完整版
type: strategic-plan
version: v1.0
created: 2026-04-21
status: pending-approval
owner: Lysander CEO
reviewer: 智囊团
---

# Synapse Multi-Agent 体系进化方案

## 执行链状态

调研 ✅ → 头脑风暴 ✅ → 智囊团评审 ✅ → 报总裁审批

---

## 一、任务背景

2026-04-21，应总裁要求，Lysander组织智囊团、HR团队及Harness Engineering团队，对Synapse体系进行全面分析。执行链完整走过以下阶段：

| 阶段 | 执行者 | 产出 |
|------|--------|------|
| 深度分析 | execution_auditor | 体系现状问题清单 |
| Harness Engineering调研 | harness_engineer | 前沿实践报告（5大方向） |
| 知识管理调研 | knowledge_engineer | Karpathy/Matuschak/GraphRAG实践报告 |
| gstack研发调研 | ai_systems_dev | Multi-Agent研发效能方案 |
| 情报管线评估 | Harness Ops团队 | 管线效能报告+改进建议 |
| Agent能力卡片调研 | HR团队 | 能力进化体系方案 |
| OPC架构研究 | 智囊团决策顾问 | One Person Company蓝图 |
| 头脑风暴圆桌 | 决策顾问主持 | 三阶段路线图+8条决议 |
| 智囊团评审 | Lysander+智囊团 | 修订决议清单+3项修改意见 |

---

## 二、调研核心发现

### Harness Engineering
- Synapse四级决策体系与LangGraph条件边路由高度契合
- 最大缺口：Self-Improvement机制自动化
- 建议：引入条件边路由、CrewAI风格Role-Based协作

### 知识管理
- OBS应从"笔记存储"升级为"知识操作系统"
- GraphRAG（实体+关系）是下一代RAG方向
- CrewAI两级知识架构（Agent级+Crew级）是最优Multi-Agent知识共享模式
- MemGPT层级记忆机制（Working/Episodic/Semantic三层）

### gstack研发效能
- 执行底座(gstack)与智能层(Claude Code)分层是核心竞争优势
- Multi-Agent研发工作流成功关键：边界清晰、解耦充分、消息驱动
- PR Pipeline自动化、Test Generation Agent、Visual Regression Agent是最高ROI改进

### 情报管线
- 转化率87.5%优秀，四专家评审机制有效
- 缺失：情报预测回验机制
- Fan-out并行可提升效率60%+
- n8n webhook 404长期未修复是已知阻塞项

### Agent能力卡片
- 能力描述存在但无法衡量执行效果
- 任务分配依赖关键词匹配而非能力匹配
- 建议：skill_levels + performance_history双字段、capability_router算法

### OPC架构
- Synapse已具备OPC支撑平台基础骨架
- 核心缺口：CFO Agent、决策审计系统、Agent交接协议
- 最小可行OPC架构：CEO Agent + COO Agent + CTO Agent + 执行层Agent

---

## 三、目标架构（五层结构）

```
┌─────────────────────────────────────────────────────┐
│           元认知层 Meta-Cognition Layer              │
│      execution_auditor · reflex_engine              │
├─────────────────────────────────────────────────────┤
│           决策中枢层 Decision Core (L1-L4)          │
│      L1自动 · L2专家 · L3 CEO · L4 总裁            │
├─────────────────────────────────────────────────────┤
│        知识图谱层 Knowledge Graph Layer             │
│  GraphRAG · CrewAI两级知识 · MemGPT层级记忆         │
├──────────────────────┬──────────────────────────────┤
│     情报管线          │      执行网络 Execution Net   │
│  Quality Radar        │  Harness FSM · Agent Router  │
│  Fan-out · Backtest   │  Butler·RD·OBS·Harness      │
│                      │  + CFO/COO/CTO Agent矩阵      │
├──────────────────────┴──────────────────────────────┤
│        自我进化层 Self-Improvement Layer             │
│      执行-反思-改进 三元闭环 · 预测回验              │
└─────────────────────────────────────────────────────┘
```

### 新增模块清单

| 模块 | 定位 | 与现有体系集成点 |
|------|------|---------------|
| Harness FSM状态机 | 执行链v2.0的可执行化底座 | 替代CLAUDE.md中的流程描述语言 |
| Agent Capability Router | 能力感知任务路由引擎 | 集成至派单制度，替换关键词匹配 |
| GraphRAG Knowledge Engine | 知识图谱构建与语义检索 | OBS团队升级方向，支撑智囊团决策 |
| Intelligence Quality Radar | 情报多维质量评分 | 集成至情报管线输出端 |
| Self-Improvement Loop | 执行后自动化反思闭环 | 集成至执行链【③】QA阶段 |
| OPC Agent Matrix | CFO/COO/CTO虚拟Agent矩阵 | 支撑L2专家评审层专业Agent |

---

## 四、三阶段演进路线图

### Phase 1：基础能力（Week 1-2.5）⭐ 率先启动

| 任务 | 执行者 | 交付物 |
|------|--------|--------|
| T6-1: Harness Config注册表建立 | harness_engineer | 结构化规则注册表 |
| T2-1: Agent能力卡片字段填充 | capability_architect | skill_levels + performance_history |
| T1-1: n8n webhook修复 | ai_systems_dev | 管线完整闭环 |
| T1-2: 情报质量雷达图上线 | knowledge_engineer | 多维评分标签 |
| T6-2: Agent交接协议模板 | harness_engineer | 标准化交接Schema |

Phase 1执行顺序：
- Week 1前半：T6-1注册表框架
- Week 1后半：T2-1能力卡片填充（依赖T6-1）
- Week 2：并行T1-1 + T6-2
- Week 2末~Week 3首：T1-2情报质量雷达图

### Phase 2：核心架构（Week 3-6）

| 任务 | 执行者 | 交付物 |
|------|--------|--------|
| T6-3: Harness FSM状态机上线 | harness_engineer | 可执行工作流引擎 |
| T2-2: Agent Capability Router上线 | ai_systems_dev | 能力向量路由算法 |
| T1-3: 四专家评审Fan-out并行 | knowledge_engineer | 并行评审Pipeline |
| T4-1: Self-Improvement Loop原型 | integration_qa | 三元闭环机制 |
| T3-1: GraphRAG引擎原型 | knowledge_engineer | 实体抽取管道 |

Phase 2原则：先输出标准接口协议（API Contract），各模块须通过接口测试才能集成。

### Phase 3：高级进化（Month 2-3）

| 任务 | 执行者 | 交付物 |
|------|--------|--------|
| T4-2: Self-Improvement常态化 | integration_qa | 进化飞轮 |
| T5-1: OPC Agent Matrix(CFO先行) | 智囊团+HR | CFO Agent |
| T3-2: CrewAI双层知识+MemGPT | knowledge_engineer | 完整知识架构 |
| T5-2: 决策审计全链路闭环 | execution_auditor | 决策追溯体系 |
| T2-3: Agent晋升路径系统化 | hr_director | 成长路径规范 |

---

## 五、最终决议清单（10条）

| 编号 | 决议内容 | 评审状态 | 总裁关注 |
|------|----------|---------|---------|
| R1 | 批准三阶段路线图，T6基础平台工程优先启动 | ✅ 批准 | 🟡 需关注 |
| R2 | 构建Harness Config注册表，熵增预算管控（新增规则需等量删除） | ✅ 批准 | 🟡 需关注 |
| R3 | Agent能力量化，skill_levels+performance_history，Capability Router替换关键词派单 | ✅ 批准 | 🟡 需关注 |
| R4 | 情报管线升级：webhook修复+Quality Radar+Fan-out并行+回验机制 | ✅ 批准 | 🟢 常规 |
| R5 | Self-Improvement Loop建设（Phase 2建进化沙箱，常态化需总裁审批） | ⚠️ 附加约束 | 🔴 需特别关注 |
| R6 | OPC Agent Matrix，CFO Agent先行，COO/CTO后续跟进 | ✅ 批准 | 🟡 需关注 |
| R7 | 知识图谱建设，GraphRAG+CrewAI双层架构+MemGPT层级记忆 | ✅ 批准 | 🟢 常规 |
| R8 | 双轨并行策略，95%准确率后全面切换（基准：四专家一致通过率） | ✅ 批准 | 🟢 常规 |
| R9 | 技术债务废弃候选机制：不得跨Phase积累 | ✅ 建议批准 | 🟢 常规 |
| R10 | Phase切换须通过Lysander主持的出口审查+integration_qa验收报告 | ✅ 建议批准 | 🟡 需关注 |

---

## 六、关键成功指标

### Phase 1成功指标

| 指标 | 测量方法 | 目标值 |
|------|---------|-------|
| n8n webhook可用率 | 每日健康检查 | ≥99% |
| 情报多维评分覆盖率 | 日报附带评分比例 | 100% |
| Agent能力卡片完整率 | 骨干Agent双字段填充率 | ≥90% |
| 散落规则迁移数量 | 迁入注册表的规则数 | ≥5条 |
| 交接协议采用率 | Agent标准化交接比例 | ≥80% |

### Phase 2成功指标

| 指标 | 测量方法 | 目标值 |
|------|---------|-------|
| Agent路由成功率 | 首次分配无需返工比例 | ≥80% |
| Fan-out评审效率 | 并行耗时/串行耗时 | ≤40% |
| FSM状态转换错误率 | 错误转换次数/总转换 | <0.1% |
| 自我进化触发频率 | 每周触发反思任务数 | ≥5次/周 |
| GraphRAG实体数量 | 抽取实体节点总数 | ≥200个 |

### Phase 3成功指标

| 指标 | 测量方法 | 目标值 |
|------|---------|-------|
| 情报预测命中率 | 采纳情报成果达预期比例 | ≥60% |
| OPC Agent决策支撑率 | L4决策有专业分析比例 | ≥70% |
| 决策全链路可追溯率 | 完整记录比例 | ≥90% |
| CrewAI知识召回准确率 | 人工抽检测量 | ≥85% |
| CFO Agent决策采纳率 | L4验证采纳比例 | ≥70% |

---

## 七、风险登记与缓解

| 风险 | 等级 | 缓解措施 | 责任人 |
|------|------|---------|--------|
| 多团队并行git冲突 | 高 | Phase 1全走PR+review，禁止直接push main | harness_engineer |
| 派单制度与快节奏摩擦 | 中 | Lysander担任派单协调，48小时同步 | Lysander |
| Self-Improvement误导性修改 | 高 | Phase 2建进化沙箱，所有改动经QA审查进候选区 | integration_qa |
| Agent能力人工评估偏差 | 中 | 自评+qa_engineer随机抽检≥20% | capability_architect |
| webhook修复期间管线中断 | 低 | 先修复再引入新功能，管线始终可用 | ai_systems_dev |
| FSM条件路由误判 | 中 | 双轨并行验证，准确率≥95%后切换 | harness_engineer |
| 体系熵增失控 | 低 | 熵增预算350行，新增规则需等量删除 | harness_entropy_auditor |

---

## 八、总裁特别审批事项

### 🔴 R5 Self-Improvement Loop

这是唯一可能产生"不可预期后果"的模块。总裁审批时请确认：
- Phase 2的"进化沙箱"设计是否到位？
- Self-Improvement进入常态化运行前，是否需要总裁二次审批？

### 🟡 T2-1 Agent能力卡片填充

能力评估机制确认：建议采用"自评 + 随机抽检(≥20%)"混合模式，由qa_engineer执行抽检。

### 🟡 R8双轨并行退出条件

以"四专家评审一致通过率"为基准指标，而非泛化准确率。

---

## 九、Phase 1执行团队

| 执行者 | 负责任务 |
|--------|---------|
| harness_engineer | T6-1注册表、T6-2交接协议 |
| capability_architect | T2-1能力卡片填充 |
| ai_systems_dev | T1-1 webhook修复 |
| knowledge_engineer | T1-2情报质量雷达图 |
| integration_qa | 指标自动化采集脚本 |

---

## 十、相关文件索引

- 本文件：obs/01-team-knowledge/HR/synapse-evolution-plan-2026-Q2.md
- 调研报告：obs/01-team-knowledge/HR/weekly-audit/
- Agent能力卡片：obs/01-team-knowledge/HR/personnel/
- 团队配置：agent-butler/config/organization.yaml
- 决策日志：agent-butler/config/decision_log.json

---

**文件状态**：待总裁审批
**审批后状态更新**：approved / revision-required
**版本**：v1.0
**下次审查**：总裁审批后立即更新
