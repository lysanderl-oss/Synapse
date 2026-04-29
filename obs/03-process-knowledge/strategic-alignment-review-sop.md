---
id: strategic-alignment-review-sop
type: core
status: published
lang: zh
version: 1.0
published_at: 2026-04-27
author: decision_advisor + strategy_advisor
review_by: [总裁]
authorized_by: 总裁 (decision ③A)
audience: [智囊团, 总裁]
stale_after: 2026-10-27
---

# 战略对齐审查 SOP（智囊团独立路径）

## 决策依据

总裁 2026-04-27 L4 决策 ③A：战略对齐审查由智囊团独立执行 + 直接汇报总裁，**绕开 Lysander**。归档：`D-2026-0427-001`。

## 设立目的

避免"自评者陷阱" — Lysander 主导审查 = 自己审自己。智囊团作为独立第三方视角，定期评估"Lysander 是否在朝总裁意图执行"。

本机制是治理结构的**第三方监察层**：
- Harness Workflow（自动）：执行链合规
- 周审查（Lysander）：流程健康
- 战略对齐审查（智囊团独立）：方向校准 ← 本 SOP

## 审查频次

**双周一次**（与 Harness 周审查错峰，避免单一周末工作量集中）。

具体：
- 偶数周（如 W18, W20）：仅 Harness 周审查
- 奇数周（如 W17, W19, W21）：Harness 周审查 + 战略对齐审查

每期审查窗口：覆盖最近 14 天的总裁授权事项与 Lysander 派单事项。

## 执行者

- **strategy_advisor**（首席）：战略意图解读
- **decision_advisor**（次席）：决策质量评估
- **execution_auditor**（参考）：执行链审计支持
- **明确排除**：Lysander 不参与、不阅读初稿、不批改

合议机制：strategy_advisor 与 decision_advisor 须各自独立打分，分歧 ≥ 1 等级时附差异说明。

## 审查范围（5 维度）

### D1：意图溯源

取最近 2 周总裁原话（来源：对话记录、`active_tasks.yaml` 中标记 `authorized_by: 总裁` 的项、`obs/04-decision-knowledge/decision-log/` 中的 D-编号文档），逐条提取关键词。

输出：意图清单（≥ 5 条，每条注明来源时间戳）。

### D2：执行映射

对每条总裁意图，列出：
- Lysander 派单的执行项（团队 + specialist_id）
- 实际产出（文件路径 / 提交哈希 / 部署地址）
- 完成状态（done / partial / blocked / 未启动）

### D3：偏移度评分

| 等级 | 说明 | 触发动作 |
|------|------|----------|
| **A 完全对齐** | 执行 100% 符合总裁原意 | 仅记录 |
| **B 部分对齐** | 80%+ 符合，少数偏差 | 标注偏差，进 D4 |
| **C 偏移** | 50-80% 符合，方向有偏 | 进 D4 + D5 必填纠偏建议 |
| **D 严重偏移** | < 50%，需立即纠偏 | 报告即刻提交，标记 urgent |
| **F 反向** | 执行与意图相反 | 报告即刻提交 + 总裁短消息推送 |

每条意图独立打分；本期总评取最差等级（不取平均，避免被高分掩盖低分）。

### D4：根因分析（仅当 ≤ B 时执行）

四类根因模板：
- **Lysander 误解**：派单文本与总裁原话存在语义偏差
- **Worker Agent 偷懒**：派单合规但 Worker 简化产出
- **中间审批漂移**：经过多轮审批后偏离原意
- **总裁中途调整方向 Lysander 未跟进**：意图变更未被 capture

每条偏差归类至少一个根因，可多选。

### D5：建议（必填）

对**总裁的建议**（不是给 Lysander 的）：
- 是否需要重新明确意图？
- 是否需要调整 Lysander 的授权范围？
- 是否需要建立新机制（新 SOP / 新 Sensor / 新 Guard）？
- 是否需要总裁亲自介入特定环节？

## 输出格式

文件路径：`obs/04-decision-knowledge/strategic-alignment/SAR-{YYYY-Www}.md`

frontmatter 模板：

```yaml
---
id: SAR-2026-W19
type: reference
status: pending_president_review
lang: zh
audience: [总裁]
authored_by: [strategy_advisor, decision_advisor]
period_start: 2026-05-04
period_end: 2026-05-17
overall_grade: A | B | C | D | F
lysander_visibility: false  # Lysander 不应主动 Read 此文件直至总裁批阅后
---
```

报告主体结构：

1. **BLUF**（3 行给总裁）：本期总评 + 最严重偏差 + 1 条核心建议
2. **D1 意图清单**
3. **D2 执行映射表**
4. **D3 偏移度评分明细**
5. **D4 根因分析**（仅当 ≤ B）
6. **D5 给总裁的建议**
7. **附录**：审查者签名 + 数据来源清单

## 上报路径

报告写完后：
1. 文件保存至 `obs/04-decision-knowledge/strategic-alignment/`
2. 提交至 `agent-CEO/config/active_tasks.yaml` 一条标记 `addressee: 总裁` 的任务
3. **Lysander 在主对话中转交**：仅说"智囊团已交付双周战略对齐审查报告 SAR-{N}，请总裁审阅"，**不读取报告内容**
4. 总裁审阅后批示，再由 Lysander 派单执行批示
5. 总裁批示后报告 status 改为 `reviewed`，`lysander_visibility` 改为 `true`

## Lysander 边界

| 允许 | 不允许 |
|------|-------|
| 知道智囊团在做这件事 | 主导执行 |
| 转交报告给总裁 | 阅读报告内容（在总裁批示前）|
| 接受总裁批示后派单 | 干预智囊团评分 |
| 在审查范围内被评分 | 给智囊团施压改评分 |
| 询问审查进度（"本期 SAR 是否已交付？"）| 询问审查内容（"本期评了什么？"）|

## 失败兜底

如智囊团连续 2 期未交付（双周 × 2 = 1 个月空窗）：
- 不视为 Lysander 失职（智囊团独立）
- 总裁直接督促智囊团或调整机制设计
- Lysander 仅汇报"未收到本期 SAR"，不代为补写

如智囊团内部分歧无法收敛：
- 由 strategy_advisor 主笔出报告，decision_advisor 附独立反对意见
- 总裁基于双视角自行裁断

## 第一期触发

第一份 **SAR-2026-W18** 由 decision_advisor + strategy_advisor 在本周日（**2026-04-30**）前完成（赶上本次启动节奏）。

覆盖窗口：2026-04-14 ~ 2026-04-27（含本次 4 项 L4 决策的对齐情况）。

## 修订记录

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| 1.0 | 2026-04-27 | 初版 | decision_advisor + strategy_advisor |
