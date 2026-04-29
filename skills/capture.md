---
name: capture
description: "Quickly capture an idea, task, or note into active_tasks.yaml"
trigger: /capture
---
# /capture — Quick Capture

Captures a new item to agent-butler/config/active_tasks.yaml.

## Usage: /capture [content]

## What butler_pmo does:
1. Parse the captured content
2. Classify: task | idea | note | follow_up
3. Append to active_tasks.yaml with status: inbox
4. Confirm capture with ID

## Output format:
✅ Captured: [ID] "[content]" → active_tasks.yaml (status: inbox)
