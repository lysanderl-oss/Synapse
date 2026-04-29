# n8n Workflow 方案评审报告

**评审人**：execution_auditor + integration_qa（联合评审组）
**评审时间**：2026-04-22
**评审级别**：Phase 1 执行前强制评审
**评审依据**：n8n_integration.yaml v3.0、T1-1 修复报告、webhook 激活测试结果、Phase1-QA-review

---

## 一、方案可行性评估

### A.1 必要性评估（每个WF）

| Workflow | 必要性 | 不可替代性 | 结论 |
|----------|--------|-----------|------|
| WF-1: intelligence-action（情报行动） | **高** | 是 | 保留 |
| WF-2: action-notify（通知） | **高** | 是 | 保留 |
| WF-3: qa-auto-review（QA自动审查） | **高** | 是 | 保留 |
| WF-4: qa-gate-85（QA门禁） | **高** | 是 | 保留 |
| WF-5: task-status（任务状态） | **中** | 部分 | 保留（建议优化触发机制） |
| WF-6: butler-execute（Butler执行） | **高** | 是 | 保留 |
| WF-7: expert-review（专家评审） | **高** | 是 | 保留 |
| WF-8: lysander-approve（Lysander审批） | **高** | 是 | 保留 |

**评审意见**：
- WF-1/WF-2/WF-3/WF-4 属于 Synapse 情报闭环核心组件（发现→评估→执行→报告），不可替代。
- WF-5（task-status）：触发条件依赖 `active_tasks.yaml` 变更，属于状态驱动的轻量通知，与 daily_pipeline 中的 06:00 Dubai 定时任务存在功能重叠。建议合并或降级为可选模块。
- WF-6/WF-7/WF-8 对应 Synapse 四级决策体系的 L1/L2/L3 层，决策链的核心组件，与现有 `decision_triggers` 配置完全对齐，不可替代。

### A.2 可行性评估

**关键发现：所有 8 个 webhook 均处于 404 未激活状态**

根据 `webhook-activation-results.md` 的测试结果：

```
POST + GET https://n8n.lysander.bond/webhook/{8个路径} → 全部返回 404
成功率：0/8
```

**根因分析**：
1. **最可能**：8 个 n8n workflow 实体未在 n8n 实例中创建（或创建了但处于 Inactive/Draft 状态）
2. **次可能**：n8n 实例本身未正确配置 webhook 路由（服务器返回 404 而非网络不可达）
3. **排除**：URL path 错误可能性低——`n8n_integration.yaml` 配置路径与 webhook-activation-results.md 中的测试路径一致

**n8n 能力可行性分析**（假设 workflow 实体存在）：

| Node 类型 | n8n 支持性 | 备注 |
|-----------|-----------|------|
| Webhook Trigger | ✅ 支持 | 基础 node |
| Schedule Trigger（cron） | ✅ 支持 | 基础 node |
| HTTP Request | ✅ 支持 | 基础 node |
| Slack/WeChat Notify | ✅ 官方集成 | n8n 社区 node |
| GitHub/Git Push Trigger | ✅ 官方集成 | n8n 社区 node |
| Claude AI / Anthropic API | ✅ HTTP Request 调用 | 需自建认证 |
| Condition / Switch | ✅ 支持 | 基础 node |
| Code (JS) | ✅ 支持 | 高级 node |

**结论**：n8n 能力层面完全支持所有 8 个 workflow 的 node 设计，**方案技术可行性的唯一阻塞项是 workflow 实体未创建**。

### A.3 扩展性评估

| 维度 | 当前评分 | 说明 |
|------|:--------:|------|
| 新增情报源 | 7/10 | event_chains 链式结构支持追加，但 schedule 硬编码需改配置 |
| 新增决策链节点 | 8/10 | decision_triggers 支持 L2/L3/L4 分层扩展 |
| 多 workflow 协同 | 6/10 | **警告**：当前缺乏跨 WF 数据传递的版本控制，旧 WF 执行可能覆盖新 WF 输入 |
| 定时任务扩展 | 8/10 | cron 配置支持任意扩展 |
| **平均** | **7.25/10** | 中等偏上，但跨 WF 数据一致性问题需关注 |

**扩展性改进建议**：
- 为 event_chains 中的每个 trigger 增加 `version` 字段，防止配置升级时与旧版本冲突
- WF-5（task-status）改为订阅模式（Event-driven）而非轮询，提升扩展性

---

## 二、运维可靠性评估

### B.1 故障自愈机制评估

| Workflow | 当前自愈设计 | 评分(1-5) | 改进建议 |
|----------|------------|:---------:|---------|
| WF-1: intelligence-action | 无自动重试配置，仅定时触发 | **1** | 增加：触发失败 → 等待10分钟 → 重试1次 → 失败则 Slack 通知 |
| WF-2: action-notify | 无重试逻辑，失败直接丢弃 | **1** | 增加：HTTP 失败重试2次（指数退避） |
| WF-3: qa-auto-review | git push 触发后无状态跟踪 | **2** | 增加：webhook 执行超时（30s）后写入失败日志并通知 |
| WF-4: qa-gate-85 | 无条件分支，score<85 时阻止但无重试 | **2** | 增加：阻止后通知integration_qa + 保留触发上下文供人工复查 |
| WF-5: task-status | 无自愈机制，yaml 写失败则静默丢失 | **1** | 增加：写入前先读当前状态，避免覆盖 |
| WF-6: butler-execute | 无超时和重试配置 | **1** | 增加：L1决策超时 60s，无响应则降级为 L2 |
| WF-7: expert-review | 无超时配置，等待专家响应 | **2** | 增加：专家 24h 无响应则升级通知 |
| WF-8: lysander-approve | 决策超时无配置（webhook等待机制缺失） | **1** | 增加：Lysander 48h 无响应则自动降级提醒 |
| **平均** | — | **1.4** | **整体极低，WF-7 相对最强** |

**核心问题**：当前 `n8n_integration.yaml` 中**没有任何 retry / timeout / fallback 配置**。所有 8 个 workflow 均依赖"成功执行一次"的乐观假设，无任何失败兜底。

### B.2 安全风险评估

| 风险ID | 级别 | 描述 | 影响 |
|--------|------|------|------|
| **SEC-P0-1** | **P0** | **所有 8 个 webhook 无认证机制** — 任何知道 URL 的主体均可触发 workflow，可能导致未授权执行（如恶意触发 qa-gate-85 伪造通过） | 情报数据污染 / QA 门禁绕过 |
| **SEC-P1-1** | P1 | qa-auto-review 的 git push 触发条件（files_match）可被绕过 — 提交任意文件到 agent-butler 目录即可触发 QA，执行任意代码 | 代码注入风险 |
| **SEC-P1-2** | P1 | butler-execute / expert-review / lysander-approve 的 webhook 无签名验证 — n8n 实例被攻破后，攻击者可直接调用决策链 | 决策链注入 |
| **SEC-P2-1** | P2 | health_check 的 critical_urls 列表未加密存储在 YAML 配置中，信息暴露 | 低风险（情报价值有限） |
| **SEC-P2-2** | P2 | n8n 实例基础认证（user/password）未在配置中说明，默认凭证风险 | 低风险（需人工确认） |

**安全评审结论**：SEC-P0-1 是**阻塞性安全漏洞**，必须修复后才能进入生产执行。当前所有 webhook 均处于"裸奔"状态。

### B.3 SLA 评估

| Workflow | 当前SLA目标 | 是否合理 | 评估意见 |
|----------|------------|:--------:|---------|
| WF-1: intelligence-action | 未定义 | ❌ | 建议：执行成功率 ≥99%（24h滚动），响应时间 ≤5分钟 |
| WF-2: action-notify | 未定义 | ❌ | 建议：送达成功率 ≥99.5%，响应时间 ≤30秒 |
| WF-3: qa-auto-review | 未定义 | ❌ | 建议：触发后 5 分钟内完成评分，结果推送 Slack |
| WF-4: qa-gate-85 | 未定义 | ❌ | 建议：评分计算 ≤1分钟，门禁判断 ≤30秒 |
| WF-5: task-status | 未定义 | ❌ | 建议：触发后 1 分钟内更新状态 |
| WF-6: butler-execute | 未定义 | ❌ | 建议：L1 决策执行 ≤60秒，超时降级 L2 |
| WF-7: expert-review | 未定义 | ❌ | 建议：专家召集 ≤30分钟，评审完成 ≤24小时 |
| WF-8: lysander-approve | 未定义 | ❌ | 建议：Lysander 决策 ≤48小时，超时自动提醒 |

**结论**：所有 8 个 workflow 的 SLA 均**未在配置中定义**，属配置缺失。需由 integration_qa 联合 harness_ops 在 Phase 1 执行后补充 SLA 定义文档。

### B.4 数据一致性评估

| 跨WF数据流 | 一致性风险 | 当前保障 | 评级 |
|-----------|-----------|---------|------|
| intelligence-action → action-notify | 前者输出被后者消费，无版本号 | 无保障 | ❌ 高风险 |
| qa-auto-review → qa-gate-85 | score 数据通过 webhook body 传递，无签名 | 无保障 | ❌ 高风险 |
| task-status → active_tasks.yaml | 并发写入时覆盖风险 | 无保障 | ❌ 高风险 |

---

## 三、综合评分

| 维度 | 得分 | 权重 | 加权分 | 说明 |
|------|:----:|:----:|:------:|------|
| 必要性 | 8.5/10 | 20% | 1.70 | 情报+决策链核心，WF-5 略冗余 |
| 可行性 | 4.0/10 | 20% | 0.80 | **0/8 webhook 已激活，P0 阻塞** |
| 扩展性 | 7.25/10 | 10% | 0.73 | 中等偏上，跨WF数据一致性需改进 |
| 故障自愈 | 2.0/10 | 25% | 0.50 | **平均 1.4/5，整体极低** |
| 安全性 | 3.0/10 | 25% | 0.75 | **SEC-P0-1 无认证，P1-1 代码注入** |
| **总分** | — | 100% | **4.48/10** | 整体可靠性严重不足 |

---

## 四、评审结论

**REJECT — 当前方案不具备生产执行条件**

### 拒绝原因

1. **P0 阻塞**：所有 8 个 n8n workflow 实体尚未在 n8n 实例中创建（0/8 激活）
2. **P0 安全漏洞**：所有 webhook 无认证机制，可被未授权触发
3. **P0 故障自愈**：8 个 workflow 平均自愈评分 1.4/5，单点故障无任何兜底

### 前提条件

以下 P0 项**必须修复**，才能将结论升为 APPROVE_WITH_CONDITIONS：

---

## 五、必须修复项（REJECT → APPROVE_WITH_CONDITIONS 门槛）

### P0 阻塞项（必须修复后才能执行）

| ID | 严重性 | 问题 | 修复方案 | 负责团队 |
|----|--------|------|---------|---------|
| **P0-A1** | **P0** | 8/8 n8n workflow 实体不存在 | 在 n8n UI 中创建所有 8 个 workflow 并激活（见人工操作清单） | **harness_ops** |
| **P0-A2** | **P0** | 所有 webhook 无认证（SEC-P0-1） | 为每个 webhook 添加 `x-n8n-webhook-signature` HMAC 验证（payload + secret 签名），n8n workflow 中增加 Code node 验证签名 | **harness_ops + ai_systems_dev** |
| **P0-A3** | **P0** | 故障自愈机制完全缺失 | 每个 workflow 增加 Retry node（指数退避，最多3次）+ Error Trigger → Slack 通知链 | **harness_ops** |

### P1 建议项（可在执行后迭代）

| ID | 严重性 | 问题 | 修复方案 | 负责团队 |
|----|--------|------|---------|---------|
| **P1-B1** | P1 | qa-auto-review 可被任意文件触发（SEC-P1-1） | 改为仅响应 git tag 或 release 事件，而非任意文件 push | **harness_ops** |
| **P1-B2** | P1 | 所有 SLA 未定义 | 创建 `n8n-sla-definition.md`，为每个 WF 定义 RTO/RPO | **integration_qa** |
| **P1-B3** | P1 | 跨 WF 数据无版本控制 | 为 event chain 中的每个 trigger 增加 `data_version` 字段 | **harness_ops** |
| **P1-B4** | P1 | WF-5 task-status 与 daily_pipeline 06:00 任务重叠 | 合并或明确区分触发条件（状态驱动 vs 定时轮询） | **harness_engineer** |
| **P1-B5** | P2 | health_check 未加密存储关键 URL | 迁移 webhook URL 到环境变量，配置中引用 `${N8N_WEBHOOK_XXX}` | **ai_systems_dev** |

---

## 六、运维手册（执行后必须建立）

> 以下为 runbook 草稿，在 P0 项修复并通过 24h 监控验证后，由 integration_qa 正式编写。

### Runbook WF-1：intelligence-action

```
触发条件：每日 Dubai 10:00 定时（UTC 06:00）
webhook URL：https://n8n.lysander.bond/webhook/intelligence-action
前置条件：n8n workflow 状态为 Active

执行检查项：
[ ] 1. 登录 n8n UI，确认 workflow 状态为 Active（绿色）
[ ] 2. 检查上次执行时间是否为今日
[ ] 3. 检查执行日志无 ERROR 级别

故障处理：
- 若执行失败：等待 10 分钟 → 自动重试（第 1 次）
- 若重试失败：Slack 通知 harness_ops → 人工介入
- 若 webhook 404：执行 Webhook 激活流程（见附录 A）

恢复验证：执行日志出现 "intelligence_action_completed" 事件
```

### Runbook WF-2：action-notify

```
触发条件：intelligence-action 完成（webhook chain 触发）
webhook URL：https://n8n.lysander.bond/webhook/action-notify
前置条件：WF-1 成功执行

执行检查项：
[ ] 1. Slack 收到任务报告消息
[ ] 2. 消息内容包含行动成果摘要（非空）

故障处理：
- 若 Slack 消息未收到：检查 Slack MCP 连接状态
- 若 webhook 超时（30s）：重试 2 次后通知 harness_ops

恢复验证：Slack channel 出现新消息（来自 Slack MCP）
```

### Runbook WF-3/WF-4：qa-auto-review / qa-gate-85

```
触发条件：git push 事件（Webhooks by GitHub / generic）
webhook URL：https://n8n.lysander.bond/webhook/{qa-auto-review,qa-gate-85}
前置条件：仓库已注册到 n8n GitHub integration

执行检查项：
[ ] 1. git push 后 5 分钟内 Slack 收到 QA 评分消息
[ ] 2. 评分 ≥85 时 delivery approved，<85 时 delivery blocked
[ ] 3. blocking 消息包含具体评分维度和改进建议

故障处理：
- 若 webhook 未触发：检查 GitHub webhook 注册状态
- 若 QA 评分计算超时：终止 workflow，写入 error_log

恢复验证：Slack 消息出现 QA Score: XX/100
```

### Runbook WF-5：task-status

```
触发条件：active_tasks.yaml 变更（File nodes watch trigger）
webhook URL：https://n8n.lysander.bond/webhook/task-status
前置条件：n8n file nodes 可访问仓库文件系统

执行检查项：
[ ] 1. active_tasks.yaml 变更后 1 分钟内 Slack 收到状态通知
[ ] 2. 通知包含任务名 + 新状态 + 时间戳

故障处理：
- 若 yaml 写入冲突：先读后写（read → modify → write），避免覆盖
- 若 webhook 超时：跳过本次通知，下次变更时重试

恢复验证：Slack 消息出现任务状态更新
```

### Runbook WF-6~8：butler-execute / expert-review / lysander-approve

```
触发条件：决策体系 L1/L2/L3 调用（http request from Agent）
webhook URL：https://n8n.lysander.bond/webhook/{butler-execute,expert-review,lysander-approve}
安全要求：所有请求必须携带 HMAC 签名（x-n8n-signature 头）

执行检查项：
[ ] 1. 请求携带有效签名
[ ] 2. workflow 在 60s 内响应（L1）或记录专家召集状态（L2/L3）
[ ] 3. L3 等待 Lysander 响应，超时 48h 自动提醒

故障处理：
- 若签名验证失败：返回 401，拒绝执行
- 若 workflow 无响应：超时后降级通知（L1→L2，L3→总裁提醒）

恢复验证：决策链日志出现对应的 decision_level 记录
```

---

## 附录 A：Webhook 激活流程（n8n UI 人工操作）

> 必须由 harness_ops 在 n8n UI（https://n8n.lysander.bond）中逐个执行

**前置条件**：
- 登录 n8n 实例（admin 权限）
- 已准备好 8 个 workflow 的 JSON 配置文件（若 workflow 不存在，需先创建）

**激活步骤**（每个 webhook 重复）：
1. 在 n8n UI 左侧菜单点击 "Workflows"
2. 打开或创建目标 workflow（如 "intelligence-action"）
3. 确认 webhook node 的 Path 为 `/webhook/intelligence-action`（无 test 后缀）
4. 点击 **"Test workflow"** 按钮（不是 Save，不是 Activate 开关）
5. 等待 5 秒，确认状态变为 "Active"
6. 使用 `curl -X POST https://n8n.lysander.bond/webhook/intelligence-action -d '{}'` 验证返回 200

**验收标准**：8/8 webhook 均返回 HTTP 200（非 404），且连续 3 次调用行为一致。

---

*评审报告生成：execution_auditor + integration_qa 联合评审组*
*生成时间：2026-04-22*
*报告版本：v1.0（Phase 1 执行前评审）*