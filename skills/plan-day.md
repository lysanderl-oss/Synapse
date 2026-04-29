---
name: plan-day
description: "Generate today's prioritized task plan from active_tasks.yaml"
trigger: /plan-day
---
# /plan-day — Daily Plan Generator

## Execution: butler_pmo + graphify_strategist

1. butler_pmo reads active_tasks.yaml — extracts all pending/in_progress items
2. graphify_strategist applies prioritization: Impact × Urgency matrix
3. Output: today's top 5 tasks with time blocks

## Output format:
### 今日计划 [date]
| 优先级 | 任务 | 预计完成时间 | 团队 |
|--------|------|-------------|------|
| P1 | ... | ... | ... |
