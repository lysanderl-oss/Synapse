# Synapse Platform Phase 1 — Re-review Report (Post WP1.5)
# [CREATED: 2026-04-27]

**Final score: 93 / 100**
**Verdict: PASS — Sprint A WP2 is APPROVED to start.**

> Authoritative gate threshold: ≥ 90/100. Score reflects rigorous (not generous) review.
> Reviewer: execution_auditor | Source: WP1.5 correction report dated 2026-04-27 |
> Working tree spot-checked: `C:\Users\lysanderl_janusd\Projects\synapse-platform`.

---

## Per-category Breakdown

### 1. P0 closure quality — 24 / 25

| Item | Score | Evidence |
|------|-------|----------|
| P0-1 State machine SSOT | 5/5 | `docs/product/02-data-model.md:290-318` transition table mirrors `src/core/fsm-engine.ts:15-61` `TRANSITION_TABLE` row-for-row. Migration map at lines 44-49 preserves orientation for old links. |
| P0-2 Approval Gate | 5/5 | `config/approval-matrix.yaml` adds `awaiting_review→completed` to `required_human_approval`; `config/case-types.yaml` sets `weekly_report.requires_approval=true`; `src/core/approval-gate.ts:55-99` is fail-loud with 3 distinct error paths (missing file / invalid YAML / schema mismatch). Path resolver covers dist + src + cwd. |
| P0-3 Owner Input deprecation | 5/5 | Repo-wide grep for `owner.input|owner-input|owner_input|Owner Input|OwnerInput` outside `agents/pm-agent/`: zero matches. |
| P0-4 Phase 1 scope lock | 5/5 | `docs/PHASE1-SCOPE-LOCK.md` declares the 3 scenarios (`weekly_report`, `meeting_prep`, `internal_service`), enumerates 4 deferred enum values, reconciles the obsolete 9/7/2 counts, and binds change control to D-编号 + L3 approval. |
| No regressions | 4/5 | 60/61 tests pass; only pre-existing `id-generator` isolation failure remains (-1 because the WP did not opportunistically fix it via a `beforeEach` reset, even though it would have been a 2-line follow-up). |

### 2. Supplementary fixes — 20 / 20

| Fix | Score | Evidence |
|-----|-------|----------|
| F-1 regex | 5/5 | `tests/integration/case-flow.test.ts:48`: `/^CASE-\d{8}-\d{4}$/` — backslashes correct. |
| F-2 model id | 5/5 | `src/integrations/claude/client.ts:28` `DEFAULT_MODEL = 'claude-sonnet-4-5-20250929'`; `02-data-model.md:59` matches. |
| F-3 new tests | 5/5 | Spot-checked `tests/integration/governance-chain.test.ts` (5 substantive cases incl. shortcut block, agent-actor block, terminal-only-archives, cancelled-cannot-revive) and `tests/unit/intake-classifier.test.ts` (mocked Claude client, 5 cases incl. malformed JSON, missing fields, unknown caseType fallback, API throw). These are real assertions, not stubs. |
| F-4 ADR-0001 | 5/5 | `docs/adr/0001-no-langgraph-phase1.md` has 5 substantive drivers, explicit consequences (positive + negative), 4 named Phase 2 re-evaluation triggers, and 4 alternatives considered. |

### 3. Code/doc consistency — 19 / 20

- Transition table in product docs and FSM code SSOT match exactly. CaseStatus enum is canonical in `src/types/case.ts`; docs cite it explicitly (`02-data-model.md:41`).
- Scope lock cleanly resolves the 9/7/2 confusion.
- **-1 deduction**: `02-data-model.md:322` summary line says "`completed → *`、`cancelled → *`、`archived → *` 永久禁止" which is technically imprecise — `completed → archived` is the legitimate terminal-to-terminal path (correctly modeled in the table at line 316 and in the matrix). The summary line should read e.g. "`completed → *`（`archived` 除外）". Cosmetic; does not affect runtime behavior.

### 4. Test coverage and quality — 14 / 15

- 25 new test cases across 5 files; assertions verify behavior, not just shape.
- Governance-chain test exercises the full pipeline: happy path, shortcut block, agent-actor block, terminal rule, cancellation invariant, and the new P0-2 `awaiting_review→completed` approval requirement.
- Intake-classifier test mocks `callClaude` and verifies error-path null returns — not a stub.
- **-1 deduction**: no test directly asserts the fail-loud behavior of `loadMatrix()` (e.g., temporarily renaming the matrix and asserting throw). The existing tests benefit from fail-loud indirectly (path resolver works), but a dedicated negative test would lock the contract. Add as backlog.

### 5. Governance soundness — 10 / 10

- Fail-loud loadMatrix is correct and verbose (path + cause in error message).
- Forbidden-transition list is now explicit and complete: 8 rows for `completed → {in_progress, awaiting_review, awaiting_approval, triaged, planned, intake, blocked, cancelled}`, 2 catch-all `cancelled→any` and `archived→any`, plus 3 cross-step blocks (`intake→completed`, `intake→archived`, `triaged→completed`). Dangerous reversions (e.g., completed→intake) are explicitly blocked.
- `completed→archived` correctly preserved as legitimate terminal transition.
- Cache reset hook (`resetCache`) exposed on ApprovalGate for test isolation — good hygiene.

### 6. Forward-readiness — 6 / 10

- Build / typecheck baseline OK; `npm test` runs in ~565 ms; ApprovalGate logs successful matrix load with `requiredApprovals=3, forbidden=13` matching the YAML.
- **-2 deduction**: naming clash `service_request` vs `internal_service` is currently treated as alias only. This is acceptable for ship but creates a small risk that a Phase 2 doc author re-introduces `service_request` literals. See recommendation below.
- **-1 deduction**: `CaseService` does not emit specialized `CASE_COMPLETED` / `CASE_CANCELLED` events; only generic `CASE_STATUS_CHANGED`. The audit-trail test compensates by inferring terminal state from `after.status`, but if any downstream consumer (e.g., notifier, KPI aggregator) is being designed in WP2 against the specialized types, this will bite.
- **-1 deduction**: platform repo is fully unstaged — no commit yet. WP2 work landing on top will entangle WP1.5 changes if not committed first.

---

## Surprise Assessment (5 items from WP1.5)

| # | Surprise | Severity | Reasoning |
|---|----------|----------|-----------|
| 1 | `resolveMatrixPath()` fix in `approval-gate.ts` | **Resolved (sound)** | The 3-candidate resolver (dist / src / cwd) covers vitest, ts-node, and compiled prod. `existsSync` short-circuits to first hit; if none found returns the cwd path so the fail-loud error message is meaningful. Acceptable. |
| 2 | `completed → any` replaced with explicit illegal list | **Resolved (correct)** | The new list explicitly blocks 8 dangerous reversions including completed→intake, completed→in_progress, etc. The legitimate completed→archived path is preserved. Verified against fsm-engine.ts TRANSITION_TABLE. |
| 3 | Naming clash `service_request` vs `internal_service` | **Follow-up (Phase 2 rename, NOT a Phase 1 blocker)** | Code SSOT is `internal_service` and is used consistently in code, config, tests. Brief-only `service_request` references are documentary, scope-lock acknowledges the alias. Recommend: keep `internal_service` as canonical; open a Phase 2 backlog item to scrub residual `service_request` mentions. Renaming code now would cascade into config, tests, and possibly Slack message templates without acceptance benefit. |
| 4 | `CaseService` emits only `CASE_STATUS_CHANGED`, not `CASE_COMPLETED` / `CASE_CANCELLED` | **Follow-up (non-blocker)** | Audit completeness is preserved (every transition logged with before/after); the specialized event types in `audit.ts` are unused but harmless. Promote to follow-up: either (a) emit specialized types in addition, or (b) delete the unused enum values. Decide in WP2 grooming, not blocking. |
| 5 | Platform repo unstaged | **Housekeeping (do before WP2 starts)** | Mandatory: commit WP1.5 to a clean branch in the platform repo before WP2 development opens new diffs. This is a 2-minute action; not a scoring deduction beyond the -1 already taken in §6. |

---

## Naming-clash Decision Recommendation

**Recommendation: KEEP `internal_service` as Phase 1 canonical. Defer `service_request` doc-scrub to Phase 2.**

Rationale:
1. Code, `config/case-types.yaml`, all tests, and the new scope-lock doc agree on `internal_service`.
2. Renaming the code identifier now means: changing `CaseType.INTERNAL_SERVICE` enum value, updating Slack message templates, regression-testing classifier prompts that may have been tuned on the literal string, and re-running 60 tests. Net: same surface, zero added value.
3. The scope-lock doc explicitly records the alias, so the next reader is not surprised.
4. Open follow-up: `tracker-followup-1` "Replace residual `service_request` literals in product docs" — small grep-and-replace pass, no code change.

---

## Sprint A WP2 Readiness Checklist

- [x] State machine SSOT aligned across code + 5 product docs
- [x] Approval Gate fail-loud + matrix complete + path resolver sound
- [x] Owner Input fully deprecated outside `agents/pm-agent/`
- [x] Phase 1 scope locked to 3 scenarios, change control bound to D-编号
- [x] Test suite green except 1 pre-existing unrelated failure
- [x] Anthropic model id current (`claude-sonnet-4-5-20250929`)
- [x] ADR-0001 documents the no-LangGraph decision with re-evaluation triggers
- [ ] **Action before WP2 first commit**: commit WP1.5 changes to platform repo on a clean branch (housekeeping)

WP2 may proceed once the WP1.5 commit lands. No further re-correction required.

---

## Outstanding Follow-ups (Non-blocking, Backlog)

1. **`fu-id-generator-isolation`** — Reset module-level ID counter in `tests/unit/id-generator.test.ts` `beforeEach`. ~5 lines.
2. **`fu-doc-summary-precision`** — Fix `02-data-model.md:322` summary to read `completed → *（archived 除外）`. Cosmetic.
3. **`fu-loadmatrix-negative-test`** — Add a vitest case that renames/removes the matrix file and asserts `loadMatrix()` throws with the descriptive message. Hardens fail-loud contract.
4. **`fu-service-request-doc-scrub`** — Phase 2 grep-and-replace residual `service_request` mentions to `internal_service` once the alias becomes confusing.
5. **`fu-specialized-audit-events`** — Decide whether to emit `CASE_COMPLETED` / `CASE_CANCELLED` events from `CaseService` or delete the unused enum members.
6. **`fu-platform-repo-commit`** — Commit WP1.5 changes to a named branch in `synapse-platform` before WP2 lands diffs on top. Not a scoring item, but a release-engineering MUST-DO.

---

## Score Summary

| Category | Max | Score |
|----------|-----|-------|
| P0 closure quality | 25 | 24 |
| Supplementary fixes | 20 | 20 |
| Code/doc consistency | 20 | 19 |
| Test coverage and quality | 15 | 14 |
| Governance soundness | 10 | 10 |
| Forward-readiness | 10 | 6 |
| **Total** | **100** | **93** |

**Verdict: PASS (≥ 90 threshold cleared by 3 points). Sprint A WP2 development is unblocked, conditional on the platform-repo commit (housekeeping) before WP2 diffs land.**

---

*Reviewer: execution_auditor | Method: WP1.5 report read + spot-check of approval-matrix.yaml, approval-gate.ts, fsm-engine.ts, 02-data-model.md, PHASE1-SCOPE-LOCK.md, ADR-0001, governance-chain.test.ts, intake-classifier.test.ts, repo-wide owner-input grep, model-id grep, full `npm test` run (60/61 pass).*
