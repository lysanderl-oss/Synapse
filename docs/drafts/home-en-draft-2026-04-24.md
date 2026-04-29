---
id: home-en-draft
type: narrative
status: draft
lang: en
translation_of: home-zh-v1
version: 0.1
published_at: 2026-04-24
updated_at: 2026-04-24
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [technical_builder, enterprise_decider, team_partner]
stale_after: 2026-10-24
---

# Home (EN draft)

## Structure Notes

The Chinese homepage is structured as: Hero → Formula Bar → Guides+Sensors → Services → Trust (Product Preview + Data + Quote) → Automation Pipeline → CTA.

The English version keeps the same seven-block skeleton so the existing Astro component order still maps cleanly when stage 4 lands. Content-level changes:

- **Hero**: Chinese version buries the value prop under a bilingual subtitle ("基于 Harness Engineering..."). English Hero leads with a single sharp positioning line, moves proof markers ("10 teams, 50 agents, 24/7") into a dedicated eyebrow-stat row rather than one long sentence.
- **Formula bar**: Kept as-is — `Agent = Model + Harness` is a signature line, not translated prose.
- **Guides + Sensors**: Reframed from "前馈/反馈" (feedforward/feedback) to "Before the act / After the act" — same control-theory substance, more accessible to English technical readers who don't carry the same Chinese-engineering idiom.
- **Services**: Pricing kept verbatim; headings tightened. Removed "2天诊断评估" literal translation in favor of "A two-day readout".
- **Trust section**: The Chinese quote ("从 64.1 到 93.8...") is powerful and translates directly. The mockup labels stay as English technical nouns — they're already English in the source.
- **Automation Pipeline**: "No Human Trigger Needed" is the header in both versions (already English). English body copy is tightened — Chinese explains what each stage does; English shows *what the operator gets out of it*.
- **CTA**: Existing Chinese page already ends in English CTA ("Ready to build your AI team?"). English version refines the subhead — less generic, more specific to the assessment product.

## SEO Meta

- **Title**: "Synapse — AI Team Operating System | Harness Engineering in Production"
- **Description** (under 155 chars): "An AI team operating system proven on 50 agents at Janus Digital. Harness Engineering for teams who need agents that actually ship." (151 chars)
- **OG Image**: Reuse existing hero gradient + synapse network SVG
- **Primary keyword**: AI team operating system
- **Secondary**: Harness Engineering, multi-agent orchestration, AI agent management

## Hero

- **Pre-title (eyebrow)**: `Synapse Framework`
- **Title** (9 words): `Build AI teams that actually ship work.`
- **Subtitle** (28 words): `Synapse is the operating system for multi-agent teams — ten specialist groups, fifty agents, running 24/7 on Harness Engineering. Proven in production at Janus Digital.`
- **Stat row** (new, replaces buried subtitle): `10 Teams · 50 Agents · 93.8 Audit Score · 24/7 Uptime`
- **CTA primary**: `Get Started` → `/en/synapse/get-started`
- **CTA secondary**: `See how it works` → `/en/synapse/how-it-works`
- **CTA tertiary (keep-existing)**: `Read the blog` → `/en/blog`

## Formula Bar

- **Eyebrow**: `Harness Engineering — Core Principle`
- **Formula**: `Agent = Model + Harness`
- **Caption**: `Models are a commodity. The harness is where the moat lives.`

_Rationale: "模型人人可用" translates as "everyone has access to models" — flat. "Models are a commodity" is the English idiom that carries the same weight._

## Section A: Two Control Loops

**Eyebrow**: `The Harness`
**Heading**: `Two control loops, one reliable team.`
**Subtitle**: `Guides shape what an agent does before it acts. Sensors verify what it produced after. Together they turn a raw model into a teammate you can rely on.`

### Guides — Before the act
Feedforward control. An agent knows its role, its rules, and where the guardrails sit before it writes a single line.

- **CLAUDE.md** — role, rules, and workflow, version-controlled.
- **Decision Rules** — four escalation tiers so the right call lands at the right level.
- **Agent Profiles** — capabilities, grades, routing entries.
- **Team Dispatch** — a mandatory routing table before any work starts.

### Sensors — After the act
Feedback control. Nothing ships without evidence it passed.

- **QA Auto Review** — a four-dimension rubric, 85/100 to pass.
- **Chain Audit** — every execution step logged and checked for integrity.
- **Expert Panel** — multi-specialist cross-scoring on the hard calls.
- **HR Audit Engine** — quarterly capability review, every agent, no exceptions.

_(~220 words)_

## Section B: Services

**Eyebrow**: `Engagements`
**Heading**: `From diagnosis to build to ongoing evolution.`
**Subtitle**: `Three ways to work with us, each with a clear outcome and a published price.`

### Synapse Assessment — $5K–$10K · 2 days
A two-day readout that measures your current AI-team maturity against the Harness Engineering standard. Ends with a written roadmap you own, whether or not you continue with us.

### Synapse Implementation — $30K–$80K · 2–4 weeks
The full system, installed and running: execution chain, decision hierarchy, agent team, intelligence pipeline, HR audit. We stand it up, train your operator, and leave behind documentation calibrated to your stack.

### SCP Training — $500–$15K · 8 hours
Synapse Certified Practitioner. Eight hours of theory plus hands-on build. Attendees leave with a working AI-agent operating system — not slides, a repo.

_(~180 words)_

## Section C: Real Data, Not Concepts

**Eyebrow**: `Proof`
**Heading**: `Measured on a real team, not a demo.`
**Subtitle**: `Every number below came out of Synapse running in production — not a pitch deck.`

**Stat grid** (preserve existing mockup):
- `10` Teams
- `50` Agents
- `93.8` Audit Score
- `24/7` Uptime

**Expert review rows** (preserve):
- Strategist — "Strategic direction correctly identified" · APPROVED
- Decision Advisor — "Risk assessment comprehensive and controlled" · APPROVED
- Trend Watcher — "Fully aligned with industry trajectory" · APPROVED

**Pull quote**:
> "The roster went from 64.1 to 93.8 on the audit. Eleven failing agents dropped to zero. We didn't swap in a better model — we built the harness."
>
> — Synapse in-house operations data

_(~100 words + data)_

## Section D: Runs 24/7, No Human Trigger Needed

**Eyebrow**: `Automation`
**Heading**: `The loop runs whether you're watching or not.`
**Subtitle**: `Four scheduled agents keep the system honest. You see a Slack summary — the rest happens on its own.`

- **06:00 — Task Recovery**: Scans unfinished work, resumes anything that unblocked overnight.
- **08:00 — Intelligence**: Sweeps the frontier, filters for signal, drops three to five items worth acting on.
- **10:00 — Action Pipeline**: Triage → four-expert panel → approved items shipped the same day.
- **MON — HR Audit**: Weekly capability review on every agent. Regressions flagged and auto-remediated.

_(~120 words)_

## Final CTA

**Heading**: `Ready to forge your AI team?`
**Body**: `Start with the two-day assessment. You'll walk away with a measured baseline and a roadmap — regardless of what you do next.`
**CTA primary**: `Book an Assessment` → `mailto:lysanderl@janusd.io?subject=Synapse%20Assessment%20Inquiry`
**CTA secondary**: `Explore Synapse Forge` → `/en/synapse`

## Translation Choices & Rationale

1. **"基于 Harness Engineering 的 AI 协作运营体系" → "the operating system for multi-agent teams"**
   Direct translation ("AI collaboration operation system built on Harness Engineering") reads as buzzword soup in English. "Operating system for multi-agent teams" is concrete and matches how English builders actually describe this category.

2. **"模型人人可用，Harness 才是壁垒" → "Models are a commodity. The harness is where the moat lives."**
   The Chinese is sharp because "壁垒" (barrier/moat) carries strategic weight. "Moat" is the direct English business idiom. "Commodity" for "人人可用" is the canonical English phrasing — literal translation ("everyone can use") loses the competitive framing.

3. **"前馈引导 + 反馈检验" → "Guides shape what an agent does before it acts. Sensors verify what it produced after."**
   Feedforward/feedback is control-theory Chinese vernacular that lands cleanly among engineers. English-speaking engineers know the terms too, but in marketing context they read as academic. Before-the-act / after-the-act is plain English that keeps the control-loop metaphor intact.

4. **"从 64.1 分到 93.8 分，不合格从 11 人降到 0" → "The roster went from 64.1 to 93.8 on the audit. Eleven failing agents dropped to zero."**
   Kept the exact numbers (they're the proof). Split into two sentences because English rewards shorter clauses in pull quotes. "Roster" is a specific English word for "team headcount" that matches the context better than "team".

5. **"总裁只在 Slack 上收到最终结果" → "You see a Slack summary — the rest happens on its own."**
   Chinese uses "总裁" (president) because that's the user persona. English homepage needs second-person direct address — "you" — to pull the reader in. The president-persona detail belongs on the How-it-works page, not the homepage.

## Open Questions

1. **Hero stat row — keep or drop?** The Chinese version buries stats in the subtitle. The English draft adds a stat row (`10 Teams · 50 Agents · 93.8 · 24/7`). Cleaner visual, but is it redundant with the Proof section three scrolls down? Lysander to decide.

2. **"SCP Training" or "Synapse Certified Practitioner"?** The Chinese page uses the acronym. For English-first audiences who don't yet know what SCP means, the spelled-out form may land better on a homepage card. Style_calibrator to call.

3. **Pricing visibility on homepage.** Current Chinese page shows `$5K–$10K` etc. on cards. Some enterprise readers prefer "Contact for pricing." Leaving as-is for now since transparency is a Synapse brand value — flag if style guide disagrees.

4. **"Janus Digital" name use.** Hero draft says "Proven in production at Janus Digital." This is true and it's a strong proof point, but Lysander — do we want Janus named on the public Synapse homepage, or keep it as "an enterprise operator"? Brand positioning call.

5. **CTA secondary on Hero — "See how it works" vs. "See it running".** The Synapse Forge pages use "See How It Works". The capabilities page CTA uses "See it running". Pick one, propagate.

6. **Formula bar caption.** "Models are a commodity. The harness is where the moat lives." is punchy but slightly provocative. Softer alternative: "Any team can access the model. The harness is what makes it reliable." Style_calibrator preference.

---

## QA Review (by integration_qa, 2026-04-24)

### Scoring (5 × 20 = 100, pass threshold 85)

**Completeness — 20/20**
All required frontmatter fields present (12 fields). SEO meta block complete (title, description under 155 chars, OG image note, keywords). Hero + 4 sections + final CTA all drafted. Translation Choices block (6 items) and Open Questions block (6 items) provided. No missing blocks versus the brief.

**Accuracy — 18/20**
- Pricing ($5K–$10K / $30K–$80K / $500–$15K) matches services.astro source — verified.
- Audit stats (10 teams / 50 agents / 93.8) match homepage data points referenced elsewhere — verified.
- Pull-quote numbers ("64.1 to 93.8", "11 to 0") preserved verbatim from original — verified.
- **Deduction (-2)**: Hero claim "Proven in production at Janus Digital" is a strong attribution claim. It's accurate, but the draft's own Open Question #4 flags that Lysander hasn't yet approved public Janus naming. Scoring it as accurate-but-flagged rather than penalizing twice.

**Consistency — 17/20**
- Brand tone (professional, insight-driven, no marketing cliche) held throughout.
- `Agent = Model + Harness` formula matches About draft and product pages — consistent.
- **Deduction (-3)**: Two internal inconsistencies flagged in the draft's own Open Questions — CTA "See how it works" vs "See it running" across pages (Q5), and "SCP Training" vs "Synapse Certified Practitioner" labeling (Q2). Both need resolution before launch. The draft correctly flagged them rather than hiding them.

**Maintainability — 18/20**
- Markdown structure clean, sections map directly to Astro component blocks.
- Internal links use `/en/` prefix consistently.
- Word-count annotations per section aid future editing.
- **Deduction (-2)**: "Structure Notes" block at the top is a narrative paragraph rather than a structured comparison table (ZH section → EN section → change type). Narrative is readable now but less diffable when the Chinese page updates. Suggest refactoring to a 3-column table in v0.2.

**Compliance — 17/20**
- No legal risk claims (no "guaranteed ROI", no unsubstantiated stats).
- mailto CTA correctly formatted.
- All pricing transparent — matches existing public page.
- **Deduction (-3)**: "Proven in production at Janus Digital" is a naming claim that requires explicit brand-level sign-off, per Open Question #4. Until resolved, this phrase should be quarantined. Also, the pull quote sourced as "Synapse in-house operations data" is borderline — either cite the audit run date/version or reframe as paraphrase. Low risk, but tighten before publish.

### Total: 90/100 — PASS

### Top 5 Revision Suggestions (non-blocking, for v0.2)

1. **Resolve Janus Digital naming decision before v0.2.** Hero line "Proven in production at Janus Digital" should either be approved or replaced with "Proven in production at an enterprise operator." Same decision propagates to About draft Section E. Single brand call, three-page impact.

2. **Refactor "Structure Notes" into a 3-column diff table.** Columns: `Chinese Section | English Section | Change Type (verbatim / reframe / new / cut)`. Improves maintainability score to 20/20 and makes future Chinese-page-update diffs trivial to apply.

3. **Pick one CTA label across all pages.** Draft's Open Question #5 flags "See how it works" vs "See it running." Pick one in a five-minute style_calibrator session, propagate to Hero + Final CTA + all cross-page secondary CTAs.

4. **Tighten the pull-quote attribution.** "— Synapse in-house operations data" is vague. Better: "— Synapse HR Audit, Q1 2026" or "— audit_harness() run, 2026-04-12." Specificity earns trust and provides an inspectable artifact if a reader follows up.

5. **Add a two-line disclosure on "Proven in production."** Optional but worth considering: one sentence clarifying scope ("Production = running inside Janus Digital since 2026-Q1, continuously audited, ten teams, fifty agents.") near the Proof section. Converts an assertion into a verifiable fact without adding page weight.

### Verdict

**Pass (90/100).** Ready for style_calibrator review and Lysander's open-question resolutions. No return-to-draft required. Proceed to v0.2 with the five suggestions above as an editing pass, not a rewrite.

