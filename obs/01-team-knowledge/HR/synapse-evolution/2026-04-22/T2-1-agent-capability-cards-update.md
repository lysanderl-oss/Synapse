# T2-1: Agent 能力卡片字段更新报告

**执行者**：capability_architect
**日期**：2026-04-22
**任务**：Phase 1 T2-1 — Agent 能力卡片字段填充
**状态**：已完成

---

## 更新范围

本次更新覆盖以下 5 个关键 Agent（覆盖 Harness 执行链路核心）：

| Agent | 团队 | 选择理由 |
|-------|------|----------|
| harness_engineer | harness_ops | Harness Engineering 核心，CLAUDE.md架构维护 |
| ai_systems_dev | harness_ops | RD 团队核心，hr_base.py/hook开发 |
| knowledge_engineer | harness_ops | 知识管理核心，OBS架构维护 |
| capability_architect | hr | HR 团队核心，能力审计与质量门禁 |
| integration_qa | harness_ops | QA 门禁核心，85分通过线守护 |

---

## 字段规范

### skill_levels（能力等级）

评分标准：1-5 分，3=独立胜任（基准线）

| 分值 | 定义 |
|------|------|
| 1 | 新手，需要详细指导 |
| 2 | 初级，能在指导下完成 |
| 3 | 独立胜任，基准线 |
| 4 | 熟练，高质量完成 |
| 5 | 顶级专家，复杂问题独立解决 |

维度池（按需选取，不强制全部填写）：

- `code_review` — 代码审查能力
- `documentation` — 文档编写能力
- `task_execution` — 任务执行能力（默认维度）
- `communication` — 跨团队沟通协作能力
- `quality_audit` — 质量审计能力
- 及其他角色特定维度

### performance_history（性能历史）

| 字段 | 类型 | 说明 |
|------|------|------|
| `tasks_completed` | int | 累计完成任务数 |
| `avg_quality_score` | float(0-5) | QA平均评分（≥3.5通过） |
| `avg_completion_rate` | float(0-1) | 按时完成率 |
| `last_active` | date | 最后活跃日期 |
| `blocked_tasks` | int | 当前阻塞任务数 |
| `escalation_count` | int | 升级到Lysander的次数 |
| `notes` | string | 估算依据说明（可选） |

> **注意**：当前数值为估算，待 T6-2 自动化采集机制建立后替换为真实数据。

---

## 更新详情

### 1. harness_engineer

**文件**：`obs/01-team-knowledge/HR/personnel/harness_ops/harness_engineer.yaml`

skill_levels：
```yaml
skill_levels:
  config_design: 5      # 配置架构设计能力，5=顶级专家
  code_review: 3         # 代码审查能力
  documentation: 4       # 文档编写与结构化能力
  system_optimization: 4 # 系统优化能力（Harness层/Prompt缓存）
  task_execution: 5     # 任务执行能力，最高
  communication: 4       # 跨团队沟通协作
```

performance_history：
```yaml
performance_history:
  tasks_completed: 18   # 估算：基于CLAUDE.md维护/fragment生成/配置管理
  avg_quality_score: 4.3 # 估算
  avg_completion_rate: 0.98  # 估算：配置工作确定性高
  last_active: "2026-04-22"
  blocked_tasks: 0
  escalation_count: 1   # 曾因P0规则变更上报Lysander一次
  notes: "估算，待T6-2自动化采集更新"
```

---

### 2. ai_systems_dev

**文件**：`obs/01-team-knowledge/HR/personnel/harness_ops/ai_systems_dev.yaml`

skill_levels：
```yaml
skill_levels:
  python_development: 5  # Python开发能力，核心专职
  hook_development: 4    # Hook脚本开发（CEO Guard）
  automation_scripting: 5 # 自动化脚本开发
  code_review: 4          # 代码审查能力
  documentation: 3       # 文档编写能力
  system_integration: 4   # 系统集成（n8n/API）
  task_execution: 5      # 任务执行能力，最高
```

performance_history：
```yaml
performance_history:
  tasks_completed: 15   # 估算：hr_base.py/hook/n8n/自动化脚本
  avg_quality_score: 4.1 # 估算：代码开发质量稳定
  avg_completion_rate: 0.96
  last_active: "2026-04-22"
  blocked_tasks: 1       # n8n集成曾因API配置阻塞
  escalation_count: 0
  notes: "估算，待T6-2自动化采集更新"
```

---

### 3. knowledge_engineer

**文件**：`obs/01-team-knowledge/HR/personnel/harness_ops/knowledge_engineer.yaml`

skill_levels：
```yaml
skill_levels:
  methodology_design: 5  # 方法论设计能力，核心专职
  documentation: 5       # 文档编写能力，核心专职
  knowledge_architecture: 4  # 知识库架构能力
  process_capture: 4      # 流程萃取能力
  template_design: 5     # 模板设计能力
  communication: 4       # 跨团队沟通
  task_execution: 4      # 任务执行能力
```

performance_history：
```yaml
performance_history:
  tasks_completed: 14   # 估算：方法论/OBS/决策日志/模板
  avg_quality_score: 4.2
  avg_completion_rate: 0.97
  last_active: "2026-04-22"
  blocked_tasks: 0
  escalation_count: 0
  notes: "估算，待T6-2自动化采集更新"
```

---

### 4. capability_architect

**文件**：`obs/01-team-knowledge/HR/personnel/hr/capability_architect.yaml`

skill_levels：
```yaml
skill_levels:
  quality_audit: 5      # 质量审计能力，核心专职
  algorithm_design: 4   # 算法设计能力（Jaccard/热力图）
  org_analysis: 4        # 组织架构分析（Conway's Law）
  documentation: 4       # 文档编写能力
  task_execution: 5      # 任务执行能力，最高
  communication: 4       # 跨团队沟通协作
  onboarding_review: 5   # 入职质量门禁评审能力
```

performance_history：
```yaml
performance_history:
  tasks_completed: 11   # 估算：audit/热力图/Jaccard/入职审批
  avg_quality_score: 4.4 # 估算：HR工作质量要求高
  avg_completion_rate: 0.98
  last_active: "2026-04-22"
  blocked_tasks: 0
  escalation_count: 2   # 曾两次因能力重叠上报Lysander
  notes: "估算，待T6-2自动化采集更新"
```

---

### 5. integration_qa

**文件**：`obs/01-team-knowledge/HR/personnel/harness_ops/integration_qa.yaml`

skill_levels：
```yaml
skill_levels:
  quality_audit: 5       # QA审计能力，核心专职
  yaml_validation: 5     # YAML语法验证能力，核心专职
  test_design: 4         # 测试设计能力
  impact_analysis: 4    # 变更影响分析能力
  regression_testing: 4 # 回归测试能力
  documentation: 3       # 文档编写能力
  task_execution: 5     # 任务执行能力，最高
```

performance_history：
```yaml
performance_history:
  tasks_completed: 22   # 估算：QA评分/YAML验证/影响分析/回归
  avg_quality_score: 4.5 # 估算：QA门禁守护者自身要求最高
  avg_completion_rate: 0.99
  last_active: "2026-04-22"
  blocked_tasks: 0
  escalation_count: 1   # 曾因严重不合格项上报Lysander
  notes: "估算，待T6-2自动化采集更新"
```

---

## 下一步

### Phase 1 剩余任务

- **T2-2**：Agent Capability Router — 基于能力向量路由（依赖 T2-1 数据）
- **T6-2**：自动化数据采集机制 — 将估算值替换为真实数据

### Phase 2 扩展计划

将字段填充扩展到全部 41 个 Agent，按执行链路关键性优先排序（见下方建议）。

---

## 附录：skill_levels 汇总表

| Agent | task_execution | 核心专长维度1 | 核心专长维度2 | 核心专长维度3 | 最高分维度 |
|-------|---------------|-------------|-------------|-------------|-----------|
| harness_engineer | 5 | config_design:5 | task_execution:5 | documentation:4 | config_design |
| ai_systems_dev | 5 | python_development:5 | automation_scripting:5 | hook_development:4 | python/automation |
| knowledge_engineer | 4 | methodology_design:5 | documentation:5 | template_design:5 | methodology/docs |
| capability_architect | 5 | quality_audit:5 | onboarding_review:5 | algorithm_design:4 | quality_audit |
| integration_qa | 5 | quality_audit:5 | yaml_validation:5 | test_design:4 | quality/yaml |

---

## 附录：performance_history 汇总表

| Agent | tasks_completed | avg_quality_score | avg_completion_rate | blocked_tasks | escalation_count |
|-------|----------------|-------------------|--------------------|--------------|-----------------|
| harness_engineer | 18 | 4.3 | 0.98 | 0 | 1 |
| ai_systems_dev | 15 | 4.1 | 0.96 | 1 | 0 |
| knowledge_engineer | 14 | 4.2 | 0.97 | 0 | 0 |
| capability_architect | 11 | 4.4 | 0.98 | 0 | 2 |
| integration_qa | 22 | 4.5 | 0.99 | 0 | 1 |

---

**【执行者】：HR团队 - capability_architect**