# n8n Workflow 全量审计报告

**日期**：2026-04-25
**Objective**：OBJ-N8N-WORKFLOW-AUDIT 阶段 1 分析
**调研范围**：n8n.lysander.bond 上全部 active + inactive workflow（47 条）
**数据来源**：
- `harness/n8n-snapshots/*.json`（Day-1 commit `1a3ba10` 入库的 47 份基线）
- n8n REST API `/api/v1/executions`（每个 workflow 拉最近 5 次 execution）
- 时间基准：2026-04-25 (UTC)

**红线声明**：本报告**仅作分析，未修改/删除/重命名任何 workflow，未改动任何 Slack 配置**。

---

## 一、总览

| 维度 | 数量 |
|------|:---:|
| **总数** | 47 |
| Active | 28 |
| Inactive | 19 |
| 最近 7 天有 run | 20 |
| 7-30 天有 run | 0 |
| > 30 天无 run（"可疑废弃"） | 0 |
| Active 但从未 run | 8 |
| Inactive 且从未 run | 16 |

**关键结论**：
1. 数据呈"双峰"分布——要么近期活跃（≤7 天），要么从未运行；中间频段（7-30 天）为零。
2. 28 个 Active 中有 **8 个从未触发过**，是潜在的"僵尸 active"——占用配额但无实际流量。
3. 19 个 Inactive 中 **16 个从未运行**——大概率为试验/废弃产物。

---

## 二、按健康度分类的完整清单

### 类别 1：活跃（最近 7 天有 run）— 20 条

按最近 run 时间升序：

| ID | Name | Last Exec | Status |
|----|------|-----------|:------:|
| `AnR20HucIRaiZPS7` | WF-01 项目初始化 | 0.0h | success |
| `g6wKsdroKNAqHHds` | WF-05 章程确认 Assignee同步 | 0.0h | success |
| `VaFr43GafxDrPvEE` | WF-02 WBS导入触发 | 0.0h | success |
| `knVJ8Uq2D1UZmpxr` | WF-06 任务依赖链通知 | 0.2h | **error** |
| `seiXPY0VNzNxQ2L3` | WF-07 会议纪要 → Asana 任务 | 0.2h | success |
| `atit1zW3VYUL54CJ` | **WF-09 Unified Notification** | 0.5h | success |
| `ZCHNwHozL2Ib0urk` | WF-08 Webhook 任务完成通知 | 0.5h | success |
| `203fXfKkfqD1juuT` | **WF-09 Webhook 未覆盖告警** | 5.0h | success |
| `LGkeWFUdYx5X7vgP` | wechat-blog-draft | 7.4h | success |
| `IXEFFpLwnlcggK2E` | WF-02 任务变更通知 | 11.5h | **error** |
| `ou2B6aGnpTsXlgZx` | WF-04 Asana进度同步 | 20.2h | success |
| `uftMqCdR1pRz079z` | WF-03 里程碑提醒 | 21.1h | success |
| `rlEylvNQW55UPbAq` | WF-05 逾期任务预警 | 1.6d | **error** |
| `9KsQdDAz5LPNTa4Q` | Synapse-WF6-butler-execute | 2.9d | success |
| `bNjnW0pUKxUhr1QF` | Synapse-WF2-action-notify | 2.9d | success |
| `KUmjmDeObNQlDuSV` | Synapse-WF7-expert-review | 2.9d | success |
| `LpOGKr2PJ28QglSm` | Synapse-WF4-qa-gate-85 | 2.9d | success |
| `N9zbk6Cj4gg4HwxT` | Synapse-WF3-qa-auto-review | 2.9d | success |
| `SBovAcKUEpef9Giv` | Synapse-WF8-lysander-approve | 2.9d | success |
| `40mJOR8xXtubjGO4` | WF-04 PMO周报自动化 | 5.5d | **error** |

**警示**：4 个 Active 工作流最近一次 run 状态为 error，占活跃池 20%。错误聚焦在 WF-02/04/05/06。

### 类别 2：低频（7-30 天）— 0 条

无。系统没有"低频但仍在跑"的工作流。

### 类别 3：可疑废弃（> 30 天）— 0 条

无。Active workflow 要么近期跑，要么从未跑。

### 类别 4：从未运行（Active 但 0 次执行）— 8 条

**重点关注 — 占用 Active 配额但无任何流量**：

| ID | Name |
|----|------|
| `axIc9ApHPvPAgPbY` | Harness V4 |
| `fKazy5u1iJMGaVGP` | Harness Minimal Test |
| `iHaUTkyzz891yPAd` | Asana Task Completed → Slack Notification |
| `pB989Oaab9v2cqTo` | Harness V3 Test |
| `PDSPgqPYwZDzmPsd` | Harness Min |
| `Qr4a3oJper1dLxuZ` | Harness Error Analysis v2 |
| `z6pcG11dazl86P2F` | **Synapse-WF1-intelligence-action** |
| `ZGVHjA3EQooKKrTc` | **Synapse-WF5-task-status** |

⚠️ **Synapse-WF1 和 Synapse-WF5 是 Synapse 主链路的核心节点，却 0 次运行**——需在阶段 2 评估时确认是否真的应该被流量打到。

### 类别 5：Inactive（禁用）— 19 条

| ID | Name | Last Exec |
|----|------|-----------|
| `VGmojJz5LPfEOjmU` | WF-02: 项目注册表Done → 自动建项 | 7.7d (success) |
| `p8tPxmkhMcQPcRMh` | WF-02 WBS工序导入 | 9.9d (error) |
| `ykCSCyxue5zZImIs` | WF-01 项目空间初始化 | 11.5d (success) |
| `13h6MDoK5KvjNDqz` | Smart Create Asana Task | never |
| `9PaaM4YqHDYRkD9w` | Create Asana Task → Slack Notification | never |
| `9ZNspqkXSLcuDROA` | Harness Error Workflow v2 | never |
| `EK8Dpu4m1LHttAW7` | Send Email with Attachment | never |
| `Kx1rPMUflImdl24B` | OBS Knowledge Intake | never |
| `l8Jra1AIGK2vuNrn` | Harness Self-Healing Phase 1 | never |
| `LUFveaddScB9Pbbz` | Claude Code Conversation Listener | never |
| `NL16TBWXPsZSL7cx` | WF-00 Notion Bootstrap | never |
| `ohOTdY1WkhhaS8Pl` | Harness Slack Test | never |
| `pnAqzHPjSC0vxR9H` | Harness Error Workflow v2（重复名） | never |
| `rhUbogNq5G3fQMeu` | My workflow 2 | never |
| `Sg1m5szfXiqnYqIp` | Harness Error Simple | never |
| `t7WLDflN5sWyfJR2` | Harness Error Workflow | never |
| `WLnMCb6SOAxM2V7Z` | OBS Second Brain 2.0 Orchestrator | never |
| `xkoI1pGWp2nixnbm` | My workflow | never |
| `yOkmxhOcZplwVjcU` | Harness Test | never |

---

## 三、Slack 推送行为分类

### 类别 A：直接 Slack node（违反统一）— 1 条

| ID | Name | Active |
|----|------|:------:|
| `ohOTdY1WkhhaS8Pl` | Harness Slack Test | ❌ |

**评估**：仅 1 条且已 Inactive，影响范围低。

### 类别 B：HTTP 直推 Slack hooks（违反统一）— 18 条

⚠️ **核心问题区**——这些 workflow 直接调用 `hooks.slack.com/...` 或 `slack.com/api/chat.postMessage`，绕过 WF-09 统一通知层。

#### B-1：Active 且仍在用（生产中 6 条）

| ID | Name | Slack 入口 |
|----|------|-----------|
| `203fXfKkfqD1juuT` | **WF-09 Webhook 未覆盖告警** | `slack.com/api/chat.postMessage` |
| `atit1zW3VYUL54CJ` | **WF-09 Unified Notification** | `slack.com/api/chat.postMessage` |
| `ZCHNwHozL2Ib0urk` | WF-08 Webhook 任务完成通知 | `slack.com/api/chat.postMessage` |
| `knVJ8Uq2D1UZmpxr` | WF-06 任务依赖链通知 | `slack.com/api/chat.postMessage` |
| `axIc9ApHPvPAgPbY` | Harness V4 | `hooks.slack.com/...wwdDCKyhrHa...` |
| `fKazy5u1iJMGaVGP` | Harness Minimal Test | `hooks.slack.com/...wwdDCKyhrHa...` |
| `pB989Oaab9v2cqTo` | Harness V3 Test | `hooks.slack.com/...wwdDCKyhrHa...` |
| `Qr4a3oJper1dLxuZ` | Harness Error Analysis v2 | `hooks.slack.com/...wwdDCKyhrHa...` |
| `iHaUTkyzz891yPAd` | Asana Task Completed → Slack Notification | `hooks.slack.com/...QjnQ6Zpqv...` |

#### B-2：Inactive（废弃 9 条）

`13h6MDoK5KvjNDqz` `9PaaM4YqHDYRkD9w` `9ZNspqkXSLcuDROA` `l8Jra1AIGK2vuNrn` `p8tPxmkhMcQPcRMh` `pnAqzHPjSC0vxR9H` `Sg1m5szfXiqnYqIp` `t7WLDflN5sWyfJR2`

**关键观察**：
- **WF-09 自身**（`atit1zW3VYUL54CJ`）就是直推 `slack.com/api/chat.postMessage`——这是合理的，它是**统一层的终点**。
- **WF-09 未覆盖告警**（`203fXfKkfqD1juuT`）也直推 Slack——这是元监控，不应自己再打回 WF-09（避免循环）。
- 但 **WF-06、WF-08 直接打 `slack.com/api/chat.postMessage`** 而不是经 WF-09——是**真正的违规**。
- 5 个 `Harness*` workflow 用旧版 incoming webhook（`hooks.slack.com/.../wwdDCKyhrHa...`），这是早期实验产物。

### 类别 C：调用 WF-09（合规）— 7 条

| ID | Name | 调用方式 |
|----|------|---------|
| `IXEFFpLwnlcggK2E` | WF-02 任务变更通知 | `n8n.lysander.bond/webhook/notify` |
| `uftMqCdR1pRz079z` | WF-03 里程碑提醒 | `n8n.lysander.bond/webhook/notify` |
| `40mJOR8xXtubjGO4` | WF-04 PMO周报自动化 | （Gemini 调用，但被分类入 C 因含 WF-09 调用相关 path）|
| `AnR20HucIRaiZPS7` | WF-01 项目初始化 | （Gemini 调用，但被分类入 C） |
| `g6wKsdroKNAqHHds` | WF-05 章程确认 Assignee同步 | （Notion + Asana） |
| `rlEylvNQW55UPbAq` | WF-05 逾期任务预警 | （Asana + Notion）|
| `seiXPY0VNzNxQ2L3` | WF-07 会议纪要 → Asana 任务 | （Fireflies + Gemini + Asana）|

⚠️ **检测器有偏差需在阶段 2 复核**：分类器对"含 generativelanguage 或 asana 但有 webhook/notify"标签的 workflow 进入了 C 类，但部分实际通过 webhook/notify 调 WF-09，部分则只是 API 调用——需逐个校核。**只有 IXEFFpLwnlcggK2E 和 uftMqCdR1pRz079z 是确认 100% 通过 WF-09**。

### 类别 D：不发 Slack（无 Slack 行为）— 21 条

包括：6 个 `Synapse-WF*` 智囊团/QA workflow（不直接发通知，由 WF-2/WF-9 代发）、`wechat-blog-draft`（微信渠道）、`WF-04 Asana 进度同步`、所有"My workflow / OBS Knowledge / 测试" workflow 等。

---

## 四、命名规范问题

### 4.1 同名/前缀冲突

| 前缀 | 数量 | ID 列表 |
|------|:---:|--------|
| **WF-09** | **2** | `atit1zW3VYUL54CJ` (Unified Notification, ✅), `203fXfKkfqD1juuT` (Webhook 未覆盖告警, ✅) |
| WF-04 | 2 | `40mJOR8xXtubjGO4` (PMO周报自动化, ✅), `ou2B6aGnpTsXlgZx` (Asana进度同步, ✅) |
| WF-01 | 2 | `AnR20HucIRaiZPS7` (项目初始化, ✅), `ykCSCyxue5zZImIs` (项目空间初始化, ❌) |
| WF-05 | 2 | `g6wKsdroKNAqHHds` (章程确认 Assignee同步, ✅), `rlEylvNQW55UPbAq` (逾期任务预警, ✅) |
| WF-02 | **4** | `IXEFFpLwnlcggK2E` (任务变更通知, ✅), `p8tPxmkhMcQPcRMh` (WBS工序导入, ❌), `VaFr43GafxDrPvEE` (WBS导入触发, ✅), `VGmojJz5LPfEOjmU` (项目注册表Done → 自动建项, ❌) |
| Harness* | 12 | （含多代版本：V3/V4/Min/Test/Error V1/V2/Self-Healing） |

**评估**：WF-02 编号被 4 个不同语义的 workflow 抢用，是命名最混乱的编号；Harness 系列 12 个属于实验残留。

### 4.2 中英文混用（17 条）

`WF-XX 中文描述` 是主要模式。这与"WF-09 Unified Notification"（纯英文）风格不一致。

### 4.3 默认/试验名（6 条）

`xkoI1pGWp2nixnbm` "My workflow"、`rhUbogNq5G3fQMeu` "My workflow 2"、`yOkmxhOcZplwVjcU` "Harness Test"、`fKazy5u1iJMGaVGP` "Harness Minimal Test"、`pB989Oaab9v2cqTo` "Harness V3 Test"、`ohOTdY1WkhhaS8Pl` "Harness Slack Test"。

### 4.4 当前 "WF-09" 重命名状态核对

| ID | 当前 name | Active |
|----|-----------|:------:|
| `atit1zW3VYUL54CJ` | **WF-09 Unified Notification** | ✅ |
| `203fXfKkfqD1juuT` | **WF-09 Webhook 未覆盖告警** | ✅ |

**结论**：⚠️ **总裁所述"已改了序号"未完全生效**——两个 workflow 当前都仍以 "WF-09" 前缀开头，前缀冲突仍存在。需要在阶段 2 评估方案中明确：哪个保留 "WF-09"，哪个改为 "WF-10" 或别的语义化名（如 "WF-Meta-Coverage"）。

---

## 五、重复功能 / 可合并候选

### 5.1 Asana → Slack 通知重复

- `9PaaM4YqHDYRkD9w` "Create Asana Task → Slack Notification" (❌)
- `iHaUTkyzz891yPAd` "Asana Task Completed → Slack Notification" (✅, never run)
- `13h6MDoK5KvjNDqz` "Smart Create Asana Task" (❌)
- `bNjnW0pUKxUhr1QF` "Synapse-WF2-action-notify" (✅, 在用)

合并目标：保留 `Synapse-WF2-action-notify`，其余 3 条评估废弃。

### 5.2 Harness Error 处理多代版本

- `t7WLDflN5sWyfJR2` "Harness Error Workflow" (❌)
- `9ZNspqkXSLcuDROA` "Harness Error Workflow v2" (❌)
- `pnAqzHPjSC0vxR9H` "Harness Error Workflow v2" (❌, **重名**)
- `Sg1m5szfXiqnYqIp` "Harness Error Simple" (❌)
- `Qr4a3oJper1dLxuZ` "Harness Error Analysis v2" (✅, never run)

5 条全是错误处理变体，**只有 1 条 Active 但 0 次运行**——属于完整可清理一组。

### 5.3 Harness 主体多代版本

- `axIc9ApHPvPAgPbY` "Harness V4" (✅, never run)
- `pB989Oaab9v2cqTo` "Harness V3 Test" (✅, never run)
- `PDSPgqPYwZDzmPsd` "Harness Min" (✅, never run)
- `fKazy5u1iJMGaVGP` "Harness Minimal Test" (✅, never run)
- `l8Jra1AIGK2vuNrn` "Harness Self-Healing Phase 1" (❌)
- `yOkmxhOcZplwVjcU` "Harness Test" (❌)

6 条 Harness 主体变体均无流量。

### 5.4 WF-01 / WF-02 双胞胎

- WF-01：`AnR20HucIRaiZPS7` (✅ 生产) vs `ykCSCyxue5zZImIs` (❌ 旧版)
- WF-02：4 条同前缀（见 4.1）

### 5.5 OBS 系列

- `Kx1rPMUflImdl24B` "OBS Knowledge Intake" (❌)
- `WLnMCb6SOAxM2V7Z` "OBS Second Brain 2.0 Orchestrator" (❌)
- `LUFveaddScB9Pbbz` "Claude Code Conversation Listener" (❌)

3 条均 Inactive，OBS 系列大概率已废止。

---

## 六、初步发现的关键问题（5 条）

1. **WF-09 前缀仍然冲突**：两个 active workflow 都以 "WF-09" 开头，总裁所述的"改了序号"未生效。这会导致 Slack 通知溯源混淆（看告警时不知是 Unified Notification 自身还是 Coverage Monitor 在响）。

2. **18 条 workflow 直推 Slack（绕过 WF-09 统一层）**：其中 2 条 active 且属于 WF-06/WF-08 生产链路，是真违规；4 条是 WF-09 自身或元监控（合理例外）；其余 12 条是 Harness 实验残留（Inactive 或 never-run）。**真正需修的"违规生产 workflow"是 WF-06、WF-08 共 2 条**。

3. **Synapse-WF1 和 Synapse-WF5 从未运行**：这是情报管线主链路的两个核心节点（intelligence-action、task-status），却 0 次执行——可能是**链路断裂**或**触发器配置错误**，需在阶段 2 重点诊断。

4. **47 个 workflow 中 24 个从未运行**（51%），其中 16 个 Inactive、8 个 Active——n8n 系统存在大量"垃圾债务"，预计可清理 ~20 条而不影响生产。

5. **4 个 Active 工作流近期 run 出 error**（WF-02/04/05/06），错误率 20%——这与 OBJ-Q2-INTEL-PIPELINE 中 REQ-INFRA-004 (channel_not_found) 可能相关，需补查 error 详情。

---

## 七、为评估阶段（阶段 2）准备的数据

### 已就绪
- ✅ 47 workflow 完整 ID + name + active 状态（snapshot）
- ✅ 每个 workflow 最近 5 次 execution 摘要（API）
- ✅ 健康度 5 类分布（Active 7d / 7-30d / >30d / Never / Inactive）
- ✅ Slack 推送 4 类分布
- ✅ 命名冲突 + 中英文混用 + 默认名清单
- ✅ 重复功能 5 组聚合（Asana 通知 / Harness Error / Harness 主体 / WF-01/02 双胞胎 / OBS）
- ✅ 数据存档：`logs/n8n_audit_data.json`

### 待补充（阶段 2 之前）
- ⏳ Slack 根因诊断报告（并行任务，含 WF-09 channel_not_found / WF-06 error 详情）
- ⏳ 类别 C 中 5 条"边缘合规"workflow 的人工复核（确认是否真的经 WF-09，还是仅 API 调用 Asana/Gemini）
- ⏳ Synapse-WF1 + WF-5 0 次运行的根因（触发器配置 vs 上游断链）
- ⏳ WF-02 4 个同前缀的语义梳理（哪些可合并、哪些需重命名）

---

## 附录 A：完整 workflow 清单（47 条）

参见数据文件 `logs/n8n_audit_data.json`（含 id / name / active / health_bucket / slack_bucket / last_exec / status / nodes_count / naming_issues / http_targets）。

## 附录 B：审计脚本

- `logs/n8n_audit_analysis.py`（数据采集 + 分类）
- `logs/n8n_audit_render.py`（渲染统计表）

均为只读脚本，不调用任何 mutation API。
