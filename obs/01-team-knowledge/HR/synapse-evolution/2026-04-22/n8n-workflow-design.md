# n8n Workflow 完整设计方案

**设计组**：ai_systems_dev + harness_engineer 联合方案设计组
**日期**：2026-04-22
**版本**：v1.0
**状态**：方案待审批
**输出路径**：`obs/01-team-knowledge/HR/synapse-evolution/2026-04-22/n8n-workflow-design.md`

---

## 一、整体架构

### 1.1 管线拓扑图

```
┌──────────────────────────────────────────────────────────────────────┐
│                           情报管线（5个 WF）                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────┐     ┌──────────────┐                              │
│   │ WF-1       │     │ WF-5         │     ┌─────────────┐            │
│   │ intelligence│────▶│ task-status  │     │ WF-3       │            │
│   │ -action    │     │ (独立定时)   │     │ qa-auto-   │            │
│   │ (10:00 Dby)│     └──────────────┘     │ review     │            │
│   └──────┬─────┘                           │ (git push) │            │
│          │                                 └──────┬──────┘            │
│          ▼                                       │                    │
│   ┌─────────────┐                                ▼                    │
│   │ WF-2       │                           ┌─────────────┐            │
│   │ action-    │◀──(高优先级行动触发)       │ WF-4       │            │
│   │ notify     │                           │ qa-gate-85 │            │
│   │ (10:30 Dby)│                           │ (评分<85)  │            │
│   └─────────────┘                           └────────────┘            │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                           决策链（3个 WF）                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────┐     ┌──────────────┐     ┌─────────────┐            │
│   │ WF-6       │────▶│ WF-7        │────▶│ WF-8       │            │
│   │ butler-    │     │ expert-     │     │ lysander-  │            │
│   │ execute    │     │ review      │     │ approve    │            │
│   │ (POST触发) │     │ (L2决策)    │     │ (L3决策)   │            │
│   └─────────────┘     └──────────────┘     └─────────────┘            │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 调用关系说明

**情报管线（并行 + 顺序混合）**
- WF-1 与 WF-5：独立定时触发，互不依赖
- WF-3 与 WF-4：WF-3 调用 WF-4（评分 <85 时 POST 触发）
- WF-1 → WF-2：WF-1 评估结果含高优先级行动时 POST 到 WF-2

**决策链（同步调用链）**
- WF-6（butler-execute）：入口网关，接收外部派单请求
- WF-6 → WF-7：当决策级别 = L2 时，同步调用 expert-review
- WF-7 → WF-8：当决策级别 = L3 时，同步调用 lysander-approve
- WF-8：决策终点，通过 / 返回最终决策

### 1.3 技术栈概览

| 组件 | 要求 |
|------|------|
| n8n 版本 | >= 1.30.0（支持 modern workflow engine） |
| n8n 部署 | `https://n8n.lysander.bond`（已验证外部可访问） |
| 数据库 | n8n 内置 SQLite（workflow 执行记录）+ 文件系统 |
| 通知服务 | Slack MCP（直连）、Email（SMTP） |
| AI 推理 | Claude API via `https://api.anthropic.com` |
| 版本控制 | Git hooks → webhook → n8n |
| 配置管理 | `agent-butler/config/n8n_integration.yaml`（配置源） |

---

## 二、Workflow 详细设计

---

### WF-1：intelligence-action（情报行动触发）

**情报管线第1步**：每日 10:00 Dubai 定时，评估最新日报，输出行动建议。

#### Trigger

| 属性 | 值 |
|------|---|
| 类型 | Schedule（Cron） |
| 配置 | `0 6 * * *`（UTC）= 10:00 Dubai |
| 备选 | Git push 事件（通过 n8n Git Trigger 节点，可选） |

#### Input Schema

```json
{
  "trigger": "schedule",
  "source": "daily_timer",
  "date": "<YYYY-MM-DD>"
}
```

#### Output Schema

```json
{
  "workflow": "intelligence-action",
  "status": "success|partial|fail",
  "evaluation_date": "<YYYY-MM-DD>",
  "intelligence_items": [
    {
      "id": "INTEL-YYYYMMDD-NNN",
      "title": "...", "priority": "P0|P1|P2",
      "action_urgency": "high|medium|low",
      "confidence_score": 0-20,
      "source": "..."
    }
  ],
  "high_priority_count": N,
  "report_path": "obs/01-team-knowledge/HR/intelligence-actions/INTEL-YYYYMMDD-ACTION.md",
  "webhook_triggered": "action-notify|null",
  "executed_at": "<ISO8601>",
  "execution_ms": NNN
}
```

#### Node 列表

| 顺序 | Node | 类型 | 作用 |
|------|------|------|------|
| 1 | `Trigger: Schedule` | Schedule | 每日 10:00 Dubai 触发 |
| 2 | `Read Files`（情报日报） | File Nodes | 读取 `obs/06-daily-reports/` 下最新 HTML 文件 |
| 3 | `HTTP Request`（Claude API） | HTTP | 调用 Claude Sonnet 4.6 评估情报，prompt 如下 |
| 4 | `Code: Parse Eval` | Code | 解析 JSON 评估结果，提取优先级 |
| 5 | `IF: Priority >= P1` | IF | 判断是否触发 action-notify |
| 6 | `Write Files`（行动报告） | File Nodes | 写入 `obs/01-team-knowledge/HR/intelligence-actions/INTEL-YYYYMMDD-ACTION.md` |
| 7 | `HTTP Request`（WF-2 POST） | HTTP | 高优先级时 POST 到 `https://n8n.lysander.bond/webhook/action-notify` |
| 8 | `Error Trigger` | Error | 捕获失败，记录错误并跳过（非阻塞） |

**Prompt 模板（Claude API）**：
```
你是 Synapse 智囊团情报行动评估专家。
分析以下情报日报，评估每条情报的行动紧迫度。

评估标准：
- P0：影响公司存续/重大不可逆风险，需立即处理
- P1：本周内必须执行，有明确行动方
- P2：观察跟踪，月内评估

对每条情报输出：
- ID、标题、优先级、行动建议、置信度评分(1-20)
- 高优先级行动（>=P1）触发 action-notify webhook

日报内容：[从文件读取的内容]
```

#### 错误处理

| 失败场景 | Fallback 策略 |
|---------|-------------|
| 最新日报不存在 | 记录日志，workflow 优雅退出（不告警，因为 10:00 可能早于 08:00 日报） |
| Claude API 超时（>60s） | 使用缓存的评估模板降级执行，记录 token 消耗异常 |
| 行动报告写入失败 | 尝试重写 tmp 路径 `obs/01-team-knowledge/HR/intelligence-actions/tmp/INTEL-YYYYMMDD-TMP.md` |
| HTTP POST 到 WF-2 失败 | 记录到 `logs/n8n_executions/intelligence-action-fail.log`，不阻塞主流程 |

#### 监控指标

| 指标 | 目标 | 告警阈值 |
|------|------|---------|
| 执行成功率 | >= 98% | < 95% 触发告警 |
| 平均执行时间 | < 90s | > 120s 触发告警 |
| 高优先级行动识别率 | >= 1 条/天 | = 0 连续 3 天触发审查 |
| Claude API 错误率 | < 5% | >= 5% 触发降级 |

---

### WF-2：action-notify（行动通知）

**情报管线第2步**：接收 WF-1 的高优先级行动，通知执行团队，更新任务状态。

#### Trigger

| 属性 | 值 |
|------|---|
| 类型 | Webhook（POST） |
| URL | `https://n8n.lysander.bond/webhook/action-notify` |
| 备选 | 独立定时（每日 10:30 Dubai）`0 6 * * *` UTC+30min |
| HTTP 方法 | POST |

#### Input Schema

```json
{
  "intelligence_items": [...],
  "evaluation_date": "<YYYY-MM-DD>",
  "triggered_by": "intelligence-action|schedule",
  "high_priority_count": N,
  "items": [
    {
      "id": "INTEL-YYYYMMDD-NNN",
      "title": "...",
      "priority": "P0|P1",
      "action_text": "...",
      "confidence_score": 0-20
    }
  ]
}
```

#### Output Schema

```json
{
  "workflow": "action-notify",
  "status": "notified|partial|skip",
  "slack_notified": true,
  "email_sent": true,
  "active_tasks_updated": N,
  "items": [
    {
      "id": "INTEL-YYYYMMDD-NNN",
      "task_id": "TASK-NNN",
      "assigned_to": "agent_id",
      "slack_status": "posted|skipped",
      "email_status": "sent|skipped"
    }
  ],
  "executed_at": "<ISO8601>"
}
```

#### Node 列表

| 顺序 | Node | 类型 | 作用 |
|------|------|------|------|
| 1 | `Webhook` | Trigger | 接收 WF-1 POST 数据 |
| 2 | `IF: Priority == P0` | Switch | P0 项目单独处理（邮件+Slack） |
| 3 | `Slack: Send Message` | Slack | 推送情报行动摘要到指定 channel |
| 4 | `Read File`（active_tasks） | File | 读取当前 active_tasks.yaml |
| 5 | `Code: Update Tasks` | Code | 将 P0/P1 行动追加到 active_tasks.yaml |
| 6 | `Write File`（active_tasks） | File | 写回 active_tasks.yaml |
| 7 | `Email: Send` | Email | P0 行动发送邮件摘要 |
| 8 | `Wait 30min` | Wait | 等待 30 分钟后发送，防止高频通知 |
| 9 | `Error Trigger` | Error | 失败时保留通知日志 |

**Slack 消息模板**：
```
[Synapse 情报行动] {evaluation_date}
高优先级行动 {high_priority_count} 条：

{P0 items}
🔥 P0 — 需立即处理
• {id}: {title}
  行动：{action_text}
  负责人：{assigned_to}

{P1 items}
⚡ P1 — 本周执行
• {id}: {title}
  行动：{action_text}
  负责人：{assigned_to}

报告路径：{report_path}
```

#### 错误处理

| 失败场景 | Fallback 策略 |
|---------|-------------|
| active_tasks.yaml 写入失败 | 追加到 `logs/n8n_executions/task-update-errors.log`，人工干预 |
| Slack 发送失败 | 降级：记录消息内容，发送邮件替代通知 |
| Email SMTP 失败 | 降级：仅 Slack 通知，不阻塞 |
| WF-1 未触发（日报不存在） | 独立定时模式兜底，每 10:30 Dubai 执行一次 |

#### 监控指标

| 指标 | 目标 | 告警阈值 |
|------|------|---------|
| 执行成功率 | >= 98% | < 95% |
| Slack 送达率 | 100% | < 100% |
| 任务写入准确率 | >= 95% | < 90% |
| P0 邮件送达率 | 100% | < 100% |

---

### WF-3：qa-auto-review（自动QA审查）

**情报管线 QA 节点**：git push 事件触发，执行 YAML 语法检查和 CLAUDE.md 行数限制验证。

#### Trigger

| 属性 | 值 |
|------|---|
| 类型 | Webhook（POST） |
| URL | `https://n8n.lysander.bond/webhook/qa-auto-review` |
| HTTP 方法 | POST |
| 来源 | Git hooks → Git 服务器 webhook |

#### Input Schema

```json
{
  "event": "push",
  "repository": { "full_name": "...", "url": "..." },
  "commits": [
    {
      "id": "sha",
      "message": "commit message",
      "added": ["file1", "file2"],
      "modified": ["file3"],
      "removed": ["file4"],
      "timestamp": "<ISO8601>"
    }
  ],
  "pusher": { "name": "...", "email": "..." }
}
```

#### Output Schema

```json
{
  "workflow": "qa-auto-review",
  "status": "pass|fail|warning",
  "score": 0-100,
  "dimensions": {
    "integrity": { "score": 0-100, "details": "..." },
    "accuracy": { "score": 0-100, "details": "..." },
    "consistency": { "score": 0-100, "details": "..." },
    "maintainability": { "score": 0-100, "details": "..." },
    "compliance": { "score": 0-100, "details": "..." }
  },
  "files_reviewed": N,
  "issues": [
    { "file": "...", "line": N, "type": "syntax|logic|compliance", "severity": "error|warning", "message": "..." }
  ],
  "gate_result": "pass|fail",
  "webhook_triggered": "qa-gate-85|null",
  "executed_at": "<ISO8601>"
}
```

#### Node 列表

| 顺序 | Node | 类型 | 作用 |
|------|------|------|------|
| 1 | `Webhook` | Trigger | 接收 git push 事件 |
| 2 | `Code: Extract Files` | Code | 从 webhook payload 提取变更文件列表 |
| 3 | `IF: files match filter` | IF | 检查是否匹配 `agent-butler/**` 或 `CLAUDE.md` |
| 4 | `Read Files` | File | 读取变更的配置文件（YAML/CLAUDE.md/py） |
| 5 | `Code: YAML Syntax Check` | Code | 执行 YAML 语法验证（pyyaml 库） |
| 6 | `Code: CLAUDE.md Line Count` | Code | 检查 CLAUDE.md 行数是否 <= 350 |
| 7 | `Code: Python Syntax Check` | Code | 检查 .py 文件语法（ast.parse） |
| 8 | `Code: Compute QA Score` | Code | 计算五维评分：integrity/accuracy/consistency/maintainability/compliance |
| 9 | `IF: score >= 85` | IF | 判断是否通过 QA gate |
| 10 | `HTTP Request`（WF-4 POST） | HTTP | score < 85 时 POST 到 qa-gate-85 |
| 11 | `Write File`（QA报告） | File | 写入 `logs/n8n_executions/qa-review-YYYYMMDD.json` |
| 12 | `Error Trigger` | Error | 错误捕获 |

**评分维度（harness_registry.yaml 一致）**：

| 维度 | 权重 | 检查方法 |
|------|------|---------|
| integrity（完整性） | 20% | 约定交付物是否齐全 |
| accuracy（准确性） | 20% | YAML 语法/代码语法无错误 |
| consistency（一致性） | 20% | 与现有系统/规范无冲突 |
| maintainability（可维护性） | 20% | 注释/结构清晰/可升级 |
| compliance（合规性） | 20% | 派单记录/执行链完整性 |

#### 错误处理

| 失败场景 | Fallback 策略 |
|---------|-------------|
| 文件无法读取 | 记录到 issues，accuracy 维度扣分，不整体失败 |
| YAML 语法错误 | accuracy = 0，跳过其他检查，直接触发 qa-gate-85 |
| score 计算异常 | 默认 score = 50，触发 qa-gate-85 |
| HTTP POST 到 WF-4 失败 | 记录错误，workflow 失败告警（critical） |

#### 监控指标

| 指标 | 目标 | 告警阈值 |
|------|------|---------|
| 执行成功率 | >= 99% | < 97% |
| 平均执行时间 | < 30s | > 60s |
| score < 85 触发率 | <= 15% | > 20% 触发系统性审查 |
| 漏检率（QA漏报人工问题） | < 5% | >= 5% |

---

### WF-4：qa-gate-85（QA门禁告警）

**情报管线 QA 门禁**：WF-3 评分 <85 时阻止交付，通知集成 QA。

#### Trigger

| 属性 | 值 |
|------|---|
| 类型 | Webhook（POST） |
| URL | `https://n8n.lysander.bond/webhook/qa-gate-85` |
| HTTP 方法 | POST |
| 来源 | WF-3（score < 85 时触发） |

#### Input Schema

```json
{
  "workflow": "qa-auto-review",
  "status": "fail",
  "score": "< 85",
  "commits": [...],  // 同 WF-3 input
  "issues": [...],   // 同 WF-3 output
  "gate_result": "fail",
  "failed_at": "<ISO8601>"
}
```

#### Output Schema

```json
{
  "workflow": "qa-gate-85",
  "status": "blocked|acknowledged",
  "alerts_sent": {
    "slack": "sent|failed",
    "email": "sent|skipped"
  },
  "git_marker": "QA FAIL added|null",
  "assigned_to": "integration_qa",
  "executed_at": "<ISO8601>"
}
```

#### Node 列表

| 顺序 | Node | 类型 | 作用 |
|------|------|------|------|
| 1 | `Webhook` | Trigger | 接收 WF-3 失败数据 |
| 2 | `Code: Format Alert` | Code | 格式化告警消息，包含问题列表和修复建议 |
| 3 | `Slack: Send Message` | Slack | 通知 harness_ops + integration_qa |
| 4 | `Email: Send` | Email | 备选通知（integration_qa 邮箱） |
| 5 | `Code: Generate Git Marker` | Code | 生成 `QA FAIL: <score> - <top issues>` 标记文本 |
| 6 | `Git: Add Commit Note` | Code | 在最近 commit message 中追加 QA FAIL 标记（如 n8n Git 节点支持） |
| 7 | `Write File`（告警日志） | File | 写入 `logs/n8n_executions/qa-gate-85-alerts.log` |
| 8 | `IF: Merge Block` | IF | 可选：返回 403 状态码阻止 merge（需 Git 服务器支持 webhook 返回值） |
| 9 | `Error Trigger` | Error | 错误处理 |

**Slack 告警模板**：
```
[QA GATE BLOCKED] score={score}/100
文件：{file_list}
问题：{top_issue}

错误详情：
{issues}

🚫 交付被阻止 — integration_qa 需修复后重提
```

#### 错误处理

| 失败场景 | Fallback 策略 |
|---------|-------------|
| Slack 发送失败 | 尝试 Email，保留告警日志，人工巡检兜底 |
| Git marker 写入失败 | 仅记录，不阻塞告警流程 |
| WF-3 重复触发 | 10 分钟去重窗口（Wait + IF） |

#### 监控指标

| 指标 | 目标 | 告警阈值 |
|------|------|---------|
| 告警送达率 | 100% | < 100% |
| 平均告警延迟 | < 30s | > 60s |
| Git marker 成功率 | >= 90% | < 80% |
| 修复周期（score 50-84） | <= 2 个会话 | > 3 个会话触发升级 |

---

### WF-5：task-status（任务状态同步）

**情报管线第5步**：每日 06:00 Dubai 读取 active_tasks.yaml，生成任务状态报告，识别逾期任务。

#### Trigger

| 属性 | 值 |
|------|---|
| 类型 | Schedule（Cron） |
| 配置 | `0 2 * * *`（UTC）= 06:00 Dubai |
| HTTP 方法 | 无（独立定时） |

#### Input Schema

```json
{
  "trigger": "schedule",
  "source": "daily_task_resume",
  "date": "<YYYY-MM-DD>"
}
```

#### Output Schema

```json
{
  "workflow": "task-status",
  "status": "success|partial",
  "report_date": "<YYYY-MM-DD>",
  "summary": {
    "total_tasks": N,
    "in_progress": N,
    "inbox": N,
    "overdue_p0": N,
    "overdue_p1": N,
    "assessed": N,
    "completed": N
  },
  "overdue_tasks": [
    { "id": "...", "title": "...", "priority": "...", "overdue_days": N, "assigned_to": "..." }
  ],
  "report_path": "obs/06-daily-reports/task-status-YYYY-MM-DD.md",
  "alerts_triggered": N,
  "executed_at": "<ISO8601>"
}
```

#### Node 列表

| 顺序 | Node | 类型 | 作用 |
|------|------|------|------|
| 1 | `Trigger: Schedule` | Schedule | 每日 06:00 Dubai |
| 2 | `Read File`（active_tasks） | File | 读取 active_tasks.yaml |
| 3 | `Code: Parse Tasks` | Code | 解析 YAML，提取所有任务状态 |
| 4 | `Code: Compute Overdue` | Code | 对比 follow_up 日期与今日，识别逾期任务 |
| 5 | `Code: Generate Summary` | Code | 生成任务状态摘要 |
| 6 | `IF: overdue_p0 > 0` | IF | P0 逾期触发紧急告警 |
| 7 | `Write File`（状态报告） | File | 写入 `obs/06-daily-reports/task-status-YYYY-MM-DD.md` |
| 8 | `Slack: Send Message` | Slack | 推送状态摘要（仅高优先级时） |
| 9 | `Code: Update active_tasks` | Code | 可选：将逾期 P0 任务的 blocker 字段更新 |
| 10 | `Error Trigger` | Error | 错误处理 |

**Markdown 报告模板**：
```markdown
# 任务状态报告 {YYYY-MM-DD}

## 摘要
- 总任务数：{total_tasks}
- 进行中：{in_progress} | 收件箱：{inbox} | 已评估：{assessed} | 已完成：{completed}

## 逾期任务
| ID | 标题 | 优先级 | 逾期天数 | 负责人 |
|----|------|--------|---------|--------|
| ... | ... | P0 | N | agent_id |

## 本日关注
{priority_highlight}
```

#### 错误处理

| 失败场景 | Fallback 策略 |
|---------|-------------|
| active_tasks.yaml 读取失败 | 读取 `active_tasks.yaml.bak`（如存在），否则告警 |
| follow_up 日期缺失 | 跳过逾期计算（视为无截止日） |
| 报告写入失败 | 写入 tmp 路径，次日合并 |
| P0 逾期告警失败 | 升级发送 Email 到 harness_ops |

#### 监控指标

| 指标 | 目标 | 告警阈值 |
|------|------|---------|
| 执行成功率 | >= 99% | < 97% |
| 逾期任务识别准确率 | >= 95% | < 90% |
| 报告生成成功率 | 100% | < 95% |
| P0 逾期告警送达率 | 100% | < 100% |

---

### WF-6：butler-execute（Butler任务执行）

**决策链第1步**：接收派单数据，解析任务类型和执行者，触发对应 Agent。

#### Trigger

| 属性 | 值 |
|------|---|
| 类型 | Webhook（POST） |
| URL | `https://n8n.lysander.bond/webhook/butler-execute` |
| HTTP 方法 | POST |
| 来源 | Lysander 主对话 / 其他 Agent / n8n API |

#### Input Schema

```json
{
  "dispatch_id": "DISP-YYYYMMDD-NNN",
  "source": "lysander_main|agent|api",
  "timestamp": "<ISO8601>",
  "task": {
    "title": "任务标题",
    "description": "任务详细描述",
    "priority": "P0|P1|P2",
    "task_type": "string",   // 路由关键词，如 "Harness|配置|代码"
    "assigned_to": "agent_id",
    "co_assigned": ["agent_id"],
    "team": "harness_ops|rd|butler|obs|...",
    "constraints": {
      "deadline": "<YYYY-MM-DD>",
      "budget_tokens": N,
      "approval_required": true|false
    }
  },
  "decision_level": "L1|L2|L3|L4",
  "execution_chain_stage": 1,
  "expected_output": "string",
  "approval": {
    "required": true|false,
    "approver": "agent_id",
    "status": "pending|approved|rejected"
  }
}
```

#### Output Schema

```json
{
  "workflow": "butler-execute",
  "receipt_id": "RCP-YYYYMMDD-NNN",
  "status": "dispatched|in_progress|completed|failed|escalated",
  "task_id": "TASK-NNN",
  "execution_log_id": "EXEC-YYYYMMDD-NNN",
  "routed_to": {
    "agent_id": "...",
    "team": "...",
    "workflow": "..."
  },
  "decision_level": "L1|L2|L3|L4",
  "next_step": {
    "workflow": "expert-review|lysander-approve|agent_execution|null",
    "input": {...}
  },
  "executed_at": "<ISO8601>",
  "execution_ms": NNN
}
```

#### Node 列表

| 顺序 | Node | 类型 | 作用 |
|------|------|------|------|
| 1 | `Webhook` | Trigger | 接收派单 JSON |
| 2 | `Code: Validate Dispatch` | Code | 验证必填字段，生成 dispatch_id |
| 3 | `Code: Route by Keywords` | Code | 按 organization.yaml routing_keywords 路由 |
| 4 | `Code: Log Execution` | Code | 写入执行日志 `logs/n8n_executions/dispatch-YYYYMMDD.log` |
| 5 | `IF: decision_level == L1` | Switch | L1 = 直接执行 |
| 6 | `IF: decision_level == L2` | Switch | L2 → 调用 expert-review |
| 7 | `IF: decision_level == L3` | Switch | L3 → 调用 lysander-approve |
| 8 | `IF: decision_level == L4` | Switch | L4 → 等待总裁确认通知 |
| 9 | `HTTP Request`（WF-7 POST） | HTTP | L2 时 POST 到 expert-review |
| 10 | `HTTP Request`（WF-8 POST） | HTTP | L3 时 POST 到 lysander-approve |
| 11 | `Slack: Send Receipt` | Slack | 返回执行回执到 Lysander |
| 12 | `Write File`（Receipt） | File | 写入 `logs/n8n_executions/receipt-RCP-YYYYMMDD-NNN.json` |
| 13 | `Error Trigger` | Error | 错误捕获 |

**决策路由逻辑**：

```
decision_level:
  L1 → 日志记录 → 直接触发 agent_execute → 返回 receipt
  L2 → POST to WF-7 (expert-review) → 等待评审结果 → 返回 receipt
  L3 → POST to WF-7 → WF-7 完成 → POST to WF-8 (lysander-approve) → 等待决策 → 返回 receipt
  L4 → Slack 通知总裁等待 → 返回 pending 状态
```

#### 错误处理

| 失败场景 | Fallback 策略 |
|---------|-------------|
| Webhook payload 无效 | 返回 400，附验证错误详情 |
| routing 失败（无匹配关键词） | 默认路由到 harness_ops，记录异常 |
| WF-7/WF-8 调用失败 | 降级为 L1 直接执行，记录降级原因 |
| 执行日志写入失败 | 仅记录内存，不阻塞主流程 |

#### 监控指标

| 指标 | 目标 | 告警阈值 |
|------|------|---------|
| 响应时间 | < 5s | > 30s |
| 派单成功率 | >= 99% | < 97% |
| L2/L3 路由准确率 | >= 90% | < 80% |
| 决策级别识别准确率 | >= 95% | < 90% |

---

### WF-7：expert-review（专家评审）

**决策链第2步**：收集相关专家 Agent 的评估意见，综合形成决策建议。

#### Trigger

| 属性 | 值 |
|------|---|
| 类型 | Webhook（POST） |
| URL | `https://n8n.lysander.bond/webhook/expert-review` |
| HTTP 方法 | POST |
| 来源 | WF-6（L2/L3 决策请求时） |
| 备选 | 独立手动触发（harness_engineer 发起） |

#### Input Schema

```json
{
  "review_id": "REV-YYYYMMDD-NNN",
  "source_workflow": "butler-execute",
  "dispatch_id": "DISP-YYYYMMDD-NNN",
  "timestamp": "<ISO8601>",
  "task": {
    "title": "...",
    "description": "...",
    "decision_level": "L2|L3",
    "priority": "P0|P1|P2"
  },
  "experts_requested": [
    { "agent_id": "graphify_strategist", "domain": "战略分析" },
    { "agent_id": "ai_ml_engineer", "domain": "AI/ML 技术" },
    ...
  ],
  "review_mode": "parallel|sequential",
  "deadline": "<ISO8601>"
}
```

#### Output Schema

```json
{
  "workflow": "expert-review",
  "review_id": "REV-YYYYMMDD-NNN",
  "status": "completed|partial|timeout",
  "expert_opinions": [
    {
      "agent_id": "...",
      "domain": "...",
      "opinion": "...",
      "confidence": 0-100,
      "recommendation": "approve|reject|modify|escalate"
    }
  ],
  "synthesis": {
    "decision_advisor_summary": "...",
    "pros": ["..."],
    "cons": ["..."],
    "recommended_action": "approve|reject|modify|escalate",
    "confidence_score": 0-100,
    "key_concerns": ["..."]
  },
  "decision_logged": true,
  "next_workflow": "lysander-approve|null",
  "next_workflow_input": {...},
  "executed_at": "<ISO8601>",
  "execution_ms": NNN
}
```

#### Node 列表

| 顺序 | Node | 类型 | 作用 |
|------|------|------|------|
| 1 | `Webhook` | Trigger | 接收 WF-6 评审请求 |
| 2 | `Code: Identify Experts` | Code | 根据 task_type + domain 确定专家列表（1-5名） |
| 3 | `HTTP Request`（Claude API） | HTTP | 并行调用 Claude API，每个专家一个 structured prompt |
| 4 | `Code: Collect Opinions` | Code | 汇总各专家意见，统一格式 |
| 5 | `Code: Synthesize` | Code | decision_advisor 综合各方意见，形成推荐方案 |
| 6 | `Write File`（决策日志） | File | 写入 `logs/n8n_executions/decision-log-REV-NNN.json` |
| 7 | `IF: decision_level == L3` | IF | L3 触发 lysander-approve |
| 8 | `HTTP Request`（WF-8 POST） | HTTP | POST 到 lysander-approve |
| 9 | `Code: Format Summary` | Code | 格式化专家意见汇总 |
| 10 | `Slack: Send to Lysander` | Slack | 通知 Lysander 评审结果（可选） |
| 11 | `Error Trigger` | Error | 超时/专家意见不一致时告警 |

**专家 Prompt 模板**：
```
你是 Synapse {domain} 专家 Agent（{agent_id}）。
当前需要评审以下任务并给出专业意见：

任务：{task.title}
描述：{task.description}
优先级：{task.priority}

请从 {domain} 专业角度分析：
1. 主要风险点
2. 可行性评估
3. 建议的行动方案
4. 你推荐的置信度（0-100）

输出格式：JSON
{
  "agent_id": "{agent_id}",
  "domain": "{domain}",
  "opinion": "...",
  "confidence": N,
  "recommendation": "approve|reject|modify|escalate"
}
```

#### 错误处理

| 失败场景 | Fallback 策略 |
|---------|-------------|
| 部分专家响应超时（>60s） | 使用已收到的意见，降级 confidence 评分 |
| 所有专家均无响应 | 降级为默认 approve，记录异常 |
| 专家意见冲突（>3个方向） | 标记为 "需要人工干预"，L3 时升级到 lysander-approve |
| WF-8 POST 失败 | 保留评审结果，日志记录，通知 Lysander 手动处理 |

#### 监控指标

| 指标 | 目标 | 告警阈值 |
|------|------|---------|
| 专家响应率 | >= 80%（至少 1/3 专家回复） | < 50% |
| 平均评审时间 | < 120s | > 300s |
| 评审覆盖率 | >= 90%（按 routing_keywords） | < 80% |
| 意见合成一致性 | >= 70% | < 50% 触发升级 |

---

### WF-8：lysander-approve（Lysander审批）

**决策链第3步**：记录待审批事项，等待 Lysander 决策，执行决策结果。

#### Trigger

| 属性 | 值 |
|------|---|
| 类型 | Webhook（POST） |
| URL | `https://n8n.lysander.bond/webhook/lysander-approve` |
| HTTP 方法 | POST |
| 来源 | WF-7（L3 决策请求） |
| 备选 | WF-6 直接请求（L4） |

#### Input Schema

```json
{
  "approval_id": "APPR-YYYYMMDD-NNN",
  "source_workflow": "expert-review|butler-execute",
  "review_id": "REV-YYYYMMDD-NNN",
  "timestamp": "<ISO8601>",
  "task": {
    "title": "...",
    "description": "...",
    "priority": "P0|P1|P2"
  },
  "synthesis": {
    "recommendation": "approve|reject|modify",
    "pros": ["..."],
    "cons": ["..."],
    "confidence_score": 0-100,
    "key_concerns": ["..."]
  },
  "expert_count": N,
  "decision_deadline": "<ISO8601>",
  "wait_timeout_hours": 24
}
```

#### Output Schema

```json
{
  "workflow": "lysander-approve",
  "approval_id": "APPR-YYYYMMDD-NNN",
  "status": "approved|rejected|modified|timeout|pending",
  "lysander_decision": {
    "action": "approve|reject|modify",
    "modifications": ["..."],   // 当 action = modify 时
    "comment": "...",
    "decided_at": "<ISO8601>"
  },
  "execution_triggered": true|false,
  "next_step": {
    "action": "execute|notify|log|close",
    "details": "..."
  },
  "notification_sent": true|false,
  "executed_at": "<ISO8601>"
}
```

#### Node 列表

| 顺序 | Node | 类型 | 作用 |
|------|------|------|------|
| 1 | `Webhook` | Trigger | 接收 L3 决策请求 |
| 2 | `Code: Format Approval Request` | Code | 格式化待审批事项，生成决策摘要 |
| 3 | `Write File`（待审批队列） | File | 写入 `logs/n8n_executions/pending-approvals/YYYYMMDD.json` |
| 4 | `Slack: Notify Lysander` | Slack | 发送审批请求通知（含决策摘要） |
| 5 | `Wait` | Wait | 等待 24 小时（可配置） |
| 6 | `Read File`（决策响应） | File | 读取 `logs/n8n_executions/pending-approvals/{approval_id}.json`（由 Lysander 填写） |
| 7 | `IF: decision == approve` | Switch | 批准 → 执行 |
| 8 | `IF: decision == reject` | Switch | 驳回 → 通知派单人 |
| 9 | `IF: decision == modify` | Switch | 修改 → 返回 WF-6 重新执行 |
| 10 | `Code: Log Decision` | Code | 写入决策日志 |
| 11 | `Slack: Send Result` | Slack | 通知决策结果 |
| 12 | `Error Trigger` | Error | 超时/无决策时升级通知 |

**Slack 审批请求模板**：
```
[Lysander 审批请求]
任务：{task.title}
优先级：{task.priority}

智囊团建议：{recommendation}（置信度 {confidence_score}/100）

优点：{pros}
风险：{cons}

⚠️ 请在 24 小时内回复：
:white_check_mark: 批准
:x: 驳回
:pencil2: 修改（请说明修改内容）

将回复写入：logs/n8n_executions/pending-approvals/{approval_id}.json
```

#### 决策响应文件格式

```json
{
  "approval_id": "APPR-YYYYMMDD-NNN",
  "decision": "approve|reject|modify",
  "modifications": ["..."],
  "comment": "总裁备注（可选）",
  "decided_by": "lysander",
  "decided_at": "<ISO8601>"
}
```

#### 错误处理

| 失败场景 | Fallback 策略 |
|---------|-------------|
| 24 小时无响应 | 升级发送 Email + Slack 催办，延长时间 12h |
| 48 小时无响应 | 自动驳回，记录超时原因，通知派单人 |
| Slack 通知失败 | 发送 Email 到预设邮箱 |
| 响应文件格式无效 | 等待重新填写，超时后按 reject 处理 |

#### 监控指标

| 指标 | 目标 | 告警阈值 |
|------|------|---------|
| 审批响应率 | >= 90% | < 80% |
| 平均审批延迟 | < 12h | > 24h |
| 自动超时率 | <= 5% | > 10% |
| 决策日志完整性 | 100% | < 100% |

---

## 三、技术依赖

### 3.1 n8n 环境要求

| 依赖项 | 版本要求 | 说明 |
|--------|---------|------|
| n8n | >= 1.30.0 | 支持 modern workflow engine |
| Node.js | >= 18.x | n8n 运行时 |
| 数据库 | SQLite（内置） | workflow 执行历史 |

### 3.2 第三方服务依赖

| 服务 | 凭证类型 | 配置位置 | 用途 |
|------|---------|---------|------|
| Claude API | API Key | `ANTHROPIC_API_KEY` env | WF-1/WF-7 AI 推理 |
| Slack | MCP 直连 | `.claude/settings.json` | 所有通知 |
| Email/SMTP | SMTP 凭证 | `agent-butler/config/n8n_integration.yaml` | P0 告警邮件 |
| Git | SSH Key / Token | n8n 节点配置 | WF-3/WF-4 Git 操作 |
| GitHub/GitLab | Webhook Token | Git 服务器 | WF-3 触发 |

### 3.3 Claude API 配置

| 参数 | 值 |
|------|---|
| Base URL | `https://api.anthropic.com/v1/messages` |
| Model | `claude-sonnet-4-7`（推荐）或 `claude-opus-4-7` |
| `task_budget` 参数 | `<= 50000` tokens/任务（成本控制） |
| Timeout | 60s（WF-1）、120s（WF-7） |
| Max retries | 3 次 |

### 3.4 文件系统约定

```
Synapse-Mini/
├── logs/
│   └── n8n_executions/           # 执行日志（配置目录）
│       ├── qa-review-*.json      # QA 报告
│       ├── qa-gate-85-alerts.log # QA 告警日志
│       ├── dispatch-*.log        # 派单日志
│       ├── receipt-*.json        # 执行回执
│       ├── decision-log-*.json   # 决策日志
│       ├── pending-approvals/     # 待审批队列
│       └── task-update-errors.log # 任务更新错误日志
└── obs/01-team-knowledge/HR/intelligence-actions/  # 情报行动输出
```

### 3.5 环境变量

```bash
# .env（由 harness_engineer 配置）
ANTHROPIC_API_KEY=sk-ant-...
N8N_BASE_URL=https://n8n.lysander.bond
N8N_API_KEY=           # 如有
SYNAPSE_LOG_DIR=./logs/n8n_executions
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...          # 使用 credentials-usage.md 规范
SLACK_BOT_TOKEN=xoxb-...
```

---

## 四、实施计划

### 4.1 创建顺序与优先级

| 优先级 | WF 编号 | 名称 | 理由 |
|--------|--------|------|------|
| P0 | WF-3 | qa-auto-review | Git push 安全网，最核心 QA 节点 |
| P0 | WF-4 | qa-gate-85 | QA-3 的下游门禁，必须同步创建 |
| P1 | WF-6 | butler-execute | 决策链入口，所有派单的必经之路 |
| P1 | WF-1 | intelligence-action | 情报管线核心，两大定时管线之一 |
| P2 | WF-2 | action-notify | 依赖 WF-1，情报行动闭环 |
| P2 | WF-5 | task-status | 任务管理辅助，独立运行 |
| P3 | WF-7 | expert-review | 专家评审，可降级为 Claude API 直接调用 |
| P3 | WF-8 | lysander-approve | Lysander 审批，可降级为 Slack 手动审批 |

### 4.2 测试策略

| 阶段 | 内容 | 验收标准 |
|------|------|---------|
| 单元测试 | 每个 workflow 独立测试（n8n Test workflow 按钮） | 所有节点绿色，无 error |
| 集成测试 | WF-3 → WF-4 串联测试（模拟 git push → QA 评分 <85） | WF-4 正确触发告警 |
| 集成测试 | WF-6 → WF-7 → WF-8 串联测试（模拟 L3 决策） | 三workflow 状态正确传递 |
| 压力测试 | WF-1 连续 30 天（情报日报运行期间并行测试） | 执行成功率 >= 98% |
| 降级测试 | 模拟 Claude API 失败，确认 fallback 正确 | 不阻塞主流程 |
| 验收测试 | T1-1 webhook 激活后 24 小时健康检查 | 所有 webhook 200 OK |

### 4.3 与现有配置的集成点

| 已有配置 | 集成点 |
|---------|--------|
| `n8n_integration.yaml`（execution_chain_triggers） | WF-1/2/3/4/5 的 webhook URL 和 schedule 需与配置文件保持一致 |
| `n8n_integration.yaml`（decision_triggers） | WF-6/7/8 的 webhook URL 需与 decision_triggers 一致 |
| `n8n_integration.yaml`（health_check） | 当前 critical_urls 和 warning_urls 已覆盖所有 8 个 webhook |
| `organization.yaml`（routing_keywords） | WF-6 路由逻辑使用 routing_keywords 进行 agent 匹配 |
| `harness_registry.yaml`（QA 维度） | WF-3 评分维度的权重和描述需与 harness_registry.yaml 完全一致 |
| `logs/n8n_executions/` | 已有目录，所有 workflow 日志均写入此目录 |

---

## 五、监控方案

### 5.1 健康检查指标

| 指标 | 定义 | 测量方法 | 目标 | 告警阈值 |
|------|------|---------|------|---------|
| **执行成功率** | (成功执行 / 总执行) × 100% | n8n 执行历史统计 | >= 99% | < 97% → critical |
| **平均响应时间** | 总执行时间 / 执行次数 | n8n execution log | < 60s（WF-1/7 < 120s） | > 150s → warning |
| **Webhook 可用率** | (200 响应 / 总调用) × 100% | health_check 每 60min | >= 99% | < 95% → critical |
| **P0 告警送达率** | (P0 告警成功送达 / P0 总数) × 100% | WF-2/WF-4/WF-8 | 100% | < 100% → critical |
| **QA 评分覆盖率** | (有评分的 push / 总 push) × 100% | WF-3 执行统计 | 100% | < 95% → warning |
| **决策日志完整性** | (有记录的决策 / 总决策) × 100% | WF-7/WF-8 执行统计 | 100% | < 100% → critical |

### 5.2 告警阈值

| 告警级别 | 条件 | 通知渠道 | 负责人 |
|---------|------|---------|--------|
| **Critical** | 执行成功率 < 97% 或 Webhook 可用率 < 95% | Slack + Email | harness_engineer |
| **Warning** | 平均响应时间 > 150s 或 QA 评分覆盖率 < 95% | Slack | integration_qa |
| **Info** | P0 任务完成 或 新 WF 上线 | Slack | harness_ops |

### 5.3 SLA

| Workflow | SLA 目标 | SLA 定义 |
|---------|---------|---------|
| WF-1 intelligence-action | >= 98% | 每月最多 1 次失败 |
| WF-2 action-notify | >= 98% | 每月最多 1 次失败 |
| WF-3 qa-auto-review | >= 99% | 每月最多 0.5 次失败 |
| WF-4 qa-gate-85 | >= 99% | 告警必须送达 |
| WF-5 task-status | >= 99% | 每日报告必须生成 |
| WF-6 butler-execute | >= 99% | 响应时间 < 5s |
| WF-7 expert-review | >= 95% | 评审结果必须输出 |
| WF-8 lysander-approve | >= 95% | 24h 内完成审批 |

### 5.4 日志与可追溯性

| 日志文件 | 内容 | 保留期 |
|---------|------|--------|
| `logs/n8n_executions/qa-review-*.json` | QA 评分详细报告 | 90 天 |
| `logs/n8n_executions/qa-gate-85-alerts.log` | QA 告警日志 | 90 天 |
| `logs/n8n_executions/dispatch-*.log` | 派单日志 | 90 天 |
| `logs/n8n_executions/receipt-*.json` | 执行回执 | 180 天 |
| `logs/n8n_executions/decision-log-*.json` | 专家评审 + 决策日志 | 180 天 |
| `logs/n8n_executions/pending-approvals/*.json` | 待审批队列 | 30 天 |
| `logs/n8n_executions/intelligence-action-fail.log` | 情报行动失败日志 | 30 天 |

---

## 附录 A：WF 快速参考表

| WF | 名称 | 触发器 | 关键节点数 | 输出文件 |
|----|------|--------|-----------|---------|
| WF-1 | intelligence-action | Schedule（10:00） | 8 | `obs/.../intelligence-actions/INTEL-*.md` |
| WF-2 | action-notify | Webhook（POST） | 9 | 更新 `active_tasks.yaml` |
| WF-3 | qa-auto-review | Webhook（POST） | 12 | `logs/.../qa-review-*.json` |
| WF-4 | qa-gate-85 | Webhook（POST） | 9 | `logs/.../qa-gate-85-alerts.log` |
| WF-5 | task-status | Schedule（06:00） | 10 | `obs/.../task-status-*.md` |
| WF-6 | butler-execute | Webhook（POST） | 13 | `logs/.../receipt-*.json` |
| WF-7 | expert-review | Webhook（POST） | 11 | `logs/.../decision-log-*.json` |
| WF-8 | lysander-approve | Webhook（POST） | 12 | `logs/.../pending-approvals/*.json` |

---

**【执行者】：ai_systems_dev + harness_engineer 联合方案设计组**
**【设计完成时间】：2026-04-22**
**【状态】：方案待 Lysander 审批 → 派单 harness_ops 执行**
