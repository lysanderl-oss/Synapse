---
id: cross-session-state
type: harness-fragment
parent: CLAUDE.md
extracted_at: 2026-04-27
moved_per: president decision ①A
---

# 跨会话状态管理（详细机制）

> 触发场景：会话开启 / 会话结束 / 续接长任务
> 核心要点已在 CLAUDE.md 工作原则中保留：「跨会话恢复 — 新会话开始时读取 active_tasks.yaml」

## 会话结束前 Lysander 必须

1. 将进行中的任务写入 `agent-CEO/config/active_tasks.yaml`
2. 记录当前执行链环节、阻塞项、下一步

## 新会话开始时 Lysander 必须

1. 读取 `active_tasks.yaml`
2. 如有进行中任务，向总裁简要汇报并继续执行

## 字段约定（active_tasks.yaml 单条任务）

```yaml
- id: TASK-YYYYMMDD-NN
  status: in_progress | blocked | approved-pending-dispatch | done
  current_stage: 0.5 | 1 | 2 | 3 | 4
  blocker: <文字描述，无则留空>
  next_step: <下一动作>
  owner: <specialist_id>
  created_at: <ISO 时间戳>
  updated_at: <ISO 时间戳>
```

## 与 Pending-Dispatch 自动 review 的关系

新会话【0.5】节点的「②.5 Pending-Dispatch INTEL 自动 review」直接消费 active_tasks.yaml 中 status=approved-pending-dispatch 的条目，规则在 `agent-CEO/config/active_objectives.yaml` 的 `dispatch_rules` 段。
