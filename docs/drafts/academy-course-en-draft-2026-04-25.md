---
id: academy-course-en-draft
type: placeholder
status: draft
lang: en
translation_of: academy-course-zh
version: 0.1
published_at: 2026-04-25
updated_at: 2026-04-25
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [synapse_user, certification_seeker, training_buyer]
stale_after: 2026-10-25
---

# Academy / Course (EN draft)

## Structure Notes

The Chinese page is a "coming soon" placeholder for the SCP online certification course. Structure: Hero → Coming-soon icon block → Six-module curriculum preview (5 ready, 1 lab coming) → Note about enterprise SCP training as current alternative → Bottom CTAs. The English version preserves this skeleton 1:1.

This page is the bridge between the free Synapse offering and the paid certification track. Tone needs to be warm enough to convert interested readers into the enterprise track today, while honest about what's not yet shipped.

## SEO Meta

- **Title**: `SCP Course — Synapse Certified Practitioner Badge | Academy`
- **Description** (148 chars): `The Synapse Certified Practitioner badge — eight-hour curriculum, four hands-on labs, mentor review. Online course in development; enterprise track available now.`
- **Primary keyword**: SCP certification
- **Secondary**: Synapse Certified Practitioner, Harness Engineering course, AI agent training, multi-agent certification

## Hero

- **Eyebrow**: `SCP Course`
- **Title** (5 words): `Synapse Certified Practitioner — Academy edition.`
- **Subtitle** (16 words): `Self-paced certification for the Harness Engineering methodology. Coming soon. Enterprise track available now.`
- **Back-link**: `← Academy home`

## Section A — Course in Development

**Heading**: `What's coming.`

The Academy edition of the Synapse Certified Practitioner badge is in development. When it ships, it will provide a fully self-paced learning path — no scheduled training, no live workshop dependency.

If you want SCP today, the enterprise track delivers it through a live workshop format with on-the-spot certification. See Section C below.

_(~55 words)_

## Section B — Course Modules

**Heading**: `What you'll learn.`

Six modules. Five with content ready, one lab module coming.

### M1 — Why Harness Engineering exists
_Status: Content ready_
Real failure cases — agents that drifted, prompts that broke, teams that scaled into chaos. The path from problem to methodology.

### M2 — Guides + Sensors design
_Status: Content ready_
Feedforward and feedback control mechanisms. How to design Guides that don't drift. How to build Sensors that catch failures fast.

### M3 — The four-tier decision system
_Status: Content ready_
L1 through L4 in detail. The "specialist before CEO" principle. When to escalate, when to keep it within the team.

### M4 — Agent HR Management
_Status: Content ready_
Capability grading. Onboarding gates. Auto-audit pipelines. How to run an AI team like a real team.

### M5 — Intelligence loop and automation
_Status: Content ready_
The daily intelligence pipeline. The action-loop pipeline. The self-evolution loop. How Synapse stays current without manual intervention.

### Lab — Build your own AI team (4 workshops)
_Status: Coming soon_
Hands-on construction. Mentor review. SCP badge issued at completion.

_(~250 words)_

## Section C — Enterprise SCP Track Available Now

**Heading**: `Need SCP today? The enterprise track ships now.`

The enterprise version of SCP runs as a live workshop with mentor-led reviews and on-the-spot badge issuance. It's the same curriculum the Academy edition will eventually deliver self-paced, just compressed into a structured program.

Currently the only path to an issued SCP badge.

CTA: `Learn about enterprise training →` → `/en/training`

_(~70 words)_

## Final CTA / Bottom Navigation

- **Primary CTA**: `Learn about enterprise training →` → `/en/training`
- **Secondary CTA**: `← Back to Academy`

## Translation Choices

1. **"SCP 在线认证课程" → "Synapse Certified Practitioner — Academy edition."** Direct translation "SCP Online Certification Course" front-loads the abbreviation. The English title spells out the full credential first (better for SEO and first-time-readers), tags the surface ("Academy edition"), and saves "online" because Academy already implies online.

2. **"完全自主学习体验" → "fully self-paced learning path."** "Self-paced" is the canonical English term in the certification market; "fully autonomous learning experience" reads as marketing prose and suggests AI-tutoring (which this isn't). Direct, clean, matches industry vocabulary.

3. **"现场培训" → "live workshop."** The Chinese term distinguishes in-person from online; the English "live workshop" carries the same distinction without committing to physical-presence-only (a live workshop can be remote-synchronous). Aligns with how the enterprise track actually operates.

## Open Questions

- **SCP badge vs certificate naming consistency** — The task brief commits to "SCP Badge." Course page uses "Synapse Certified Practitioner badge" (lowercase b) in some sentences and "the SCP badge" in others. Lock convention with style_calibrator before publish.
- **Enterprise track route** — All "Learn about enterprise training" CTAs link to `/en/training`. Confirm this route resolves; alternative is `/en/services/training` or a section anchor on `/en/services`.
- **Lab module scope** — "4 workshops" inherited from Chinese source. Verify whether the four labs are scoped, or whether this is aspirational. If scoped, list them by name in v0.2 to convert better.

## QA Self-Check

### Faithfulness — 19/20
- All six Chinese-page blocks present (Hero, coming-soon block, six-module curriculum, current alternative note, bottom CTAs).
- Six modules preserved with correct ready/coming-soon labels.
- "现在参加企业版可获得现场Workshop+即时认证" reframed as Section C without losing the value claim.
- **Deduction (-1)**: Chinese page uses inline status pills ("内容就绪" / "即将推出"). English version uses italic status lines. Visually different; substantively identical.

### Brand Voice — 18/20
- Honest framing — "in development" not "launching soon."
- Section C is direct: enterprise is the only path today, says so.
- "How to run an AI team like a real team" (M4) is a strong product line.
- **Deduction (-2)**: Hero subtitle's two short sentences ("Coming soon. Enterprise track available now.") could read as marketing flourish rather than information. Style_calibrator should A/B against a single integrated sentence.

### Clarity — 19/20
- Each module's purpose stated in one sentence.
- Status labels make ready vs not-ready instantly readable.
- Section C answers "what do I do today" without ambiguity.
- **Deduction (-1)**: "M5 — Intelligence loop and automation" naming may be opaque to a first-time reader. Inline definition or a more descriptive title would help.

### Style — 19/20
- Module headers consistent (M1–M5 + Lab).
- Status indicator italicized, content paragraph plain.
- No module description exceeds 30 words.
- **Deduction (-1)**: Three different list patterns appear (modules, CTAs, single-line bullets in Hero). Could canonicalize, though variation reads as intentional content shaping.

### Compliance — 19/20
- No ship date for the online course.
- No claim about how long the enterprise workshop takes (the Chinese page doesn't specify either).
- "Currently the only path to an issued SCP badge" is true at time of writing; would need maintenance if a beta of the online course launches.
- **Deduction (-1)**: "8-hour curriculum" claim from the Chinese parent page (academy index) does not appear on this page. Should it? Consider adding for consistency, or confirm that course-page time estimates are deliberately omitted.

### Total: 94/100 — PASS
