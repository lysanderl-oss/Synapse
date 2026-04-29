---
name: Agent能力卡片进化体系调研报告
description: Synapse Agent能力评估/进化路径/OPC能力矩阵深度调研
type: research-report
research_id: E
executor: HR团队（capability_architect+hr_director）
date: 2026-04-21
version: v1.0
---

# Agent能力卡片进化体系调研报告

**执行者**：HR团队（capability_architect+hr_director联合调研）
**日期**：2026-04-21

---

## 核心发现摘要

### TOP 5可落地建议

1. **建立Agent能力评分体系（P0）**：skill_levels+performance_history字段，让任务分配从"关键词匹配"升级为"智能推荐"
2. **引入capability_router算法（P1）**：能力向量路由，基于skill_levels×成功率×当前负载加权
3. **设计Agent成长路径（P1）**：L1/L2/L3晋升标准，能力升级须通过评审
4. **建立Agent备份机制（P2）**：关键Agent必须指定备份，防止单点故障
5. **引入能力演化轨迹追踪（P2）**：每次任务完成自动记录核心能力/QA评分/新方法论

### 核心洞察
- 能力描述存在但无法衡量执行效果
- 任务分配应从"关键词匹配"升级为"能力向量路由"
- Synapse 41个Agent已高度冗余，建议合并冗余，专注补足缺口

---

## 方向一：Agent能力卡片体系现状

### 结构完整性：高
Synapse已建立统一YAML模板，全团队41个Agent卡片均遵循同一结构。

### 能力描述质量：有分层机制
- A级：含具体方法论+工具/框架+可测量输出
- B级：含领域工具但缺方法论细节
- C级：仅列活动名称（自动拒绝）
- capability_architect具备A/B/C自动审计能力

### 关键缺口（3项）

| 缺口 | 影响 | 现状 |
|------|------|------|
| 无技能熟练度等级 | 无法判断同一任务谁做得更好 | max_concurrent_tasks=3-5，无差异化 |
| 无任务-能力匹配评分 | 任务分配依赖关键词，精度不足 | 仅靠summon_keywords模糊匹配 |
| 无能力演化记录 | 升级靠手工，无轨迹追踪 | evolution_engine管版本，不管Agent能力演化 |

## 方向二：Multi-Agent能力评估最佳实践

### GAIA基准（General AI Assistants）
- Level 1：直接查询
- Level 2：多步协调
- Level 3：长程规划
启示：Synapse的S/M/L分级与GAIA分级逻辑对齐，但缺少任务难度自动标定机制。

### Task Complexity与Agent能力的动态匹配

最佳实践模式：
1. 输入任务 → 自动拆解为子任务
2. 为每个子任务匹配最适Agent（能力覆盖度×当前负载×历史成功率）
3. 执行 → 结果验证 → 反馈写入Agent能力记录

Synapse现状：execution_auditor负责分级，但无自动化能力匹配算法。

## 方向三：Agent进化路径设计

### Specialist→Generalist演进路径

```
入门级Specialist（L1）
  ↓ 积累10+成功案例
中级Specialist（L2）
  ↓ 跨域协作>3个团队
高级Specialist（L3）→ 可触发Generalist转型
  ↓ 掌握2+领域方法论
Generalist → 多任务自适应
```

### 能力提升机制最佳实践

| 机制 | 描述 | Synapse现状 |
|------|------|-------------|
| Gap Analysis | 定期扫描能力矩阵，识别缺失项 | evolution_engine有Gap矩阵，针对体系而非Agent |
| Skill Rotation | Agent间交换任务，扩展能力边界 | 无 |
| Shadowing | 新Agent观察专家执行，模仿学习 | 无 |
| Knowledge Distillation | 将专家能力压缩为可迁移模式 | 无 |

## 方向四：One Person Company能力矩阵

### 最小完备能力集（MVC）分析
- Synapse 41个Agent已高度冗余，部分能力域过度覆盖
- butler_pmo+harness_entropy_auditor功能高度重叠
- content_strategist+growth_insights存在能力交集
- 建议：合并冗余Agent，专注补足缺口

### 能力备份策略
- 无Agent备份机制（单点故障风险）
- rd_tech_lead是唯一架构评审，无备份
- execution_auditor工作负载已达high，无冗余

## Agent能力卡片增强字段

```yaml
skill_levels:           # 技能熟练度（1-5）
  task_routing: 4       # 任务路由精准度
  quality_output: 3     # 输出质量稳定性
  cross_team_collab: 2  # 跨团队协作能力

performance_history:   # 绩效历史
  tasks_completed: 47
  avg_quality_score: 4.2
  avg_response_time: "<5min"

evolution_trail:       # 能力演化轨迹
  last_upgraded: "2026-04-10"
  capability_added: "ReAct pattern integration"
  upgrade_trigger: "performance_review"

specialty_score:       # 专精评分
  rank: 2/5
  gap_to_top: "缺少Multi-Agent Orchestration方法论"
```

**【执行者】：HR团队（capability_architect+hr_director联合）**
