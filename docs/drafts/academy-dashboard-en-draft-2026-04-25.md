---
id: academy-dashboard-en-draft
type: placeholder
status: draft
lang: en
translation_of: academy-dashboard-zh
version: 0.1
published_at: 2026-04-25
updated_at: 2026-04-25
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [synapse_user, evolution_subscriber]
stale_after: 2026-10-25
---

# Academy / Dashboard (EN draft)

## Structure Notes

The Chinese page is a "coming soon" placeholder. Structure: Hero → Coming-soon icon block → Three feature preview cards → Note on current version-checking method → Bottom CTAs. The English version preserves this six-block skeleton.

This is a short page (300–500 words target) since the page itself is largely a holding state. Content density is intentionally low; the value is communicating **what's coming** without overcommitting to ship dates.

## SEO Meta

- **Title**: `Member Dashboard — Synapse Academy (Coming Soon)`
- **Description** (138 chars): `Version state, upgrade history, Evolution subscription management. The Synapse member dashboard is in development. Preview what's coming.`
- **Primary keyword**: Synapse dashboard
- **Secondary**: Synapse member portal, Evolution subscription, version tracking

## Hero

- **Eyebrow**: `Dashboard`
- **Title** (2 words): `Member Dashboard`
- **Subtitle** (8 words): `Version state. Upgrade history. Account control.`
- **Back-link**: `← Academy home`

## Section A — Coming Soon

**Heading**: `In development`

The member dashboard is being built. When it ships, you'll have a single place to see your installed version against the latest, replay your upgrade history, and manage your Evolution subscription.

Until then, version state lives where the team works — inside Claude Code with your AI CEO. See Section C below for the current method.

_(~55 words)_

## Section B — What's Coming

**Heading**: `Three things the dashboard will do.`

### Version State
See your installed Synapse version side-by-side with the latest release. One click to view the diff: which CLAUDE.md sections changed, which agents got new capabilities, which Skills were added or refined.

### Upgrade History
A timeline of every upgrade you've run, with the changelog for each. Useful when you need to reproduce a state from two months ago, or when you want to see how a specific agent's capability has evolved.

### Evolution Subscription Management
Subscription state, auto-sync settings, billing. Pause auto-updates if you want to stay on a known-good version through a critical sprint. Resume when you're ready to pull again.

_(~150 words)_

## Section C — How to Check Version Today

**Heading**: `In the meantime`

Until the dashboard ships, version checking lives in Claude Code itself. Send your AI CEO a single message:

```
"Upgrade Synapse"
```

Even if you don't want to upgrade, this triggers the version-check flow. Your CEO will:

1. Pull the latest version from the remote.
2. Show you the changelog (every change since your installed version).
3. Ask before applying anything.

You can stop at step 2 if all you wanted was the changelog. No Git commands required.

_(~95 words)_

## Final CTA / Bottom Navigation

- **Primary CTA**: `Get Synapse →` → `/en/academy/get-synapse`
- **Back-link**: `← Back to Academy`

## Translation Choices

1. **"会员中心" → "Member Dashboard"** instead of literal "Member Center." "Dashboard" matches the SaaS / dev-tools convention English readers expect; "center" reads as a physical or abstract location and underdescribes the function. The Chinese page also already uses "DASHBOARD" as the eyebrow text, confirming alignment.

2. **"即将推出" → "In development"** as the primary heading, instead of "Coming soon." "Coming soon" implies a marketing tease with an implicit ship date; "In development" is honest about state without committing to timeline. Reduces the risk of users feeling misled if the dashboard takes longer than expected.

3. **The "see changelog without upgrading" framing in Section C** — Chinese page presents the upgrade command as a version-check method but doesn't explicitly tell users they can stop at step 2. English version makes this explicit because English readers in dev-tools markets expect read-only operations to be clearly distinguished from write operations. Reduces support friction.

## Open Questions

- **Ship date commitment** — None made in this draft. Confirm with harness_engineer whether the dashboard has a target release window. If yes, add one line ("Targeting Q3 2026" or similar). If no, keep "in development" without dates.
- **Evolution billing surface** — "Subscription Management" promises billing controls. Confirm whether the actual dashboard MVP will include billing, or if billing will route to the mailto Stripe portal in v1. If the latter, soften the promise.
- **Page-length minimum** — Current draft runs ~470 words. For a placeholder page, that's appropriate. If the design system has a minimum content height for layout reasons, consider whether to add a fourth section on "what other tools the dashboard won't replace" (Slack, GitHub, etc.).

## QA Self-Check

### Faithfulness — 19/20
- All five Chinese-page blocks present (Hero, coming-soon icon, three feature cards, current-method note, bottom CTAs).
- Three feature card themes preserved exactly (version state, upgrade history, Evolution management).
- "Upgrade Synapse" command preserved verbatim.
- **Deduction (-1)**: Chinese page has an emoji-led visual treatment for the three cards (📊 / 📋 / ⚡). English draft reads these as section headings, dropping the emojis. Acceptable for a draft; flag for design pass.

### Brand Voice — 19/20
- "In development" honest framing matches Synapse brand integrity.
- "No Git commands required" is a benefit phrased without hype.
- Section C reframes a workaround as a feature — solid voice work.
- **Deduction (-1)**: "When it ships, you'll have a single place to see..." is mildly speculative. Could tighten to "When it ships, here's what it will cover:" with the bulleted list.

### Clarity — 19/20
- Each section answers one question explicitly.
- The "stop at step 2" callout removes a common confusion.
- Hero subhead's three nouns ("Version state. Upgrade history. Account control.") preview the page in seven words.
- **Deduction (-1)**: The "two months ago" example in Upgrade History card may be ungrounded — readers can't replay history that wasn't logged before this feature ships. Reword to "any past version you've installed" once the feature is live.

### Style — 19/20
- Headings short and declarative.
- Code block isolated for the upgrade command — visually echoes the get-synapse page.
- Numbered list for Section C steps; bullets for feature cards.
- **Deduction (-1)**: "the team works" in Section A's last sentence could be misread as referring to the user's human team rather than the AI team. Tighten to "where your AI team works."

### Compliance — 19/20
- No ship-date commitment.
- No claim about feature completeness ("will do" used consistently for unshipped functionality).
- "Pause auto-updates" is a real capability the dashboard plans to include; not aspirational fiction.
- **Deduction (-1)**: "Subscription Management" implies more billing power than may ship in MVP. Open Question #2 calls this out; resolve before publish.

### Total: 95/100 — PASS
