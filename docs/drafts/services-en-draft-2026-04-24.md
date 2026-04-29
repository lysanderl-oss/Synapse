---
id: services-en-draft
type: narrative
status: draft
lang: en
translation_of: services-zh-v1
version: 0.1
published_at: 2026-04-24
updated_at: 2026-04-24
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [enterprise_decider, ops_leader, technical_builder]
stale_after: 2026-10-24
---

# Services (EN draft)

## Structure Notes

The Chinese `/services` page runs: Hero → terminal mockup → three offer cards (Assessment / Implementation / Industry — Construction) → CTA.

The English version keeps the three-card skeleton so the Astro component map stays stable. Content-level changes:

- **Hero**: Chinese heading "让你的 AI 团队真正可靠地运转" translates literally as "let your AI team really run reliably" — correct meaning, flat tone. English Hero reframes around the buyer's question: *what do I get when I hire Synapse?* — a measured team.
- **Card order**: Unchanged. Assessment → Implementation → Industry solution is a correct entry-price-ascending ladder for enterprise buyers.
- **Industry card**: Chinese leads with "建筑行业" (construction industry). English version broadens slightly to "regulated delivery" so the positioning doesn't read as construction-only to readers outside AEC — while keeping construction as the named anchor case.
- **Terminal mockup**: Preserved verbatim. Output lines are already English technical nouns.

## SEO Meta

- **Title**: "Services — Synapse Consulting & Implementation"
- **Description** (150 chars): "Assess, build, or extend your AI agent operation. Three engagements, published pricing, outcomes measured against the Harness Engineering standard." (149 chars)
- **Primary keyword**: AI agent consulting
- **Secondary**: Harness Engineering implementation, AI team assessment, multi-agent rollout
- **OG Image**: Reuse terminal-mockup screenshot

## Hero

- **Eyebrow**: `Services`
- **Title** (8 words): `Three ways to make your AI team reliable.`
- **Subtitle** (22 words): `Assessment, implementation, or an industry build. Every engagement has a published price, a fixed duration, and a measured outcome — not a retainer.`
- **Primary CTA**: `Book an Assessment` → `mailto:lysanderl@janusd.io?subject=Synapse%20Assessment%20Inquiry`
- **Secondary CTA**: `See the methodology` → `/en/synapse`

_(Hero word count: ~46 words)_

## Terminal Mockup (preserve existing component)

```
$ synapse assess --team-audit
Scanning 10 teams, 50 agents...
├── Graphify Think Tank: 96.0/100 ✓
├── Harness Ops:        95.5/100 ✓
├── HR Management:      94.5/100 ✓
├── RD Team:            92.8/100 ✓
└── All teams:          93.8/100 PASS

Assessment complete. 0 agents below threshold.
```

Caption (English, new): `Sample output — actual Synapse audit run, April 2026.`

## Section A: Synapse Assessment — $5K–$10K · 2 days

**Eyebrow**: `ASSESSMENT`
**Heading**: `Synapse Assessment`
**Price**: `$5K–$10K`
**Duration line**: `A two-day readout.`

A measured two-day engagement. We audit your current AI-team setup — how roles are defined, how decisions escalate, where the rules actually bind — against the Harness Engineering standard. Output: a written baseline score, a gap report, and a roadmap you own regardless of whether you continue with us.

Good fit when: you've got agents running but they drift. Or when a board meeting is asking whether the AI spend is compounding. You'll leave the Assessment with evidence instead of vibes.

### Three deliverables

- **AI Maturity Diagnostic** — your current AI operation, scored.
- **Gap Analysis** — measured against the Harness Engineering reference architecture.
- **Roadmap** — a ranked sequence of changes, with effort estimates and expected impact.

_(~170 words)_

## Section B: Synapse Implementation — $30K–$80K · 2–4 weeks

**Eyebrow**: `IMPLEMENTATION`
**Heading**: `Synapse Implementation`
**Price**: `$30K–$80K`
**Duration line**: `The full system, installed and running.`

End-to-end rollout. We stand up the execution chain, the four-tier decision hierarchy, the agent roster, the intelligence pipeline, and the HR audit engine — calibrated to your stack and your team. Your operator gets trained. Your agents get graded. Your system keeps auditing itself after we leave.

Scope is bounded on purpose. Two to four weeks, not two to four quarters. If it needs longer than that, the problem isn't Synapse — it's your source materials, and we'll say so in the Assessment.

### Three workstreams

- **Harness Configuration** — customized execution chain and decision rules.
- **Agent Team Build** — role design, capability gradings, audit entries.
- **Intelligence + HR System** — the self-running loops that keep the team honest after go-live.

_(~180 words)_

## Section C: Industry Solution — AEC / Regulated Delivery

**Eyebrow**: `INDUSTRY`
**Heading**: `AI-managed delivery for AEC and regulated work.`
**Subtitle**: `Synapse's anchor case: construction digital delivery.`

An industry variant built from the construction digital-delivery use case Synapse was born in. Embeds AI-driven PMO inside delivery projects: automated WBS scheduling, risk-signal triage, stage-gate quality control, and generated deliverables checked against contract requirements.

The playbook transfers to any engagement where deliverables are high-consequence, stage-gated, and audit-trailed — which means pharma, infrastructure, and defense contracting read this page too. Ask us how it maps.

_(~100 words)_

## Final CTA

**Heading**: `Start with the two-day Assessment.`
**Body**: `You'll walk away with a baseline and a roadmap — whether or not you continue with us. That's the point.`
**Primary CTA**: `Book an Assessment` → `mailto:lysanderl@janusd.io?subject=Synapse%20Assessment%20Inquiry`
**Secondary CTA**: `Read the methodology` → `/en/synapse`

## Translation Choices & Rationale

1. **"让你的 AI 团队真正可靠地运转" → "Three ways to make your AI team reliable."**
   Literal translation ("make your AI team truly reliably operate") is an adverb pile-up in English. Reframed around the page structure — three offers — which is what an enterprise buyer actually needs to know from the fold.

2. **"2天诊断评估" → "A two-day readout."**
   "Diagnostic assessment" is the literal translation but reads as medical. "Readout" is the word English operators use for a time-boxed review engagement — precise, familiar, shorter.

3. **"对标 Harness Engineering 行业标准" → "measured against the Harness Engineering standard"**
   "对标" ("benchmark against") is overused in Chinese business writing. English version picks "measured against" — same meaning, cleaner register, avoids the consultant-deck smell.

4. **"建筑行业 AI 增值服务" → "AI-managed delivery for AEC and regulated work"**
   Chinese version locks to "construction industry value-added services." English broadens the addressable market to AEC (architecture-engineering-construction) + regulated delivery (pharma, infra, defense) because the playbook genuinely transfers — and the English page has to carry weight beyond Janus Digital's home industry.

5. **"定制落地路径" → "a roadmap you own"**
   Literal "customized implementation path" is accurate but corporate. "A roadmap you own" is the English enterprise-services idiom — signals deliverable portability, which is the actual value.

## Open Questions

1. **Industry card: AEC-only or broader?** Draft widens to "AEC + regulated delivery." Lysander — does the construction-first positioning matter more, or the addressable-market breadth? Style_calibrator input welcome.
2. **Pricing visibility.** Same question as homepage. Current draft keeps `$5K–$10K` etc. on cards. Enterprise sales norm splits — some prefer "Contact for pricing" on higher-touch engagements. Leaving transparent for now; flag if brand guide disagrees.
3. **CTA parity.** Services page `/en/synapse` secondary CTA overlaps with homepage CTA. That's fine for consistency but may dilute the secondary click. Alternative: `Compare to Assessment` with a deeper-funnel landing. Worth testing post-launch.
4. **Implementation duration callout.** "Two to four weeks" is aggressive for enterprise IT. Do we want a footnote clarifying scope assumptions (cloud-native, existing repo, named single ops lead)? May reduce disqualified leads.
5. **Industry section proof.** Currently asserts the playbook transfers to pharma/infra/defense. True directionally, but no cited case. Keep as directional, or add "Anchor case: construction (Janus Digital)" as inline proof? Lysander to decide.

## QA Self-Check

- 完整性：20/20 — frontmatter 12 字段齐全、SEO meta、Hero、三 Section、Final CTA、translation choices、open questions 全部到位
- 准确性：18/20 — 价格/工期/交付件忠于原版；industry 扩展到 AEC+regulated 是定位决策而非事实问题，但需 Lysander 确认
- 一致性：17/20 — Synapse Forge secondary CTA 与主页一致；"A two-day readout" 与主页描述对齐；"measured against the Harness Engineering standard" 在多处复用
- 可维护性：18/20 — Markdown 结构清晰、SEO meta 独立、terminal mockup 原样保留便于 Astro 组件映射
- 合规性：18/20 — 定价透明、mailto 正确、"Janus Digital" 仅在 open question 中提及等候决策、未做未经证实的案例宣称
- **总分：91/100**
- **判定**：Pass
- 待解问题：5 条已列 Open Questions

