---
id: automation-event-chain
type: harness-fragment
parent: CLAUDE.md
extracted_at: 2026-04-27
moved_per: president decision ①A
---

# 自动化编排 — Harness Automation Layer（详细 event chain）

> 触发场景：定时任务变更、远程 Agent 调度、自动化诊断
> 概述已在 CLAUDE.md 保留一行 reference

## 每日自动化全流程

```
  6:00am Dubai ── 任务自动恢复Agent
                   │ 检查 active_tasks.yaml
                   │ 恢复阻塞已解除的任务
                   │ 续接未完成工作
                   ↓
  8:00am Dubai ── 情报日报Agent
                   │ 搜索AI前沿动态
                   │ 筛选实践价值内容
                   │ 生成情报日报 → HTML → git push
                   ↓
 10:00am Dubai ── 情报行动Agent
                   │ 提取日报建议 → 4专家评估 → 评审决策
                   │ Harness Ops团队执行批准项
                   │ 生成行动成果报告 → HTML → git push
                   ↓
  完成 ────────── Slack通知总裁
```

## 触发机制

详见 `agent-CEO/config/n8n_integration.yaml`：

- **定时触发**：3 个远程 Agent 按时间编排运行
- **事件触发**：代码变更 → 自动 QA 审查（webhook）
- **状态触发**：任务阻塞解除 → 自动恢复执行

## 远程定时任务管理面板

https://claude.ai/code/scheduled
