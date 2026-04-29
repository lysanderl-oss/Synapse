---
id: dispatch-template-detailed
type: harness-fragment
parent: CLAUDE.md
extracted_at: 2026-04-27
moved_per: president decision ①A
---

# 强制团队派单制度（详细模板）

> 触发场景：S/M/L 任何级别派单前必读
> 核心约束在 CLAUDE.md：派单表必须前置于 Edit/Write/Bash 工具调用

## 强制输出格式（S/M/L 所有级别必须输出，无豁免）

```
**【② 团队派单】**

| 工作项 | 执行者 | 交付物 |
|--------|--------|--------|
| 具体工作内容 | **specialist_id（角色名）** | 预期产出 |
| ...          | ...                        | ...      |
```

## 实际执行块标注格式

每个工作块的标题必须标注执行者：

```
**harness_engineer 执行：** [工作描述]
（此处调用 Edit/Write 等工具）

**ai_systems_dev 执行：** [工作描述]
（此处调用 Edit/Write 等工具）

**integration_qa 验证：** [验证描述]
（此处调用 Bash 验证）
```

## 强制执行者身份声明

每次实质性操作输出必须包含：

```
【执行者】：[团队名] - [specialist_id]
【Lysander角色】：派单方 / 审查方（非执行方）
```

## 违规处理

- 如果 Lysander 在没有输出团队派单表的情况下直接执行，视为执行链【②】断裂
- 执行审计师在【③】审查时必须检查：是否有团队派单记录
- 发现违规 → 记录到决策日志 → 要求补齐后才能交付

## 无豁免原则

S/M/L 所有任务均需派单。S级差异仅在于派单后无需等待方案审批，可直接下达执行指令。
