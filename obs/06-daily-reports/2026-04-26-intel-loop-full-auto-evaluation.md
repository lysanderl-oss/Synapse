# 情报管线全自动方案重评估

**日期**：2026-04-26
**作者**：synapse_product_owner + harness_engineer（联合子 Agent，独立上下文）
**派单方**：Lysander
**触发**：总裁追问"方案 B 无法实现全自动，我想实现全自动还有什么更合适的方案？"

---

## 一、问题陈述与误判溯源

### 1.1 总裁诉求

总裁明确表达：**情报管线必须实现全自动闭环**，半自动方案（B）无法接受。

### 1.2 之前 Lysander 的拒绝理由

档 A（情报评估高分项 → 自动写入 active_tasks.yaml / 自动派单）被 Lysander 拒绝，理由是：

> "违反 CLAUDE.md L168 强制 Lysander 主对话派单原则。"

### 1.3 实证发现：L168 引用错误

经实证，CLAUDE.md L168 实际内容是：

> ```
> 168 │       3. 截图未通过 → 任务不得标记完成，必须返工
> ```

L168 是 **Visual QA 截图验收规则**，与"派单原则"完全无关。

**真正的派单约束位于：**

| 行号 | 规则块 | 内容 |
|---|---|---|
| L65–L88 | CEO 执行禁区（P0） | "Lysander 主对话不得直接调用 Bash/Edit/Write" |
| L201–L240 | 强制团队派单制度 | "Lysander 在调用 Edit/Write/Bash 之前必须先输出团队派单表" |
| L75–L83 | 唯一合法执行路径 | Lysander 主对话 → 派单 → 子 Agent 执行 |

### 1.4 关键问题：约束的真实射程

CLAUDE.md 的派单约束**只针对一种情境**：

> **当 Lysander 主对话本身需要执行 Edit/Write/Bash 时，必须先派单给子 Agent。**

它**没有约束**：
- GitHub Actions cron job（无 Lysander 介入的纯自动化）
- 子 Agent 在自己的子上下文内的工具调用
- 任何不经过 Lysander 主对话的写操作

**结论：之前 Lysander 以"违反 L168"否决档 A，是引用错误 + 范围误判。**

---

## 二、L168 实证（直接文本）

### 2.1 实证结论

| 项目 | 内容 |
|---|---|
| L168 实际内容 | Visual QA 截图未通过 → 必须返工 |
| 与"派单"关系 | **无关** |
| 真正的派单约束位置 | L65–L88 CEO 执行禁区、L201–L240 强制派单制度 |
| 派单约束的真实射程 | **仅限 Lysander 主对话内**，不约束 GitHub Actions / cron |

### 2.2 文本引用（CEO 执行禁区，L70–L86）

```
**Lysander 作为 CEO，被明确禁止以下行为：**
- 在主对话中直接调用 Bash、Edit、Write、WebSearch、WebFetch 工具
- 在未完成 Lysander 承接（【0.5】）的情况下直接派单或执行 ← P0 违规

**唯一合法执行路径：**
  1. 分析任务 → 确定执行团队
  2. 输出团队派单表（强制前置）
  3. 调用 Agent 工具 或 /dispatch Skill → 创建子 Agent
  4. 子 Agent 在独立上下文中执行 Bash/Edit/Write
  5. 子 Agent 返回结果 → Lysander 审查交付

**工具白名单（主对话允许）：** Read · Skill · Agent · Glob · Grep
**工具黑名单（主对话禁止）：** Bash · Edit · Write · WebSearch · WebFetch
```

**关键短语**：禁止"**在主对话中**直接调用"、"**主对话**禁止"。
**适用主体**：Lysander（CEO 角色）的主对话上下文。
**不适用主体**：GitHub Actions / cron / 已派单的子 Agent。

---

## 三、三角色权限边界

| 角色 | 主对话/上下文 | 写 yaml 权限 | 派单权限 | 是否需 Lysander 介入 |
|---|---|:---:|:---:|:---:|
| Lysander 主对话 | 单次会话 | ✅（先派单） | ✅ | — |
| Lysander 派单的子 Agent | 独立上下文 | ✅（已被派一次） | ❌ | 仅一次派单 |
| GitHub Actions cron | 无对话 | ✅（**已有先例**） | ❌ | **无需介入** |

### 3.1 GitHub Actions 自动写仓的现存先例（实证）

| 工作流 | 自动 commit 内容 | 是否经 Lysander 主对话 | 是否违反 P0 |
|---|---|:---:|:---:|
| `intel-daily.yml` | `obs/06-daily-reports/*-intelligence-daily.html` | ❌ | ❌ |
| `intel-action.yml` | `obs/06-daily-reports/*-action-report.md` | ❌ | ❌ |
| `task-resume.yml` | **`agent-CEO/config/active_tasks.yaml`** + summary md | ❌ | ❌ |
| `blog-publish.yml` | `obs/...` + `lysander-bond` 同步 | ❌ | ❌ |

**最强证据**：`task-resume.yml`（L66）已经在每天 06:00 Dubai **自动 commit `active_tasks.yaml`**：

```yaml
git add agent-CEO/config/active_tasks.yaml obs/06-daily-reports/*-resume-summary.md
git commit -m "chore(resume): task resume ${{ github.run_id }}"
```

**结论**：GitHub Actions 自动写 `active_tasks.yaml` 已是生产级先例，与 P0 约束完全兼容。
**推论**：档 A1 的"全自动写 active_tasks.yaml"在合规性上**与 task-resume 同源**，不存在新的违规风险。

---

## 四、4 档全自动方案

### 档 A1：全自动入 active_tasks.yaml（不派单不发 Slack）

**机制**：
- `intel-action.yml` 增加一步：解析 action_agent 输出的 yaml 块，append 到 `active_tasks.yaml`，状态 `status: approved-pending-dispatch`
- 不直接派单（派单权仍在 Lysander 主对话）
- 不立即执行（执行授权仍在 Lysander 主对话）
- 总裁/Lysander 在合适时机 review active_tasks.yaml，决定派单或忽略

**优点**：
- 完全自动闭环到 inbox
- 与 task-resume 同构，合规性 100%
- 风险下限（不动生产，不抢资源）

**缺点**：
- INTEL 条目可能积累，需周期性清理
- 总裁需主动看 inbox（但 task-resume 早报已通知）

### 档 A2：全自动入需求池 + 自动派单到专业 Agent

**机制**：
- 高分（≥18/20）情报 → 自动升级为 REQ + 自动派单到 graphify_strategist 等
- 中分（12–17）→ 入 active_tasks.yaml
- 低分（<12）→ 忽略

**优点**：
- 最大自动化程度

**缺点**：
- 绕过 Lysander 派单权（即使派给的是专业 Agent，也违反"Lysander 主对话作为唯一派单方"的精神）
- 风险高：错误评分会触发实际生产动作
- Lysander 失去资源调度把控

### 档 A3：全自动入池 + Slack 通知 #ai-agents-noti

**机制**：
- 在档 A1 基础上，调用 WF-09 通知"今日新增 N 条 INTEL，详见 active_tasks.yaml"
- 总裁/Lysander 异步消化

**优点**：
- A1 的合规性 + 可观测性提升
- 总裁有"被动感知"通道

**缺点**：
- 通知噪声（每天都会有）
- 需占用 WF-09 配额

### 档 A4：分层自动化（基于决策类型分级）

**机制**：
| 决策类型 | 自动化等级 | 行为 |
|---|---|---|
| `execute`（高分立即执行）| ❌ 不自动 | 必须 Lysander 主对话派单 |
| `inbox`（入 active_tasks）| ✅ 全自动 | GH Actions 写 |
| `deferred`（延后评估）| 仅生成报告 | 无写入 |
| `rejected` | 忽略 | 无写入 |

**优点**：
- 把"全自动"限定在最低风险面（inbox）
- 与现有架构（Lysander 派单 + cron 自动）天然对齐
- 决策面分层，每层风险可独立审计

**缺点**：
- 实现复杂度略高（需要 prompt 让 action_agent 输出决策类型分类）
- 高分项仍需 Lysander 介入（部分自动）

---

## 五、加权评分矩阵

### 5.1 权重设计

| 维度 | 权重 | 说明 |
|---|:---:|---|
| 自动化程度 | 30% | 是否真正"全自动"，无人工介入 |
| 合规性 | 25% | 不违反 CLAUDE.md P0 约束 |
| 安全性 | 20% | 不会乱动生产、不抢资源 |
| 可观测性 | 15% | 总裁/Lysander 能否感知发生了什么 |
| 实施成本 | 10% | 工作量大小（分越高 = 成本越低） |

### 5.2 评分（5 分制）

| 维度 | 权重 | A1 | A2 | A3 | A4 |
|---|:---:|:---:|:---:|:---:|:---:|
| 自动化程度 | 30% | 4 | 5 | 4 | 4.5 |
| 合规性 | 25% | 5 | 2 | 5 | 5 |
| 安全性 | 20% | 5 | 2 | 5 | 4.5 |
| 可观测性 | 15% | 3 | 3 | 5 | 4 |
| 实施成本 | 10% | 5 | 3 | 4 | 3.5 |

### 5.3 加权得分

| 档 | 计算 | 加权得分 |
|---|---|:---:|
| **A1** | 4·0.30 + 5·0.25 + 5·0.20 + 3·0.15 + 5·0.10 | **4.40** |
| A2 | 5·0.30 + 2·0.25 + 2·0.20 + 3·0.15 + 3·0.10 | 2.95 |
| A3 | 4·0.30 + 5·0.25 + 5·0.20 + 5·0.15 + 4·0.10 | **4.60** |
| **A4** | 4.5·0.30 + 5·0.25 + 4.5·0.20 + 4·0.15 + 3.5·0.10 | **4.45** |

### 5.4 排序

1. **A3（4.60）** — 全自动入池 + Slack 通知
2. **A4（4.45）** — 分层自动化
3. **A1（4.40）** — 全自动入池（无通知）
4. A2（2.95）— 自动派单（合规性差）

---

## 六、综合推荐

### 6.1 首选：档 A3

**Lysander 推荐档 A3：全自动入 active_tasks.yaml + Slack 通知 #ai-agents-noti**

**理由**：
1. **合规性 100%**：与 task-resume.yml 同构，已有生产级先例
2. **可观测性最佳**：总裁不会"被偷偷写 yaml"，每天有通知
3. **风险最低**：只入 inbox，不抢资源、不动生产、不替 Lysander 派单
4. **自动化达成总裁诉求**：从"评估完写报告 → 等人看"升级到"评估完入池 + 通知"，闭环完整

### 6.2 实施工作量

| 工作项 | 执行者 | 工作量 |
|---|---|---|
| 修改 `action_agent.py`：解析模型输出的 yaml 块，append 到 `active_tasks.yaml` | ai_systems_dev | ~60 行 Python |
| 修改 `intel-action.yml`：新增 `git add agent-CEO/config/active_tasks.yaml` | harness_engineer | 1 行 YAML |
| 修改 prompt（intelligence-action）：要求模型按 schema 输出 yaml 块 | knowledge_engineer | ~20 行 prompt |
| 调用 WF-09 通知"今日新增 N 条 INTEL" | ai_systems_dev | ~30 行 Python |
| QA：dry-run 一次完整链路，验证不破坏现有 task-resume | integration_qa | 1 次端到端测试 |

预计总工作量：**1 个 S–M 级派单可完成**。

### 6.3 备选：档 A4

如果总裁担心 A3 通知噪声，备选 **A4 分层自动化**（4.45）：
- inbox 全自动（同 A1）
- execute 类决策保留为 Lysander 主对话审批
- Slack 通知降级为"周报 / 阈值触发"

### 6.4 否决：档 A2

档 A2 因绕过 Lysander 派单权，违反 CLAUDE.md L65–L88 CEO 执行禁区精神，**否决**。

---

## 七、与档 B 半自动方案的对比

档 B（已被总裁否决）：评估完仅生成 markdown 报告，等 Lysander 主对话 review 后手动派单。

| 维度 | 档 B（半自动）| 档 A3（推荐）|
|---|---|---|
| 评估 → 报告 | ✅ 自动 | ✅ 自动 |
| 报告 → 入池 | ❌ 手动 | ✅ 自动 |
| 入池 → 派单 | ❌ 手动 | ❌ 手动（保留人工把关）|
| 派单 → 执行 | ❌ 手动 | ❌ 手动 |
| 总裁感知 | ❌ 需主动看 | ✅ Slack 推 |
| 闭环完整性 | 50% | 80% |

**A3 把 B 的"评估→报告→等人"升级为"评估→报告→入池→通知"，闭环度从 50% 提升到 80%。**

剩余 20%（入池→派单→执行）刻意保留为人工，**因 CLAUDE.md P0 约束的精神就在这里**：派单和执行是 Lysander 主对话的核心职责，不能让 cron 自动接管。

---

## 八、原档 A 否决理由的纠正

| 项 | 之前判断 | 实证后判断 |
|---|---|---|
| 引用 L168 | "违反派单原则" | **L168 是 Visual QA 规则，与派单无关** |
| 真正约束位置 | 未引用 | L65–L88（CEO 执行禁区）+ L201–L240（强制派单）|
| 约束射程 | 推断"覆盖所有自动写操作" | **仅限 Lysander 主对话**，不覆盖 GH Actions |
| 档 A 是否违反 | "违反" | **档 A1/A3/A4 不违反**；档 A2 违反派单权精神 |

**结论**：原档 A 否决理由 = **误判**。
**应纠正**：档 A1/A3/A4 全部合规，可以推进；档 A2 因独立的派单权精神问题保持否决。

---

## 九、给 Lysander 的一行

`✅ 全自动方案重评估：L168 实证 = Visual QA 规则（非派单约束），推荐档 A3（加权 4.60，全自动入 active_tasks.yaml + Slack 通知，与 task-resume 同构合规），原档 A 否决理由 = 误判（L168 引用错误 + 约束射程误读），应纠正后推进 A3 实施。`
