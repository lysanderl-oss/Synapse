# Phase 3 Sprint E — pgvector RAG Pipeline — Delivery Report

**Date:** 2026-04-27
**Branch:** phase3-sprint-e
**Commit:** fdcd834
**Decision:** D-2026-0427-013

---

## Goal A–F Status

| Goal | Description | Status |
|------|-------------|--------|
| A | DB migration 003 (knowledge_chunks + HNSW index) | DONE |
| B | CorpusIngester (chunking, OpenAI embed, idempotent upsert) | DONE |
| C | SemanticRetriever (cosine search, graceful degradation) | DONE |
| D | RAG wired into PMAgent / ResearchAgent / ContentAgent at intake | DONE |
| E | CLI ingest script + `rag:ingest` npm script | DONE |
| F | Unit tests: corpus-ingester (7) + semantic-retriever (6), all mocked | DONE |

---

## Test Results

| Metric | Before | After |
|--------|--------|-------|
| Test count | 183 | **196** |
| Failures | 0 | **0** |
| Test files | 28 | 30 |

New tests: `tests/unit/corpus-ingester.test.ts` (7 tests), `tests/unit/semantic-retriever.test.ts` (6 tests).

---

## TypeScript Status

`npx tsc --noEmit` — **0 errors**.

---

## RAG Architecture Summary

**Chunking strategy:**
- Character-based sliding window: 2048-char chunks, 256-char overlap
- Approximates 512-token / 64-token overlap at ~4 chars/token
- Supported file types: `.md`, `.json`, `.txt` (recursive scan of `agents/{agent-id}/`)

**Embedding model:** OpenAI `text-embedding-3-small` (1536 dimensions)
- Batch size: up to 100 chunks per API call
- Idempotent: checks `(agent_id, source_file, chunk_index)` before embedding

**Vector index:** HNSW on `knowledge_chunks.embedding vector(1536)`
- `m = 16`, `ef_construction = 64`
- Distance metric: cosine (`vector_cosine_ops`)
- Query: `ORDER BY embedding <=> $2 LIMIT $3`

**Retrieval pattern at intake:**
1. Agent receives a Case (title + description)
2. `retrieveContext(title + description, agentId, pool, topK=5)` called
3. If chunks returned, appended as an `ephemeral` system block: `## Relevant knowledge retrieved:`
4. Falls through to existing static KB blocks + playbook + template blocks

---

## Graceful Degradation Verification

All degradation paths return `[]` (empty array) — confirmed by unit tests:

| Condition | Behavior |
|-----------|----------|
| `pool = null` | Returns `[]`, logs debug |
| `pool = undefined` | Returns `[]`, logs debug |
| `OPENAI_API_KEY` absent | Returns `[]`, logs warning |
| OpenAI API throws | Returns `[]`, logs warning |
| Agent has no `pool` (FileStore backend) | RAG block silently skipped |

Agents never crash — they fall back to the existing static knowledge base file loading behavior.

---

## Files Created / Modified

**New files:**
- `src/rag/knowledge-chunk.ts` — KnowledgeChunk type
- `src/rag/corpus-ingester.ts` — CorpusIngester with `ingestAgentCorpus()` + `chunkText()`
- `src/rag/semantic-retriever.ts` — SemanticRetriever with `retrieveContext()`
- `src/rag/ingest-cli.ts` — CLI ingestion script
- `src/storage/migrations/003_pgvector_knowledge_chunks.sql` — UP migration
- `src/storage/migrations/003_down.sql` — DOWN migration
- `tests/unit/corpus-ingester.test.ts` — 7 unit tests
- `tests/unit/semantic-retriever.test.ts` — 6 unit tests

**Modified files:**
- `src/storage/migrations/run-migrations.ts` — runs 001 + 003 in sequence
- `src/agents/pm-agent.ts` — RAG injection at intake + pool dep
- `src/agents/research-agent.ts` — RAG injection at intake + pool dep
- `src/agents/content-agent.ts` — RAG injection at intake + pool dep
- `package.json` — `rag:ingest` script + `openai ^6.34.0` dependency
- `.env.example` — `OPENAI_API_KEY` entry added

---

## Sprint F Readiness Note

Sprint E delivers the full RAG pipeline plumbing. Sprint F can focus on:
1. **Live integration test** — Docker Compose with pgvector image + real corpus ingestion
2. **Retrieval quality tuning** — `ef_search` parameter, topK calibration
3. **Cache invalidation** — re-ingest trigger when agent KB files change (file mtime tracking)
4. **Metrics** — RAG hit rate, latency tracking in EvidenceBundle metadata
5. **Multi-agent corpus** — cross-agent retrieval (e.g., content-agent querying pm-agent chunks)

No breaking changes in Sprint E — all 183 pre-existing tests continue to pass.
