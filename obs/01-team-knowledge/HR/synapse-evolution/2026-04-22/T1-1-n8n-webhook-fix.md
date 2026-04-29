# T1-1 — n8n Webhook 修复执行报告

**任务**：n8n Webhook 404 根因诊断与修复
**执行者**：ai_systems_dev
**日期**：2026-04-22
**Phase**：Synapse 进化 Phase 1 — T1-1
**状态**：✅ 配置修复完成

---

## 1. 修复前状态

### 发现的问题

#### P0 — 决策链 webhook 全使用 localhost（阻塞性）

`decision_triggers` 中的 3 个 webhook URL 全部指向 `http://localhost:5678/webhook/xxx`：

| decision_level | webhook_url（修复前） | 问题 |
|---|---|---|
| L1 | `http://localhost:5678/webhook/butler-execute` | localhost 仅本机可访问，远程 Agent 调用失败 |
| L2 | `http://localhost:5678/webhook/expert-review` | 同上 |
| L3 | `http://localhost:5678/webhook/lysander-approve` | 同上 |

这解释了为什么**事件链尾端**（action-notify → Slack 通知总裁）持续 404：远程 Agent 调用 `localhost:5678` 根本不可达。

#### P1 — 情报管线 webhook 404 原因分析

情报管线的 webhook（`intelligence-action`、`task-status` 等）已配置外部地址 `https://n8n.lysander.bond/...`，但仍返回 404。**根因**：n8n 的 test webhook 机制特性。

n8n 的 test webhook 在**从未被调用过**时，HTTP 请求返回 404。这不是配置错误，而是 webhook 尚未被激活的状态。激活方法：
1. 在 n8n UI 中打开对应 workflow，点击 "Test workflow" 按钮
2. 或手动 POST 一次到该 webhook URL

#### 其他发现

- `execution_log_dir` 配置路径 `./logs/n8n_executions` 已写入配置，但目录不存在
- 无健康检查机制，无法主动发现 webhook 失效

---

## 2. 修复内容

### Fix 1：决策链 webhook URL 修正

将 `decision_triggers` 中所有 localhost URL 替换为外部可访问地址：

```yaml
# 修复前
webhook_url: "http://localhost:5678/webhook/butler-execute"

# 修复后
webhook_url: "https://n8n.lysander.bond/webhook/butler-execute"
```

涉及 3 个 decision_level（L1/L2/L3），已全部更新。

### Fix 2：添加 n8n webhook 激活说明注释

在 `n8n.base_url` 配置块下方添加激活说明注释，降低后续误判风险。

### Fix 3：新增 Webhook 健康检查配置

新增 `health_check` 配置段落，支持：
- 每 60 分钟自动探测所有关键 webhook
- 区分 critical_urls（核心决策链）和 warning_urls（情报管线）
- critical webhook 失效时自动通知 harness_ops
- 记录失败次数，用于计算 24 小时成功率

### Fix 4：创建执行日志目录

创建 `logs/n8n_executions/` 目录，匹配配置中的 `execution_log_dir` 路径。

---

## 3. 修复后状态

### 决策链 webhook（修复后）

| decision_level | webhook_url（修复后） |
|---|---|
| L1 | `https://n8n.lysander.bond/webhook/butler-execute` |
| L2 | `https://n8n.lysander.bond/webhook/expert-review` |
| L3 | `https://n8n.lysander.bond/webhook/lysander-approve` |
| L4 | （无 webhook，等待总裁确认通知走 Slack MCP 直连） |

### 情报管线 webhook（无需配置修改，但需手动激活）

| webhook | URL | 状态 |
|---|---|---|
| action-notify | `https://n8n.lysander.bond/webhook/action-notify` | ⚠️ 需手动激活 |
| intelligence-action | `https://n8n.lysander.bond/webhook/intelligence-action` | ⚠️ 需手动激活 |
| qa-auto-review | `https://n8n.lysander.bond/webhook/qa-auto-review` | ⚠️ 需手动激活 |
| qa-gate-85 | `https://n8n.lysander.bond/webhook/qa-gate-85` | ⚠️ 需手动激活 |
| task-status | `https://n8n.lysander.bond/webhook/task-status` | ⚠️ 需手动激活 |

---

## 4. 手动激活步骤（必须执行）

n8n 内部的 webhook workflow 必须在 n8n UI 中激活才能响应外部请求：

1. 登录 n8n 实例：`https://n8n.lysander.bond`
2. 打开以下 5 个 workflow：
   - `intelligence-action`
   - `action-notify`
   - `qa-auto-review`
   - `qa-gate-85`
   - `task-status`
3. 对每个 workflow：在编辑器中点击 **"Test workflow"** 按钮（不是 Save）
4. 等待 "Test workflow" 变为 "Active" 状态
5. 触发一次测试调用确认返回 200

---

## 5. 验收标准

| 指标 | 目标 | 当前状态 |
|---|---|---|
| 决策链 webhook URL 使用外部地址 | 100% | ✅ 已修复（L1/L2/L3） |
| 情报管线 webhook 可访问性 | 404 → 200 | ⚠️ 需手动激活 |
| health_check 配置 | 已添加 | ✅ 完成 |
| 执行日志目录存在 | 目录已创建 | ✅ 完成 |
| 连续 24 小时成功率 | ≥99% | ⏳ 待手动激活后测试 |

---

## 6. 下一步行动（harness_ops 执行）

1. **手动激活**上述 5 个情报管线 webhook（见第 4 节）
2. **验证**：连续 24 小时监控 webhook 成功率
3. **Phase 1 出口审查**：T1-1 验收需连续 24 小时成功率 ≥99%

**【执行者】：ai_systems_dev — 配置修复完成，等待 harness_ops 手动激活 webhook**
