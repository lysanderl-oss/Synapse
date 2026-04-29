# P2-B 垃圾债务处置报告

**日期**: 2026-04-25
**OBJ**: OBJ-N8N-WORKFLOW-AUDIT 阶段 4 / 子任务 P2-B
**执行**: harness_engineer + n8n_ops 联合子 Agent
**输入**: 阶段 1 审计 `logs/n8n_audit_data.json`（47 条 workflow 全量）

---

## 一、24 条从未运行 workflow 分类与处置

### 类 1 自动删（6 条）— 全部已 archive + 删除

命名匹配 `test/temp/My workflow` 等明显废弃特征。

| ID | Name | active | 删除原因 | Archive 路径 |
|----|------|--------|----------|--------------|
| `fKazy5u1iJMGaVGP` | Harness Minimal Test | True | 命名含 `Test` | `_archive/fKazy5u1iJMGaVGP.json` |
| `ohOTdY1WkhhaS8Pl` | Harness Slack Test | False | 命名含 `Test` | `_archive/ohOTdY1WkhhaS8Pl.json` |
| `pB989Oaab9v2cqTo` | Harness V3 Test | True | 命名含 `Test` | `_archive/pB989Oaab9v2cqTo.json` |
| `rhUbogNq5G3fQMeu` | My workflow 2 | False | 默认 `My workflow` 命名 | `_archive/rhUbogNq5G3fQMeu.json` |
| `xkoI1pGWp2nixnbm` | My workflow | False | 默认 `My workflow` 命名 | `_archive/xkoI1pGWp2nixnbm.json` |
| `yOkmxhOcZplwVjcU` | Harness Test | False | 命名含 `Test` | `_archive/yOkmxhOcZplwVjcU.json` |

**执行结果**: 6/6 全部 DELETE 200 OK，archive 文件已写入。

### 类 2 [archived] 重命名（12 条）— 8 条手工改名 + 4 条已是 n8n 原生 archived

Inactive 且从未运行，可能有用但休眠。

#### 2.1 已成功改名（8 条）

| ID | 旧名 | 新名 |
|----|------|------|
| `13h6MDoK5KvjNDqz` | Smart Create Asana Task | `[archived] Smart Create Asana Task` |
| `9PaaM4YqHDYRkD9w` | Create Asana Task → Slack Notification | `[archived] Create Asana Task → Slack Notification` |
| `EK8Dpu4m1LHttAW7` | Send Email with Attachment | `[archived] Send Email with Attachment` |
| `Kx1rPMUflImdl24B` | OBS Knowledge Intake | `[archived] OBS Knowledge Intake` |
| `LUFveaddScB9Pbbz` | Claude Code Conversation Listener | `[archived] Claude Code Conversation Listener` |
| `NL16TBWXPsZSL7cx` | WF-00 Notion Bootstrap | `[archived] WF-00 Notion Bootstrap` |
| `t7WLDflN5sWyfJR2` | Harness Error Workflow | `[archived] Harness Error Workflow` |
| `WLnMCb6SOAxM2V7Z` | OBS Second Brain 2.0 Orchestrator | `[archived] OBS Second Brain 2.0 Orchestrator` |

#### 2.2 已是 n8n 原生 archived（4 条，无需操作）

PUT 返回 `400 Cannot update an archived workflow.`，检查 backup 文件 `isArchived: true`，确认 n8n 已在服务端将其标记为 archived，等价于本任务的目标态，无需重复处理。

| ID | Name | n8n 服务端状态 |
|----|------|----------------|
| `9ZNspqkXSLcuDROA` | Harness Error Workflow v2 | `isArchived: true` |
| `l8Jra1AIGK2vuNrn` | Harness Self-Healing Phase 1 | `isArchived: true` |
| `pnAqzHPjSC0vxR9H` | Harness Error Workflow v2 (重名) | `isArchived: true` |
| `Sg1m5szfXiqnYqIp` | Harness Error Simple | `isArchived: true` |

**注**：所有 12 条均已 backup 至 `_pre-p2b-backup/`，回滚可行。

### 类 3 用途不明，调研结果（6 条，未处置）

Active 但从未运行 → 用途不明 / 未触发 / 可能是断裂态。

| ID | Name | Trigger | 节点结构 | 业务推测 | 处置建议（呈报用）|
|----|------|---------|----------|----------|-------------------|
| `axIc9ApHPvPAgPbY` | Harness V4 | webhook `harness-v4` | 4 节点（Webhook → Set → Gemini → Slack）| Harness 错误处理 V4 候选迭代版，等同 Harness Min 但引入 Gemini 分析 | 🟡 **建议保留**：webhook 路径 `harness-v4` 是新一代候选，与生产 `harness-error` 共存合理；如确认弃用可改名 `[archived]` |
| `iHaUTkyzz891yPAd` | Asana Task Completed → Slack Notification | asanaTrigger | 2 节点（Asana → Slack）| Asana 任务完成后推 Slack 通知 | 🟡 **建议保留**：Asana 集成业务通道，未触发可能因近期无任务完成事件；可保留观察 7 天 |
| `PDSPgqPYwZDzmPsd` | Harness Min | webhook `harness-error` | 5 节点（Webhook → Prepare → Gemini → Slack）| **生产 Harness Error 主入口**（webhook 路径 `harness-error`）| 🟢 **强烈保留**：这是 Harness 错误上报的实际生产入口，未运行说明本周无 Harness error 事件触发，不是断裂 |
| `Qr4a3oJper1dLxuZ` | Harness Error Analysis v2 | webhook `harness-analyze` | 4 节点（Webhook → Analyze Server → Slack）| Harness 错误深度分析（调用外部分析服务）| 🟡 **建议保留**：webhook 路径 `harness-analyze` 是分析专用通道，未触发可能因无错误事件 |
| `z6pcG11dazl86P2F` | **Synapse-WF1-intelligence-action** | cron `0 10 * * *` | **2 节点（Schedule → HTTP）** | 每日 10:00 UTC 触发情报行动通知 | 🔴 **断裂**：详见第三节 |
| `ZGVHjA3EQooKKrTc` | **Synapse-WF5-task-status** | cron `0 6 * * *` | **2 节点（Schedule → noOp）** | 每日 06:00 UTC 任务状态检查 | 🔴 **断裂**：详见第三节 |

---

## 二、4 条 Active error workflow 错误根因

| ID | Name | 失败节点 | 错误信息 | 根因分类 | 修复评估 |
|----|------|----------|----------|----------|----------|
| `IXEFFpLwnlcggK2E` | WF-02 任务变更通知 | 搜索变更任务 | `Bad request - You must specify at least one search filter.` | **Notion API 入参缺失**：search 节点未传 filter（最近一次执行 2026-04-24 18:30）| 🟡 **代码可修**：Notion search 节点补齐 filter 参数，预计 5 分钟 |
| `40mJOR8xXtubjGO4` | WF-04 PMO 周报自动化 | 写入 Notion 周报库 | `Could not find database with ID: 2c3a7590-d03b-482a-bcf1-c70ecf11c852` | **Notion DB ID 失效或集成 Janus PMO n8n 未授权该 DB**（最近一次 2026-04-19 17:27）| 🟢 **配置可修**：在 Notion 端将该 DB 共享给 `Janus PMO n8n` 集成，或更新为正确 DB ID |
| `rlEylvNQW55UPbAq` | WF-05 逾期任务预警 | 写入 Notion 逾期预警日志 | `Could not find database with ID: f5cf12cf-b6b6-4664-b5ce-5fa3956b7174` | **同 WF-04**：Notion DB 未授权（最近一次 2026-04-23 17:00）| 🟢 **配置可修**：同 WF-04 |
| `knVJ8Uq2D1UZmpxr` | WF-06 任务依赖链通知 | 查询近期完成任务 | `A 'json' property isn't an object [item 0]` | **n8n 数据格式问题**：上游节点返回数据未包装为 `{json: {...}}`（最近一次 2026-04-25 06:00）| 🟡 **代码可修**：上游节点改用 Code/Set 节点正确包装 JSON，预计 10 分钟 |

**汇总**：4 条 error 中，2 条（WF-04 / WF-05）是同一根因（Notion 集成授权），1 条（WF-02）是 Notion 调用参数缺失，1 条（WF-06）是 n8n 节点数据格式。**全部为可修复型，非架构性问题**。

---

## 三、Synapse-WF1 / WF5 断裂调研

### 3.1 Synapse-WF1-intelligence-action

- **ID**: `z6pcG11dazl86P2F`
- **active**: True
- **创建/更新**: 2026-04-22 08:02:48 UTC（仅 ~3 天前）
- **Trigger**: `n8n-nodes-base.cron`
- **Cron 表达式**: `0 10 * * *`（每日 10:00 UTC，即 Dubai 14:00）
- **节点结构**: 仅 2 节点（Schedule Trigger → HTTP POST `https://n8n.lysander.bond/webhook/action-notify`）
- **执行历史**: **0 次**
- **断裂判定**: 🔴 **真断裂**
  - 创建 3 天，至少应有 2-3 次定时触发；实际 0 执行
  - 推测原因：
    1. **n8n cron 节点未被调度器注册**（n8n 重启后 active workflow 偶发不重新登记，已知 bug）
    2. 节点类型用的是旧版 `n8n-nodes-base.cron`，新版应为 `n8n-nodes-base.scheduleTrigger`
    3. 下游 webhook `/webhook/action-notify` 的接收方未确认存在
- **修复方向（不在本任务范围）**:
  1. 升级触发节点为 `scheduleTrigger`
  2. 确认 `/webhook/action-notify` 由哪个 workflow 接收
  3. 如确认无业务消费方，建议改名 `[archived]` 或删除

### 3.2 Synapse-WF5-task-status

- **ID**: `ZGVHjA3EQooKKrTc`
- **active**: True
- **创建/更新**: 2026-04-22 08:10:13 UTC（仅 ~3 天前）
- **Trigger**: `n8n-nodes-base.cron`
- **Cron 表达式**: `0 6 * * *`（每日 06:00 UTC，即 Dubai 10:00）
- **节点结构**: 仅 2 节点（Schedule Trigger → **noOp** 节点 `operation: log`，仅输出 `Task status check at 6am`）
- **执行历史**: **0 次**
- **断裂判定**: 🔴 **真断裂 + 实现不完整**
  - 与 WF1 同样的 cron 调度器问题
  - 即使触发，下游 noOp 节点没有实际任务状态查询逻辑，仅 log 字符串
- **业务推测**: 是 PMO 任务状态体检的占位 workflow，开发未完成
- **修复方向（不在本任务范围）**:
  1. 升级触发节点为 `scheduleTrigger`
  2. 实现真实的任务状态查询（Notion / PMO API）
  3. 如确认废弃，建议改名 `[archived]`

**根因小结**：WF1/WF5 与现役 PMO Auto V2.0 GA workflow（WF-02/04/05/06）共存但风格断裂——后者用 `scheduleTrigger`，前者用旧版 `cron`，命名前缀也不同（`Synapse-WF` vs `WF-`）。**疑似不同迭代的两个团队产物**。

---

## 四、archive / 备份文件清单

### 4.1 永久档案（`harness/n8n-snapshots/_archive/`）

类 1 删除前的全量 export，6 个文件：

```
fKazy5u1iJMGaVGP.json   Harness Minimal Test
ohOTdY1WkhhaS8Pl.json   Harness Slack Test
pB989Oaab9v2cqTo.json   Harness V3 Test
rhUbogNq5G3fQMeu.json   My workflow 2
xkoI1pGWp2nixnbm.json   My workflow
yOkmxhOcZplwVjcU.json   Harness Test
```

### 4.2 改名前备份（`harness/n8n-snapshots/_pre-p2b-backup/`）

类 2 改名前的全量 export，12 个文件（含 4 个 n8n-native archived，便于回滚）。

### 4.3 处置数据日志（`logs/`）

```
p2b_classification.json        — 3 类初始分类
p2b_class1_results.json        — 类 1 删除结果
p2b_class2_results.json        — 类 2 改名结果
p2b_class3_investigation.json  — 类 3 节点结构
p2b_error_investigation.json   — 4 条 error 根因详情
```

---

## 五、给 Lysander 的呈报点（待审批 / 决策）

### 5.1 类 3 待呈报总裁（6 条）

| ID | Name | 我的建议 | 需总裁拍板 |
|----|------|----------|------------|
| `PDSPgqPYwZDzmPsd` | Harness Min | **保留**，是 Harness Error 生产入口 | ✅ 不需要拍板，技术上确认 |
| `axIc9ApHPvPAgPbY` | Harness V4 | 保留观察 | 是否合并到 Harness Min？ |
| `Qr4a3oJper1dLxuZ` | Harness Error Analysis v2 | 保留观察 | 是否合并到 Harness Min？ |
| `iHaUTkyzz891yPAd` | Asana Task Completed → Slack | 保留观察 7 天 | 是否替换为 PMO Auto V2.0 路径？ |
| `z6pcG11dazl86P2F` | **Synapse-WF1-intelligence-action** | 修复或删除 | 是否仍是有效情报闭环组件？ |
| `ZGVHjA3EQooKKrTc` | **Synapse-WF5-task-status** | 删除（未完成的占位）| 是否替换为 WF-02 任务变更通知？ |

### 5.2 4 条 error workflow 修复授权请求

| Workflow | 修复方式 | 工作量 | 是否授权后续 P3 阶段统一修复 |
|----------|----------|--------|-------------------------------|
| WF-02 | 加 Notion search filter | 5 min | 待批 |
| WF-04 | 在 Notion 端将 DB `2c3a7590...` 共享给 `Janus PMO n8n` | 2 min（人工 Notion 操作）| 待批 |
| WF-05 | 同 WF-04（DB `f5cf12cf...`）| 2 min | 待批 |
| WF-06 | Code/Set 节点 wrap JSON | 10 min | 待批 |

---

## 六、剩余清单

**P2-B 处置前**：47 条 workflow（24 从未运行 + 4 active error + 19 其它）

**P2-B 处置后**：
- 删除 6 条 → 剩 41 条
- 改名 8 条（仍存在，前缀 `[archived]`）
- 4 条 n8n-native archived（仍存在）
- 6 条 类 3 等待决策（仍存在）
- 4 条 error active（仍存在，等 P3 修复）
- **健康 active workflow**: 41 - 12（archived 类）- 6（类 3 待审）- 4（error）= **19 条产线 healthy active**

下一阶段（P3）建议：先修 WF-02/04/05/06 这 4 条 error，再处置类 3 中的 Synapse-WF1/WF5。
