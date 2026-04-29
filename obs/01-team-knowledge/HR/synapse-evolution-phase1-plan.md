---
name: Phase 1详细执行计划
description: Synapse体系进化Phase 1（Week 1-2.5）详细实施计划
type: execution-plan
phase: Phase 1
version: v1.0
created: 2026-04-22
status: pending-start
owner: Lysander CEO
depends_on: [synapse-evolution-plan-2026-Q2.md]
---

# Phase 1 详细执行计划
# Week 1-2.5 | 基础能力建设

## 执行顺序与依赖

### Week 1 前半（Day 1-3）
**T6-1: Harness Config注册表建立**（优先）
- 执行者：harness_engineer
- 交付物：`.claude/harness/rule-registry.yaml`
- 步骤：
  1. 从CLAUDE.md提取所有散落规则（Harness层/Prompt层/决策规则）
  2. 为每条规则定义：rule_id, priority(P0/P1/P2), condition, action, version
  3. 建立规则依赖关系图
- 验收标准：≥5条散落规则完成注册
- 预计工时：4小时

### Week 1 后半（Day 4-5）
**T2-1: Agent能力卡片字段填充**
- 执行者：capability_architect
- 依赖：T6-1完成
- 交付物：更新所有骨干Agent卡片，增加skill_levels和performance_history字段
- 步骤：
  1. 试点5个核心Agent：execution_auditor、harness_engineer、rd_tech_lead、ai_systems_dev、knowledge_engineer
  2. 每张卡片填写skill_levels（1-5熟练度）和performance_history（近10次任务记录）
  3. capability_architect自评 + qa_engineer抽检≥20%
- 验收标准：5个核心Agent完成双字段填充，通过率≥90%
- 预计工时：3小时

### Week 2（Day 6-10）
**并行执行：**

**T1-1: n8n webhook修复**
- 执行者：ai_systems_dev
- 交付物：nocalhost webhook URL更新，测试成功率≥99%
- 步骤：
  1. 诊断webhook 404根因（n8n cloud实例重建/URL变更）
  2. 重建webhook或更新URL配置
  3. 集成健康检查探测（每日自动）
- 验收标准：连续24小时webhook调用成功率≥99%
- 预计工时：1-2小时

**T6-2: Agent交接协议模板**
- 执行者：harness_engineer
- 交付物：`.claude/harness/agent-handoff-protocol.yaml`
- 内容：
  ```yaml
  agent_handoff_schema:
    input_contract:
      required_fields: [task_id, source_agent, target_agent, deadline]
      context_summary: string  # 不超过200字
      constraints: []  # 限制条件列表
    output_contract:
      required_fields: [task_id, result, quality_score, issues]
      artifacts: []  # 产出物清单
      next_hints: string  # 后续建议
  ```
- 验收标准：交接协议被≥80%的跨Agent任务采用
- 预计工时：2小时

### Week 2末-Week 3首（Day 11-12）
**T1-2: 情报质量雷达图上线**
- 执行者：knowledge_engineer
- 交付物：情报日报附带多维评分标签
- 评分维度（权重）：
  - 时效性(20%): 发布时间 vs 事件发生时间
  - 相关性(25%): 与Synapse战略关键词匹配度
  - 可执行性(30%): 是否含具体行动方
  - 置信度(15%): 来源权威性 × 交叉验证数量
  - 独特性(10%): 与历史情报库去重得分
- 验收标准：100%的情报日报附带质量雷达评分
- 预计工时：4小时

## 48小时同步机制

Phase 1期间：
- Lysander每48小时主持一次同步会议
- 各执行者汇报：已完成、进行中、阻塞项
- 阻塞项在24小时内升级至Lysander

## Phase 1出口审查

Phase 1完成条件（全部满足方可进入Phase 2）：
1. T6-1：≥5条规则完成注册
2. T2-1：5个核心Agent能力卡片完整率≥90%
3. T1-1：webhook连续24小时成功率≥99%
4. T1-2：情报多维评分覆盖率100%
5. T6-2：交接协议草案完成

出口审查执行者：Lysander CEO + integration_qa
