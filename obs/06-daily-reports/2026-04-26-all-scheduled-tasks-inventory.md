# Synapse 体系全量定时任务清单（2026-04-26）

**调研日期**：2026-04-26 18:05 Dubai
**调研维度**：GitHub Actions / Windows Task Scheduler / n8n / Claude Code Routines / lysander-server systemd+cron
**执行者**：harness_engineer（子 Agent，纯只读调研）
**Lysander 角色**：派单方 / 审查方

---

## 一、总览

| 维度 | Active | Disabled | 健康 | 异常 |
|------|:------:|:--------:|:----:|:----:|
| GitHub Actions cron | 7 | 0 | 7 | 0 |
| Windows Task Scheduler（Synapse 相关） | 2 | 1 | 1 | 1（NotionDailySync 0x80070002） |
| n8n schedule trigger（active） | 14 | — | 14 | 0 |
| Claude Code Routines | 0 | 6 | — | — |
| lysander-server systemd timer | 16 | 0 | 16 | 0 |
| lysander-server user crontab | 10 | 0 | 10 | 0 |
| lysander-server root crontab | 1 | 0 | 1 | 0 |
| **合计 Active 定时任务** | **50** | **7** | **49** | **1** |

---

## 二、GitHub Actions cron（synapse-ops 仓库）

| Workflow | yml 路径 | UTC cron | Dubai 时间 | 状态 |
|----------|---------|----------|-----------|:----:|
| n8n Workflow Snapshot | `n8n-snapshot.yml` | `0 1 * * *` | 05:00 | active |
| Task Auto-Resume | `task-resume.yml` | `0 2 * * *` | 06:00 | active |
| Intelligence Daily Report | `intel-daily.yml` | `0 4 * * *` | 08:00 | active |
| Intelligence Action Report | `intel-action.yml` | `0 6 * * *` | 10:00 | active |
| Intelligence Heartbeat Check | `heartbeat-check.yml` | `0 9 * * *` | 13:00 | active |
| Blog Pipeline (cloud-native) | `blog-publish.yml` | `0 18 * * *` | 22:00 | active |
| Blog Pipeline Heartbeat | `blog-heartbeat.yml` | `0 19 * * *` | 23:00 | active |

仓库：`lysanderl-glitch/synapse-ops`，全部 active，无 disabled。

---

## 三、Windows Task Scheduler（本机）

| TaskName | State | LastRun | LastResult | NextRun | 备注 |
|----------|:-----:|---------|:----------:|---------|------|
| Synapse-NotionDailySync | Ready | 2026/4/26 18:00 | **0x80070002** | 2026/4/27 18:00 | ⚠️ 文件未找到错误 |
| Synapse-SessionsWatcher | Ready | 2026/4/26 17:58 | 0x00000000 | 2026/4/26 18:03（5分钟一次） | 健康 |
| Synapse-WorklogExtractor | **Disabled** | 2026/4/26 01:36 | 0x80070002 | — | 已禁用 |

---

## 四、n8n schedule（lysander-server，14 个 active）

| ID | Name | Cron / Interval | Dubai 触发 |
|----|------|----------------|-----------|
| AnR20HucIRaiZPS7 | WF-01 项目初始化 | every 5 min | 持续 |
| IXEFFpLwnlcggK2E | WF-02 任务变更通知 | `*/30 5-14 * * 1-5` | 工作日 09:00–18:00 每 30 分钟 |
| uftMqCdR1pRz079z | WF-03 里程碑提醒 | `0 5 * * 1-5` | 工作日 09:00 |
| 40mJOR8xXtubjGO4 | WF-04 PMO周报自动化 | `0 1 * * 1` | 周一 05:00 |
| rlEylvNQW55UPbAq | WF-05 逾期任务预警 | `0 1 * * 1-5` | 工作日 05:00 |
| ZGVHjA3EQooKKrTc | Synapse-WF5-task-status | `0 6 * * *` | 每日 10:00 |
| knVJ8Uq2D1UZmpxr | WF-06 任务依赖链通知 | every 60 min | 持续 |
| seiXPY0VNzNxQ2L3 | WF-07 会议纪要 → Asana | every 30 min | 持续 |
| VaFr43GafxDrPvEE | WF-11 WBS导入触发 | every 5 min | 持续 |
| ou2B6aGnpTsXlgZx | WF-13 Asana进度同步 | `0 6 * * *` | 每日 10:00 |
| g6wKsdroKNAqHHds | WF-14 章程确认 Assignee同步 | every 5 min | 持续 |
| z6pcG11dazl86P2F | Synapse-WF1-intelligence-action | `0 10 * * *` | 每日 14:00 |
| 203fXfKkfqD1juuT | Synapse-Audit-Webhook-Coverage | `5 5 * * *` | 每日 09:05 |
| LGkeWFUdYx5X7vgP | wechat-blog-draft | `45 18 * * *` | 每日 22:45 |

n8n 总 active workflow 数：26（其中 14 含 schedule trigger，其余 12 为 webhook 触发）。

---

## 五、Claude Code Routines

**当前 active = 0**（CronList 验证：No scheduled jobs）。

历史 6 个 Routine 全部 disabled：

| Name | Schedule | Status |
|------|---------|:------:|
| Active Task Auto-Resume | 06:00 Dubai | ⛔ disabled |
| Daily Intelligence + Evolution Analysis | 08:00 Dubai | ⛔ disabled |
| Intelligence Action Pipeline | 10:00 Dubai | ⛔ disabled |
| Daily Follow-up Check | 09:00 Dubai | ⛔ disabled |
| Weekly HR Audit | Mon 07:00 | ⛔ disabled |
| Weekly Evolution Report | Fri 12:00 | ⛔ disabled |

前 3 个已迁移到 GitHub Actions（task-resume / intel-daily / intel-action）。

---

## 六、lysander-server systemd timer（16 个）

系统级 timer（Ubuntu 自带 + Synapse 相关）：

| Timer | 下次触发 | 用途 |
|-------|---------|------|
| stock-trading-rebuild-progress.timer | 19:00 Dubai 每日 | Synapse 自有 — 股票交易进度 |
| certbot.timer | 01:44 + 13:44 每日 | SSL 证书续签 |
| sysstat-collect.timer | 每 10 分钟 | 系统监控 |
| sysstat-summary.timer | 00:07 每日 | 系统摘要 |
| fwupd-refresh.timer | 每日 | 固件更新检查 |
| dpkg-db-backup.timer | 00:00 每日 | dpkg 数据库备份 |
| logrotate.timer | 00:00 每日 | 日志轮转 |
| apt-daily.timer | 00:52 每日 | apt 元数据更新 |
| apt-daily-upgrade.timer | 06:27 每日 | apt 升级检查 |
| man-db.timer | 04:28 每日 | man 索引 |
| update-notifier-download.timer | 09:53 每日 | 升级提醒 |
| update-notifier-motd.timer | 每日 | MOTD 更新 |
| systemd-tmpfiles-clean.timer | 10:03 每日 | 临时文件清理 |
| motd-news.timer | 20:11 每日 | MOTD 新闻 |
| fstrim.timer | 周一 00:08 | 磁盘 TRIM |
| e2scrub_all.timer | 周日 03:10 | 文件系统检查 |

仅 1 个为 Synapse 业务（stock-trading-rebuild-progress），其余 15 个为系统级。

---

## 七、lysander-server crontab

### user (ubuntu) crontab — 10 条

| Cron | 命令 | Dubai 触发 |
|------|------|----------|
| `30 * * * *` | knowledge-base/sync.sh | 每小时 :30 |
| `0 22 * * *` | daily-session-summary.sh | 每日 22:00 |
| `30 22 * * *` | archive-sessions.sh | 每日 22:30 |
| `0 9 * * 1-5` | harness-phase2-daily.sh | 工作日 09:00 |
| `0 9 * * 1` | harness-weekly.sh | 周一 09:00 |
| `0 15 * * 5` | harness-weekly.sh | 周五 15:00 |
| `0 10 1-3 * *` | harness-monthly.sh | 月初 1-3 日 10:00 |
| `0 19 * * *` | harness-collect-errors.sh | 每日 19:00 |
| `30 22 * * *` | harness-daily-publish.sh | 每日 22:30 |
| `0 4 * * *` | hr_base.py sync | 每日 04:00 |

### root crontab — 1 条

| Cron | 命令 |
|------|------|
| `*/5 * * * *` | stargate (腾讯云监控代理) |

---

## 八、按 Dubai 时间排序的 24h 任务图

```
00:00 lysander: dpkg-db-backup, logrotate
00:07 lysander: sysstat-summary
00:08 lysander: fstrim (周一)
00:52 lysander: apt-daily
01:44 lysander: certbot.timer (auto-renew)
03:10 lysander: e2scrub (周日)
04:00 lysander cron: hr_base.py sync
04:28 lysander: man-db
05:00 GH Actions: n8n-snapshot
05:00 n8n: WF-04 PMO周报 (周一)、WF-05 逾期任务 (工作日)
06:00 GH Actions: task-resume
06:27 lysander: apt-daily-upgrade
09:00 n8n: WF-03 里程碑、Synapse-Audit-Webhook (09:05)
09:00 lysander cron: harness-phase2-daily, harness-weekly (周一)
09:00–18:00 n8n: WF-02 任务变更 (每30min, 工作日)
09:53 lysander: update-notifier-download
10:00 GH Actions: intel-action
10:00 n8n: Synapse-WF5-task-status, WF-13 Asana同步
10:03 lysander: tmpfiles-clean
13:00 GH Actions: heartbeat-check
13:44 lysander: certbot.timer (第二次)
14:00 n8n: WF-01 intelligence-action
15:00 lysander cron: harness-weekly (周五)
19:00 lysander: stock-trading-rebuild-progress
19:00 lysander cron: harness-collect-errors
20:11 lysander: motd-news
22:00 GH Actions: blog-publish
22:00 lysander cron: daily-session-summary
22:30 lysander cron: archive-sessions, harness-daily-publish
22:45 n8n: wechat-blog-draft
23:00 GH Actions: blog-heartbeat
持续: n8n WF-01/06/07/11/14、Win SessionsWatcher
```

---

## 九、关键发现

1. **Claude Code Routines 完全清零** — 6 个全 disabled，CronList 验证 0 active。3 个核心管线已迁移 GH Actions，无遗留。

2. **唯一异常**：`Synapse-NotionDailySync`（Windows Task）连续返回 `0x80070002`（文件未找到），需排查脚本路径或恢复 disabled。

3. **任务密度最高时段**：22:00–22:45 Dubai（4 个任务连发：blog-publish + daily-session-summary + archive-sessions + harness-daily-publish + wechat-blog-draft）。建议监控 IO 是否有冲突。

4. **重复触发可疑点**：`Synapse-WF5-task-status`（n8n, 10:00）与 `intel-action`（GH Actions, 10:00）同时段，确认 n8n 这条是否还需要（已被 GH Actions 替代过 1 次）。

5. **持续高频任务**：n8n 有 4 个 every-5-min 触发器（WF-01/11/14 + Win SessionsWatcher 5min），构成 Synapse 实时层。

6. **lysander-server 业务负载轻**：systemd 16 个 timer 中仅 1 个为 Synapse 业务（stock-trading），其余皆系统维护；user cron 集中在 harness self-healing（5 条）+ session 归档（3 条）+ knowledge sync（1 条）+ HR sync（1 条）。

---

## 十、给 Lysander 的一行

`✅ 全量定时任务清单：5 维度共 50 条 Active（GH 7 / Win 2 / n8n 14 / Claude 0 / lysander-server 27），健康 49 / 异常 1（NotionDailySync 0x80070002）/ 禁用 7。报告已沉淀。`
