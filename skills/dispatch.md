---
name: dispatch
description: "Standard task dispatch entry point — routes any task to the correct specialist via the routing table"
trigger: /dispatch
---

# /dispatch — Synapse Standard Dispatch

## Purpose
Routes any task description to the correct team and specialist based on the routing table in CLAUDE.md.

## Usage
```
/dispatch [task description]
```

## Execution Flow
1. Parse the task description for routing keywords
2. Match against the routing table (see CLAUDE.md LAYER 3)
3. Identify the target team and lead specialist
4. Output a formatted dispatch table
5. Create sub-agent to execute the task

## Routing Logic
The dispatch skill consults the routing table in CLAUDE.md LAYER 3. If multiple teams match, priority is:
1. Most specific keyword match wins
2. If tie: harness_ops > rd > graphify (system stability over analysis over execution)

## Output Format
```
**【② 团队派单】**

| 工作项 | 执行者 | 交付物 |
|--------|--------|--------|
| [task] | **[specialist_id]（[角色名]）** | [expected deliverable] |
```

## Routing Table Reference
See CLAUDE.md LAYER 3 — 路由表 section for the complete keyword-to-team mapping.
