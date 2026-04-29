# 情报管线"自我进化闭环"审计报告

**日期**：2026-04-26
**议题**：总裁观察"只看到日报，没看到升级动作"，实证情报管线 4 步闭环（发现→评估→执行→报告）的真实状态
**审计员**：integration_qa（子 Agent，独立上下文）
**方法**：实证（git / gh / grep / 代码静读），不修改任何代码或配置

---

## 一、CLAUDE.md 设计 vs 实际运行

### 1.1 设计意图（4 步闭环）

按 CLAUDE.md L101 "情报闭环管线 — 发现→评估→执行→报告"：

| 层 | 名称 | 自动化机制 | 应有产出 |
|----|------|-----------|---------|
| L1 | 发现 | `intel-daily.yml` (08:00 Dubai) | `obs/06-daily-reports/{D}-intelligence-daily.html` |
| L2 | 评估 | `intel-action.yml` (10:00 Dubai) | `obs/06-daily-reports/{D+1}-action-report.md` + 派单/入池 |
| L3 | 执行 | Lysander 派单 Harness Ops 团队落地 | git commits / 文档 / 配置变更 |
| L4 | 报告 | `active_tasks.yaml` 关闭 + `requirements_pool.yaml` 升级 | INTEL-* 状态 done / source: INTEL-* 的 REQ |

### 1.2 实证结论（一句话）

**闭环只走到 L2 的"产出 markdown 报告"为止；L2 中的"派单/入池"动作和 L3/L4 全部断裂**，因为 `action_agent.py` 不写回 `active_tasks.yaml` 或 `requirements_pool.yaml`，只生成报告 markdown。

---

## 二、Layer 1 发现层：intel-daily 实证

### 2.1 文件产出（最近 8 天）

```
2026-04-19 daily.html  ✓
2026-04-20 daily.html  ✓
2026-04-21 daily.html  ✓
2026-04-22 daily.html  ✗（无产出）
2026-04-23 daily.html  ✗（无产出）
2026-04-24 daily.html  ✓
2026-04-25 daily.html  ✓
2026-04-26 daily.html  ✓
```

### 2.2 workflow run 状态

最近 10 次 intel-daily 状态：8 次 success / 1 次 failure / 多次重跑。 **L1 基本健康，但有 2 天空窗（04-22/04-23）**。

### 2.3 L1 评分：⚠️ 基本正常（83% 覆盖率，有 2 天空窗未补跑）

---

## 三、Layer 2 评估层：intel-action 实证

### 3.1 workflow 运行情况

```
2026-04-26T07:19  schedule  success  id=24951021659
2026-04-25T07:05  schedule  success  id=24925313600
2026-04-24T16:52  workflow_dispatch  success  id=24901344126
2026-04-24T16:43  workflow_dispatch  success  id=24900981659
```

**注意**：仅 4 条记录！workflow 文件中标注 "Week 2 切流生产启用（2026-04-24）"，schedule trigger 在 04-25 才开始。04-19 至 04-23 期间 **workflow 根本未运行**，只有手动触发的两次（04-17、04-19、04-20 的 action-report 是手动跑的）。

### 3.2 文件产出（最近 8 天）

```
2026-04-17 action-report.md  ✓
2026-04-19 action-report.md  ✓
2026-04-20 action-report.md  ✓
2026-04-21 action-report.md  ✗（缺）
2026-04-24 action-report.md  ✗（缺，只有 daily 没有 action）
2026-04-25 action-report.md  ✓
2026-04-26 action-report.md  ✓
```

### 3.3 决策分布（2026-04-26 报告）

读 `obs/06-daily-reports/2026-04-26-action-report.md` 摘要：
- 情报条目总数：7（含 1 条截断）
- execute 决策：3 条（INTEL-20260426-001/002/003，P1）
- inbox 决策：4 条（004/005/006/007，P2）
- deferred / rejected：0 条

**报告本体写得很好**——包含 4 专家评分矩阵 + 派单清单 + 完整 yaml block 列出"要追加到 active_tasks.yaml 的新任务"。

### 3.4 L2 评分：⚠️ 报告生成正常，但"派单/入池动作"形同虚设（详见第四节）

---

## 四、Layer 3 执行层：闭环关键审计 ← 决定性证据

### 4.1 active_tasks.yaml 中的 INTEL-* 任务

```bash
$ grep -E "id:.*INTEL-20260" agent-CEO/config/active_tasks.yaml
INTEL-20260419-001    INTEL-20260419-002    INTEL-20260419-003
INTEL-20260419-004    INTEL-20260419-005    INTEL-20260420-001
INTEL-20260420-002    INTEL-20260420-003    INTEL-20260420-004
INTEL-20260420-005    INTEL-20260420-006    INTEL-20260420-007
INTEL-20260421-001
```

**最新 INTEL-* 任务 = INTEL-20260421-001**。

但是 04-25 action-report 生成了 7 个 `INTEL-20260425-001..007`，04-26 action-report 生成了 5 个 `INTEL-20260426-001..005`。

```bash
$ grep -E "INTEL-20260425|INTEL-20260426" agent-CEO/config/active_tasks.yaml
（无任何输出）
```

**实证结论**：04-25 和 04-26 评估层产出的 12 条新任务，**0 条**写入了 `active_tasks.yaml`。

### 4.2 requirements_pool.yaml 中 source: INTEL-* 的 REQ

```bash
$ grep -E "source:.*INTEL-" obs/02-product-knowledge/requirements_pool.yaml
source: "INTEL-20260420-002 立项"   → REQ-JD-001 (Janus Digital)
source: "INTEL-20260420-003 立项"   → REQ-EG-001 (Enterprise Governance)
```

**只有 2 条 REQ 来自 INTEL，且都是 04-20 的，时间 = 2026-04-24 立项**。这两条是 Lysander 在 04-24 主对话中**手动**整理立项的，**不是 intel-action.yml 自动写的**。

### 4.3 action_agent.py 是否真的写回这两个 yaml？← 决定性代码证据

读 `scripts/intelligence/action_agent.py`（211 行）：

```python
# action_agent.py 全文 import:
from shared_context import (
    ...
    load_active_tasks,         # 只 load，不 write
    load_organization_yaml,    # 只 load，不 write
    ...
)

# run_action_report() 写文件部分（第 138-156 行）:
output_file = REPORTS_DIR / f"{report_date}-action-report.md"
output_file.write_text(final_md, encoding="utf-8")
print(f"[Done] 行动报告已写入 {output_file}")
```

**全文 211 行中：**
- `write_text` 只调用一次 → 写 `*-action-report.md`
- 无任何 `active_tasks.yaml` 写入逻辑
- 无任何 `requirements_pool.yaml` 写入逻辑

**workflow yaml 进一步证实**（`.github/workflows/intel-action.yml` 第 71 行）：

```yaml
git add obs/06-daily-reports/*-action-report.md || true
```

git add 只匹配 `*-action-report.md`，**即使 action_agent.py 改动了 yaml 文件，也不会被提交**。

### 4.4 L3 评分：❌ 完全断裂（0 条自动写回）

---

## 五、Layer 4 报告层：沉淀机制

### 5.1 完整闭环案例（INTEL → REQ → shipped）

| INTEL ID | 升级路径 | 当前状态 |
|---------|---------|---------|
| INTEL-20260420-002 | → REQ-JD-001 | in_progress（手动立项 2026-04-24） |
| INTEL-20260420-003 | → REQ-EG-001 | in_progress（手动立项 2026-04-24） |
| 其他 11 条 INTEL-* | 未升级 | inbox 状态停留 |
| INTEL-20260425/26-* | 未进 active_tasks | 仅在 markdown 报告中存在 |

### 5.2 INTEL-20260420-007（停服迁移，P0）

**唯一一个有真实 evidence 的执行案例**——但是因为它是 4-20 立项的手动派单，notes 中显示"2026-04-22 rd_devops 完成全库扫描"，证明 **L3 执行靠的是 Lysander 主对话手动驱动，不是自动派单**。

### 5.3 L4 评分：❌ 沉淀机制依赖人工，自动化为零

---

## 六、根因判定

### 选 **结论 A**：intel-action 在跑，但只生成 markdown 报告，没有"派单/入池"动作

**决定性证据三条**：

1. **代码证据**：`action_agent.py` 整文件只写 `*-action-report.md`，无任何 yaml 写回逻辑（第 138-156 行）。
2. **workflow 证据**：`intel-action.yml` 第 71 行 `git add obs/06-daily-reports/*-action-report.md`，git stage 范围只含 markdown。
3. **数据证据**：04-25/04-26 action-report 共计生成 12 条 INTEL-2026042{5,6}-* 任务 ID，0 条写入 `active_tasks.yaml`。

排除其他可能：
- ❌ 结论 B（写回逻辑有 bug）：根本没有写回逻辑，不存在 bug
- ❌ 结论 C（全部 deferred）：04-26 决策中 3 execute + 4 inbox + 0 deferred，不是质量问题
- ❌ 结论 D：实证已穷尽

### 总裁感知的精确解释

总裁说"只看到情报日报，没看到升级动作"——精确原因是：

1. **8:00 daily（发现）有产出 → 总裁能看到**
2. **10:00 action（评估）有产出 → 报告 markdown 存在但总裁没意识到这是"评估"，因为它不出现在 active_tasks.yaml**
3. **派单/入池（升级）= 0 → 看不到，因为根本没发生**
4. **执行/沉淀 = 0 → 看不到，因为没派单**

总裁本能感知正确：**情报管线在第 2.5 步（评估完成 → 派单前）断裂**。

---

## 七、给 Lysander 综合后呈报总裁的核心要点

### 7.1 总裁问题的精确答复

> "情报管线我只看到了情报日报，但没有看到情报日报的选择性升级的动作"

**实证答复**：

1. **评估层在跑，但是产物只有 markdown 报告**（`obs/06-daily-reports/{D}-action-report.md`）。报告里有完整的 4 专家评分 + 决策 + 派单清单 + yaml block，但是这个 yaml block **从未被写入** `active_tasks.yaml`，**仅作为建议文本存在于 markdown 中**。
2. **过去 7 天产出了 12 条新 INTEL 任务 ID（04-25 七条 + 04-26 五条），实际进入 active_tasks 的 = 0 条**。
3. **历史上唯二的 INTEL → REQ 升级案例**（REQ-JD-001、REQ-EG-001）都是 Lysander 在 04-24 主对话中**手动**立项，不是自动管线产出。
4. **代码层根因**：`scripts/intelligence/action_agent.py` 不调用 yaml 写回。

### 7.2 修复方案候选（3 档）

| 档 | 名称 | 实现成本 | 风险 | 自动化程度 |
|---|------|---------|------|-----------|
| **A** | 全自动派单 | 高（200-300 行 Python） | 中（误派单 / 路由错误，需 QA） | 100% |
| **B** | 半自动 inbox | 中（50-100 行 Python） | 低（只入池不派单，Lysander 手动 review） | 70% |
| **C** | 周一全量 review | 低（流程改造） | 极低（保持现状 + 流程节奏） | 0%（人工） |

#### 档 A — 全自动派单
- 改造点：`action_agent.py` 解析报告中的 yaml block → 用 `ruamel.yaml` 写回 `active_tasks.yaml`；如有 high-score 候选 → 写 `requirements_pool.yaml`
- workflow 改造：`intel-action.yml` 的 `git add` 改为 `git add obs/ agent-CEO/`
- 风险：自动派单到错误 specialist；与 Lysander 派单制度冲突（CLAUDE.md L168 强制 Lysander 主导派单）

#### 档 B — 半自动 inbox（推荐）
- 改造点：`action_agent.py` 在 yaml block 落地时，**统一标 status: pending_review**，写入 `active_tasks.yaml` 的 inbox 区
- Lysander 在主对话中或定期会话开场时，**手动审查 inbox 候选** → 决定派单 / 升级 REQ / 拒绝
- workflow 改造同档 A
- 优点：保留 Lysander 的派单决策权（合规 CLAUDE.md L168）；解决"看不见升级动作"的问题（candidate 出现在 active_tasks）；Lysander 可在每日开场扫一眼

#### 档 C — 维持现状 + 流程改造
- 不改代码
- 改 CLAUDE.md：增加"每周一 Lysander 主对话第一件事 = 复盘上周 7 份 action-report，决定派单/入池"
- 风险：依赖人 disciplined；与 CLAUDE.md L114 "每日自动化全流程"叙事冲突

### 7.3 Lysander 评价（建议立场）

**强烈推荐档 B**：

1. **合规性**：保留 CLAUDE.md L168 强制派单制度（Lysander 主导，子 Agent 执行）
2. **可见性**：解决总裁感知问题（候选在 active_tasks 可见）
3. **可观测性**：Lysander 每日开场能扫到 pending_review，自动驱动派单链
4. **实施成本**：50-100 行代码改造，1 个 PR 即可上线
5. **演进路径**：B 稳定后，可对低风险类目（如纯文档类、纯研究类）演进为档 A 自动派单

不推荐档 A：与现有 CLAUDE.md 强制派单制度冲突，需要先做规则修订。
不推荐档 C：违背"自动化全流程"设计原则，且依赖人工 discipline，长期失败概率高。

---

## 八、给 Lysander 的一行

✅ **闭环审计：第 L2→L3 之间断裂（评估完成但未派单/入池），根因 = `action_agent.py` 仅写 markdown 不写回 yaml，推荐方案档 B（半自动 inbox + Lysander 手动 review）**
