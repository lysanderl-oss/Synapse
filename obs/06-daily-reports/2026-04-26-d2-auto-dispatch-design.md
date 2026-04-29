# D2 全自动 INTEL 消化设计文档

**版本**：v1.0 设计稿
**作者**：synapse_product_owner（子 Agent，Lysander 派单）
**日期**：2026-04-26
**总裁批准**：D2 升级 — Lysander 会话 resume 时自动消化 pending-dispatch INTEL
**关联 Objective**：OBJ-INTEL-LOOP-CLOSURE（情报管线全自动闭环 档 A3）
**审查方法**：按 `feedback_doc_citation_must_verify`，所有引用基于实际文件 Read 验证，非凭印象。

---

## 一、当前 7 条 pending-dispatch INTEL 实证

### 1.1 数据来源

- 文件：`agent-CEO/config/active_tasks.yaml`
- 筛选：`status == 'approved-pending-dispatch'`
- 写入来源：`source: intel-action 自动评估`（情报行动管线 2026-04-27 批次）

### 1.2 7 条 INTEL 全量实证表

| ID | priority | team | assigned_to | co_assigned | 综合评分 | 原始 RICE |
|----|----------|------|-------------|-------------|----------|----------|
| INTEL-20260427-001 | P1 | ai_ml | ai_ml_engineer | harness_engineer | 19/20 | None |
| INTEL-20260427-002 | P1 | graphify | graphify_strategist | harness_engineer | 18/20 | None |
| INTEL-20260427-003 | P1 | harness_ops | harness_engineer | ai_ml_engineer | 17/20 | None |
| INTEL-20260427-004 | P2 | harness_ops | knowledge_engineer | graphify_strategist | 15/20 | None |
| INTEL-20260427-005 | P2 | graphify | ai_tech_researcher | (空) | 14/20 | None |
| INTEL-20260427-006 | P2 | graphify | graphify_strategist | financial_analyst | 12/20 | None |
| INTEL-20260427-007 | P2 | ai_ml | ai_ml_engineer | (空) | (notes 中无评分字段) | None |

### 1.3 关键实证发现（与原任务设想的偏差）

> **任务原文给出的 schema 假设字段是 `rice`（RICE 分数）。实际数据中 `rice: None`。**
> 真正可用的"分数"嵌入在 `notes` 字段，格式为 `综合评分 X/20`，需要正则提取。

| 假设字段 | 实际状态 | 处理方案 |
|---------|----------|----------|
| `rice.score` | 全部 `None` | 不可用 |
| `notes` 内 `综合评分 X/20` | 6/7 条命中，1 条缺失 | 用作主要评分，正则 `综合评分\s*(\d+)\s*/\s*20` |
| `priority` | P1×3, P2×4，全部填充 | 可作主分级条件 |
| `team` / `assigned_to` | 全部填充，无空 | 可作派单路由 |

**结论**：dispatch_rules 必须基于 `priority + composite_score (extracted)` 而不是 RICE，否则规则全部 fallback 到"无分数→keep_pending"，失去自动消化能力。

### 1.4 priority 分布

- P0：0 条
- P1：3 条（高分 19/18/17）
- P2：4 条（15/14/12/无评分）
- P3：0 条

### 1.5 team 分布

- ai_ml：2 条
- graphify：3 条
- harness_ops：2 条

---

## 二、设计原则（基于 CLAUDE.md 实证引用）

### 2.1 【0.5】Lysander 承接逻辑（CLAUDE.md L118-131 实文）

```
【0.5】Lysander 承接与目标确认（强制前置步骤，不可跳过）
        Lysander 必须：
        ① 复述总裁的目标/需求（用自己的语言）
        ② 对齐理解（确认没有偏差）
        ③ 判断决策级别（L1-L4）
        ④ 判断是否需要派单（还是 Lysander 直接处理）
        ⑤ 如需派单 → 输出派单表 → 进入步骤【②】
        ⑥ 调用 LysanderInterceptor.intercept() 记录本次诉求
```

**D2 接入点**：在第 ⑥ 步之后、进入【①】之前，新增 ②.5 节点"Pending-Dispatch INTEL 自动 review"。理由：诉求记录后，Lysander 已对齐当前会话目标，此时消化 pending INTEL 不会和总裁主诉求冲突。

### 2.2 决策体系 L1-L4 定义（CLAUDE.md L304-309 实文）

| 级别 | 决策者 | 适用场景 |
|------|--------|----------|
| **L1** | 系统自动 | 例行操作、标准流程、信息查询 |
| **L2** | 智囊团+领域专家 | 专业问题先由专家分析，给出建议和方案 |
| **L3** | Lysander CEO | 基于专家建议做管理决策，跨团队协调、资源分配 |
| **L4** | 总裁刘子杨 | 外部合同/法律、>100万预算、公司存续级不可逆决策 |

**D2 定级**：
- 自动消化本身 → **L1**（已批准的持续运行任务，规则已在 yaml 固化）
- 单条 INTEL 升级 REQ 或派单 → **L2/L3**，但因 dispatch_rules 已经过总裁批准，每次匹配执行属于 L1 内嵌
- 任一条 INTEL 触发 halt_conditions（真阻塞/超授权/偏离>30%/L4 触发）→ 跳出自动消化，进入 L3 人工评审

### 2.3 INTEL → REQ 升级历史案例（实证：requirements_pool.yaml L268-283）

```yaml
- id: REQ-JD-001
  title: "Janus Digital Q2 Agent 产品路线图制定"
  source: "INTEL-20260420-002 立项"
  product: janus_digital
  priority: P1
  status: in_progress
  rice: {reach: 5, impact: 5, confidence: 3, effort: 4, score: 18.75}
```

**模式提取**：
- `source` 字段保留原 INTEL ID（"INTEL-XXXXXX-XXX 立项"）
- 升级到 REQ 时，必须补齐结构化 RICE（5×5×3 / 4 = 18.75），不能空缺
- `status` 从 INTEL 的 `approved-pending-dispatch` → `in_progress`（进入需求池开始排期）

**D2 升级路径**：自动升级时若原 INTEL 缺 RICE，由 Lysander 通过启发式映射 `composite_score` → `rice.score`（见 §3.3）。

---

## 三、Dispatch Rules 配置 schema

### 3.1 完整 YAML 定义（追加到 active_objectives.yaml 顶层）

```yaml
# 总裁批准的自动消化规则（D2 升级 2026-04-26）
# 与 objectives 同级，Lysander 每次会话 resume 时按此规则自动处理 pending-dispatch INTEL
dispatch_rules:
  enabled: true
  source: "OBJ-INTEL-LOOP-CLOSURE D2 升级"
  approved_by: 总裁刘子杨
  approved_at: "2026-04-26"
  schema_version: "1.0"

  # 评分提取（适配真实数据：notes 中嵌入"综合评分 X/20"）
  score_extraction:
    primary_source: "task.rice.score"  # 优先使用结构化 RICE（如有）
    fallback_source: "task.notes"
    fallback_regex: "综合评分\\s*(\\d+(?:\\.\\d+)?)\\s*/\\s*20"
    fallback_scale: 20  # 提取值除以 20 作为归一化分数（0-1）
    rice_scale_max: 100  # 假设 RICE 满分参考 100

  # 规则按优先顺序匹配，命中即停止
  rules:
    - name: "R1-P0立即派单"
      priority_match: P0
      composite_score_min: 16  # ≥16/20 = 0.8 归一化
      action: dispatch_immediately
      target_team_field: "task.team"
      target_role_field: "task.assigned_to"
      notes: "Lysander 主对话立即调 Agent 工具创建子 Agent 执行"

    - name: "R2a-P1高分派单"
      priority_match: P1
      composite_score_min: 18
      action: dispatch_immediately
      notes: "P1 高分（≥18/20）等同紧急行动，直接派单"

    - name: "R2b-P1升级REQ"
      priority_match: P1
      composite_score_min: 15
      composite_score_max: 17.99
      action: upgrade_to_req
      target_pool: "obs/02-product-knowledge/requirements_pool.yaml"
      target_status: in_progress
      target_priority: P1
      req_id_prefix: "REQ-INTEL-"
      notes: "进入需求池待 Q2/Q3 排期，附 source: 原 INTEL ID"

    - name: "R3-P2入池低优先"
      priority_match: P2
      composite_score_min: 12
      composite_score_max: 15
      action: upgrade_to_req
      target_status: backlog
      target_priority: P2
      req_id_prefix: "REQ-INTEL-"
      notes: "Q3 或之后排期，不进 in_progress"

    - name: "R4-自动延期"
      priority_match: [P3]
      OR_composite_score_max: 10  # P3 或评分<10 任一命中
      action: mark_deferred
      target_status: deferred
      notes: "记录但不处理，季度 review 时人工评估"

    - name: "R5-fallback人工review"
      default_fallback: true
      action: keep_pending
      notes: "未匹配前 4 条规则的 INTEL（如评分缺失）保留 pending，Lysander 在 snapshot 中显式列出"

  # 安全护栏（防爆量、防误派）
  safeguards:
    max_auto_dispatch_per_session: 3       # 单次会话立即派单上限
    max_auto_upgrade_per_session: 10       # 升级 REQ 上限
    max_auto_defer_per_session: 5          # 自动延期上限（防止误判全延期）
    require_lysander_summary: true         # 必须给总裁产出 snapshot
    revert_on_error: true                  # 任一条处理失败 → 回滚本次会话所有 D2 操作
    score_missing_default_action: keep_pending  # 评分缺失永不自动派单
    error_log_path: "logs/d2-dispatch-errors.log"

  # 总裁手动覆盖（关键字优先级最高，命中即跳过 D2）
  override_keywords:
    - "暂停自动消化"
    - "全部留待审查"
    - "D2 关闭"
    - "skip dispatch"

  # RICE 启发式映射（升级 REQ 时若原 INTEL 缺 RICE，自动生成）
  rice_heuristic_mapping:
    method: "composite_score 映射"
    formula: "score_20 / 20 * 25 → rice.score"  # 20/20 → 25.0；15/20 → 18.75
    default_components:
      reach: 4      # 默认覆盖 4 团队
      impact: 4     # 默认中高影响
      confidence: 3 # 默认中等置信
      effort: 3     # 默认中等工作量
    notes: "仅作占位，REQ owner 接手后必须人工修订"
```

### 3.2 与 active_objectives.yaml 集成方式

```yaml
version: "1.2.0"  # 从 1.1.0 → 1.2.0
last_updated: "2026-04-26"

dispatch_rules:   # ← 新增段落（顶层）
  ...

objectives:       # ← 保持不变
  - id: OBJ-INTEL-LOOP-CLOSURE
  ...
```

### 3.3 RICE 启发式映射示例

| composite_score | rice.score (映射) | 默认 RICE 4 元组 |
|----------------|-------------------|------------------|
| 19/20 | 23.75 | {5, 5, 3, 3} |
| 18/20 | 22.50 | {4, 5, 3, 3} |
| 17/20 | 21.25 | {4, 4, 3, 3} |
| 15/20 | 18.75 | {4, 4, 3, 3} |
| 12/20 | 15.00 | {3, 4, 3, 3} |

---

## 四、按当前 7 条数据模拟规则匹配（实证模拟）

| INTEL ID | priority | composite_score | 命中规则 | action | 模拟结果 |
|----------|----------|-----------------|----------|--------|----------|
| INTEL-20260427-001 | P1 | 19/20 | R2a-P1高分派单 | dispatch_immediately | Lysander 主对话立即派单 ai_ml_engineer + harness_engineer |
| INTEL-20260427-002 | P1 | 18/20 | R2a-P1高分派单 | dispatch_immediately | Lysander 主对话立即派单 graphify_strategist + harness_engineer |
| INTEL-20260427-003 | P1 | 17/20 | R2b-P1升级REQ | upgrade_to_req | 升级为 REQ-INTEL-001（in_progress, P1），rice.score=21.25 |
| INTEL-20260427-004 | P2 | 15/20 | R3-P2入池低优先 | upgrade_to_req | 升级为 REQ-INTEL-002（backlog, P2），rice.score=18.75 |
| INTEL-20260427-005 | P2 | 14/20 | R3-P2入池低优先 | upgrade_to_req | 升级为 REQ-INTEL-003（backlog, P2），rice.score=17.50 |
| INTEL-20260427-006 | P2 | 12/20 | R3-P2入池低优先 | upgrade_to_req | 升级为 REQ-INTEL-004（backlog, P2），rice.score=15.00 |
| INTEL-20260427-007 | P2 | 缺失 | R5-fallback人工review | keep_pending | 保留 pending，snapshot 显式列出 |

### 4.1 安全护栏触发情况

| 护栏项 | 上限 | 本批次实际 | 状态 |
|--------|------|-----------|------|
| max_auto_dispatch_per_session | 3 | 2 | 通过 |
| max_auto_upgrade_per_session | 10 | 4 | 通过 |
| max_auto_defer_per_session | 5 | 0 | 通过 |
| score_missing_default_action | keep_pending | 触发 1 次（INTEL-007） | 正确 |

### 4.2 模拟产出后 active_tasks.yaml 状态变化

| 状态 | 处理前 | 处理后 |
|------|--------|--------|
| approved-pending-dispatch | 7 | 1（INTEL-007） |
| dispatched | 0 | 2（INTEL-001, 002） |
| upgraded-to-req | 0 | 4（INTEL-003, 004, 005, 006） |

requirements_pool.yaml 新增 4 条 REQ-INTEL-XXX。

---

## 五、安全护栏

### 5.1 数量护栏（防爆量）

- `max_auto_dispatch_per_session: 3` — 单次会话最多 3 条立即派单
- `max_auto_upgrade_per_session: 10` — 升级 REQ 上限
- `max_auto_defer_per_session: 5` — 自动延期上限

### 5.2 质量护栏（防误判）

- `score_missing_default_action: keep_pending` — 评分缺失时永远不自动派单
- `revert_on_error: true` — 任一条处理失败 → 回滚本次会话所有 D2 操作
- `error_log_path` — 错误必须落盘到 `logs/d2-dispatch-errors.log`

### 5.3 总裁覆盖关键字

- "暂停自动消化"
- "全部留待审查"
- "D2 关闭"
- "skip dispatch"

命中任一关键字 → D2 在当次会话内全部跳过，所有 pending INTEL 保持原状等总裁手动决策。

### 5.4 跨会话状态护栏

D2 操作日志写入 `logs/d2-session-log.yaml`，每次会话开场前 Lysander 必须读取并自检：
- 上一次会话有无未完成 D2 操作（dispatch 但子 Agent 未返回）
- 是否存在已 revert_on_error 的孤儿任务

---

## 六、CLAUDE.md 【0.5】升级方案

### 6.1 现有 6 步逻辑（CLAUDE.md L119-131）

```
① 复述总裁目标
② 对齐理解
③ 判断决策级别（L1-L4）
④ 判断是否派单
⑤ 如需派单 → 输出派单表 → 进入【②】
⑥ 调用 LysanderInterceptor.intercept()
```

### 6.2 D2 升级后 7 步逻辑（新增 ②.5）

```
① 复述总裁目标
② 对齐理解
②.5 [D2 新增] Pending-Dispatch INTEL 自动 review     ← 新增
     - Read agent-CEO/config/active_tasks.yaml
     - 筛选 status == 'approved-pending-dispatch'
     - 加载 active_objectives.yaml 的 dispatch_rules
     - 检查 override_keywords 是否命中（命中 → 跳过整个 ②.5）
     - 按 rules 顺序匹配 → 执行 action（受 safeguards 限制）
     - 写 snapshot 给总裁（§7 模板）
③ 判断决策级别（L1-L4）
④ 判断是否派单（含 ②.5 触发的派单）
⑤ 如需派单 → 输出派单表 → 进入【②】
⑥ 调用 LysanderInterceptor.intercept()
```

### 6.3 Harness 治理合规

按 CLAUDE.md L380-396「Harness 治理规则」：
- ②.5 节点为 P1 规则变更（不属于 P0 CEO 执行禁区或熵增预算）
- 流程：harness_engineer 提案 → Lysander 批准 → 执行
- 时间戳：`# [ADDED: 2026-04-26]`
- CLAUDE.md 总行数预计从 397 → 410 行，仍在 350 行收紧目标外（需在 Phase 2 时同步收紧）

---

## 七、汇报 snapshot 模板

每次会话开场，Lysander 完成 ②.5 自动消化后，必须给总裁产出固定格式 snapshot：

```
========== D2 Pending-Dispatch INTEL 自动消化 Snapshot ==========
会话时间：2026-04-26 14:32 Dubai
本次发现：7 条 pending-dispatch INTEL
override 命中：无

【已立即派单】（2/3 上限）
  - INTEL-20260427-001【P1, 19/20】Claude 4 API 迁移准备
    → ai_ml_engineer + harness_engineer，子 Agent 已创建
  - INTEL-20260427-002【P1, 18/20】OpenAI Agents SDK 1.0 竞品对比
    → graphify_strategist + harness_engineer，子 Agent 已创建

【已升级 REQ】（4/10 上限）
  - INTEL-20260427-003 → REQ-INTEL-001（P1, in_progress）
  - INTEL-20260427-004 → REQ-INTEL-002（P2, backlog）
  - INTEL-20260427-005 → REQ-INTEL-003（P2, backlog）
  - INTEL-20260427-006 → REQ-INTEL-004（P2, backlog）

【保留待人工 review】
  - INTEL-20260427-007【P2, 评分缺失】→ keep_pending（fallback R5）
    建议：Lysander 在合适时机评估其评分

【护栏触发】
  - score_missing_default_action 命中 1 次（INTEL-007）正确处理

【errors】无

=================== End Snapshot ===================
```

---

## 八、给 Lysander 的一行

```
✅ D2 设计完成：dispatch_rules 5 条 + safeguards 4 项 + 7 条 INTEL 模拟匹配，待 harness_engineer 落地配置
```

---

## 附录 A：实证引用清单（防 doc_citation 违规）

| 引用内容 | 文件 | 行号 |
|---------|------|------|
| 【0.5】6 步逻辑 | CLAUDE.md | L118-131 |
| L1-L4 决策表 | CLAUDE.md | L304-309 |
| L4 上报标准 4 条 | CLAUDE.md | L330-335 |
| Harness 治理规则 | CLAUDE.md | L380-396 |
| OBJ-INTEL-LOOP-CLOSURE | active_objectives.yaml | L16-54 |
| REQ-JD-001（INTEL→REQ 案例） | requirements_pool.yaml | L268-283 |
| 7 条 pending-dispatch INTEL | active_tasks.yaml | tasks[status=approved-pending-dispatch] |

## 附录 B：未决问题（待 harness_engineer 落地时确认）

1. REQ-INTEL-XXX 编号是否需要进入全局序号池（避免与 REQ-JD/REQ-EG/REQ-INFRA 冲突）
2. 子 Agent 派单失败的 retry 策略（建议 1 次重试，仍失败 → keep_pending + log）
3. ②.5 在 Auto Mode 下是否需要 require_lysander_summary 仍为 true（建议是，便于审计）
4. dispatch_rules 修改本身的决策级别（建议 P1 规则变更，harness_engineer 提案）
