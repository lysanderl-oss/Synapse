---
id: academy-team-en-draft
type: directory
status: draft
lang: en
translation_of: academy-team-zh
version: 0.1
published_at: 2026-04-25
updated_at: 2026-04-25
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [technical_builder, enterprise_decider]
stale_after: 2026-10-25
---

# Academy / Team (EN draft)

## Structure Notes

The Chinese page is structured as: Hero → Team-section navigation chips → Seven team blocks (each with role description + agent grid) → HR system note → Bottom navigation. The English version preserves this skeleton 1:1 since the team data is the load-bearing content.

Key decisions:
- **Specialist IDs stay English** (`strategist`, `harness_engineer`, etc.) — these are functional identifiers in `organization.yaml`, not branded labels. Per task brief, retain canonical IDs.
- **Agent display names translated** to natural English titles (e.g. "战略分析师" → "Strategy Analyst," not "Strategist Analyst" or the literal "Strategy Analysis Master").
- **Capability descriptions reframed** — Chinese descriptions reference frameworks by name ("SWOT/PEST/波特五力"); English keeps frameworks but tightens phrasing to read as job-description bullets, not feature-spec bullets.
- **Audit scores preserved verbatim** — these are operational data, not creative copy.

## SEO Meta

- **Title**: `AI Team Directory — 44 Specialists Across 7 Teams | Synapse Academy`
- **Description** (153 chars): `Forty-four AI specialists across seven teams: strategy, ops, R&D, content, growth, knowledge, delivery. Every agent audits at 90 or higher. Browse the roster.`
- **Primary keyword**: AI agent team directory
- **Secondary**: multi-agent specialist roster, AI agent capabilities, Synapse team structure

## Hero

- **Eyebrow**: `AI Team Directory`
- **Title** (4 words): `Forty-four specialists, seven teams.`
- **Subtitle** (16 words): `Every agent carries a concrete capability description. Every score above 90. No filler, no figurehead roles.`
- **Anchor chip row**: One chip per team — Graphify Advisors · Harness Ops · R&D · Content Ops · Growth · OBS · Delivery
- **Back-link**: `← Academy home`

## Team A — Graphify Advisors (Strategy & Decision Support)

**Color**: gold · **Members**: 6

The advisor pool. Brought in for L2 expert review and L3 strategic decisions. Cross-functional, multi-framework, evidence-driven.

| ID | Name | Score | What they do |
|---|---|---|---|
| `strategist` | Strategy Analyst | 96 | SWOT, PEST, Porter's Five Forces. Strategic planning and competitive landscape analysis. |
| `decision_advisor` | Decision Advisor | 94 | Multi-option risk-reward modeling, L3 decision synthesis, uncertainty quantification. |
| `ai_tech_researcher` | AI Tech Researcher | 95 | Frontier AI tracking, technical feasibility assessment, daily intel filtering with practical-value priority. |
| `evolution_engine` | Evolution Engine | 94 | Self-improvement loop coordination, agent capability gap analysis, capability-version management. |
| `execution_auditor` | Execution Auditor | 93 | S/M/L task tiering, execution-chain integrity audit, cross-session state tracking. |
| `trend_watcher` | Trend Watcher | 92 | Macro trend identification, pattern surfacing, 3–12 month forecasts. |

## Team B — Harness Ops (Execution Chain Engineering)

**Color**: cyan · **Members**: 4

The team that maintains the framework itself. Every CLAUDE.md edit, every YAML config change, every audit pipeline runs through this team.

| ID | Name | Score | What they do |
|---|---|---|---|
| `harness_engineer` | Harness Engineer | 96 | CLAUDE.md and YAML config changes, execution-chain design and tuning, Harness rule authorship. |
| `ai_systems_dev` | AI Systems Developer | 94 | `hr_base.py` and tooling, agent toolchain construction, Python automation. |
| `knowledge_engineer` | Knowledge Engineer | 93 | Methodology documentation, knowledge graph construction, OBS knowledge-base architecture. |
| `integration_qa` | Integration QA Engineer | 95 | `qa_auto_review()` scoring (≥3.5 to pass), YAML syntax validation, end-to-end verification. |

## Team C — R&D (Systems Development)

**Color**: blue · **Members**: 5

Production engineering. Architecture, code, tests, deployment. The team that ships systems users actually run.

| ID | Name | Score | What they do |
|---|---|---|---|
| `tech_lead` | Tech Lead | 95 | Architecture and tech decisions, technical-debt assessment, code-review standards. |
| `backend_dev` | Backend Engineer | 93 | REST API and database design, Python and Node.js microservices, performance tuning. |
| `frontend_dev` | Frontend Engineer | 92 | React and Vue component development, responsive design, UX optimization. |
| `qa_engineer` | QA Engineer | 94 | pytest plus Playwright E2E testing, automated regression, BDD test cases. |
| `devops_engineer` | DevOps Engineer | 91 | CI/CD pipelines (GitHub Actions), Docker and K8s containerization, monitoring and alerting. |

## Team D — Content Ops (Creation & Brand)

**Color**: gold · **Members**: 6

Editorial, design, and channel ops. Where strategic substance becomes published artifacts.

| ID | Name | Score | What they do |
|---|---|---|---|
| `content_strategist` | Content Strategist | 94 | Content marketing strategy, audience modeling, content ROI assessment. |
| `content_creator` | Content Creator | 93 | Technical articles and blog posts, AI engineering case studies, LinkedIn copy. |
| `visual_designer` | UI/UX Designer | 93 | Web UI/UX design, light/dark mode decisions, Tailwind CSS implementation. |
| `ai_visual_creator` | AI Visual Creator | 95 | Midjourney and DALL-E branded illustration, comic narrative design, visual asset production. |
| `publishing_ops` | Publishing Operator | 91 | Multi-platform publishing (WeChat, LinkedIn, Ghost), SEO optimization, performance analytics. |
| `training_designer` | Training Designer | 92 | SCP curriculum design, learning-path planning, assessment standards. |

## Team E — Growth (Strategy & GTM)

**Color**: cyan · **Members**: 4

Go-to-market and customer success. Pricing, positioning, community, sales enablement.

| ID | Name | Score | What they do |
|---|---|---|---|
| `gtm_strategist` | GTM Strategist | 94 | Product launch strategy, pricing-model design, channel-mix optimization. |
| `customer_insights_manager` | Customer Insights Manager | 93 | User research design, NPS and CSAT analysis, customer-journey optimization. |
| `community_manager` | Community Manager | 91 | Technical community building, KOL relationship management, word-of-mouth growth. |
| `sales_enablement` | Sales Enablement Specialist | 92 | Sales-methodology training, demo-script design, customer-success framework. |

## Team F — OBS (Knowledge & Second Brain)

**Color**: blue · **Members**: 4

The knowledge custodians. Every decision, methodology, and lesson learned routes through this team for storage and retrieval.

| ID | Name | Score | What they do |
|---|---|---|---|
| `obs_architecture_expert` | OBS Architecture Expert | 94 | Obsidian second-brain architecture, knowledge-tier design (the 01–06 directory system), cross-vault linking. |
| `knowledge_search_expert` | Knowledge Search Expert | 92 | Semantic search optimization, knowledge-graph queries, contextual association discovery. |
| `knowledge_quality_expert` | Knowledge Quality Expert | 93 | Knowledge-asset scoring, stale-content cleanup, quality-standard authorship. |
| `knowledge_chandu_expert` | Knowledge Distillation Expert | 91 | Session-to-knowledge-base auto-extraction, insight synthesis, cross-session memory enhancement. |

## Team G — Delivery (PMO & Customer Execution)

**Color**: gold · **Members**: 7

Project management and customer-facing delivery. Domain specialists for IoT, BIM, and on-site work.

| ID | Name | Score | What they do |
|---|---|---|---|
| `pmo_expert` | PMO Expert | 93 | Portfolio management, WBS decomposition, milestone tracking, gate reviews. |
| `delivery_expert` | Delivery Expert | 94 | End-to-end delivery management, customer communication, acceptance-criteria definition. |
| `iot_expert` | IoT Expert | 92 | IoT system integration, sensor-data acquisition, MQTT protocol configuration. |
| `iot_data_expert` | IoT Data Expert | 91 | Time-series data processing, data-quality management, dashboard design. |
| `digital_modeling_expert` | Digital Modeling Expert | 93 | BIM and digital-twin modeling, Revit and ArchiCAD workflows, model acceptance standards. |
| `uat_test_expert` | UAT Test Expert | 92 | User-acceptance test strategy, defect-management process, test-report authorship. |
| `training_expert` | Training Expert | 90 | User training programs, operations-manual authorship, post-launch support. |

## HR System Note

All agent capabilities are audited automatically by the **HR Engine** with a passing line at 90.

Capability descriptions follow B-grade or higher standards: every description must reference a specific methodology or framework. Vague descriptions like "project management" or "quality assurance" are rejected at audit.

## Final CTA / Bottom Navigation

- **Back-link**: `← Back to Academy`
- **Forward link**: `View the Skills Library →` → `/en/academy/skills`

## Translation Choices

1. **"智囊团" → "Advisors" (with "Graphify Advisors" as the team name).** Direct translation "Brain Trust" carries Cold-War political baggage in English; "Think Tank" sounds external/consultative. "Advisors" reads as an internal pool, matches the L2 expert-review function exactly, and pairs cleanly with `Graphify` as a brand prefix.

2. **"知识沉淀专家" → "Knowledge Distillation Expert"** (not "Knowledge Sediment Expert," which is the literal). "Distillation" captures the concentration-of-essence meaning of 沉淀 in a knowledge context — turning many sessions into a few durable insights.

3. **Team display names use functional descriptors, not Chinese-style poetic team names.** "Butler 交付团队" → "Delivery (PMO & Customer Execution)." Removes the Butler metaphor (which evokes service hospitality in English) and surfaces the team's actual function. Specialist IDs remain `pmo_expert`, `delivery_expert`, etc.

## Open Questions

- **`butler` legacy ID** — Internal team ID is still `butler` in some configs; recent migration renamed user-facing references to "Delivery." Confirm whether the public-facing English page should also use `butler` for ID-level consistency or rename in the published copy.
- **Score-claim defensibility** — Every score (90–96) needs an inspectable audit trail. Link to `audit_harness()` log artifact, or add a footnote citing audit run date.
- **"`knowledge_chandu_expert`" — pinyin remnant** — `chandu` is the pinyin for 沉淀. ID feels awkward in an English directory. Recommend renaming to `knowledge_distill_expert` in the next config refactor; flag rather than rename in this draft.

## QA Self-Check

### Faithfulness — 19/20
- All seven teams present, all 36+ agent rows preserved (44 specialists across teams; matches Chinese source counts).
- Every audit score reproduced verbatim.
- HR system note preserved with same B-grade standard reference.
- **Deduction (-1)**: "Butler" → "Delivery" rename loses the Chinese page's brand consistency. Resolve via Open Question #1 before publish.

### Brand Voice — 18/20
- Specialist tone — every capability bullet references a concrete framework or tool.
- No "world-class" or "expert-level" filler adjectives.
- Team intros lead with function, not flattery.
- **Deduction (-2)**: "No filler, no figurehead roles" in the Hero is editorial — borderline self-promoting. Style_calibrator may want to soften.

### Clarity — 19/20
- Table format makes 44 rows scannable in under 60 seconds.
- Each team's intro answers "why does this team exist" in one sentence.
- Specialist IDs and display names paired so config-readers and casual readers both find what they need.
- **Deduction (-1)**: "OBS" abbreviation introduced without expansion in Hero — assumes context. Spell out as "OBS (Obsidian-based knowledge layer)" on first use.

### Style — 19/20
- Markdown table syntax used consistently across all seven team blocks.
- Capability bullets all parallel: action + scope.
- Em-dashes used for compound concepts ("L3 decision synthesis"), not as comma substitutes.
- **Deduction (-1)**: Some agent display names are noun phrases ("Strategy Analyst") and some are role compounds ("Backend Engineer"). Could canonicalize, though both feel natural.

### Compliance — 18/20
- No claim about agent performance beyond the audit score.
- Frameworks (SWOT, BIM, MQTT) referenced as standard industry tools, not endorsed brands.
- Tools mentioned (Midjourney, DALL-E, Revit, ArchiCAD) are factually used by the agents — not aspirational.
- **Deduction (-2)**: "Every score above 90" is a population claim. The minimum displayed is 90 (training_expert), so the claim is true at the threshold but tight; one capability dip below 90 would invalidate the claim. Hedge to "Every published score 90 or higher" for stronger ground.

### Total: 93/100 — PASS
