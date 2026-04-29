# 定时任务全量审计报告（2026-04-26）

**审计员**：integration_qa（Lysander 派单）
**审计时间**：2026-04-26 06:15 UTC（Dubai 10:15）
**仓库**：`lysanderl-glitch/synapse-ops`
**审计范围**：GitHub Actions 5 个 workflow，cron 配置 + 04-25 / 04-26 运行记录
**红线遵守**：仅查询，未修改任何 cron / 未触发任何 workflow run

---

## 一、当前 GitHub Actions cron 时间表

| UTC | Dubai | Workflow | File | 状态 | Workflow ID |
|-----|-------|----------|------|------|-------------|
| 01:00 | 05:00 | n8n Workflow Snapshot | `n8n-snapshot.yml` | active | 266155714 |
| 02:00 | 06:00 | Task Auto-Resume | `task-resume.yml` | active | 265904458 |
| 04:00 | 08:00 | Intelligence Daily Report | `intel-daily.yml` | active | 265904457 |
| 06:00 | 10:00 | Intelligence Action Report | `intel-action.yml` | active | 265904456 |
| 07:00 | 11:00 | Intelligence Pipeline Heartbeat Check | `heartbeat-check.yml` | active | 265933928 |

**5 个 workflow 全部 active，触发方式均为 `schedule + workflow_dispatch`。**

每个 workflow 都设置了 `concurrency` 组（n8n-snapshot / task-resume / intel-daily / intel-action / heartbeat 互不冲突的独立 group），`cancel-in-progress: false`（不取消进行中的 run）。

---

## 二、昨日 (2026-04-25) 运行情况

### 2.1 schedule 触发记录

| Workflow | 计划 UTC | 实际触发 UTC | 漂移 | 结论 |
|----------|---------|-------------|------|------|
| n8n-snapshot | 01:00 | **未运行** | n/a | workflow 04-25 09:32 才创建（看文件 mtime），昨日尚未生效 |
| task-resume | 02:00 | 04:27:53 | **+2h27m** | success |
| intel-daily | 04:00 | 05:43:45 | **+1h43m** | success |
| intel-action | 06:00 | 07:05:01 | **+1h05m** | success |
| heartbeat | 07:00 | 08:04:40 | **+1h04m** | **failure（按设计）** |

**昨日 schedule 触发 = 4 次，失败 = 1 次（heartbeat，设计上正确）。**

heartbeat 失败原因（已实证）：检查 04-24 日报 + 行动报告完整性 → `obs/06-daily-reports/2026-04-24-action-report.md` 缺失（因为 04-24 是 Week 2 切流首日，仅生成 daily，未生成 action）→ `healthy=false` → `sys.exit(1)` → GH Actions 标记红 + Slack 告警已正常投递（`status=200 slack_ok=true`，channel C0AV1JAHZHB）。这是预期行为，不是 bug。

### 2.2 workflow_dispatch 记录（04-25）

| 时间 UTC | Workflow | 状态 |
|---------|----------|------|
| 04:46:35 | intel-daily | success |
| 04:55:16 | intel-daily | success |
| 05:29:02 | intel-daily | success |
| 06:26:36 | intel-daily | success |

intel-daily 04-25 当日总共触发 5 次（4 次手动 + 1 次 schedule），全部 success。

### 2.3 失败 run

仅 heartbeat 1 次，按设计正确（见上）。

---

## 三、今日 (2026-04-26) 运行情况（截至 06:15 UTC）

| 计划 UTC | Workflow | 实际 UTC | 漂移 | 结论 |
|---------|----------|----------|------|------|
| 01:00 | n8n-snapshot | 04:21:33 | **+3h21m** | success（首次 schedule 运行） |
| 02:00 | task-resume | 04:51:13 | **+2h51m** | success |
| 04:00 | intel-daily | 06:01:40 | **+2h01m** | success |
| 06:00 | intel-action | **未触发** | 已超 15 min | **待观察**（drift 中或 skipped） |
| 07:00 | heartbeat | 未到时间 | n/a | 待 |

**关键观察**：今日 intel-action（06:00 UTC）截至 06:15 UTC 仍未触发，无 queued/in-progress 状态。考虑历史漂移 1-3h，预期将在 07:00-09:00 UTC 之间触发。**heartbeat 计划 07:00 UTC，可能在 intel-action 完成前即触发，导致再次误报失败**。

---

## 四、时间冲突分析

### 4.1 任务依赖关系

| 依赖关系 | 计划间隔 | 实际间隔（04-25） | 评估 |
|---------|---------|------------------|------|
| intel-action 依赖 intel-daily 当天产出 | 2h（04:00 → 06:00 UTC） | 1h21m（05:43 → 07:05） | 正常，足够 |
| heartbeat 检查前一天产出 | 独立（不依赖当天） | n/a | 独立，OK |
| task-resume 独立 | n/a | n/a | OK |
| n8n-snapshot 独立 | n/a | n/a | OK |

intel-daily → intel-action 计划间隔 2h、实际 ~1.3h，**当前 daily 运行 ~1m 完成，intel-action 等待充分**。无依赖风险。

### 4.2 push 冲突风险

4 个 workflow 会 commit + push 到 main：
- task-resume（push `agent-CEO/config/active_tasks.yaml`、`*-resume-summary.md`）
- intel-daily（push `*-intelligence-daily.html`）
- intel-action（push `*-action-report.md`）
- n8n-snapshot（push `harness/n8n-snapshots/`）

**计划时间间隔分析（UTC）**：
- 01:00 → 02:00（n8n → task-resume）：1h，安全
- 02:00 → 04:00（task-resume → intel-daily）：2h，安全
- 04:00 → 06:00（intel-daily → intel-action）：2h，安全

**实际漂移时间间隔（04-26）**：
- n8n-snapshot 04:21 → task-resume 04:51 → intel-daily 06:01：间隔 30min / 1h10m

**push 冲突保护**：
- task-resume / intel-action 实现了 3 次 retry + `git pull --rebase` 后重推（强保护）
- intel-daily 仅 `|| echo "Push skipped"`（**弱保护，不重试**）
- n8n-snapshot 实现了 3 次 retry + rebase（强保护）

**潜在风险**：intel-daily 与 task-resume 漂移后接近（30-40 min 间隔），如果同时 push 撞车，intel-daily 会丢更新（仅 echo skip 不重试）。

### 4.3 cron 漂移观察

GitHub Actions schedule cron 漂移在工作日早晨美东时段普遍 5-30 min，**本仓库观察到 1-3h 漂移**，超出常规范围。可能原因：
- 仓库低活跃度 schedule 优先级降低
- 该 region runner 高峰时段排队
- GitHub 方近期已知问题

漂移后果：
1. 下游依赖时序假设失效（intel-action 在 intel-daily 完成前误判 daily 缺失，但当前有 daily-first ordering 保护）
2. heartbeat 07:00 UTC 触发时，intel-action 可能未完成 → heartbeat 检测到 missing → 误报告警
3. 日报投递时间 = Dubai 09:00-10:00（不是宣传的 08:00），影响用户体感

---

## 五、关键发现

1. **【P1】GH Actions schedule 漂移 1-3h 已持续 2 天**：04-25 / 04-26 均如此，daily 报告实际投递在 Dubai 09:00-10:00（计划 08:00），此为 GitHub 平台特性，不是仓库 bug。

2. **【P1】heartbeat 07:00 UTC 触发可能早于 intel-action 完成**：今日 intel-action 06:00 计划 + 漂移 1-3h → 实际 07:00-09:00 完成；heartbeat 07:00 触发可能误报"action_report missing"。设计层已知风险但未消除。

3. **【P2】intel-daily push 重试缺失**：与 task-resume / intel-action 不一致（后两者都有 retry），漂移后窗口接近时存在丢更新风险。

4. **【P2】Node.js 20 deprecation 警告**：`actions/checkout@v4`、`actions/setup-python@v5` 在 5 个 workflow 全部存在该警告，2026-09-16 后 Node.js 20 将从 runner 移除，需在此之前升级 action 版本。

5. **【P3】昨日 heartbeat 失败为预期**：04-24 切流首日仅运行 daily 未运行 action（手动测试期），04-25 heartbeat 检查 04-24 数据正确发现缺失。今日（04-26 07:00 UTC）heartbeat 将检查 04-25 数据，应通过（04-25 daily + action 都已生成）。

---

## 六、调整建议候选（仅建议，不执行）

### 建议 1【P1】heartbeat 时间右移以容纳 intel-action 漂移

| 项 | 当前 | 建议 | 理由 |
|----|------|------|------|
| cron | `0 7 * * *`（07:00 UTC） | `0 9 * * *`（09:00 UTC，Dubai 13:00） | intel-action 漂移上限 ~08:30 UTC，heartbeat 09:00 触发可避免误报 |

### 建议 2【P2】intel-daily push 与 intel-action 对齐重试机制

| 项 | 当前 | 建议 | 理由 |
|----|------|------|------|
| push 块 | `|| echo "Push skipped"` 一次失败即放弃 | 与 intel-action 一致：3 次 retry + `git pull --rebase` | 漂移后 task-resume/n8n-snapshot/intel-daily 时间窗口接近，push 冲突需重试 |

### 建议 3【P2】统一升级 actions 版本

| 项 | 当前 | 建议 | 理由 |
|----|------|------|------|
| 5 个 workflow | `actions/checkout@v4` + `actions/setup-python@v5`（Node.js 20） | 跟踪官方升级到 Node.js 24 兼容版本 | 2026-09-16 之前必须完成 |

### 建议 4【P3】启用 schedule 漂移监控

| 项 | 当前 | 建议 | 理由 |
|----|------|------|------|
| 监控 | 无 | heartbeat 增加漂移度量上报（实际 vs 计划差） | 长期跟踪 GitHub 平台 SLA，决定是否迁移到自托管 runner |

**调整建议候选数量：4 条**（P1×1，P2×2，P3×1）。

---

## 七、给 Lysander 的一行

✅ GH Actions 审计完成：cron 5 个 / 昨日 schedule 触发 4 次（1 失败按设计）/ 关键问题 5 个（2×P1 + 2×P2 + 1×P3）/ 调整建议 4 条，待综合后呈报总裁。
