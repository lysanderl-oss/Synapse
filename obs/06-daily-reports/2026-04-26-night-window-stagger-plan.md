# 22:00-22:45 拥塞窗口错峰方案

**调研日期**：2026-04-26 Dubai
**执行者**：harness_engineer（子 Agent，纯只读调研）
**Lysander 角色**：派单方 / 审查方
**总裁批准要点**：22:00-22:45 IO 拥塞窗口（5 个任务）每半小时错开一个
**红线**：本报告仅产出方案，不修改任何 cron schedule。

---

## 一、当前任务实证（22:00-22:45 Dubai 拥塞窗口）

精确还原自 `2026-04-26-all-scheduled-tasks-inventory.md`：

| # | 任务名 | 当前时间（Dubai） | UTC cron | 系统位置 | 用途 |
|:-:|------|:----:|:----:|------|------|
| 1 | Blog Pipeline (cloud-native) | 22:00 | `0 18 * * *` | GitHub Actions（`.github/workflows/blog-publish.yml`） | 云端博客发布管线 |
| 2 | daily-session-summary | 22:00 | `0 22 * * *` | lysander-server user cron（ubuntu） | 每日会话摘要生成 |
| 3 | archive-sessions | 22:30 | `30 22 * * *` | lysander-server user cron（ubuntu） | 会话归档 |
| 4 | harness-daily-publish | 22:30 | `30 22 * * *` | lysander-server user cron（ubuntu） | Harness 日报发布 |
| 5 | wechat-blog-draft | 22:45 | `45 18 * * *` | n8n（`LGkeWFUdYx5X7vgP`） | 微信公众号草稿生成 |

**实证结论**：5 个任务，分布在 3 个系统（GH Actions × 1、lysander-server cron × 3、n8n × 1），其中 22:00 双发 + 22:30 双发 + 22:45 单发。

---

## 二、错峰设计（每半小时一个）

### 排序原则

1. **业务依赖优先**：`blog-publish` 必须最早 — 它是产出源头，下游 `blog-heartbeat`（23:00）和 `wechat-blog-draft` 都依赖其输出
2. **数据依赖次之**：`daily-session-summary` 须在 `archive-sessions` 之前（先摘要再归档）
3. **生成与消费同序**：`harness-daily-publish` 依赖一日内的 harness 错误数据（`harness-collect-errors` 19:00 已完成），可灵活排
4. **n8n 草稿排末**：`wechat-blog-draft` 仅做草稿，无下游硬依赖，最后排不影响业务

### 时间表

| 错峰前 | 错峰后 | 任务 | 排序理由 |
|:----:|:----:|------|------|
| 22:00 | **22:00**（保持） | blog-publish | 产出源头，下游全部依赖，必须最早 |
| 22:00 | **22:30** | daily-session-summary | 会话摘要 — archive 的前置 |
| 22:30 | **23:00** | archive-sessions | 归档 — 依赖 summary，挪后半小时 |
| 22:30 | **23:30** | harness-daily-publish | 日报发布 — 数据已就绪，挪到末尾窗口 |
| 22:45 | **00:00**（次日） | wechat-blog-draft | 草稿生成，无硬下游，跨日影响最小 |

### cron 表达式映射

| 任务 | 旧 cron（UTC） | 新 cron（UTC） | 旧 Dubai | 新 Dubai |
|------|:----:|:----:|:----:|:----:|
| blog-publish | `0 18 * * *` | `0 18 * * *`（不变） | 22:00 | 22:00 |
| daily-session-summary | `0 22 * * *` | `30 18 * * *` | 22:00 | 22:30 |
| archive-sessions | `30 22 * * *` | `0 19 * * *` | 22:30 | 23:00 |
| harness-daily-publish | `30 22 * * *` | `30 19 * * *` | 22:30 | 23:30 |
| wechat-blog-draft | `45 18 * * *` | `0 20 * * *` | 22:45 | 00:00（次日 Dubai） |

**注**：lysander-server 的 cron 表达式按服务器时区（UTC）计算。需在迁移时确认服务器 TZ 设置。

---

## 三、依赖关系考虑

```
blog-publish (22:00)
    ├──> blog-heartbeat (23:00, GH Actions, 不在本窗口)
    └──> wechat-blog-draft (新 00:00) — 拉取 blog 内容生成草稿

daily-session-summary (新 22:30)
    └──> archive-sessions (新 23:00) — 必须在 summary 之后

harness-collect-errors (19:00, 不在本窗口)
    └──> harness-daily-publish (新 23:30) — 数据早已就绪，挪后无影响
```

无循环依赖，错峰后排序与业务流向一致。

---

## 四、风险

### 风险 1：GitHub Actions cron 漂移

实证记录显示 GH Actions cron **漂移 1-3 小时是常态**（参见 `2026-04-26-cron-audit-report.md`）。即便错峰半小时，blog-publish 实际可能仍延迟到 22:30+ 触发，与 daily-session-summary（新 22:30）再次叠加。

**缓解**：错峰目标是**降低概率而非保证不重叠**，本方案将 5 个任务跨度从 45 分钟拉长到 120 分钟，重叠概率大幅下降。

### 风险 2：跨日影响 — wechat-blog-draft 改至 00:00

- **任务恢复逻辑**：`task-resume.yml`（06:00 Dubai）的"今日任务"基线如果用 Dubai 日期判断，则 wechat-blog-draft 会变成"次日的今日任务"，需确认此逻辑是否兼容
- **报告归属**：若产出日报标题用 Dubai 日期，wechat-blog-draft 在 00:00 触发会归属到次日报告，与 22:00 的 blog-publish 错位
- **缓解备选方案**：将 wechat-blog-draft 排到 23:45（仍保持半小时间距，但与 blog-heartbeat 23:00 仅差 45 分钟）— 待 Lysander 决策

### 风险 3：lysander-server 时区

如服务器 TZ 不是 UTC（如 Asia/Dubai），新 cron 表达式需重算。建议执行前先 SSH 验证 `date && timedatectl`。

### 风险 4：archive-sessions 与 harness-daily-publish 旧时间相同

旧 cron 两者都是 `30 22 * * *`，意味着它们目前**已经强相关**。错峰后拉开 30 分钟，IO 竞争降低；但若 harness-daily-publish 依赖 archive 完成的归档数据，需确认顺序无误（当前设计：archive 23:00 → harness-daily-publish 23:30，符合数据流向）。

---

## 五、实施清单

### 修改文件总览

| # | 任务 | 系统 | 修改位置 | 旧值 | 新值 |
|:-:|------|------|------|:----:|:----:|
| 1 | blog-publish | GH Actions | `.github/workflows/blog-publish.yml` L?（schedule.cron） | `0 18 * * *` | （不变） |
| 2 | daily-session-summary | lysander-server user cron | `crontab -e`（user=ubuntu） | `0 22 * * *` | `30 18 * * *` |
| 3 | archive-sessions | lysander-server user cron | `crontab -e`（user=ubuntu） | `30 22 * * *` | `0 19 * * *` |
| 4 | harness-daily-publish | lysander-server user cron | `crontab -e`（user=ubuntu） | `30 22 * * *` | `30 19 * * *` |
| 5 | wechat-blog-draft | n8n | workflow ID `LGkeWFUdYx5X7vgP` 的 schedule trigger node | `45 18 * * *` | `0 20 * * *` |

### 实施步骤建议

1. **lysander-server cron**（3 项）：SSH 进入 lysander-server，`crontab -e -u ubuntu`，按上表替换 3 行；执行后 `crontab -l` 复核
2. **n8n**（1 项）：通过 n8n UI 或 API（PATCH `/workflows/LGkeWFUdYx5X7vgP`）修改 schedule node cron 字段
3. **GH Actions**（0 项）：blog-publish 保持不变，无需修改
4. **回滚预案**：保留原 cron 文本备份至 `obs/06-daily-reports/2026-04-26-night-window-stagger-rollback.txt`，48 小时观察期内异常立即回退

### 验证清单

- [ ] 实施后第 1 个 24h：每 30 分钟检查 5 个任务是否按新时间触发，记录实际触发时间
- [ ] 实施后第 2 个 24h：检查日报归属、归档数据、wechat-blog-draft 内容是否正常
- [ ] 实施后第 7 天：统计漂移分布，对比错峰前后 IO 重叠概率

---

## 六、给 Lysander 的一行

`✅ 22:00-22:45 实证 5 任务（GH 1 / lysander-cron 3 / n8n 1），错峰方案（每半小时，22:00→22:30→23:00→23:30→00:00）已设计，跨日风险有备选 23:45 方案待选，等批准执行。`
