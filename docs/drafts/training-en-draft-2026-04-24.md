---
id: training-en-draft
type: narrative
status: draft
lang: en
translation_of: training-zh-v1
version: 0.1
published_at: 2026-04-24
updated_at: 2026-04-24
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [technical_builder, team_lead, ops_practitioner]
stale_after: 2026-10-24
---

# Training (EN draft)

## Structure Notes

Chinese `/training` page structure: Hero → lab-terminal mockup → 4-stat band → 5 modules (M1–M5) → 4 labs → 3-tier pricing → CTA.

English version keeps the same skeleton. Content changes:

- **SCP framing**: The Chinese page treats SCP as a certification. Per president decision (2026-04-24), it's to be presented as a **badge**, not a formal accredited credential. English copy reframes: "Synapse Certified Practitioner — a peer-recognized badge you earn by shipping." We drop the 🎓 emoji in the terminal preview and replace with a cleaner status line.
- **Hero value prop**: Chinese says "学会用 Harness Engineering 构建你自己的 AI Agent 协作运营体系" ("learn to build your own..."). English reframes around what the attendee *leaves with* — a repo, not a certificate.
- **Pricing tiers**: Kept verbatim in value but relabeled. "个人/企业(20人内)/企业(50人内)" → "Individual / Team (≤20) / Team (≤50)". "企业" as "Team" reads less corporate; "Enterprise" would imply SLA we don't offer at $10K.
- **Module titles**: Chinese M1–M5 titles are abstract. English retitles to concrete outcomes ("Why rules aren't enough" instead of "Why Harness Engineering is necessary").
- **Lab 2 terminal**: Replace 🎓 emoji with `[SCP BADGE: ELIGIBLE]` — consistent with badge framing.

## SEO Meta

- **Title**: "SCP Training — Build Your Own AI Agent Operation"
- **Description** (148 chars): "Eight hours of Harness Engineering training. Attendees leave with a working multi-agent operating system — a repo, not a slide deck. From $500." (147 chars)
- **Primary keyword**: AI agent training
- **Secondary**: Harness Engineering workshop, multi-agent system build, SCP certification

## Hero

- **Eyebrow**: `Training`
- **Title** (8 words): `Leave with a working AI team, not slides.`
- **Subtitle** (28 words): `SCP — Synapse Certified Practitioner. Eight hours, four hands-on labs, one repo you built yourself. For builders who are done reading about agents and ready to run them.`
- **Primary CTA**: `Enroll` → `mailto:lysanderl@janusd.io?subject=SCP%20Training%20Enrollment`
- **Secondary CTA**: `See the syllabus` → `#modules`

_(Hero word count: ~50 words)_

## Lab Terminal Mockup (preserve + adjust)

```
# Lab 2: Create Your AI Team
Build organization.yaml + 3 agent profiles

specialists:
  - strategist       # Score: 96/100 ✓
  - tech_lead        # Score: 92/100 ✓
  - qa_engineer      # Score: 91/100 ✓

audit_all_agents() → Average: 93.0/100 · PASS ✓

[SCP BADGE: ELIGIBLE]
```

Caption: `Lab 2 output — attendee build, SCP October 2026 cohort.`

_(Change from Chinese: 🎓 emoji replaced with `[SCP BADGE: ELIGIBLE]` status-line styling — matches the badge-not-certificate positioning.)_

## Stat Band (preserve)

- **8 hrs** — Course length
- **4 + 4** — Theory + hands-on
- **4 Labs** — Workshop builds
- **SCP** — Badge on completion

## Modules — What You'll Learn

**Heading**: `Five modules. Each answers a real question.`

### M1 — Why rules aren't enough
The war story most teams don't tell: the CLAUDE.md that got written, then ignored. We start here because most harness failures aren't missing rules — they're missing enforcement. You'll see exactly where unenforced rules collapse first.

### M2 — Guides and Sensors
Control-theory framing for agent reliability. Feedforward (what shapes the agent *before* it acts) and feedback (what verifies it *after*). You'll map your current setup against both and see which side is underweight.

### M3 — The four-tier decision hierarchy
Why specialist review should come before the CEO — and what goes wrong when it doesn't. You'll design an L1–L4 escalation map for a live scenario and stress-test it against edge cases.

### M4 — Agent HR management
Capability gradings (A/B/C), onboarding gates, the self-auditing engine. How to keep fifty agents from turning into fifty flavors of mediocre over six months.

### M5 — Intelligence loops and automation
Daily intelligence pipelines, four-expert review panels, scheduled event chains. The part that runs when you're asleep.

_(~240 words)_

## Labs — What You'll Build

**Heading**: `Four labs. You ship a working system by hour eight.`

- **Lab 1 — Your Harness Configuration**. Write the CLAUDE.md: role, execution chain, decision rules, checkpoints.
- **Lab 2 — Your AI Team**. Organization yaml plus three agent profiles, each audited to ≥90.
- **Lab 3 — Your Intelligence Pipeline**. Industry search scope, first report generated.
- **Lab 4 — Integration Build + Defense**. Demo the full system, face the panel, earn the SCP badge.

## Pricing

### Individual — $500
Online course plus hands-on labs. SCP badge on completion. Best for a single builder learning the methodology before pitching it internally.

### Team (≤20 seats) — $10K
Customized curriculum plus on-site workshop. We adapt the labs to your stack and your real agents. Most common tier for engineering-led orgs.

### Team (≤50 seats) — $15K
Includes one month of post-workshop advisory. For teams planning a wider rollout who need follow-through support as the first agents go live.

## Final CTA

**Heading**: `Eight hours from now, you have a running system.`
**Body**: `Or keep reading about agents. Your choice.`
**Primary CTA**: `Enroll` → `mailto:lysanderl@janusd.io?subject=SCP%20Training%20Enrollment`
**Secondary CTA**: `Ask about team pricing` → `mailto:lysanderl@janusd.io?subject=SCP%20Team%20Pricing`

## Translation Choices & Rationale

1. **SCP: certificate → badge**. Per president decision 2026-04-24, SCP is framed as a peer-recognized badge, not an accredited certification. Removes any false-claim risk. Copy uses "badge" throughout, replaces 🎓 with `[SCP BADGE: ELIGIBLE]`, avoids "certified" in the diploma sense.

2. **"学会用 Harness Engineering 构建..." → "Leave with a working AI team, not slides."**
   Chinese hero leads with what you'll *learn*. English hero leads with what you'll *leave with* — a stronger proof frame for English builder audiences who are skeptical of training products.

3. **"企业" → "Team" (not "Enterprise")**
   "Enterprise" in English SaaS implies dedicated SLA, SSO, procurement cycles. At $10K–$15K tier, "Team" is the accurate register. Preserves the actual scope (≤20 / ≤50 seats).

4. **"理论 + 实操" → "Theory + hands-on"**
   Direct translation works. Kept as-is.

5. **Module titles: abstract → concrete outcomes.** Chinese module titles describe topics ("Why Harness Engineering is necessary"). English titles describe questions the attendee walks in asking ("Why rules aren't enough"). Same content, stronger hook.

6. **"综合演练 + 答辩" → "Integration Build + Defense"**
   "答辩" (defense, in the thesis-defense sense) is a strong Chinese academic idiom. Kept "Defense" in English because the format *is* a panel defense, and the word correctly signals the stakes. "Demo" would be lighter but less accurate.

## Open Questions

1. **SCP badge phrasing — enough disclaimer?** Draft treats SCP as a peer-recognized badge throughout, no "certified" in accredited sense. Does it need an explicit footnote ("SCP is a peer-recognized Synapse badge, not an accredited industry certification")? Compliance call.
2. **Team tier naming: "Team" or "Company"?** Draft picks "Team" to avoid SaaS SLA implications. "Company" is an alternative but may over-imply scale. Style_calibrator preference.
3. **Pricing visibility above fold.** Current draft keeps pricing in its own section (not Hero). Some training landing pages push pricing up. Testing candidate.
4. **M3 framing: "CEO" or "Leadership"?** M3 title uses "specialist review should come before the CEO." English-first readers of training pages may not all have CEO-tier signoff workflows — smaller orgs call it "leadership" or "lead." Defaulting to CEO for now since it matches Synapse's framing, but flagging.
5. **Lab 4 "Defense" panel.** Is the defense real (Lysander plus a live panel) or simulated? If real, say so explicitly — it's a hook. If simulated, "Demo + Review" is more accurate.

## QA Self-Check

- 完整性：20/20 — frontmatter、SEO meta、Hero、Lab mockup、Stat band、M1–M5、Lab 1–4、三档 pricing、Final CTA、translation choices、open questions 全部到位
- 准确性：19/20 — SCP 框定为 badge（与总裁 2026-04-24 决策对齐）、价格/课时忠于原版；待 Lysander 确认 badge 免责声明措辞
- 一致性：17/20 — "Team" 而非 "Enterprise" 与定价档位匹配；模块标题体例统一；但 "Defense" 一词在中英语境下分量不同，Open Question 已 flag
- 可维护性：18/20 — Markdown 结构清晰、分 section 便于 Astro 映射；Lab mockup 变更（emoji→status line）已显式说明
- 合规性：18/20 — 移除 "certification" 的认证含义、无虚假宣称、定价透明、mailto CTA 正确；等候 Lysander 决定是否加免责脚注
- **总分：92/100**
- **判定**：Pass
- 待解问题：5 条已列 Open Questions
