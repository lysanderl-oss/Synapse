---
name: weekly-review
description: "Weekly retrospective: completed, incomplete, next week priorities"
trigger: /weekly-review
---
# /weekly-review — Weekly Review

## Execution: execution_auditor + graphify_strategist

1. execution_auditor scans active_tasks.yaml for the past 7 days
2. Produces: completed / incomplete / blocked breakdown
3. graphify_strategist synthesizes: key wins, lessons, next week focus

## Output format:
### 本周回顾 [date range]
**完成** (N项): ...
**未完成** (N项): ...
**阻塞** (N项): ...
**下周重点**: ...
**执行链健康度**: X/10
