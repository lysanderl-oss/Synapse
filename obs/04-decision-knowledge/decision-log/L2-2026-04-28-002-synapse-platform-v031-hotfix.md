---
decision_id: L2-2026-04-28-002
level: L2
title: synapse-platform v0.3.1 — Live E2E 热修复归档
status: shipped
decided_by: Lysander CEO
decided_at: 2026-04-28
commit: 822860c
tag: v0.3.1
---

# L2 决策：v0.3.1 热修复归档

## 触发事件

2026-04-28 Live E2E 验证期间（总裁参与）发现两个生产级问题：
1. Claude API 无超时保护 — PMAgent MEETING_PREP 调用挂起 6分17秒
2. MEETING_PREP maxTokens=4096 过大 — 导致不必要的长时等待

## 修复内容

| 文件 | 修复 |
|------|------|
| `src/integrations/claude/client.ts` | 添加 120s AbortController 超时，DEFAULT_TIMEOUT_MS=120_000 |
| `src/agents/pm-agent.ts` | MEETING_PREP 场景 maxTokens=1500（WEEKLY_REPORT 保留4096）|

## 验证结果

- 274/274 测试通过，零回归
- Live E2E 完整链路验证：Boss EN → PM ZH 审批 → Boss EN 结果
- 总裁全程参与验证，E2E PASS 确认

## 版本锁定

- VERSION: 0.3.1
- commit: 822860c
- tag: v0.3.1
- CHANGELOG: 已更新

**编制**：Lysander CEO · **生效**：2026-04-28
