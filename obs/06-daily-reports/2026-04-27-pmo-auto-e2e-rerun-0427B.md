---
id: pmo-auto-e2e-rerun-0427B
type: narrative
status: published
lang: en
version: 2.4.0
published_at: "2026-04-27"
updated_at: "2026-04-27"
author: pmo_test_engineer
review_by: [integration_qa]
audience: [team_partner]
---

# PMO Auto v2.4.0 E2E Test Report — Run 0427B

**Test Run ID**: 0427B  
**Date**: 2026-04-27  
**Executor**: pmo_test_engineer + integration_qa  
**Test Page**: `Singapore Keppel Project [Test Copy - 0427B]`  
**Notion Page ID**: `34f114fc-090c-81c0-bed2-cc6d81f1ddfd`  
**Asana Project GID**: `1214308816239545`  
**n8n WF-01 Execution ID**: `13762` (triggered at 2026-04-27T13:00:46Z)

---

## 0. PRINCIPLE-002 Pre-flight Compliance

**Result: PASS (at page creation time)**

| Field | Value | Status |
|-------|-------|--------|
| 团队信息维护 | `已维护` | PASS |
| PM邮箱 | `lysanderl@janusd.com` | PASS |
| DE邮箱 | `spikez@janusd.com` | PASS |
| SA邮箱 | `rosaw@janusd.com` | PASS |
| CDE邮箱 | `suzyl@janusd.com` | PASS |

> NOTE: After WF-01 execution, `团队信息维护` was reverted to `未维护` by a side-effect in WF-01's Notion update nodes (`回填注册表链接` and subsequent patch calls). This is a WF-01 bug (see BUG-001 below). The pre-condition was correctly set — the reversion occurs post-initialization, not during the PRINCIPLE-002 check window.

---

## TC-A01 — 项目录入 + WF-01 触发

**Result: PARTIAL-PASS**

- Notion page created at 2026-04-27T12:58Z with all required fields
- PRINCIPLE-002 fields verified immediately after creation: all OK
- WF-01 (exec ID 13762) triggered at 13:00:46Z (2 min 46s after page creation — within 5-min polling window)
- WF-01 status: **success**
- Asana project created: GID `1214308816239545`

**Pass criteria assessment:**
| Criterion | Result |
|-----------|--------|
| WF-01 execution success | PASS |
| Asana project created | PASS |
| Team member count ≥ 2 | **FAIL** — only 1 member added (PM only) |

**BUG-001 (TC-A01 member count)**: `过滤成员GID` node only selected PM GID `1213400756695149`. Workspace lookup correctly returned all 6 members (including DE/SA/CDE), but the filter logic only matched the PM email `lysanderl@janusd.com`. DE (spikez@janusd.com), SA (rosaw@janusd.com), CDE (suzyl@janusd.com) were excluded. Root cause: WF-01 filter logic does not cross-reference DE/SA/CDE email fields from Notion to Asana workspace members.

**BUG-002 (PRINCIPLE-002 reversion)**: WF-01 Notion update nodes (`回填注册表链接`, `回填注册表AsanaGID`, `标记WBS待导入`, `回填根Page链接到注册表`) reset `团队信息维护` to `未维护`. These PATCH calls likely omit the `团队信息维护` field, causing Notion to reset it to the default value. Fix: include `团队信息维护` in the update payload or use a partial update that preserves the field.

---

## TC-A02 — WBS 同步到 Asana

**Result: PASS**

- WBS导入状态 transitioned: `待导入` → `导入中` → `已完成`
- Import completed within ~2 minutes of WF-01 setting status to `待导入`
- Total tasks imported: **111**
  - L2 (sections): 13
  - L3 (tasks): 67
  - L4 (subtasks): 31

| Criterion | Result |
|-----------|--------|
| Task count ≥ 50 | PASS (111 tasks) |
| Notion WBS导入状态 = 已完成 | PASS |

---

## TC-A03 — Notion Hub 页 + GID 回填

**Result: PASS**

| Field | Value | Status |
|-------|-------|--------|
| AsanaGID | `1214308816239545` | PASS |
| 交付Asana项目链接 | `https://app.asana.com/0/1214308816239545/list` | PASS |
| 章程状态 | `草稿` | PASS |
| 项目目录Notion页链接 | `https://www.notion.so/Singapore-Keppel-Project-Test-Copy-0427B-34f114fc090c81a386a8efcba07c93a1` | PASS |

All 4 fields populated. TC-A03: **PASS**

---

## TC-A04 — Webhook 注册

**Result: PASS**

- `POST https://pmo-api.lysander.bond/webhooks/asana/register-team` called
- Response: project `1214308816239545` appeared in `registered` list
- Webhook GID assigned: `1214313918875877`
- Total registered in this call: 2 (0427B + 0427 which was also new)
- Total skipped (already registered): 41

TC-A04: **PASS**

---

## TC-A05 — 幂等验证

**Result: PASS**

- Second call to `register-team` immediately after TC-A04
- Project `1214308816239545` appeared in `skipped` list with `reason: already_exists`
- Total registered: 0 (no duplicate registrations)

TC-A05: **PASS**

---

## TC-A06 — 任务完成 Webhook 通知

**Result: PASS**

- Smoke test webhook sent to `https://n8n.lysander.bond/webhook/wf08-task-completed`
- Payload: event_key=`e2e-0427B-smoke`, task GID `1214144030436659` completed
- HTTP 200 response: `{"ok": true}`

TC-A06: **PASS**

---

## PRINCIPLE-001 — WBS 任务粒度验证

**Result: PASS (with observation)**

| Metric | Value |
|--------|-------|
| Total tasks | 111 |
| L2 sections | 13 |
| L3 tasks | 67 |
| L4 subtasks | 31 |
| L3 with correct L2 parent | 67/67 (100%) |
| L4 with correct L3 parent | 31/31 (100%) |
| Tasks with assignee | 35/111 (31.5%) |
| L3 assigned | 30/67 (44.8%) |
| L4 assigned | 5/31 (16.1%) |
| L2 assigned | 0/13 (expected — sections) |

**Hierarchy correctness**: PASS — all L3 tasks have valid L2 parents, all L4 tasks have valid L3 parents.

**Assignee coverage observation**: 35/111 tasks (31.5%) have assignees. L2 sections are expected to have no assignees (they are containers). Of L3+L4 tasks (98 total), 35 have assignees (35.7%). The unassigned L3/L4 tasks (63) likely correspond to roles not yet mapped to Asana workspace members — this is expected behavior when DE/SA/CDE were not added to the project (linked to BUG-001). Once BUG-001 is fixed and team members are added, assignee coverage should increase significantly.

---

## Suite B — REQ Compliance

| REQ | Description | Result |
|-----|-------------|--------|
| REQ-009 | pmo-api health (wbs_exists, hub_exists, credentials present) | PASS |
| REQ-005 | WF-01 active on n8n | PASS |
| REQ-003 | Notion Registry DB accessible | PASS |
| REQ-004 | Asana PAT valid | PASS |

Suite B: **4/4 PASS**

---

## Bug Summary

| ID | Severity | Component | Description | Impact |
|----|----------|-----------|-------------|--------|
| BUG-001 | P1 | WF-01 `过滤成员GID` | Filter only adds PM to Asana project; DE/SA/CDE excluded despite correct emails in Notion | TC-A01 member count FAIL; downstream assignee coverage reduced |
| BUG-002 | P1 | WF-01 Notion update nodes | Multiple PATCH nodes reset `团队信息维护` to `未维护` post-initialization | PRINCIPLE-002 post-flight check shows `未维护`; misleading state |

---

## Evidence

- n8n WF-01 exec: `13762` (2026-04-27T13:00:46Z, success)
- Notion page: `34f114fc-090c-81c0-bed2-cc6d81f1ddfd`
- Asana project: `1214308816239545`
- Webhook registered: GID `1214313918875877`
- WF-08 smoke test: HTTP 200, `{"ok": true}`

---

## Overall Verdict: PARTIAL PASS

| Category | Result |
|----------|--------|
| Pre-flight (PRINCIPLE-002) | PASS |
| TC-A01 (WF-01 + Asana creation) | PARTIAL (project created, member count = 1 not ≥ 2) |
| TC-A02 (WBS import) | PASS |
| TC-A03 (Notion backfill) | PASS |
| TC-A04 (Webhook register) | PASS |
| TC-A05 (Idempotency) | PASS |
| TC-A06 (WF-08 smoke) | PASS |
| PRINCIPLE-001 (WBS granularity) | PASS |
| Suite B (REQ compliance) | PASS |

**6/7 TCs PASS, 1 PARTIAL. 2 P1 bugs identified (BUG-001, BUG-002). Core pipeline (WBS import, Notion backfill, webhook, idempotency) fully functional. Action required: fix WF-01 member filter logic and Notion update node field preservation.**
