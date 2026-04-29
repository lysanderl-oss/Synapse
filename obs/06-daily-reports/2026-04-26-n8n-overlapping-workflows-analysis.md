# n8n 重复任务调研报告

**调研日期**：2026-04-26
**调研者**：n8n_ops 子 Agent（Lysander 派单）
**红线**：仅只读调研，未修改任何 workflow
**触发问题**：总裁 Q3（"06:00 n8n WF-XX 是什么"）+ Q5（"WF5-task-status / GH intel-action 删哪个"）

---

## 一、Q3 答复：06:00 Dubai n8n workflow 实证

### 1.1 服务器时区推断

通过 WF-13 实际执行历史反推：cron `0 6 * * *` 实际触发于 **UTC 10:00:00.0xx**，连续 5 天稳定。
意味着 n8n 服务器 cron 解释器把 `hour=6` 当作 **本地时间**，本地时间 06:00 = UTC 10:00 → **服务器时区 = UTC-4**（疑似 EDT/AST，非 Dubai 时区）。
即：`0 6 * * *` cron 实际 = UTC 10:00 = **Dubai 14:00**，**不是总裁理解的 Dubai 06:00**。

### 1.2 active workflow 中 cron `0 6 * * *` 的清单

| ID | 真实名称 | 节点链 | 业务用途 |
|---|---|---|---|
| `ZGVHjA3EQooKKrTc` | **Synapse-WF5-task-status** | Schedule Trigger → noOp `Task Status Check` (log "Task status check at 6am") | **空壳 stub，无业务逻辑** |
| `ou2B6aGnpTsXlgZx` | **WF-13 Asana进度同步** | Schedule Trigger → 查询交付中项目 → 提取项目列表 → 检查跳过 → 获取 Asana 任务 → 计算进度 → 更新 Notion 进度 | 每日同步 Asana 任务进度到 Notion 项目卡（**真正干活的**） |

### 1.3 结论

总裁清单里写的"06:00 n8n WF-XX"，实际上：

- 实际触发时间是 **Dubai 14:00**（不是 06:00），因服务器时区配置为 UTC-4
- **Synapse-WF5-task-status** 是 2026-04-22 创建的空壳 noOp，没业务作用
- **WF-13 Asana进度同步** 才是真正每日跑的有效任务，把 Asana 项目进度同步到 Notion

> **精确答案**：清单里的"06:00 WF-XX"应该是 **`WF-13 Asana进度同步`**（拉 Asana 算进度推 Notion），但其实际触发时刻是 **Dubai 14:00 而非 06:00**。"06:00" 是 cron 表达式里的 hour=6 在 UTC-4 服务器上的字面值，不是实际触发时刻。

---

## 二、Q5 答复：n8n WF5-task-status vs GH intel-action

### 2.1 n8n Synapse-WF5-task-status 实证

- **ID**：`ZGVHjA3EQooKKrTc`
- **当前真名**：`Synapse-WF5-task-status`（**未被改名为 WF-14**，WF-14 是独立的另一个 workflow）
- **创建时间**：2026-04-22T08:10:13Z
- **active**：true
- **timezone**：未显式设置（用服务器默认 UTC-4）
- **节点链**（共 2 个节点）：
  1. Schedule Trigger（cron `0 6 * * *`）
  2. noOp `Task Status Check`（参数：`{operation: "log", message: "Task status check at 6am"}`）
- **执行历史**：API 查询返回空，未见执行记录
- **业务用途**：**无任何实际业务逻辑**，纯空壳/占位符

### 2.2 GH intel-action 用途

- **文件**：`.github/workflows/intel-action.yml`
- **触发**：cron `0 6 * * *` UTC = **Dubai 10:00**（GH Actions runner 时区固定 UTC，不会漂移）
- **业务流程**：
  1. checkout repo + 装 Python 依赖（anthropic、ruamel.yaml 等）
  2. 跑 `scripts/intelligence/action_agent.py`
  3. action_agent.py 读 `obs/06-daily-reports/{昨日}-intelligence-daily.html`
  4. 调 Claude 4 做 4 专家评分 + 决策 + 派单
  5. 输出 `obs/06-daily-reports/{今日}-action-report.md`
  6. 自动 commit & push（含冲突 rebase 重试 3 次）
  7. Slack 通知

### 2.3 对比矩阵

| 维度 | n8n Synapse-WF5-task-status | GH intel-action |
|------|---|---|
| 业务领域 | （无） | 情报评估与决策派单 |
| 数据源 | 无 | obs/06-daily-reports/*-intelligence-daily.html |
| 输出 | 无（仅 noOp log） | obs/06-daily-reports/*-action-report.md + Slack |
| 触发表达式 | `0 6 * * *`（n8n） | `0 6 * * *`（GH UTC） |
| 实际触发时刻 | Dubai 14:00（服务器 UTC-4） | Dubai 10:00（GH 固定 UTC） |
| 节点 / 步骤数 | 2（trigger + noOp） | 5+（含 Claude API 调用与 commit） |
| 依赖 secrets | 无 | ANTHROPIC_API_KEY、SLACK_WEBHOOK_N8N |
| 创建于 | 2026-04-22 | （早于 Week 2 切流，2026-04-24 启用 schedule） |

### 2.4 是否真重复？

**不重复，但 n8n WF5 是无用空壳。**

- 业务上：完全不重叠。GH intel-action 做情报评估，WF5 啥也不做
- 实际触发时间：**也错峰**（Dubai 14:00 vs Dubai 10:00），不冲突
- 名字误导：`Synapse-WF5-task-status` 与 `task-status` 命名容易让人以为它在跑任务状态检查；实际只有 noOp log，**名字承诺与实现不一致**

### 2.5 删除建议

> **强烈推荐删除 `Synapse-WF5-task-status`（n8n ID `ZGVHjA3EQooKKrTc`）**

**理由**（按权重排序）：

1. **零业务价值**：唯一节点是 noOp `log`，没有 HTTP/数据库/Slack/任何外部副作用
2. **命名误导**：名字 `task-status` 暗示任务状态监控，但实现是空壳，会让维护者误判为"已实现"
3. **占用 active 配额**：n8n 当前 26 个 active workflow，每多一个空壳增加审计负担
4. **同源孤儿**：与 `Synapse-WF1-intelligence-action`（cron 10:00 → 调 webhook `action-notify`）和 `Synapse-WF2-action-notify`（webhook 收到 → noOp `Log Action`）是同批次创建的 stub 三件套（均 2026-04-22 创建），**这一整套都是空壳**，应一并清理：
   - `Synapse-WF1-intelligence-action`（z6pcG11dazl86P2F）
   - `Synapse-WF2-action-notify`（bNjnW0pUKxUhr1QF）
   - `Synapse-WF5-task-status`（ZGVHjA3EQooKKrTc）
5. **GH intel-action 已是真实现**：情报评估流水线已在 GH Actions 上线（含 Claude API、commit、Slack），n8n 端的 stub 完全无必要

**保留 GH intel-action**：唯一有业务逻辑的实现，删除会破坏情报闭环管线。

### 2.6 附加建议

- 若日后想用 n8n 做编排，应**重写**这三个 stub，而不是在空壳上加节点（容易误以为已实现）
- 服务器时区配置 UTC-4 是个独立问题，建议另行核查（cron 表达式与触发时刻不直观，已造成总裁误读"06:00"为 Dubai 06:00）

---

## 三、给 Lysander 的一行

`✅ Q3 = WF-13 Asana进度同步（实际跑在 Dubai 14:00 不是 06:00，是服务器 UTC-4 时区漂移），Q5 推荐删 Synapse-WF5-task-status（n8n stub 空壳，含同批次 WF1/WF2 共 3 个孤儿 workflow 应一并清理；GH intel-action 是唯一有业务逻辑的实现，必须保留）`
