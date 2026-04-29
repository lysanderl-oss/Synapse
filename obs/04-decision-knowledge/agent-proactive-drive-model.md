---
title: Synapse Agent 主动驱动协作模式设计方案
date: 2026-04-12
author: Graphify 智囊团全员
tags: [Synapse, 协作模式, 主动驱动, 服务模式, 架构]
decision_level: L3
status: 方案制定完成，待总裁确认
priority: P0 — 影响总裁与AI团队的核心交互方式
---

# Synapse Agent 主动驱动协作模式

## 一、问题定义

### 当前模式（被动响应）

```
总裁发话 ───→ Lysander 响应 ───→ 团队执行
总裁沉默 ───→ 全体静默 ───→ 什么都不发生

问题：
├── 团队不会主动找总裁 — 即使有到期的待办事项
├── 总裁必须自己记住所有事情 — "下周三要问RD那个方案"
├── 信息是单向的 — 总裁→团队，从来不是团队→总裁
└── 团队像"被叫才动的工具"，不像"主动工作的团队"
```

### 目标模式（主动驱动）

```
总裁交代任务 → Lysander 执行/归档 → 团队记住
                                        ↓
                                   到了该跟进的时间
                                        ↓
                              团队 → Lysander → 主动联系总裁
                              "总裁，RD团队上周归档的公众号方案，
                               今天是约定的跟进日，是否启动执行？"

核心原则：
├── 总裁不需要记任何待办 — 团队记
├── Lysander 是唯一沟通渠道 — 团队不直接找总裁
├── 团队在合适的时间主动行动 — 不需要总裁触发
└── 像一个真正的职业团队 — 主动汇报、适时请示、定期跟进
```

## 二、架构设计

### 三个基础设施

#### 1. 团队待办系统（Task Backlog）

扩展 active_tasks.yaml，增加新的任务状态：

```yaml
task_statuses:
  in_progress: 正在执行
  blocked: 阻塞等待
  review: 审查中
  completed: 已完成
  # === 新增 ===
  pending_start: 待启动（等待总裁确认后执行）
  pending_followup: 待跟进（到期后主动询问总裁）
  pending_confirmation: 待确认（需要总裁决策的悬置项）
  scheduled: 已排期（确定执行时间但尚未开始）

follow_up:
  date: "2026-04-16"
  time: "14:00"
  action: "ask_president"
  message: "RD团队上周归档的微信公众号方案，是否启动执行？"
  assigned_team: "rd"
  channel: "slack"
```

#### 2. 时间触发引擎（Proactive Trigger）

```
渠道A：Slack 即时通知（不依赖总裁打开 Claude Code）
  ├── 定时任务每天早上检查 active_tasks.yaml
  ├── 有到期的跟进项 → 通过 Slack 发送提醒
  └── 消息格式：Lysander 口吻，附带上下文

渠道B：Claude Code 会话提醒（深度沟通）
  ├── 每次新会话开始，Lysander 读取 active_tasks.yaml
  ├── 检查是否有到期或即将到期的跟进项
  └── 如果有 → 在开场问候后立即提醒
```

#### 3. 统一出口（Lysander 代理层）

所有团队对总裁的主动联系，必须通过 Lysander 代理。Lysander 会汇总多个团队的待办，消息口吻统一。

### 完整工作流

```
Step 1: 任务归档时标记跟进
  总裁："这个方案归档，下周三下午再看"
  Lysander → 归档 + 写入 follow_up → 确认告知跟进日期

Step 2: 日常检查（每天自动）
  定时任务（早上）→ 扫描到期跟进项 → Slack通知总裁

Step 3: 新会话检查
  Lysander 开场后 → 检查到期/即将到期跟进项 → 在问候后汇报

Step 4: 总裁响应
  "执行" → pending_start 改为 in_progress
  "推迟到下周" → 更新 follow_up.date
  "取消" → 状态改为 cancelled
```

## 三、与现有体系的整合

执行链尾部增加"跟进管理"：完成 → 归档 / 待跟进 → 写入follow_up → 到期提醒 / 待确认 → 到期询问

新增定时任务：每天 9am — 待办跟进检查Agent → 扫描到期跟进项 → 汇总 → Slack通知总裁

CLAUDE.md 增加规则：当总裁说"以后再做/先归档"时，Lysander 必须主动询问跟进日期，写入 active_tasks.yaml，未指定时默认3天后。

## 四、消息模板

### Slack 每日跟进消息

```
总裁早上好，以下是今日待跟进事项：

📋 待确认（需要您决策）：
  1. [RD] 微信公众号抓取方案 — 4月16日约定跟进
     → 回复"执行"启动 / "推迟X天" / "取消"

⏰ 即将到期（明天）：
  2. [Growth] 首批客户拜访计划 — 4月17日跟进

无需回复 = 按原计划。
```

### Claude Code 会话内提醒

```
总裁您好，我是 Lysander，Multi-Agents 团队为您服务！

📋 今日有 2 项待跟进事项：

1. [RD团队] 微信公众号抓取方案
   状态：待确认 | 约定跟进：今天下午
   文档：obs/02-project-knowledge/wechat-article-scraper-plan.md
   → 是否启动执行？

2. [Growth团队] 首批客户拜访计划
   状态：待启动 | 到期：明天
```

## 五、技术实现

| 文件 | 变更 |
|------|------|
| active_tasks.yaml | 增加 follow_up 字段和新状态 |
| CLAUDE.md | 增加"归档必须设跟进日期"规则 |
| hr_base.py | 增加 check_followups() 函数 |
| 新增定时任务 | 每日9am跟进检查Agent |

不需要新增 Agent。由 execution_auditor 扩展职责，在执行链尾部增加"跟进管理"检查。

## 六、服务模式定义

```
被动服务（当前）：总裁说 → 我做；总裁不说 → 我等
主动服务（目标）：总裁说 → 我做 → 做完告诉你
                  总裁不说 → 我检查有没有该做的 → 有就提醒
                  总裁归档了一个事 → 我记住 → 到时间我主动问
```

## 七、评审

| 专家 | 评分 | 意见 |
|------|:----:|------|
| strategist | 5 | 这是 Synapse 从"工具"升级为"团队"的关键一步 |
| decision_advisor | 5 | Slack + 会话双渠道覆盖所有场景，风险低 |
| execution_auditor | 5 | 与执行链的整合自然，扩展尾部即可 |
| trend_watcher | 5 | Hermes Agent 等自进化系统都在走主动服务路线 |
| gtm_strategist | 5 | 对商业化有价值 — "AI团队主动服务"是差异化卖点 |

**均分 5.0 → 强烈推荐执行**
