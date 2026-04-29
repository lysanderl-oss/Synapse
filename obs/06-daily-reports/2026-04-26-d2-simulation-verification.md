# D2 dispatch_rules 模拟验证报告

- **日期**：2026-04-26
- **执行者**：integration_qa（子 Agent）
- **派单方**：Lysander（CEO）
- **任务**：用 7 条今日实际 pending-dispatch INTEL 数据，模拟 D2 dispatch_rules 匹配，验证规则合理性
- **关键约束**：仅模拟不修改 active_tasks.yaml，不实际派发任何 action

---

## 一、配置读取确认

| 项 | 状态 |
|---|---|
| `dispatch_rules.enabled` | ✅ true |
| 规则数（rules） | 5 条 |
| 安全门（safeguards） | 4 条 |
| 来源 | OBJ-INTEL-LOOP-CLOSURE D2 升级 |
| 批准人 | 总裁刘子杨 |
| 批准日期 | 2026-04-26 |
| CLAUDE.md ②.5 步 | ✅ 已落地 |

**已加载 5 条规则**（按顺序匹配）：

1. P0 立即派单 — `priority=P0, rice_score_min=18` → `dispatch_immediately`
2. P1 高分升级 REQ — `priority=P1, rice_score_min=15` → `upgrade_to_req`
3. P2 中分入池低优先 — `priority=P2, rice_score_min=10` → `upgrade_to_req`
4. P3 / 低分自动延期 — `priority=P3` → `mark_deferred`
5. 未匹配规则保留待人工 — `default_fallback` → `keep_pending`

**已加载 4 条 safeguards**：

- `max_auto_dispatch_per_session: 3`
- `max_auto_upgrade_per_session: 10`
- `require_lysander_summary: true`
- `revert_on_error: true`

---

## 二、7 条 pending-dispatch INTEL 模拟匹配

> ⚠️ **关键发现**：规则中 `rice_score_min` 字段引用 `task.rice.score`，但 7 条 INTEL **均无 `rice` 字段**，分数嵌入在 `notes` 文本中（"综合评分 N/20"）。
> 故同时跑两种模式：
> - **literal** = 严格按 yaml 字段（无 rice → score=None → 命中条件失败）
> - **realistic** = 从 notes 正则提取分数（模拟 Lysander/人脑的实际行为）

### 2.1 literal 模式（严格按字段）

| INTEL ID | priority | rice.score | 命中规则 | action |
|---|---|---|---|---|
| INTEL-20260427-001 | P1 | None | 未匹配规则保留待人工 | `keep_pending` |
| INTEL-20260427-002 | P1 | None | 未匹配规则保留待人工 | `keep_pending` |
| INTEL-20260427-003 | P1 | None | 未匹配规则保留待人工 | `keep_pending` |
| INTEL-20260427-004 | P2 | None | 未匹配规则保留待人工 | `keep_pending` |
| INTEL-20260427-005 | P2 | None | 未匹配规则保留待人工 | `keep_pending` |
| INTEL-20260427-006 | P2 | None | 未匹配规则保留待人工 | `keep_pending` |
| INTEL-20260427-007 | P2 | None | 未匹配规则保留待人工 | `keep_pending` |

### 2.2 realistic 模式（从 notes 提取嵌入分）

| INTEL ID | priority | embedded_score | 命中规则 | action |
|---|---|---|---|---|
| INTEL-20260427-001 | P1 | 19/20 | P1 高分升级 REQ | `upgrade_to_req` |
| INTEL-20260427-002 | P1 | 18/20 | P1 高分升级 REQ | `upgrade_to_req` |
| INTEL-20260427-003 | P1 | 17/20 | P1 高分升级 REQ | `upgrade_to_req` |
| INTEL-20260427-004 | P2 | 15/20 | P2 中分入池低优先 | `upgrade_to_req` |
| INTEL-20260427-005 | P2 | 14/20 | P2 中分入池低优先 | `upgrade_to_req` |
| INTEL-20260427-006 | P2 | 12/20 | P2 中分入池低优先 | `upgrade_to_req` |
| INTEL-20260427-007 | P2 | 无嵌入分 | 未匹配规则保留待人工 | `keep_pending` |

---

## 三、Action 分布

| Action | literal 模式 | realistic 模式 |
|---|---|---|
| `dispatch_immediately` | 0 | 0 |
| `upgrade_to_req` | 0 | 6 |
| `mark_deferred` | 0 | 0 |
| `keep_pending` | 7 | 1 |
| `NO_MATCH` | 0 | 0 |

---

## 四、Safeguards 触发情况

**两种模式均未触发 safeguards**：

- `dispatch_immediately = 0` < `max_auto_dispatch_per_session = 3` ✅
- `upgrade_to_req = 0/6` ≤ `max_auto_upgrade_per_session = 10` ✅

→ 当前 7 条 INTEL 数据下 safeguards 设计**安全余量充足**。

---

## 五、NO_MATCH 情况

**两种模式 NO_MATCH 均为 0**，因为 `default_fallback` 兜底正确生效。规则覆盖完整。

---

## 六、人工 review 角度合理性评估

### 6.1 realistic 模式逐条评估（实际生效模式）

| INTEL | 模拟 action | 人工评估 | 一致性 |
|---|---|---|---|
| 001 Claude 4 API 迁移准备（19/20） | upgrade_to_req | P1 顶分项，应入需求池等 Q2 排期 | ✅ |
| 002 (18/20, P1) | upgrade_to_req | 同上，符合预期 | ✅ |
| 003 (17/20, P1) | upgrade_to_req | 同上 | ✅ |
| 004 Stanford HAI 白皮书研读（15/20, P2） | upgrade_to_req | 有学术价值，入低优先池合理 | ✅ |
| 005 (14/20, P2) | upgrade_to_req | 合理 | ✅ |
| 006 (12/20, P2) | upgrade_to_req | 合理（≥10 阈值） | ✅ |
| 007 (无嵌入分, P2) | keep_pending | 缺分数无法判断，留待人工合理 | ✅ |

**realistic 模式合理性：高**

### 6.2 literal 模式问题（设计缺陷暴露）

literal 模式下 7 条全部 `keep_pending`，**等于 D2 自动消化机制完全失效**——
因为 intel-action 写入 active_tasks 时**未填充 rice 结构化字段**。

这不是规则本身的逻辑问题，而是**数据契约缺失**：rules 期望 `task.rice.score`，
但生产数据流（intel-action → active_tasks.yaml）只把分数写进 notes 文本。

---

## 七、推荐调整

### P0（必须修复，否则 D2 自动消化跑不起来）

**Option A（推荐）：改 intel-action 写入逻辑**，让 INTEL 任务带结构化 `rice` 字段：

```yaml
- id: INTEL-20260427-001
  priority: P1
  rice:
    score: 19
    reach: ...
    impact: ...
    confidence: ...
    effort: ...
  notes: "..."
```

负责团队：harness_engineer + ai_systems_dev（改 `scripts/intelligence/action_agent.py`）

**Option B（兼容方案）：改 dispatch 执行器逻辑**，匹配时同时尝试从 notes 正则提取分数：

```python
def get_score(task):
    rice = task.get('rice')
    if isinstance(rice, dict): return rice.get('score')
    m = re.search(r'综合评分\s*(\d+)/20', task.get('notes',''))
    return int(m.group(1)) if m else None
```

负责团队：harness_engineer（改 dispatch 执行逻辑，未来落地时）

### P1（建议）

- INTEL-20260427-007 没有嵌入分 → 上游 intel-action 应保证**所有 INTEL 必带分数**，否则 keep_pending 兜底数会越来越大，D2 自动化效率下降
- safeguards `max_auto_upgrade_per_session=10` 在当前 6 条 upgrade 下还有 4 条余量，但**多日累积**时可能触发——建议加 `max_auto_upgrade_per_day` 维度

### P2（小优化）

- 规则匹配是"短路"（首条命中即停），P0 规则的 `rice_score_min=18` 排除了"P0 但低分"场景——当前不可能但需在文档中说明

---

## 八、给 Lysander 的一行

✅ D2 模拟验证：realistic 模式 7 条 INTEL 分布 [upgrade_to_req=6 / keep_pending=1]，safeguards 未触发，规则逻辑合理性 **高**；但暴露 **P0 数据契约缺陷**——rules 引用 `task.rice.score` 而生产 INTEL 无此字段，literal 模式下 7 条全部退回 keep_pending（自动消化失效），需 harness_engineer 同步改 intel-action 写入逻辑或 dispatch 执行器加 notes 提取兜底。
