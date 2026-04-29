# D-2026-04-29-002 — synapse-platform v0.4.0 RBAC Phase 4 + Agent Training Layer 3/4 + CI/CD

**决策级别**: L2（总裁授权 → Lysander 统筹执行）
**日期**: 2026-04-29
**状态**: ✅ 已执行并验证
**提案人**: 总裁刘子杨（"lysander 组织推进 v0.4.0执行，完成后我们启动正式训练"）
**批准人**: Lysander CEO
**执行团队**: RD Team + Product Team + QA

## 决策背景

v0.3.3 企业级 RAG 管线交付后，总裁授权推进 v0.4.0，完成 Agent 训练体系的全部 4 层，并补齐 RBAC 基础 + CI/CD 基础设施，为正式训练启动做最终准备。

要求：
1. 产品团队全面审查，避免遗留问题
2. 全面 E2E 验证
3. 验证完成后汇报总裁验收

## 执行摘要

| 模块 | 状态 | 说明 |
|------|------|------|
| RBAC Phase 4 | ✅ | NoOpPermissionGate + RbacPermissionGate + migration 004 |
| Layer 3 Feedback Rules | ✅ | rules-upload.ts + PMAgent injection + add-rule CLI |
| Layer 4 Progressive Memory | ✅ | memory-accumulator.ts + approve_handoff 触发 |
| CI/CD (REQ-SP-002) | ✅ | .github/workflows/ci.yml + .env.example + check:env |
| 产品审查 CRITICAL 修复 | ✅ | README 虚假 API 文档已移除 |
| Orchestrator 类型验证 | ✅ | 未注册 runner → BLOCKED（替代 throw） |
| 20 个新单元测试 | ✅ | knowledge-upload/golden-ingester/reranker/embedder/memory-accumulator |

## 验证结果

- 294/294 测试通过（从 274 增至 294，+20 新测试）
- TypeScript 编译无错误
- 全 6 项 feature wire-up 检查通过
- DB migration 004 已应用到 Supabase
- 产品审查：无 CRITICAL 遗留问题

## Agent 训练体系完整状态

| 层级 | 状态 | 触发方式 |
|------|------|---------|
| Layer 1 知识上传 | ✅ | npm run rag:ingest |
| Layer 2 风格捕捉 | ✅ | approve_handoff → golden 样本 |
| Layer 3 反馈规则 | ✅ | npm run rules:add → PMAgent 注入 |
| Layer 4 渐进记忆 | ✅ | approve_handoff → memory-seed.json |

## 版本标记

- Commit: `e273a04`
- Tag: `v0.4.0`
- Branch: `acceptance-simulation`
- 23 files changed, 983 insertions, 25 deletions

## 下一步

- 总裁验收后：启动 PMAgent 正式训练
  1. `npm run rules:add` 添加首批规则
  2. 通过 Slack 发送任务 → 审批 → 自动积累 golden + memory
- v0.5.0 计划：RBAC Phase 5（真实权限执行）+ Jina Reader PDF 入库 + DB agentId 统一
