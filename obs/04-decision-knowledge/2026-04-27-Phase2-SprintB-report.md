# Phase 2 Sprint B Delivery Report

**Date:** 2026-04-27
**Branch:** phase2-sprint-b
**Base branch:** phase2-wp0 (90 tests, 0 tsc errors)
**Commit:** b4d36a9
**Final state:** 135 tests passed across 24 files | tsc: 0 errors

---

## Summary

Phase 2 Sprint B implemented 6 goals that complete the Phase 2 core platform expansion from 3 case types to 7.

---

## Goals Delivered

### Goal A — RoutingRulesEngine

**File:** `src/core/routing-rules-engine.ts`

Created `RoutingRulesEngine` class with the same fail-loud YAML-loading pattern as `ApprovalGate`. Loads `config/routing-rules.yaml` and exposes:
- `resolveAgent(caseType)` — throws for unknown types
- `resolveAgentWithFallback()` — falls back to `agent.ops`
- `getEntry()`, `getAllCaseTypes()`, `resetCache()`

Wired into `OrchestratorAgent` (constructor injection with fallback to classifier output if routing engine throws).

Tests: `tests/unit/routing-rules-engine.test.ts` — 7 routing assertions, cache test, fallback test.

---

### Goal B — ResearchAgent

**Files:**
- `src/agents/research-agent.ts`
- `agents/research-agent/profile.json`
- `agents/research-agent/memory-seed.json`
- `agents/research-agent/playbooks/research-request.md`
- `agents/research-agent/playbooks/data-analysis.md`
- `agents/research-agent/templates/research-request.md`
- `agents/research-agent/templates/data-analysis.md`

`agent.research` handles `research_request` and `data_analysis` case types. Mirrors PMAgent pattern: loads profile, memory-seed, playbook, and template as ephemeral-cached `extraSystemBlocks`. Writes `ArtifactType.REPORT` artifacts and persists `EvidenceBundle`.

Agent persona: MECE issue decomposition, hypothesis-driven analysis, evidence triangulation, pyramid synthesis. Minimum 3 independent sources before stating conclusions.

Tests: `tests/integration/research-request-e2e.test.ts` + `tests/integration/data-analysis-e2e.test.ts`

---

### Goal C — ContentAgent

**Files:**
- `src/agents/content-agent.ts`
- `agents/content-agent/profile.json`
- `agents/content-agent/memory-seed.json`
- `agents/content-agent/playbooks/content-draft.md`
- `agents/content-agent/playbooks/decision-brief.md`
- `agents/content-agent/templates/content-draft.md`
- `agents/content-agent/templates/decision-brief.md`

`agent.content` handles `content_draft` (ArtifactType.DRAFT) and `decision_brief` (ArtifactType.DOCUMENT). Same structure as ResearchAgent.

Agent persona: SCQA framing, Pyramid Principle, Amazon 6-pager discipline, Chicago Manual of Style editorial standards. Decision briefs always include minimum 3 options with explicit recommendation.

Tests: `tests/integration/content-draft-e2e.test.ts` + `tests/integration/decision-brief-e2e.test.ts`

---

### Goal D — IntakeClassifier Phase 2 Signals

**File:** `src/agents/intake-classifier.ts`

Added 4 keyword arrays and 4 detector functions for Phase 2 scenario types:
- `detectResearchRequestSignal()` — research, investigate, 调研, competitive analysis
- `detectDataAnalysisSignal()` — analyze data, 数据分析, dashboard, metrics, trend analysis
- `detectContentDraftSignal()` — write an article, draft a blog, blog post, 撰写, draft an email (no broad single-word terms to avoid false positives)
- `detectDecisionBriefSignal()` — decision, decide, 决策, options, evaluate alternatives

Order: decision_brief checked first (most specific), then data_analysis, then research_request, then content_draft.

**Fix applied:** Removed broad terms `'report'`, `'content'`, `'draft'` from CONTENT_DRAFT_KEYWORDS after discovering they caused false positive for "weekly report" input.

Tests: `tests/unit/intake-classifier-phase2.test.ts`

---

### Goal E — Bolt Socket-Mode Smoke Test

**File:** `tests/smoke/bolt-init.test.ts`

3 tests verifying:
1. Bolt App instantiates without throwing (mocked tokens)
2. Action and event handlers can be registered without throwing
3. `createSlackApp()` singleton returns an App instance

---

### Goal F — Cross-Channel Delivery Routing

**File:** `src/integrations/slack/action-handler.ts`

On `approve_case`, the handler now reads `targetCase.metadata?.['slackChannel']` and `targetCase.metadata?.['slackThreadTs']`. When present:
- Posts delivery notification to original request channel (threaded if `slackThreadTs` is set)
- Also posts brief notice to approval channel if they differ

Falls back to approval-channel-only behavior when metadata is absent (Phase 1 backward compat preserved).

Tests: New `describe` block appended to `tests/integration/approval-action.test.ts`

---

### Supporting Changes

- **`src/integrations/claude/prompt-templates.ts`**: Added `research` and `content` system prompts (McKinsey Pyramid, MECE, SCQA, Amazon 6-pager standards). Updated `orchestrator` prompt to include `agent.research` and `agent.content`.
- **`src/index.ts`**: Registered `ServiceAgent`, `ResearchAgent`, `ContentAgent` in bootstrap.
- **`src/agents/orchestrator-agent.ts`**: RoutingRulesEngine injected with fallback.

---

## Test Results

| File | Tests |
|------|-------|
| tests/unit/routing-rules-engine.test.ts | 6 |
| tests/unit/intake-classifier-phase2.test.ts | 12 |
| tests/smoke/bolt-init.test.ts | 3 |
| tests/integration/research-request-e2e.test.ts | 3 |
| tests/integration/data-analysis-e2e.test.ts | 1 |
| tests/integration/content-draft-e2e.test.ts | 2 |
| tests/integration/decision-brief-e2e.test.ts | 2 |
| (20 pre-existing test files) | 106 |
| **Total** | **135 passed** |

tsc: 0 errors | 24 test files | 0 failures

---

## Notable Technical Decisions

1. **ResearchAgent/ContentAgent constructor**: Takes `{ artifactStore?, evidenceStore? }` dependency bag (same pattern as PMAgent) rather than positional arg, enabling flexible injection in tests.

2. **CONTENT_DRAFT_KEYWORDS false positive fix**: Original broad keywords (`'report'`, `'content'`, `'draft'`) caused "weekly report" to match content_draft before calling Claude. Fixed by restricting to specific multi-word phrases.

3. **E2E test file pattern**: Had to match the established test pattern exactly — `createCase(input, actor)` with two args, `TRIAGED → PLANNED` transitions before `executeCase()`, and `artifactStore.findByCaseId()` for artifact content verification.

4. **Routing rules ordering**: Decision brief checked before data_analysis and research_request to prevent false positives from overlapping keywords (e.g., "data options" would otherwise hit research_request).
