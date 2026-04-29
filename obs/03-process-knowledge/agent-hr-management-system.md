# Agent HR Management System — Synapse v3.0

## Overview

The Agent HR Management System governs the full lifecycle of all AI agents — onboarding, active service, quality assurance, and retirement.

**Core principle**: Every agent must demonstrate specific, measurable capabilities. Vague role descriptions ("项目管理", "知识沉淀") are rejected at intake.

---

## Agent Lifecycle

```
新Agent提案
    ↓
hr_director 入职审批 (role gap validation + overlap check)
    ↓
capability_architect 能力评审 (A/B/C 三级标准)
    ↓ (达到B级以上才通过)
status: probation (2周试用期)
    ↓ (表现合格)
status: active
    ↓ (每周定期审计)
audit_all_agents() — 自动评分 (85/100 通过线)
    ↓ (分数 < 90)
能力升级流程 (限期改进)
    ↓ (持续不合格)
status: inactive → 退役归档
```

---

## Capability Quality Standards

| Grade | Standard | Example |
|-------|----------|---------|
| **A (Target)** | Specific tool/framework + measurable output | "基于 pytest + Playwright 的端到端测试框架搭建：page object model / fixture管理 / CI集成 → 覆盖率报告+失败截图" |
| **B (Minimum)** | Specific methodology/framework named | "SWOT分析、PEST分析、波特五力模型应用，输出结构化战略分析报告" |
| **C (Reject)** | Vague activity description | "项目管理"、"知识沉淀"、"团队协作"、"数据分析" |

All active agents must have B-level capabilities at minimum. A-level is the target standard.

---

## Audit Scoring (85/100 Standard)

`qa_auto_review()` in `hr_base.py` evaluates each agent card across 5 dimensions (20 pts each):

| Dimension | Max | Criteria |
|-----------|-----|---------|
| **Integrity** | 20 | All required fields present and non-empty |
| **Accuracy** | 20 | Capabilities are factually achievable; no hallucinated tools |
| **Consistency** | 20 | specialist_id matches filename; keywords in organization.yaml match summon_keywords |
| **Maintainability** | 20 | Capabilities specific enough to update; role boundaries clear |
| **Compliance** | 20 | No C-level descriptions; status follows lifecycle rules; HR process followed |

**Score thresholds**:
- ≥90 pts → Active status maintained ✅
- 80-89 pts → Improvement required (upgrade to A-level, 1-week deadline)
- 60-79 pts → Failing — immediate revision required
- <60 pts → Severe non-compliance — downgrade to `inactive`

---

## New Agent Onboarding Checklist

- [ ] **Gap justification**: Why is this agent needed? What capability does not exist?
- [ ] **Overlap check**: Jaccard similarity <30% with all existing agents
- [ ] **Card draft**: Use `obs/templates/agent_card_template.yaml`
- [ ] **Capability quality**: All items at B-level or above
- [ ] **hr_director approval**: Role + team placement sign-off
- [ ] **capability_architect sign-off**: Capability quality certification
- [ ] **organization.yaml update**: routing_keywords section updated
- [ ] **Initial status**: `probation` (2-week trial period)
- [ ] **Post-trial review**: `capability_architect` upgrades to `active`

---

## Overlap Detection

`capability_architect` runs Jaccard similarity before approving any new agent:

```python
def jaccard_similarity(keywords_a: set, keywords_b: set) -> float:
    intersection = len(keywords_a & keywords_b)
    union = len(keywords_a | keywords_b)
    return intersection / union if union > 0 else 0.0

# Extract domain + capability keywords from each agent card
# If similarity > 0.30 with any existing active agent → reject or restructure
```

**Policy**: >30% overlap → reject new agent, or restructure both agents' boundaries before approval.

---

## Weekly Audit Protocol

Every Monday, `hr_director` triggers `audit_all_agents()` in `hr_base.py`:

1. Load all YAML cards from `obs/01-team-knowledge/HR/personnel/`
2. Score each card using `qa_auto_review()` (5 dimensions × 20 pts)
3. Generate audit report: scores, flags, improvement recommendations
4. Cards <90 pts → trigger capability upgrade workflow
5. Report summary to Lysander CEO

---

## Retirement Protocol

When an agent is no longer needed or cannot meet quality standards after improvement attempts:

1. `hr_director` marks status: `inactive`
2. Remove agent from `organization.yaml` routing_keywords
3. Archive card to `obs/01-team-knowledge/HR/archive/`
4. Update collaboration references in other agents' cards
5. Log retirement event in `CHANGELOG.md` with date and reason
