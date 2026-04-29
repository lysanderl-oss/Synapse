---
id: L2-2026-04-28-003
title: synapse-platform v0.3.2 — Personal Agent Training Layer 1+2
decision_level: L2
decided_by: Lysander CEO
date: 2026-04-28
product: synapse_platform
version: v0.3.2
status: executed
---

# L2 决策：synapse-platform v0.3.2 Personal Agent Training System

**决策级别**：L2（PMC 技术方案，Lysander 签发）  
**执行日期**：2026-04-28  
**授权依据**：总裁 2026-04-28 批准「授权lysander全权组织执行，我要去睡觉了，过程中不要找我审批。【原则不能影响前面已经跑通的功能】」

---

## 决策背景

v0.3.1 完成端到端验证后，总裁提出需要为 PMAgent 构建个人化训练能力（知识、风格、feedback）。经专家评审，采用四层渐进式架构方案。v0.3.2 交付第一、二层。

## 决策内容

### Layer 1 — Knowledge Upload API（个人知识库上传）

**新增文件**：
- `src/storage/migrations/005_add_chunk_type.sql` — `knowledge_chunks` 表新增 `chunk_type TEXT NOT NULL DEFAULT 'corpus'` 列及索引
- `src/storage/migrations/005_down.sql` — 回滚迁移
- `src/api/knowledge-upload.ts` — `uploadKnowledge(input, pool)` — 幂等性个人知识上传（chunk_type: personal/golden/rule）
- `agents/pm-agent/personal-kb/README.md` — 个人知识库投放目录

**修改文件**：
- `src/rag/semantic-retriever.ts` — 新增 `chunkTypes?: string[]` 过滤参数；默认 topK 从 5 升至 8；完全向后兼容

### Layer 2 — Style Capture / Golden Examples（审批驱动风格捕获）

**新增文件**：
- `src/rag/golden-ingester.ts` — `ingestGoldenExample(agentId, content, sourceLabel, pool)` — 将审批通过的输出以 `chunk_type='golden'` 写回向量库

**修改文件**：
- `src/integrations/slack/action-handler.ts` — `approve_handoff` 处理器在批准后 fire-and-forget `ingestGoldenExample`；`RegisterActionHandlersDeps` 新增可选 `pool` 字段
- `src/agents/pm-agent.ts` — RAG 检索过滤 `['corpus','personal']`（topK=8）；新增 golden few-shot 块（检索 `['golden']` top-2 作为风格锚点注入 system prompt）
- `src/index.ts` — postgres 模式下创建 `actionHandlerPool` 并传入 `registerActionHandlers`

## 质量验证

- 274/274 tests PASS（0 回归）
- 所有新 pool 引用可选/可空，graceful degradation
- golden 写入 fire-and-forget，不阻塞审批流
- TypeScript 编译通过（exactOptionalPropertyTypes: true）

## 约束遵守

- ✅ 不影响前面已跑通功能（v0.3.1 E2E 验证链路无变化）
- ✅ 向后兼容（chunk_type DEFAULT 'corpus'，现有语料查询不受影响）
- ✅ 版本号 0.3.1 → 0.3.2，CHANGELOG 已更新

## 下一里程碑

- v0.3.x Layer 3：Feedback Rules（LangMem 元提示合并）
- v0.3.x Layer 4：Progressive Memory（memory-seed.json 累积）
- v0.4.0：RBAC（REQ-SP-001）
- v0.4.0：CI/CD Pipeline（REQ-SP-002）

---

**编制**：knowledge_engineer · **生效**：2026-04-28 · **关联**：D-2026-04-28-002（synapse-platform 独立 PMC）
