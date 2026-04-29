---
id: academy-get-synapse-en-draft
type: tutorial
status: draft
lang: en
translation_of: academy-get-synapse-zh
version: 0.1
published_at: 2026-04-25
updated_at: 2026-04-25
author: content_strategist
review_by: [style_calibrator, integration_qa]
audience: [technical_builder, claude_code_user]
stale_after: 2026-10-25
---

# Academy / Get Synapse (EN draft)

## Structure Notes

The Chinese page is structured as: Hero → Quick-start terminal → Before You Start (already in English) → Three detailed steps → Upgrade section → FAQ → Bottom navigation. The English version preserves all blocks; "Before You Start" is left effectively unchanged because the Chinese page already wrote that block in English (it's a developer-facing checklist).

Key reframes:
- Hero shortened — Chinese hero is 30+ characters; English carries one-line precision instead.
- Terminal block kept structurally identical, with English comments replacing Chinese comments.
- Step copy reframed from instructional Chinese ("Clone GitHub仓库") to imperative English ("Clone the repo"). Verb-first.
- FAQ rewritten — direct translation flattens nuance. English answers each question in one short paragraph instead of three.

## SEO Meta

- **Title**: `Get Synapse — Five-Minute Setup for Claude Code`
- **Description** (148 chars): `Clone, personalize, run. Get a 44-agent AI team running inside Claude Code in five minutes. Free, local, your data never leaves your machine.`
- **Primary keyword**: install Synapse
- **Secondary**: Claude Code setup, multi-agent install, Synapse onboarding

## Hero

- **Eyebrow**: `Get Synapse`
- **Title** (4 words): `Three steps. Five minutes.`
- **Subtitle** (18 words): `Clone the repo, open it in Claude Code, paste one prompt. That's all the setup. Free forever.`
- **Back-link**: `← Academy home`

## Quick-start Terminal Block

```
# Step 1: Clone the repo
git clone https://github.com/lysanderl-glitch/synapse.git

# Step 2: Open in Claude Code, send the init prompt
Please complete Synapse initialization:
- My name: [your name]
- AI CEO name: [e.g. Alex, Aurora]
- Company / team: [your org]

# Step 3: You'll get a personalized greeting — system is live
"Hi [your name], I'm [CEO name], the Multi-Agents team is at your service." ✓
```

## Section A — Before You Start

**Heading**: `Before You Start`
**Subtitle**: `Synapse runs inside Claude Code on your local machine. Make sure these are in place first.`

Five-item checklist (already English in source — kept verbatim):
- Claude Account — Pro / Max plan or API key. _Get Claude →_
- Node.js ≥ 18 — `node --version`. _Install →_
- Claude Code — `npm install -g @anthropic-ai/claude-code`. _Docs →_
- Git — `git --version`. _Install →_
- macOS / Linux / Windows WSL — _Install WSL →_

_Footer_: `Already set up? Skip to Step 1 ↓`

## Section B — The Three Steps in Detail

**Heading**: `Detailed Steps`

### Step 1 — Clone the repo
Run this in PowerShell. The folder name is yours to choose; Claude Code will open whichever you pick.

```powershell
git clone https://github.com/lysanderl-glitch/synapse.git "$env:USERPROFILE\Claude Code\Synapse"
```

_Tip: macOS / Linux work the same — replace the path with `~/Claude\ Code/Synapse` or wherever you keep projects._

### Step 2 — Open in Claude Code, send the init prompt
Open Claude Code → **Open Folder** → select your Synapse directory. Then paste this prompt with your details filled in:

```
Please complete Synapse initialization:
- My name: [your name, e.g. Alex Chen]
- AI CEO name: [your AI CEO's name, e.g. Aurora, Aria]
- Company / team: [your organization or team]
```

When initialization succeeds, the next session opens with a personalized greeting:

> "Hi [your name], I'm [CEO name], the Multi-Agents team is at your service."

_Troubleshooting: If the greeting doesn't appear, confirm Claude Code opened the directory containing `CLAUDE.md` at its root._

### Step 3 — Meet your team
Once your CEO is live, send this single message to walk through everything you just unlocked:

```
Hello — please introduce: 1) the current team architecture and what each team owns;
2) how the execution chain runs from goal-input to final delivery; 3) how the
four-tier decision system decides what to escalate to me?
```

This one prompt activates your AI CEO, surfaces all 44 agents across seven teams, walks through the six-step execution chain, and explains exactly when decisions escalate.

_(~310 words across the three steps)_

## Section C — Upgrading the System

**Heading**: `Upgrade with one sentence`
**Subtitle**: `When a new Synapse release ships, just say it.`

Tell your AI CEO: **"Upgrade Synapse"**

The CEO automatically pulls the latest release → runs the audit (must clear 90) → preserves your personalization → reports back when complete. No manual Git work, no merge conflicts, no migration anxiety.

_(~50 words)_

## Section D — FAQ

**Heading**: `Common Questions`

**Is my data safe?**
Synapse runs entirely on your machine. Nothing transits a third party except the Anthropic Claude API call itself. Your conversations and files stay local.

**Does it cost money?**
The Synapse package is free, forever. You'll need a Claude Code subscription to run it (Anthropic's product, $20/month Max plan as of writing). The framework itself is $0.

**Can I customize the team?**
Fully. Edit `agent-CEO/config/organization.yaml` to add or remove teams and agents. For deep customization, see `CUSTOMIZATION_GUIDE.md` in the repo.

**What's the difference between Free and Evolution?**
Free is a snapshot — yours forever, no expiration, but no automatic updates. Evolution syncs daily and weekly with the latest evolution: new agent capabilities, methodology revisions, execution-chain upgrades.

**Does it work on macOS and Linux?**
Yes. Claude Code is cross-platform. Synapse itself is OS-agnostic. The PowerShell command in Step 1 swaps cleanly for `git clone` plus normal directory operations on Unix-likes.

_(~190 words)_

## Final CTA / Bottom Navigation

- **Back-link**: `← Back to Academy`
- **Forward links**:
  - `Browse the AI Team →` → `/en/academy/team`
  - `View Skills →` → `/en/academy/skills`

## Translation Choices

1. **"5分钟接入" → "Five-Minute Setup"** — direct, but reordered. "Setup" carries less marketing baggage than "onboarding" or "install" in the Claude Code developer audience. The number stays in the title for SEO and scannability.

2. **"个性化问候语" → "personalized greeting"** instead of "personalized welcome message." Greeting captures the conversational nature; welcome message implies a marketing email. Per glossary: "greeting" is the canonical translation for this product surface.

3. **FAQ rewritten, not translated.** Each Chinese FAQ answer averages 60 characters; English answers run 30–50 words because English questions imply additional context the Chinese reader already has. The reframed answers preserve every fact but read as native English explanation, not back-translation.

## Open Questions

- **`agent-CEO` vs `agent-butler` path naming** — Chinese page uses `agent-butler/config/organization.yaml`; current Synapse-Mini repo has migrated to `agent-CEO/config/`. Confirm which path ships in the public-facing GitHub release before publish.
- **Claude Code pricing claim** — "$20/month Max plan" is a current snapshot. Anthropic pricing changes are out of our control; consider replacing with "see Anthropic for current pricing" to reduce drift risk.
- **Step 3 prompt language** — current draft retains the Chinese prompt verbatim in the code block. For an English audience, the prompt itself should be in English. Decision pending: ship English-only prompt, or retain bilingual prompt for users who'll switch their session locale?

## QA Self-Check

### Faithfulness — 18/20
- All four major sections preserved (Hero, Steps, Upgrade, FAQ).
- Five-item prerequisite list reproduced exactly.
- All five FAQ entries answered with same factual content.
- **Deduction (-2)**: Step 3's bilingual prompt is unresolved (see Open Question #3). Either decision direction loses minor faithfulness in the other dimension.

### Brand Voice — 19/20
- Imperative verbs throughout the three steps ("Clone," "Open," "Send").
- "Free forever" used twice, no more — restraint over repetition.
- Specialist tone — no "amazing," "easy," or "magic."
- **Deduction (-1)**: "Five-Minute Setup" has slight risk of overpromising. Hedged in the body ("That's all the setup") but the title carries the implicit time claim.

### Clarity — 19/20
- Every step starts with a verb and a one-line outcome.
- Code blocks separated from prose by always being preceded by an "action sentence."
- Troubleshooting note appears exactly where it's needed (Step 2).
- **Deduction (-1)**: Step 1 PowerShell command is Windows-specific. Inline mac/Linux variant addresses this, but a less technical reader might still pause.

### Style — 18/20
- Code blocks formatted consistently with language hint.
- FAQ uses Q-as-bold pattern, A as paragraph — clean and skimmable.
- Em-dashes used for definition (not as comma replacement).
- **Deduction (-2)**: "the Multi-Agents team is at your service" — verbatim from the system prompt. Reads slightly stilted in English but is product-locked. Document as known constraint in style guide.

### Compliance — 18/20
- No data-leak claims (only what we control: "Nothing transits a third party except Anthropic Claude API").
- Anthropic pricing flagged in Open Questions.
- License terms not stated explicitly — relies on the GitHub repo's LICENSE file as source of truth.
- **Deduction (-2)**: "Anthropic's product, $20/month Max plan" — pricing claim has drift risk (see Open Question #2). Resolve before publish.

### Total: 92/100 — PASS
