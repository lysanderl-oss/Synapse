# Founding 30 — Welcome Email Templates

> 新成员欢迎邮件模板（中英双语）。
> Owner: growth_lead（模板）+ Lysander（签名）
> Last updated: 2026-04-23
> Usage: 接受申请后 24 小时内发出

---

## 使用规则

1. **双语原则**：按申请人邮件使用的语言回复（英文申请 → 英文模板；中文申请 → 中文模板）
2. **个性化必做**：
   - 每封邮件开头一定要有 1–2 句引用对方申请信中的具体内容（证明我们真的读了）
   - 不要群发感的措辞（避免 "Dear applicant" 之类）
3. **Founding Number**：由 growth_lead 在发送前从 advocate-list.md 取序号，填入模板中的 `#{FOUNDING_NUMBER}`
4. **签名**：Lysander 亲笔（如是 AI 代发，签名写 "Lysander (Synapse Forge CEO)"）

---

## 模板 A — English Version

```
Subject: Welcome to Synapse Forge — You are Founding Member #{FOUNDING_NUMBER}

Hi {FIRST_NAME},

Thanks for applying. {PERSONAL_HOOK — quote one specific thing they wrote, e.g. "I especially appreciated your note on how you're currently losing context between Claude sessions — that is exactly one of the problems the execution chain was built for."}

You're in. You are Founding Member #{FOUNDING_NUMBER} of 30.

Here is what that means, and what happens next.

## What you now have

1. **Founding Member #{FOUNDING_NUMBER}** — a permanent spot on the Synapse site when we publish the co-creators list.
2. **Lifetime Pro** — when we launch the commercial tier, your team gets full Pro access, forever.
3. **1h / quarter with Lysander** — direct architecture / rollout co-creation, scheduled on your initiative.
4. **First dibs on new modules** — Janus, Stock, and everything else we ship.

## What happens this week

- Slack / Discord invitation: {INVITE_LINK}
- Founding Resource Pack: {RESOURCE_LINK}
  - Open source repository
  - Personalized CLAUDE.md starter
  - Quick Start guide (5 min read)
  - 72-hour deployment check template
- A short onboarding video call within your first 7 days (reply to this email with 3 time slots in your timezone and I'll pick one)

## What we'll ask of you

1. Complete your first Synapse deployment within 2 weeks (CLAUDE.md personalized + first dispatch runs clean).
2. Submit at least one structured feedback per month — the template lives in the Slack channel.
3. Allow us to reference your experience anonymously in our learning library (nothing public without your approval).
4. Show up in the Friday weekly thread when you can. Async, low-noise.

## One small request

Within 72 hours of receiving this email, would you mind filling in the short Deployment Check form in the Resource Pack? It helps us catch the first blocker early, rather than discovering it two weeks in.

That is all from my side for now. Welcome. The Founding 30 is about to be a real thing.

Best,
Lysander
CEO, Synapse Forge
lysanderl@janusd.io
https://lysander.bond/synapse
```

---

## 模板 B — 中文版

```
Subject: 欢迎加入 Synapse Forge — 你是 Founding Member #{FOUNDING_NUMBER}

{NAME}，你好：

感谢申请。{PERSONAL_HOOK — 引用对方申请信里的一个具体点，例如："你信里提到当前团队在多个 Claude 会话之间持续丢失上下文 — 这正是执行链和 active_tasks.yaml 机制要解决的问题。"}

你被录取了。你是 Founding 30 中的 #{FOUNDING_NUMBER}。

以下是你现在拥有的，以及接下来一周会发生的事。

## 你现在拥有的

1. **Founding Member #{FOUNDING_NUMBER}** — 我们发布 co-creators 名单时，你的名字永久出现在 Synapse 网站。
2. **Pro 订阅终身免费** — 未来商业化 tier 启动后，你的团队保留完整 Pro 权限，永久有效。
3. **每季度 1 小时 Lysander 咨询** — 架构 / 推广 / 落地难题，由你发起预约。
4. **新模块优先使用权** — Janus（建筑数字化）、Stock（量化交易），以及未来所有模块。

## 本周会发生的事

- Slack / Discord 频道邀请链接：{INVITE_LINK}
- Founding Resource Pack：{RESOURCE_LINK}
  - 开源仓库
  - 个人化 CLAUDE.md 模板
  - Quick Start 指南（5 分钟）
  - 72 小时部署 Check 表单
- 7 天内一次 30 分钟视频 onboarding（回此邮件给我 3 个你时区的空档，我来挑一个）

## 我们希望你做到

1. 2 周内完成首次 Synapse 部署（CLAUDE.md 个人化配置 + 首次 dispatch 跑通）
2. 每月至少一次结构化反馈（模板在 Slack 频道）
3. 允许我们在学习库中匿名引用你的使用经验（公开署名前一定先征得你同意）
4. 能来的时候参加每周五的 Slack 站会。异步、低噪声。

## 一个小请求

收到此邮件 72 小时内，麻烦花 5 分钟填下 Resource Pack 里的 Deployment Check 表单。这样我们可以尽早发现你的第一个阻塞点，而不是两周后才知道。

我这边先写这么多。欢迎你。Founding 30 马上要变成真正可见的事物了。

祝好，
Lysander
Synapse Forge CEO
lysanderl@janusd.io
https://lysander.bond/synapse
```

---

## 附件：拒绝邮件模板

> 评估分数 ≤ 12 时使用。语气：感谢 + 开源免费提示 + 保留联系。

### English

```
Subject: Re: Synapse Forge Beta Application — Thanks, and an alternative

Hi {NAME},

Thanks for your interest in Synapse Forge's closed beta. After reading through the applications, we are keeping the Founding 30 intentionally tight this round, and I can't offer you a spot this time.

That said — Synapse is free and open source. You can use the full system today at https://lysander.bond/synapse/get-started. If you hit something worth discussing, the GitHub Discussions are actively monitored and I reply there personally.

We are planning a second intake down the line. If you'd like me to keep your email on file for that, just reply "keep me in".

Best,
Lysander
```

### 中文

```
Subject: Re: Synapse Forge Beta 申请 — 感谢与替代方案

{NAME}，你好：

感谢你对 Synapse Forge 封闭测试的申请。这一轮我们有意控制 Founding 30 的招募规模，这次没办法为你保留席位。

不过 — Synapse 是开源免费的，你现在就可以完整使用整套系统：
https://lysander.bond/synapse/get-started

如果遇到值得讨论的问题，GitHub Discussions 活跃维护中，我会亲自回复。

我们后续会有第二批次招募。如果希望我把你的邮箱留存到下一轮候选，直接回复一句 "保留我" 即可。

祝好，
Lysander
```

---

## 变量占位符说明

| 占位符 | 填写方式 |
|--------|----------|
| `{FOUNDING_NUMBER}` | 从 advocate-list.md 取当前序号（001, 002, ..., 030） |
| `{FIRST_NAME}` / `{NAME}` | 按对方申请邮件中的署名 |
| `{PERSONAL_HOOK}` | 1-2 句，必须引用对方申请信里的具体内容 |
| `{INVITE_LINK}` | Slack / Discord 邀请链接（阶段 B 启动前由 growth_lead 统一生成常驻链接） |
| `{RESOURCE_LINK}` | Founding Resource Pack 的公开链接（Google Drive / Notion / GitHub page） |

---

## 发送前 Checklist

- [ ] Founding Number 已从 advocate-list.md 取得，且该号码未被占用
- [ ] {PERSONAL_HOOK} 已替换成对方申请信的真实引用
- [ ] 邀请链接可点击（本人先点一次验证）
- [ ] Resource Pack 链接可访问
- [ ] 邮件发出后 → 立即在 advocate-list.md 更新状态为"已接受"+ 填入 Founding Number + 接受日期
