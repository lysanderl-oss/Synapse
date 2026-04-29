---
date: 2026-04-25
type: diagnosis-report
objective: OBJ-N8N-WORKFLOW-AUDIT
phase: stage-1-slack-routing-rca
author: harness_engineer + n8n_ops (sub-agent)
classification: read-only-investigation
---

# WF-09 Slack 路由诊断报告

**日期**：2026-04-25
**Objective**：OBJ-N8N-WORKFLOW-AUDIT 阶段 1 子任务 — Slack 路由根因
**调研范围**：WF-09 Unified Notification (`atit1zW3VYUL54CJ`) 当前实际行为
**红线遵守**：仅读取节点定义 + 历史 executions，未修改任何 workflow，未发送任何测试 Slack 消息

---

## 一、当前 WF-09 实际配置

### 1.1 Workflow 元信息
- ID：`atit1zW3VYUL54CJ`
- Name：**`WF-09 Unified Notification`**（**未改名**）
- Active：`true`
- updatedAt：`2026-04-25T04:55:44.393Z`（今早被改过）

### 1.2 Send Slack 节点（HTTP Request → chat.postMessage）
- URL：`https://slack.com/api/chat.postMessage`
- channel 字段：`{{ $json.channelId }}` ← **不是硬编码 channel，靠 Parse Recipient 上游决定**
- body：`*{{title}}*\n\n{{body}}\n\n_来源: {{source}} | 优先级: {{priority}}_`
- 鉴权：`genericCredentialType` httpHeaderAuth（OAuth Bot Token）

### 1.3 Parse Recipient 节点（关键路由逻辑）
完整 JS code（来自当前线上 workflow）：
```js
const b = $input.first().json;
const r = b.recipient || '';
let ch = r;
if (r === 'president') ch = 'C0AV1JAHZHB';  // #ai-agents-noti
else if (r.startsWith('@U')) ch = r.substring(1);
return [{ json: { channelId: ch, ...b } }];
```

**路由规则解读**：
- 调用方传 `recipient='president'` → `channelId='C0AV1JAHZHB'`（#ai-agents-noti channel） ✅ 正确路由
- 调用方传 `recipient='@U...'` → 截掉 @ → 投到该用户 DM
- 调用方传**裸 UID**（如 `U0ASLJZMVDE`）→ **fallback 直接 `ch = r;`** → Slack API 收到 UID 自动转 DM `D0AUZENMGMS`

### 1.4 重命名核实（针对总裁的"改序号"操作）
| Workflow ID | 当前 name | updatedAt |
|---|---|---|
| `atit1zW3VYUL54CJ` | **`WF-09 Unified Notification`** | 2026-04-25 04:55:44 |
| `203fXfKkfqD1juuT` | **`WF-09 Webhook 未覆盖告警`** | 2026-04-24 16:43:35 |

**结论**：两个 workflow 都仍叫 "WF-09 ..."，**重命名未生效或被回滚**。两者并未发生编号冲突（只是前缀重名），不影响调用，但治理上仍是技术债。

---

## 二、最近 10 次 executions 实际投递目标

| Exec ID | 时间 (UTC) | source | recipient 输入 | channelId 输出 | Slack 实际 channel | ok |
|---|---|---|---|---|---|---|
| 11608 | 2026-04-25 05:44:53 | intel-daily | `U0ASLJZMVDE` | `U0ASLJZMVDE` | **D0AUZENMGMS (总裁 DM)** | ✅ |
| 11596 | 2026-04-25 05:30:12 | intel-daily | `U0ASLJZMVDE` | `U0ASLJZMVDE` | **D0AUZENMGMS** | ✅ |
| 11583 | 2026-04-25 05:09:53 | intel-daily (diag) | `U0ASLJZMVDE` | `U0ASLJZMVDE` | **D0AUZENMGMS** | ✅ |
| 11582–11576 | 2026-04-25 05:09:44–52 | intel-daily (diag x7) | `U0ASLJZMVDE` | `U0ASLJZMVDE` | **D0AUZENMGMS** | ✅ |

**铁证**：最近 10 次 execution **0 次**进入 `C0AV1JAHZHB` (#ai-agents-noti)，**100%** 投递到总裁 DM (`D0AUZENMGMS`)。Slack 层面 `ok=true`，所以总裁的"看到了消息"是真的，"在 slack bot DM 里"也是真的。

---

## 三、调用方传 recipient 当前值

### 3.1 shared_context.notify_slack 默认逻辑
`scripts/intelligence/shared_context.py:357-359`：
```python
# 默认 recipient（总裁 DM UID）
if recipient is None:
    recipient = os.environ.get("SLACK_DEFAULT_RECIPIENT", "U0ASLJZMVDE")
```
**默认就是裸 UID**，恰好命中 Parse Recipient 的 fallback 分支。

### 3.2 4 个调用方的实际传参
| 调用方 | 文件:行 | 传 recipient？ | 实际值 |
|---|---|---|---|
| daily_agent (情报日报) | `daily_agent.py:186` | ❌ 不传 | 走默认 `U0ASLJZMVDE` |
| action_agent (情报行动) | `action_agent.py:164` | ❌ 不传 | 走默认 `U0ASLJZMVDE` |
| resume_agent (任务恢复) | `resume_agent.py:229` | ❌ 不传 | 走默认 `U0ASLJZMVDE` |
| heartbeat_check | `heartbeat_check.py:79` | ✅ **传 `'president'`** | → `C0AV1JAHZHB` (#ai-agents-noti) |

**关键差异**：heartbeat 已经按新契约迁移完成（用 `'president'` 关键字路由），但 daily/action/resume 三个核心管线**完全没有迁移**。

### 3.3 与 2026-04-24 工作日志的交叉验证
工作日志 `obs/00-daily-work/2026-04-24-work-log.md:11-12, 25` 已记录："WF-09 路由切换至 #ai-agents-noti，根因是调用方传入的 payload 字段契约不对齐"。**说明问题昨日已被识别但只完成了 WF-09 侧的改造（加 'president' 分支）+ heartbeat 一个调用方迁移**，daily/action/resume 三方未迁移，所以总裁今日观察"还是发到 bot DM"是真实的。

---

## 四、根因结论

**根因 = A 型（"半改完"状态，调用方未同步迁移）**

证据链：
1. WF-09 已具备路由到 #ai-agents-noti 的能力（Parse Recipient 的 `'president'` 分支 + 硬编码 channel `C0AV1JAHZHB`）
2. 但触发该分支的前提是**调用方传 `recipient='president'`**
3. 实际调用方 daily/action/resume 三者**完全不传 recipient**，走默认 `U0ASLJZMVDE`
4. Parse Recipient 对裸 UID 的 fallback 是"原样透传"，UID 直接送进 chat.postMessage 的 channel 字段
5. Slack API 对收到 UID 的行为是**自动转 DM**，导致全部消息进入 `D0AUZENMGMS`（总裁与 bot 的 1:1 DM）
6. 最近 10 次 execution 0 次进入 #ai-agents-noti，100% 进入 DM — 实证完成

**排除 B**：不是 channel 配置/样式问题，消息从未到达 #ai-agents-noti
**排除 C**：总裁改的就是 atit1zW3VYUL54CJ（updatedAt 04:55 与今早一致），对的 workflow

---

## 五、对总裁观察的解读

总裁原话："**所有的管线推送 我看都推送到了 slack bot 中，但 slack bot 的效果不好。我已经安排 WF-09 的 slack 通知工作流变更为推送到 slack channel #ai-agents-noti 中**"

精准解读：
- "推到 slack bot 中" = **物理事实**：所有 daily/action/resume 消息进入了**总裁与 Synapse bot 的 1:1 DM**（channel ID `D0AUZENMGMS`，D 前缀代表 Direct Message）。这就是俗称的"slack bot 收件箱"。
- "效果不好" = 推断为以下之一（或多重叠加）：
  - DM 列表里多个 bot 消息混杂、无法快速定位
  - 团队协作场景缺失（DM 只有总裁一人能看，其他 agent 角色无法响应）
  - 移动端 Slack 推送策略对 bot DM 不友好（默认静音/折叠）
  - 缺少 channel 上下文（没有 thread / pinned / channel 历史检索）
- "已变更为 #ai-agents-noti" = **WF-09 节点配置已部分变更**（加了 'president' 分支），但因调用方未迁移而未生效。这不是总裁的判断错误，而是改造只完成了链路的一半。

---

## 六、修复方案候选（仅列出，不执行）

### 档 A：调用方迁移 — 3 个 agent 改默认值
**操作**：把 `SLACK_DEFAULT_RECIPIENT` 默认值从 `U0ASLJZMVDE` 改为 `'president'`，或在 daily/action/resume 三处显式传 `recipient='president'`。
**优点**：与 heartbeat 已采用的契约一致；保留 WF-09 多目标路由能力（未来某条消息要发 DM 仍可显式传 UID）；改动量极小（1 处环境变量 或 3 处代码 1 行）；无 n8n 风险。
**缺点**：仍需所有未来新增调用方记得传 `'president'`，存在重复犯错风险。
**契约清晰度**：⭐⭐⭐⭐

### 档 B：WF-09 Parse Recipient 强制重定向
**操作**：把 JS 改为 "无论收到什么 recipient，统一 ch = 'C0AV1JAHZHB'"（去除 fallback 透传）。
**优点**：调用方零改动；最快生效；总裁观察的"通通进 channel"立即实现。
**缺点**：永久失去多目标路由能力；未来需要 P0 告警发 DM 给特定值班人时无法支持；与 heartbeat 已传 `'president'` 的设计冗余但无害。
**契约清晰度**：⭐⭐⭐（功能退化）

### 档 C：WF-09 移除 recipient 概念，硬编码
**操作**：Parse Recipient 节点直接删除，Send Slack 节点 channel 字段写死 `C0AV1JAHZHB`。
**优点**：节点最少、最简单。
**缺点**：同 B，且更激进；调用方继续传 recipient 字段会变成无效字段（兼容但浪费）；后续要恢复多目标需重建节点。
**契约清晰度**：⭐⭐（语义丢失）

### 档 D：双轨制（推荐方向）
**操作**：档 A + 在 shared_context.py 增加 `recipient` 参数显式默认值规范 + 在 README/契约文档中明确"业务通知传 'president'，紧急 DM 才传 UID" + 加 lint/CI 检查未传 recipient 的 notify_slack 调用 → 警告。
**优点**：长期治理；契约即代码；不依赖人脑记住。
**缺点**：工作量略大（需加 lint 规则）；但与"feedback_root_cause_first" + "契约对齐"治理理念最一致。
**契约清晰度**：⭐⭐⭐⭐⭐

---

## 七、给评估阶段的输入数据

**核心事实清单**（评估阶段直接复用）：
1. 现状：3/4 调用方未迁移，100% 发到总裁 DM
2. WF-09 已具备路由能力，channel ID `C0AV1JAHZHB` 已硬编码且可用
3. heartbeat 是迁移参考样板（`recipient='president'`）
4. 默认值变更为 `'president'` 是单点低风险修复
5. 改 Parse Recipient 是 n8n 侧改动（有静默失败历史风险，需要 dry-run 验证）
6. 治理债：两个 workflow 都叫 "WF-09 *"，总裁的"改序号"未落地

**待评估阶段决策点**：
- 短期止血：档 A（调用方改默认） vs 档 B（WF-09 强制路由）— 哪个先上？
- 长期治理：是否做档 D 的 lint 规则？
- 治理债清理：是否在本次一并处理 WF-09 重命名？
- 风险评估：档 A 改 1 行环境变量是否需要走完整 PR + QA 流程？

---

**报告完毕。等待评估阶段综合后呈报总裁。**
