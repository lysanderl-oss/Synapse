---
id: academy-skills-en-draft
type: directory
status: draft
lang: en
translation_of: academy-skills-zh
version: 0.1
published_at: 2026-04-25
updated_at: 2026-04-25
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [technical_builder, claude_code_user]
stale_after: 2026-10-25
---

# Academy / Skills (EN draft)

## Structure Notes

The Chinese page is structured as: Hero → "How it works" example → 14-skill grid → Custom-skill creation note → Bottom navigation. The English version preserves this skeleton 1:1.

Key decisions:
- **Skill commands stay as-is** (`/dispatch`, `/qa-gate`, etc.) — these are functional triggers, not localized strings.
- **Skill names translated to imperative or noun-phrase form** (e.g. "任务派单" → "Dispatch," not "Task Dispatch"). Shorter, punchier, matches the slash-command verb feel.
- **Skill descriptions reframed** — Chinese tends to lead with "做什么" (what it does); English leads with the user-facing outcome ("Output: ..." or "Triggers: ...").
- **Tag categories preserved** — Core, Decision, R&D, Content, Intel, Knowledge, Management.

## SEO Meta

- **Title**: `Skills Library — 14 Built-in Workflows | Synapse Academy`
- **Description** (152 chars): `Fourteen ready-to-run skill workflows for Synapse. /dispatch for routing, /qa-gate for quality, and twelve more. One slash command, structured AI execution.`
- **Primary keyword**: Synapse skills
- **Secondary**: Claude Code slash commands, AI workflow library, multi-agent skills

## Hero

- **Eyebrow**: `Skills Library`
- **Title** (4 words): `Fourteen workflows. One command each.`
- **Subtitle** (16 words): `Built-in slash commands that trigger structured execution. No prompt engineering, no manual orchestration. Just type `/`.`
- **Back-link**: `← Academy home`

## Section A — How Skills Work

**Heading**: `What Skills Are`

Skills are structured workflows baked into Synapse. Type `/command-name` in Claude Code, and your AI CEO triggers the matching multi-step execution — no need to describe each step yourself.

### Example: triggering a dispatch

```
# What you type:
You: /dispatch analyze competitors and write me a report

# What Lysander CEO does automatically:
→ execution_auditor tiers the task (M-grade)
→ strategist + relation_discovery split the analysis
→ knowledge_engineer assembles the report
→ integration_qa verifies quality ✓
```

One slash command, four specialists coordinated, structured output. That's a Skill.

_(~85 words including code block)_

## Section B — The 14 Built-in Skills

Grid of fourteen skills, organized by tag.

### Core (3 skills)

**`/dispatch` — Dispatch**
_Tag: Core_
Structured task decomposition and team routing. Input a goal, output a dispatch table with specialist assignments, deliverables, and acceptance criteria. Guarantees execution-chain step ② never breaks.

**`/qa-gate` — QA Gate**
_Tag: Core_
Runs `qa_auto_review()`. Auto-scoring (≥3.5 to pass), YAML validation, execution-chain integrity check. Mandatory step ③ enforcement.

**`/synapse` — System Upgrade**
_Tag: Core_
The Synapse Upgrade Protocol: check remote version → show changelog → confirm with operator → upgrade Core → QA verify → done.

### Decision (1 skill)

**`/graphify` — Advisor Analysis**
_Tag: Decision_
Convenes the Graphify Advisors (six specialists) on complex problems. Outputs structured decision recommendations with risk assessment and confidence scoring.

### R&D (5 skills)

**`/dev-plan` — Development Plan**
_Tag: R&D_
R&D team produces a technical proposal: architecture design, task decomposition, risk identification, effort estimate. Output is an executable development plan document.

**`/dev-qa` — Code QA Review**
_Tag: R&D_
QA Engineer plus Tech Lead conduct multi-dimensional code review: functional correctness, security, performance, maintainability — each dimension scored.

**`/dev-review` — Code Review**
_Tag: R&D_
Structured code review pipeline. Output: issue list, improvement recommendations, severity classification.

**`/dev-secure` — Security Audit**
_Tag: R&D_
Scans code for security vulnerabilities (OWASP Top 10), secret leakage, permission misconfigurations. Output: hardening recommendations.

**`/dev-ship` — Ship & Deploy**
_Tag: R&D_
DevOps Engineer runs the standard release flow: build verify → test → canary → full rollout → monitor confirmation.

### Content (1 skill)

**`/daily-blog` — Daily Blog Post**
_Tag: Content_
Content Ops team takes today's work or intel and produces a publishable technical blog post — SEO-optimized title and meta included.

### Intelligence (1 skill)

**`/intel` — Intelligence Daily**
_Tag: Intel_
Triggers the daily AI-tech intelligence pipeline: frontier search → key-person tracking → gap analysis → Markdown plus HTML report.

### Knowledge (2 skills)

**`/retro` — Retrospective**
_Tag: Knowledge_
Auto-generates session or daily-work retrospective. Surfaces highlights, issues, improvement items. Optional HTML report for the OBS knowledge base.

**`/knowledge` — Knowledge Distillation**
_Tag: Knowledge_
OBS team extracts insights, decisions, and methodologies from the current session and writes them into the matching OBS directory (01–06).

### Management (1 skill)

**`/hr-audit` — HR Audit**
_Tag: Management_
Runs `audit_all_agents()`. Bulk scans every agent's capability description, outputs the list of any falling below 90 for remediation.

_(~520 words across all 14 skill cards)_

## Section C — Build Your Own Skill

**Heading**: `Custom Skills`

Create a folder under `.claude/skills/` and add a `SKILL.md` file describing the trigger conditions and execution steps. That's it — your custom workflow now lives alongside the built-ins.

Reference any existing skill file in the repo for the format. The minimum viable Skill is one trigger condition plus one execution outline; everything else is optional metadata.

_(~55 words)_

## Final CTA / Bottom Navigation

- **Back-link**: `← Back to Academy`
- **Forward link**: `Get Synapse now →` → `/en/academy/get-synapse`

## Translation Choices

1. **"工作流" → "workflows" (not "workflow library" or "process library").** Direct, technical, matches Claude Code's existing developer vocabulary. The Chinese title "Skills 工作流库" became "Skills Library" — drops the redundant "workflow" since the example block clarifies the concept.

2. **Skill names translated as imperative noun phrases, not literal verb-object compounds.** "任务派单" → "Dispatch" (not "Task Dispatch"). "代码评审" → "Code Review." This matches the muscle-memory of Unix-style CLI thinking: short verbs.

3. **"智囊团" carried forward as "Graphify Advisors"** (consistent with team page). Skill `/graphify` keeps its slash name; the description names the team explicitly so a reader who lands directly on this page understands who's being convened.

## Open Questions

- **Skill count consistency** — Hero says "Fourteen workflows"; previous main-site copy may have used "14+ Skills" with a plus sign. Decide between "fourteen" (lock-in claim) and "fourteen plus" (room to grow). Lower-risk: name the exact current count, update at release time.
- **`/synapse` command name** — Reads strangely in the page since "Synapse" is also the product name. Could rename to `/upgrade` for clarity. Flag for harness_engineer review; do not change in this draft.
- **R&D skill naming pattern (`/dev-*`)** — Five skills share the `/dev-` prefix. Some users may expect `/qa-*` or `/sec-*` instead. Acceptable inconsistency for now; revisit when adding the next R&D skill.

## QA Self-Check

### Faithfulness — 19/20
- All 14 skills present in same order as the Chinese source.
- Every command name and tag reproduced exactly.
- "How it works" example block preserved with same `/dispatch` walkthrough.
- **Deduction (-1)**: Custom-skill creation note slightly tightened in English — Chinese reads as a paragraph, English as two crisp sentences. Substance fully preserved.

### Brand Voice — 19/20
- Specialist tone — every skill description names the executing agent or pipeline.
- No "powerful," no "amazing," no "intuitive."
- Em-dashes used to define, never to dramatize.
- **Deduction (-1)**: "Just type `/`" in the subtitle is borderline conversational. Could read as cute. Holds in a developer audience but worth A/B.

### Clarity — 19/20
- Each skill card answers "what it does" + "what it produces" in two sentences max.
- Tag categories explicit at section level — readers can skip sections that don't apply.
- Code block in "How Skills Work" makes the abstraction concrete in 5 lines.
- **Deduction (-1)**: Section B's flat-list structure (one card per skill) is correct for completeness but a quick-reference table would aid scanning. Worth considering for v0.2.

### Style — 19/20
- Skill names bolded with backticks, consistent across all 14 entries.
- Tag line italicized to provide visual hierarchy.
- No skill description exceeds 30 words.
- **Deduction (-1)**: The 14 entries break the audit-table aesthetic from the team page. Worth standardizing on either tables or cards across both directory pages.

### Compliance — 19/20
- No claim about skill effectiveness beyond what the description states.
- All command names verifiable in `.claude/skills/` directory of the repo.
- Custom-skill instruction accurate and verifiable.
- **Deduction (-1)**: "Mandatory step ③ enforcement" for `/qa-gate` is true but uses internal jargon (step numbering). External reader may not know what step ③ is. Inline a one-phrase reminder ("the QA verification step") for self-containment.

### Total: 95/100 — PASS
