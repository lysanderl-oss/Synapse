---
id: academy-index-en-draft
type: navigation
status: draft
lang: en
translation_of: academy-index-zh
version: 0.1
published_at: 2026-04-25
updated_at: 2026-04-25
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [technical_builder, enterprise_decider, team_partner]
stale_after: 2026-10-25
---

# Academy Index (EN draft)

## Structure Notes

The Chinese page is structured as: Hero → Navigation cards (6 sub-pages) → Tier pricing → "What's inside" → Final CTA. The English version preserves this five-block skeleton so the existing Astro layout maps directly when stage 4 lands.

Key reframes:
- Hero pivots from "5分钟拥有" (literal "have in 5 minutes") to a benefits-first framing — readers in English markets respond to "team that ships," not to time-to-clone.
- Navigation card descriptions tightened — Chinese explains *what is in the link*; English signals *what the user will get out of it*.
- Pricing kept verbatim ($0 / $99 / $999) — these are operational numbers, not marketing copy.
- "What's inside" reframed as "What ships in the box" — same content, more concrete metaphor.

## SEO Meta

- **Title**: `Synapse Academy — A Multi-Agent AI Team You Can Run Today`
- **Description** (151 chars): `Get a 44-agent AI team running inside Claude Code. Built on Harness Engineering. Free core, paid evolution, enterprise-ready. Open the box and ship.`
- **Primary keyword**: multi-agent AI team
- **Secondary**: Synapse Academy, Harness Engineering, AI agent framework, Claude Code agents

## Hero

- **Eyebrow**: `Synapse Multi-Agent Academy`
- **Title** (8 words): `An AI team that's already in the room.`
- **Subtitle** (24 words): `Forty-four specialist agents, fourteen ready-to-run skills, four decision tiers. Cloned once, configured in three minutes, working alongside you from the first message.`
- **Stat row**: `44 Agents · 14+ Skills · 4 Decision Tiers`
- **CTA primary**: `Get Synapse Free` → `/en/academy/get-synapse`
- **CTA secondary**: `Read the methodology` → `/en/academy/learn`

## Section A — Choose Your Entry Point

**Eyebrow**: `Academy Navigation`
**Heading**: `Pick where to start.`

Six entry points map to who you are right now:

- **Get Synapse** — Free clone, three-step personalization, working in five minutes. _Free →_
- **Meet the Team** — Forty-four specialists across seven groups, full capability map. _Browse Team →_
- **Skills Library** — Fourteen built-in workflows including `/dispatch` and `/qa-gate`. _See All →_
- **Harness Methodology** — Five core principles. Why `Agent = Model + Harness`. _Start Learning →_
- **Member Dashboard** — Version state, upgrade history, account. _Coming soon →_
- **SCP Course** — Synapse Certified Practitioner badge. Eight-hour curriculum. _Coming soon →_

_(~85 words)_

## Section B — Choose Your Edition

**Eyebrow**: `Pricing`
**Heading**: `Pick the version that matches how you'll use it.`
**Subtitle**: `Free users get a complete snapshot. Evolution users ride the daily release train.`

### Free — $0 forever
A one-time setup, yours to keep:
- Synapse Core v1.0.0 — the full system
- CLAUDE.md plus all 44 agents
- 14+ skill workflows
- Harness Engineering methodology in full
- Every helper script and tool

CTA: `Get it free →`

### Evolution — $99 / month
Recommended for active operators. Everything in Free, plus:
- Daily and weekly Core updates
- First access to new agents as they're released
- Methodology updates as the framework evolves
- One-line upgrade command (just say "upgrade Synapse")
- Weekly evolution report

CTA: `Talk to us →` (mailto)

### Enterprise — $999 / month
Custom-fit for serious teams. Everything in Evolution, plus:
- Industry-specific agent teams built for your domain
- One-on-one Synapse advisory
- Priority access to new capabilities
- Dedicated Slack support channel
- Team training workshop included

CTA: `Talk to us →` (mailto)

_(~155 words)_

## Section C — What Ships in the Box

**Eyebrow**: `What You Get`
**Heading**: `The complete operating system.`

Four assets, fully integrated:

- **Harness Configuration (CLAUDE.md)** — The control center. Defines the CEO execution chain, the four-tier decision system, the dispatch protocol, and cross-session state. The single source of truth for how the system runs.
- **Forty-four AI Specialists** — Seven teams across strategy, R&D, ops, content, growth, intelligence, and HR. Every specialist carries a concrete capability description (B-grade or above) and audits at 90 or higher.
- **14+ Skill Workflows** — One-line triggers for structured work: `/dispatch` for routing, `/qa-gate` for quality, `/retro` for review, `/graphify` for advisor analysis, `/dev-plan` for engineering, and more.
- **HR Engine (`hr_base.py`)** — Auto-scoring (90 to pass), capability grading (A/B/C), onboarding gates, cross-session state tracking. A complete governance layer for an AI team.

_(~170 words)_

## Final CTA

- **Heading**: `Ready? Five minutes from here to a working team.`
- **Subhead**: `Free. Runs locally. No third party touches your data.`
- **CTA primary**: `Get Synapse now →` → `/en/academy/get-synapse`
- **CTA secondary**: `View on GitHub →` → `https://github.com/lysanderl-glitch/synapse`

## Translation Choices

1. **"学院" → "Academy"** (canonical from glossary). "Multi-Agent Academy" reads natural in English; "Multi-Agents Academy" (the literal Chinese) carries an SEO penalty for the redundant plural.

2. **"Synapse Certified Practitioner" framed as a badge, not a certificate** (Decision A). The Chinese page allows ambiguity ("认证课程" = "certification course"). English copy commits explicitly to "SCP badge" to avoid implying accredited certification.

3. **"5分钟拥有" → "An AI team that's already in the room."** Direct translation ("have an AI team in 5 minutes") is a marketing cliché in English and triggers AI-tool fatigue in technical readers. The reframe leans on presence and inevitability — same urgency, different idiom.

## Open Questions

- **Janus Digital naming** — Inherits from main-site five-page Open Question #4. Academy index doesn't reference Janus directly, but the trust model echoes through. Resolve at site level.
- **SCP Badge naming** — Confirm "Synapse Certified Practitioner badge" everywhere it appears (academy index, course page, learn page deep-dive section).
- **CTA verb consistency** — "Get Synapse Free" vs "Get Started" — current draft uses both depending on context. Style_calibrator pass should pick one primary verb across the seven-page batch.

## QA Self-Check

### Faithfulness — 18/20
- All seven Chinese sections present with equivalent content density.
- Pricing numbers (USD/month) match Chinese page exactly.
- "Coming soon" status preserved for Dashboard and Course cards.
- **Deduction (-2)**: Hero replacement of stat strip ("44 / 14+ / 4级") with prose stat row loses the numeric punch of the Chinese visual treatment. Acceptable for first draft; flag for design review.

### Brand Voice — 18/20
- Specialist, not salesy. No "revolutionary," no "game-changing."
- Concrete numbers replace marketing adjectives.
- Sentence rhythm varies — long-short-long across CTA blocks.
- **Deduction (-2)**: "An AI team that's already in the room" risks reading too clever. Style_calibrator should A/B against a flatter alternative ("Forty-four specialists ready on day one.").

### Clarity — 19/20
- Every section answers "what is this and what's it for?" within the first sentence.
- Pricing tiers self-describe — no jargon required to choose.
- Navigation cards each carry a verb ("Get," "Browse," "See," "Start").
- **Deduction (-1)**: "What ships in the box" metaphor may not survive ESL readers. Worth confirming in next round.

### Style — 18/20
- Lists follow parallel structure (em-dash + concrete asset name + scope).
- No semicolons in marketing copy (per house style).
- All headings under 10 words.
- **Deduction (-2)**: Section A introduces a colon-heavy pattern ("Get Synapse — Free clone, three-step...") that repeats across six items. Could break rhythm with one variant card.

### Compliance — 17/20
- No "guaranteed ROI" claims.
- mailto CTAs correctly formatted.
- "Free forever" is supported by GitHub repo public-license commitment.
- **Deduction (-3)**: "An AI team already in the room" implies persistence/availability — needs to be hedged ("from the first message" already present, but add a footnote on session vs persistent state in next pass). Also, "44 specialists at 90+" requires the audit dataset to be inspectable; link to /en/academy/team to satisfy.

### Total: 90/100 — PASS
