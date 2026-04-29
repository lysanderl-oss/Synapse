---
id: academy-learn-en-draft
type: methodology
status: draft
lang: en
translation_of: academy-learn-zh
version: 0.1
published_at: 2026-04-25
updated_at: 2026-04-25
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [technical_builder, enterprise_decider, methodology_reader]
stale_after: 2026-10-25
---

# Academy / Learn — Harness Engineering (EN draft)

## Structure Notes

The Chinese page is structured as: Hero → Core Formula → "Why Harness Engineering?" (problem/solution comparison) → Five Core Principles → "Synapse as implementation" → Deep-dive links → Bottom navigation. The English version preserves this seven-block skeleton.

Key reframes:
- "前馈/反馈" (feedforward/feedback) → "before-the-act / after-the-act." Same control-theory concept, more accessible to English technical readers without classical-control background.
- "为什么AI不遵守规则" → "Why AI agents drift." Drift is the right term in the LLM-ops literature; saves a paragraph of exposition.
- Core formula (`Agent = Model + Harness`) kept verbatim — signature line.
- Principle headlines reframed from explanatory phrases ("Guides+Sensors双保险") to declarative claims ("Two control loops, never one").

## SEO Meta

- **Title**: `Harness Engineering — Why AI Agents Drift, and How to Fix It`
- **Description** (149 chars): `The methodology behind Synapse. Five principles for building multi-agent systems that ship reliable work. Read the framework, then run it.`
- **Primary keyword**: Harness Engineering
- **Secondary**: AI agent reliability, multi-agent methodology, Agent operating system, AI agent drift

## Hero

- **Eyebrow**: `Methodology`
- **Title** (3 words): `Harness Engineering.`
- **Subtitle** (32 words): `You wrote the rules, but the agent ignores them. You ran the same prompt, but got different results. Harness Engineering is the methodology that fixes both — at the structural level.`
- **Back-link**: `← Academy home`

## Section A — Core Formula

**Eyebrow**: `Core Formula`

> **Agent = Model + Harness**

Models are the ceiling of capability. The harness is what makes capability consistent.

An agent without a harness can be brilliant once and useless the next minute. With a harness, even a modest model delivers reliably. The model is the engine; the harness is everything around it that turns engine into vehicle.

_(~50 words)_

## Section B — Why You Need a Harness

**Eyebrow**: `The Problem`
**Heading**: `Why Harness Engineering exists.`

Two columns, side by side.

### Without a harness
- Rules go in the prompt. The agent reads them once, then drifts.
- The CEO agent ends up doing search, writing code, running analyses — the management role collapses into the worker role.
- Same prompt, different answer every session.
- Each new agent makes the system more chaotic, not more capable.
- Switch models and you start from zero.

### With a harness
- Execution steps have hard checkpoints. Skipping is not a soft failure — it's a logged violation.
- The CEO orchestrates. Specialists execute. Roles stay separate.
- Structured workflows produce repeatable outcomes.
- Teams scale because every agent passes the same audit standard.
- The harness travels. Capability accumulates across model upgrades.

_(~150 words)_

## Section C — Five Core Principles

**Heading**: `The five principles of Harness Engineering.`

### 1. Two control loops, never one.
Feedforward (Guides) tells the agent what to do before it acts. Feedback (Sensors) verifies what got done after. Guides alone drift over time. Sensors alone catch problems too late. Together they keep the system on rails.

> Example: Guide says "every reply must output a dispatch table first." Sensor checks "did a dispatch record actually get logged?" Mismatch triggers a violation entry.

### 2. The execution chain doesn't bend.
Every task moves through a fixed sequence: receive goal → tier → propose → dispatch → execute → QA → deliver. Skipping a step is structural failure. The harness defines checkpoints; checkpoints don't accept "this one didn't need it."

> Sequence: ① tier → ② dispatch (mandatory) → ③ execute → ④ QA (mandatory) → ⑤ deliver

### 3. Roles separate, routing decides.
Management roles never execute. Execution roles never manage. Routing rules send each task to the most capable specialist, not the most convenient one.

> Example: code → `harness_engineer` or `ai_systems_dev`. Strategy → `strategist` or `decision_advisor`.

### 4. Four decision tiers.
L1 auto-execute → L2 expert review → L3 CEO call → L4 escalate to operator. Specialists go before the CEO. The CEO goes before the operator. The operator should be guessing far less than 5 percent of the time.

> L4 triggers: external contracts, budgets above $1M-equivalent, existential decisions, operator-flagged items.

### 5. Capability is auditable.
Every agent has an explicit capability description (B-grade or above: must reference a methodology). Auto-scoring runs at 90 to pass. Below the line, the agent's capability gets upgraded — not the score.

> A-grade: "E2E testing framework using pytest plus Playwright." C-grade (failing): "testing" or "quality management."

_(~340 words)_

## Section D — Synapse as Implementation

**Eyebrow**: `Implementation`
**Heading**: `Synapse is Harness Engineering, made operational.`

Synapse isn't a rules document. It's the five principles built into a working multi-agent team:

- **CLAUDE.md** is the harness configuration — Guides, Sensors, and constraints, all in one file.
- **`organization.yaml`** defines roles and routing rules.
- **`hr_base.py`** is the capability-audit engine (90-or-better passing line).
- **`decision_rules.yaml`** encodes the four-tier decision system.
- **The 14 Skills** are execution-chain checkpoints, made concrete and triggerable.
- **`evolution_engine`** closes the self-improvement loop.

Read it as a methodology, then clone the repo to see exactly how each principle compiles into a file.

_(~120 words)_

## Section E — Go Deeper

**Heading**: `Continue learning.`

Two further entry points:

- **Harness Engineering Complete Guide** — A long-form essay that walks through all five principles with implementation cases. _Blog post →_ → `/en/blog/harness-engineering-guide`
- **SCP Badge Course** — Eight-hour curriculum with four hands-on labs. Earn the Synapse Certified Practitioner badge. _Training →_ → `/en/training`

## Final CTA / Bottom Navigation

- **Back-link**: `← Back to Academy`
- **Forward link**: `Get Synapse now →` → `/en/academy/get-synapse`

## Translation Choices

1. **"前馈/反馈" → "before-the-act / after-the-act"** instead of literal "feedforward/feedback." The Chinese terms carry classical-control engineering weight that older Chinese technical readers recognize instantly. English readers — even technical ones — split into camps: control-systems folks know "feedforward/feedback," but software engineers don't always. The reframe is colloquial enough to land without losing the substance.

2. **"AI不遵守规则" → "agents drift."** "Drift" is the canonical term in LLM-ops and Anthropic-adjacent literature for the phenomenon of agents diverging from instructions over a session or across runs. Using it signals to readers that this page belongs to that conversation.

3. **"四级决策体系" → "four decision tiers."** Direct translation "four-level decision system" is technically correct but reads as bureaucratic. "Tiers" implies hierarchy without sounding like a corporate org chart. The L1-L4 abbreviations match the existing in-code labels.

## Open Questions

- **Diagram inclusion** — Chinese page has no diagrams; principles are explained in prose blocks. English version inherits prose-only. Consider commissioning one diagram for the execution-chain sequence (Principle 2) and one for the four-tier escalation (Principle 4) for v0.2 — these two are the ones readers most often ask to see.
- **"L4 triggers" budget threshold** — Chinese page says "预算 > 100万" (1M RMB-equivalent). English draft says "budgets above $1M-equivalent." Confirm whether public-facing copy should use a USD-fixed number or maintain "$1M-equivalent" hedge.
- **SCP Badge link** — Section E links to `/en/training`. Confirm this route exists in the English-site Astro config; alternative is `/en/academy/course`.

## QA Self-Check

### Faithfulness — 18/20
- All five blocks of the Chinese page present in same order.
- Five principles preserved 1:1, with original examples retained.
- Six implementation files referenced in Section D match the Chinese source.
- **Deduction (-2)**: Section B's "five points each" parallel structure was retained, but the Chinese version uses "❌/✅" emoji headers. English draft replaced with prose section headings. Visually less punchy; substantively identical. Confirm with style_calibrator.

### Brand Voice — 19/20
- Methodology tone — confident, declarative, no hedging.
- "The harness travels" and "the harness doesn't bend" are signature lines, useable as pull-quotes.
- Examples concrete, not abstract.
- **Deduction (-1)**: Hero's three opening sentences ("You wrote the rules, but the agent ignores them...") leans into a problem-agitation rhetorical pattern that's slightly sales-adjacent. Hold for now; revisit if it tests cliché.

### Clarity — 19/20
- Each principle is one declarative headline plus one paragraph plus one example block.
- "L1 auto-execute → L2 expert review..." sequence shown linearly.
- Section D maps abstract principle to concrete file — closes the loop.
- **Deduction (-1)**: Principle 5's A-grade vs C-grade example is excellent but assumes the reader knows what an "audit score of 90" means in this context. One sentence linking to `hr_base.py` documentation would close the gap.

### Style — 19/20
- Headlines short (3–8 words). Bodies concise (40–60 words per principle).
- Em-dashes for definition and parallel structure.
- Code-style labels (`organization.yaml`, `hr_base.py`) consistent with prior drafts.
- **Deduction (-1)**: Quote blocks under each principle vary in length (one-line vs multi-line). Standardize on one-line for visual rhythm.

### Compliance — 18/20
- "Below the line, the agent's capability gets upgraded — not the score" is a strong claim about the system's behavior. True per the design, but worth a footnote linking to the audit pipeline.
- "Specialists go before the CEO" — clear and accurate.
- **Deduction (-2)**: L4 budget threshold needs to lock in either a USD-fixed number or an "equivalent" hedge to avoid drift across markets. Open Question #2 calls this out.

### Total: 93/100 — PASS
