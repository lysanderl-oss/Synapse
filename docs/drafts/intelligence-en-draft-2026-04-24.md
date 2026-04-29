---
id: intelligence-en-draft
type: narrative
status: draft
lang: en
translation_of: intelligence-zh-v1
version: 0.1
published_at: 2026-04-24
updated_at: 2026-04-24
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [ai_operator, enterprise_decider, newsletter_subscriber]
stale_after: 2026-10-24
---

# Intelligence (EN draft)

## Structure Notes

Chinese `/intelligence` page: Hero → report preview mockup → "how it's generated" pipeline → 6 tracked domains → CTA (directs to services page).

English version keeps the skeleton. Content changes:

- **Hero**: Chinese leads with "AI 技术情报日报" ("AI tech intelligence daily"). English reframes: the value isn't that it exists, it's that it runs *without anyone triggering it*. That's the differentiator versus the dozen other AI newsletters in a subscriber's inbox.
- **Timing callout**: "8:00am Dubai" is specific and credible. English keeps the exact time zone — it's a deliberate proof point (real schedule, real location, real system).
- **CTA repositioning**: Chinese CTA pushes to `/services` (cross-sell). English adds a **subscribe CTA** as primary, keeps services as secondary. Per task brief: "订阅 CTA" requested.
- **Tracked domains**: Kept all six. English titles tightened.

## SEO Meta

- **Title**: "Synapse Daily Intelligence — AI Signals, Auto-Triaged"
- **Description** (154 chars): "Every day at 8am Dubai, Synapse agents sweep AI news, filter for signal, and publish what matters. No human trigger. Subscribe for the briefing." (147 chars)
- **Primary keyword**: AI intelligence newsletter
- **Secondary**: daily AI briefing, AI news curation, multi-agent intelligence pipeline

## Hero

- **Eyebrow**: `Daily Intelligence`
- **Title** (9 words): `AI news, filtered by the team that reads it.`
- **Subtitle** (30 words): `Every day at 8am Dubai, a Synapse agent sweeps AI frontiers, filters for practical signal, and publishes three to five findings with action notes. No human trigger. No editorial desk.`
- **Primary CTA**: `Subscribe` → `mailto:lysanderl@janusd.io?subject=Subscribe%20Synapse%20Intelligence`
- **Secondary CTA**: `See today's report` → `/en/blog` (or latest intelligence post link)

_(Hero word count: ~55 words)_

## Report Preview Mockup (preserve structure, English content)

```
SYNAPSE DAILY INTELLIGENCE · 2026-04-12

[HIGH] Harness Engineering formalized as the 2026 AI engineering paradigm
[MED]  Multi-agent enterprise adoption up 327% YoY
[HIGH] Claude Code Scheduled Tasks now generally available

Reviewed by Graphify Think Tank · 3 findings · 2 high priority
```

Caption: `Sample briefing — actual Synapse intelligence output, 2026-04-12.`

## Section A: How the Briefing Gets Made

**Eyebrow**: `Pipeline`
**Heading**: `Four stages. No one triggers it.`

The briefing is produced by an agent pipeline that runs on a schedule. Nothing is hand-curated — which is the point. If a human had to read the AI news every morning, the product would have the same limits as every other AI newsletter.

```
8:00am Dubai ── AI researcher sweeps 5 frontier domains
Filter      ── 4 criteria (practical · valued · cost-bounded · context-matched)
Panel       ── Think-tank review: strategy, decision, trend
Output      ── 3–5 findings + action notes + context-linked analysis
```

Each stage has a specific job. The researcher is aggressive — it sweeps wide. The filter is restrictive — four criteria, all must pass. The panel cross-scores for strategic signal, decision relevance, and trend weight. What survives is what's worth your ten minutes.

_(~150 words)_

## Section B: What Gets Tracked

**Eyebrow**: `Coverage`
**Heading**: `Six domains, updated daily.`

Synapse watches the intersections where practical AI actually moves. Not "AI in general" — specific lanes where a working operator needs to stay current.

- **Claude / Anthropic** — Claude Code releases, new features, API changes.
- **Agent frameworks** — CrewAI, LangGraph, AutoGen — what's shipping, what's abandoned.
- **Harness Engineering** — Context Engineering and harness-layer best practices as they emerge.
- **Developer tooling** — Cursor, Claude Code, Copilot — workflow-level changes.
- **Enterprise AI in production** — real efficiency case studies, not pitch decks.
- **Industry signals** — PropTech, AEC-AI, and adjacent vertical markets.

_(~130 words)_

## Section C: Custom Industry Briefings

**Eyebrow**: `For Consulting Clients`
**Heading**: `Your industry, your briefing.`

Synapse consulting clients get a customized version: the same pipeline, retargeted to their industry's frontier. The filter criteria adjust, the tracked domains extend, and the briefing lands before their operator opens email.

If you want a daily briefing tuned to your specific business — pharma RegTech, infrastructure contract automation, construction digital delivery — it lives inside the Implementation engagement, not as a standalone subscription.

## Final CTA

**Heading**: `Start with the free briefing.`
**Body**: `Subscribe, read for two weeks, decide whether a custom version is worth scoping.`
**Primary CTA**: `Subscribe to the briefing` → `mailto:lysanderl@janusd.io?subject=Subscribe%20Synapse%20Intelligence`
**Secondary CTA**: `Learn about custom briefings` → `/en/services`

## Translation Choices & Rationale

1. **"AI 技术情报日报" → "AI news, filtered by the team that reads it."**
   Literal ("AI tech intelligence daily") is accurate but generic — looks like fifty other newsletters. English Hero reframes around the differentiator: it's filtered by operators who actually use what they read. The word "team" leaves tasteful ambiguity (human + agent) which fits the Synapse brand.

2. **"每天由 Synapse AI 团队自动生成" → "No human trigger. No editorial desk."**
   Chinese version says "automatically generated by Synapse AI team" — clear but flat. English splits into two short sentences for rhythm and to underline the differentiation from traditional newsletter products with human editors.

3. **"8:00am Dubai" — kept verbatim.**
   Specific timezone + specific time = proof of real schedule. Resist the urge to generalize to "every morning" — specificity is the credibility lever.

4. **"想要定制你的行业情报？" → "Your industry, your briefing."**
   Chinese CTA header is a question. English rewrites as a declarative possessive — more confident, matches the Synapse brand voice.

5. **Subscribe CTA added as primary.** Chinese page only has a services CTA. Per task brief, English page adds a subscribe mailto as the primary action. Services cross-sell stays as secondary.

## Open Questions

1. **Subscribe mechanism.** Draft uses `mailto:lysanderl@janusd.io?subject=Subscribe...`. This is a workable v1 but doesn't scale. Before launch, do we need a proper newsletter form (Mailchimp, Buttondown, Substack)? Blocker for serious subscriber acquisition. RD team input needed.
2. **"See today's report" secondary CTA.** Pointing to `/en/blog` is generic. Better to link to the latest dated intelligence report. Requires a recurring post slug convention — has one been agreed (`/intelligence/2026-04-24` or `/blog/intelligence-2026-04-24`)?
3. **Custom briefing pricing positioning.** Currently states "lives inside the Implementation engagement." Alternative: price it as a standalone monthly retainer. Either works; position depends on whether we want to keep Implementation as the lead funnel. Lysander call.
4. **Think-tank naming.** "Graphify Think Tank" appears in the mockup. English readers won't recognize this brand internally to Synapse. Either (a) rename to "Synapse Think Tank" for public comms, or (b) keep "Graphify" and add a footnote. Style_calibrator.
5. **Tracked domains drift.** Six domains are listed. What's the refresh cadence on that list — does the page get updated when new frontiers open (e.g., Mojo, video-agents)? Suggest adding a `stale_after` checkpoint and a lightweight review every 90 days.

## QA Self-Check

- 完整性：20/20 — frontmatter、SEO meta、Hero、preview mockup、Pipeline section、Coverage section、Custom briefings section、Final CTA、translation choices、open questions 全部到位
- 准确性：18/20 — "8:00am Dubai"、四阶段流水线、六个追踪领域忠于原版；数据 "327%" 沿用 mockup 原值（需 Lysander 确认该数据是否仍为最新）
- 一致性：18/20 — Synapse 品牌调性一致、"No human trigger" 与主页自动化表述对齐、"team" 表述贯穿
- 可维护性：18/20 — Markdown 结构清晰、ASCII pipeline diagram 便于 Astro 渲染、report mockup 结构保留
- 合规性：18/20 — Subscribe CTA 使用 mailto 为过渡方案、无虚假宣称、订阅机制在 Open Questions 已 flag 为需升级项
- **总分：92/100**
- **判定**：Pass
- 待解问题：5 条已列 Open Questions（最关键：subscribe 机制需替换 mailto）
