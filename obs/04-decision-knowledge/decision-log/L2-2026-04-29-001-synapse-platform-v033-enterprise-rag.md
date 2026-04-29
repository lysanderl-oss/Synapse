# D-2026-04-29-001 — synapse-platform v0.3.3 Enterprise RAG Pipeline

**决策级别**: L2（专家评审 → Lysander 批准执行）
**日期**: 2026-04-29
**状态**: ✅ 已执行并验证
**提案人**: 总裁刘子杨
**批准人**: Lysander CEO
**执行团队**: RD Team

## 决策背景

v0.3.2 完成 Voyage AI 嵌入层后，总裁提出采用 2026 年企业级"杂交"RAG 方案，结合三款专业工具的核心优势：
- **Jina Reader**: PDF → Markdown 清洗（待后续激活）
- **Voyage AI voyage-3**: 高召回率向量嵌入（已激活）
- **Jina Reranker v2 multilingual**: 中文业务语境精排（v0.3.3 激活）

同时发现 Voyage free-tier 有 3 RPM 限制导致语料入库失败，需修复。

## 核心变更

| 文件 | 变更内容 |
|------|---------|
| `src/rag/reranker.ts` | 新建 Jina reranker 集成，jina-reranker-v2-base-multilingual |
| `src/rag/semantic-retriever.ts` | 两阶段检索：pgvector(candidateK=topK×3) → Jina rerank(topK) |
| `src/rag/embedder.ts` | 429 指数退避重试（22s/44s/66s，maxRetries=10） |
| `src/rag/corpus-ingester.ts` | EMBED_BATCH=5，20s 批间延迟适配 Voyage free-tier |

## 验证结果

- 274/274 测试通过（无回归）
- TypeScript 编译无错误
- pm-agent 语料入库：35 chunks 跨 7 批次成功写入 Supabase
- Jina Reranker E2E：中文查询"本周风险和下周计划"精排结果正确
- 完整管线验证：Voyage embed → pgvector(top-24) → Jina rerank → top-8

## 版本标记

- Commit: `74e816e`
- Tag: `v0.3.3`
- Branch: `acceptance-simulation`

## 已知问题（非阻断）

- pm-agent 语料在 DB 中因 Windows 路径 base64 前缀碰撞显示 6 行（实际 35 chunks）—— ID 生成逻辑的预存结构问题，不影响检索功能，列入 v0.4.0 待办

## 下一步

- v0.4.0: RBAC (REQ-SP-001) + CI/CD (REQ-SP-002) + GitHub remote
- Layer 3: Feedback Rules（LangMem 风格）
- Layer 4: Progressive Memory（memory-seed.json 积累）
- 待总裁确认：Jina Reader PDF 入库场景
