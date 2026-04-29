---
title: n8n Workflow 治理评估报告（OBJ-N8N-WORKFLOW-AUDIT 阶段 2）
date: 2026-04-25
chair: synapse_product_owner
status: evaluation_ready
for_review: Lysander → 总裁审批
---

# n8n Workflow 治理评估报告

> 阶段 1 已产出 2 份分析报告（全量审计 + WF-09 根因），本报告为阶段 2 评估，
> 将问题分组并为每组提供多档方案，待总裁审批后进入阶段 3 执行。

## 一、问题分组（基于阶段 1 分析）

将所有发现的问题按紧迫度分为 4 组：

### 组 P0：Slack 路由不生效（紧急生产事故）
- **现象**：4 个情报管线 Python agent 调用 WF-09 时未传 `recipient`，使用默认 `SLACK_DEFAULT_RECIPIENT='U0ASLJZMVDE'`（总裁裸 UID），WF-09 fallback 路径直接透传 → Slack API 自动转 DM
- **数据**：最近 10 次 execution 100% 投到总裁 DM，0 次到 #ai-agents-noti
- **影响**：总裁 DM 被情报管线刷屏，#ai-agents-noti 形同虚设
- **紧迫度**：当晚需修

### 组 P1：WF-09 命名冲突 + WF-06/WF-08 直推违规
- **现象 1**：WF-09 前缀冲突未解决（`atit1zW3VYUL54CJ` Unified Notification 与 `203fXfKkfqD1juuT` Webhook 未覆盖告警）
- **现象 2**：18 条 HTTP 直推 Slack workflow 中，**WF-06 / WF-08 是生产违规**（绕过 WF-09 统一入口），其余 16 条为 Harness 实验残留（多为 Inactive）
- **影响**：统一通知架构被破坏，未来若改 Slack token / channel 需多处同步
- **紧迫度**：本周内

### 组 P2：垃圾债务清理 + 情报管线断裂
- **现象 1**：47 条 workflow 中 24 条从未运行（51%），其中潜在垃圾混入
- **现象 2**：4 条 Active error workflow（WF-02 / WF-04 / WF-05 / WF-06）持续报错
- **现象 3**：Synapse-WF1 (intelligence-action) 与 Synapse-WF5 (task-status) **从未运行** —— 怀疑为情报管线主链路断裂，非垃圾
- **紧迫度**：本月内

### 组 P3：命名规范化（最后做）
- WF-09 / WF-02 / WF-01 / WF-04 / WF-05 编号冲突
- Harness* 系列 12 个未规范前缀
- 中英文混用 17 条
- 默认/试验名 6 条
- **紧迫度**：完成 P0-P2 后统一命名（治本动作放最后避免反复改）

---

## 二、每组的多档方案

### 组 P0 方案（Slack 路由修复）

#### 方案 P0-A：调用方改默认 recipient='president'（推荐）
- **变更点**：改 `scripts/intelligence/shared_context.py` 默认值，或修改 `SLACK_DEFAULT_RECIPIENT` GitHub Secret 为 `'president'`
- **覆盖**：daily_agent / action_agent / resume_agent / heartbeat_check 全部走 `'president'` → WF-09 已有的 channel 路由分支 → #ai-agents-noti
- **工作量**：5 分钟（1 行变更或 1 个 Secret 修改）
- **风险**：极低（fallback 路径已验证可用，'president' 关键字路由已实现）
- **评分**：⭐⭐⭐⭐⭐

#### 方案 P0-B：WF-09 fallback 改为强制 → #ai-agents-noti
- **变更点**：改 WF-09 Parse Recipient 节点的 fallback 分支，无论传什么 recipient 都进 channel
- **工作量**：10 分钟（n8n UI 操作）
- **风险**：低，但破坏"DM/channel"语义灵活性，未来若需向特定用户私发会受阻
- **评分**：⭐⭐⭐

#### 方案 P0-C：调用方传 channel ID 'C0AV1JAHZHB' 直传
- **变更点**：4 个调用方明确传 channel ID
- **工作量**：10 分钟
- **风险**：低，但 channel ID 硬编码，万一 channel 改名 / 重建需多处同步
- **评分**：⭐⭐⭐

**推荐：P0-A** —— 最小改动 + 语义清晰 + 复用 WF-09 已有的 'president' 关键字路由

---

### 组 P1 方案（WF-09 重命名 + WF-06/08 改造）

#### 方案 P1-A：WF-09 重命名 + WF-06/WF-08 改造为走 WF-09（推荐，治本）
- **变更点 1（重命名）**：
  - `203fXfKkfqD1juuT` 去 WF-09 前缀（具体新名见决策点 3）
  - `atit1zW3VYUL54CJ` 保留为唯一 WF-09 Unified Notification
- **变更点 2（WF-06 改造）**：
  - 当前：内部 HTTP 直推 Slack API
  - 改造后：内部 HTTP 改调 WF-09 webhook，传 `recipient='president'` + 自定义 message
  - 验证：触发一次 WF-06 → 确认消息出现在 #ai-agents-noti
- **变更点 3（WF-08 改造）**：同 WF-06 改造逻辑
- **执行顺序**：先改测试环境 → 验证 → 改生产 → 监控 24 小时
- **工作量**：30-60 分钟（含 export 留底 + 小流量测试）
- **风险**：中（修生产 workflow，但有 git snapshot + 单点触发可立即对比）
- **评分**：⭐⭐⭐⭐

#### 方案 P1-B：仅重命名，WF-06/WF-08 保持现状
- **变更点**：仅解命名冲突，Slack 直推先记入需求池
- **工作量**：5 分钟
- **风险**：低，但不彻底 —— WF-06/WF-08 直推违规未解
- **评分**：⭐⭐⭐

**推荐：P1-A**

---

### 组 P2 方案（垃圾债务清理 + 情报管线断裂调研）

#### 方案 P2-A：直接删除 24 条从未运行 + 4 条 error
- **变更点**：一次性清理
- **工作量**：30 分钟
- **风险**：中（误删风险高，未细分用途）
- **评分**：⭐⭐

#### 方案 P2-B：分类处置（推荐）
- **24 条从未运行 → 进一步分 3 类**：
  - **类 1（删除候选）**：明显废弃。判定标准：命名含 `test` / `draft` / `temp` / `copy` / `unnamed` / 默认 `My workflow N` / 全英文乱码占位名
    - 处置：export JSON 入归档 → 从 n8n 删除 → 提交 git
  - **类 2（休眠归档）**：命名规范但长期未触发，未来可能复用
    - 处置：改名加 `[archived-2026-04]` 前缀 + 状态保持 Inactive，不删（保留可观测性）
  - **类 3（未知用途）**：命名特殊但无明显废弃信号
    - 处置：Lysander 个案调研，确认用途后归入类 1 或类 2
- **4 条 Active error workflow（WF-02 / WF-04 / WF-05 / WF-06）** → 各自定位错误原因
  - 步骤：拉取最近 5 次 execution log → 识别错误类型（auth 失效 / node 配置错 / 上游变更）→ 修复或停用
  - 必修项：WF-06 因属于 P1-A 改造范围，需与 P1-A 协同处置
- **Synapse-WF1 / WF5 从未运行** → **独立调研，不当垃圾处理**
  - WF1 (intelligence-action) 从未运行 → 检查触发器配置 / 上游 webhook 是否注册
  - WF5 (task-status) 从未运行 → 检查是否有 cron 漏配 / 调用方未实现
  - 调研结论二选一：补全调用链 / 确认废弃后归入类 1
- **工作量**：2-3 小时（不含 WF1/WF5 修复时间）
- **风险**：低（删除前全部 export JSON 留底，可手动恢复）
- **评分**：⭐⭐⭐⭐⭐

**推荐：P2-B**

---

### 组 P3 方案（命名规范化）

#### 方案 P3-A：制定命名规范 + 一次性重命名（推荐）
- **规范草案（待审批）**：`WF-XX [产品线] [中文功能名]`
  - **格式三段式**：编号 + 产品线 + 功能描述
  - **示例**：
    - `WF-09 Synapse 统一通知`
    - `WF-10 Synapse 情报日报触发器`
    - `WF-15 PMO 任务变更通知`
    - `WF-22 Harness Webhook 未覆盖告警`
  - **规则**：
    1. 编号唯一（每个 workflow 一个独立编号，不再有 WF-09a/b）
    2. 产品线必填：Synapse / PMO / Harness / Stock 等
    3. 功能名中文为主（运营友好），英文专有名词保留
    4. 试验/草稿统一前缀 `[draft]` + 不分配正式编号
    5. 归档统一前缀 `[archived-YYYY-MM]`
- **执行步骤**：
  1. 规范文档入 `obs/03-process-knowledge/n8n-naming-convention.md`
  2. 现存 workflow 出映射表（旧名 → 新名）→ Lysander 审批
  3. 一次性批量重命名（n8n API 或 UI）
- **工作量**：1 小时（含规范文档 30 分钟 + 重命名执行 30 分钟）
- **评分**：⭐⭐⭐⭐

#### 方案 P3-B：仅修复编号冲突（最小化）
- **变更点**：只解 WF-09 / WF-02 等冲突，其他保持
- **工作量**：15 分钟
- **评分**：⭐⭐⭐

**推荐：P3-A**

---

## 三、综合执行排序（推荐组合：P0-A + P1-A + P2-B + P3-A）

```
当晚（紧急）：     P0-A（Slack 路由修复）             → 5 分钟
今夜或明日：       P1-A（WF-09 重命名 + WF-06/08 改造）→ 30-60 分钟
本周内：           P2-B（垃圾清理 + WF1/WF5 断裂调研） → 2-3 小时
P2-B 完成后：      P3-A（命名规范统一）               → 1 小时
```

**总工作量**：约 4-5 小时分散在数日，按紧迫度顺序执行

---

## 三点五、方案对比矩阵（速览）

| 组 | 推荐档 | 工作量 | 风险 | 治本程度 | 可独立回滚 |
|----|--------|--------|------|----------|-----------|
| P0 | P0-A 调用方默认改 'president' | 5 分钟 | 极低 | 完全治本 | 是（git revert） |
| P1 | P1-A 重命名 + WF-06/08 改造 | 30-60 分钟 | 中 | 完全治本 | 是（snapshot 还原） |
| P2 | P2-B 分类处置 + 断裂调研 | 2-3 小时 | 低 | 部分治本（需 P3 收尾） | 是（archive 恢复） |
| P3 | P3-A 命名规范统一 | 1 小时 | 极低 | 完全治本 | 是（n8n 历史名） |

**组合执行特性**：4 组方案彼此独立，任一组单独执行都有意义；P0-A 不依赖任何其他组，可立即启动。

---

## 四、风险与回滚

| 阶段 | 回滚机制 | 留底位置 |
|------|----------|----------|
| P0-A | 改 1 行代码 / 1 个 Secret，git revert 即回滚 | git history |
| P1-A | WF-09 修改 snapshot 入 git（commit 1a3ba10 已存）；WF-06/08 改造前 export 当前 JSON | `harness/n8n-snapshots/` |
| P2-B | 删除前先 export 全部候选 JSON 入归档目录（可手动恢复） | `harness/n8n-snapshots/_archive/` |
| P3-A | 重命名仅改 name 字段，n8n 提供历史名查询，可逆 | n8n 自身 |

**核心原则**：每个阶段执行前必先 export 受影响 workflow 的 JSON 入 git，保证可回滚。

---

## 四点五、关键假设与未决问题

执行前需 Lysander 或总裁明确以下假设：

1. **假设 A**：`SLACK_DEFAULT_RECIPIENT` GitHub Secret 改为 `'president'` 后，所有未显式传 recipient 的调用方都会走 #ai-agents-noti，**不会**有调用方需要保留 DM 行为
   - 风险：若有调用方确实需要 DM（如安全告警），需独立配置传具体 UID
2. **假设 B**：WF-06 / WF-08 的当前直推 Slack 行为可被 WF-09 完全替代，无特殊节点格式（如 Block Kit / 文件附件）依赖
   - 验证方法：执行 P1-A 前导出 WF-06/08 JSON 检查节点配置
3. **假设 C**：24 条从未运行 workflow 中无未来即将上线的预留 workflow
   - 验证方法：P2-B 执行前 Lysander 逐条勾选确认
4. **假设 D**：WF-09 的 `203fXfKkfqD1juuT` 重命名不影响任何外部调用方（webhook URL 由 ID 决定，name 仅显示用）
   - 验证方法：搜索代码库确认无 workflow name 字符串依赖

---

## 五、需总裁审批的关键决策点

1. **是否同意推荐组合方案 P0-A + P1-A + P2-B + P3-A 整体执行**（一字"批准"即可启动 P0-A）
2. **P2-B 中"明显废弃"分类标准**：执行前先提供 24 条从未运行的清单待您勾选确认
3. **WF-09 重命名 → 另一个候选新名选择**：
   - 候选 1：`WF-10 Webhook 未覆盖告警`
   - 候选 2：`WF-99 Webhook 未覆盖告警`
   - 候选 3：`Synapse-Audit-Webhook-Coverage`（去 WF 编号，独立体系）
4. **是否需要在 P2-B 执行前再次审视 24 条删除候选**（避免误删，建议保留此关卡）

---

## 六、给 Lysander 综合后呈报总裁的核心要点

1. 当前问题分 4 组（P0-P3），紧迫度从高到低
2. 各组多档方案 + 推荐档（推荐组合：P0-A + P1-A + P2-B + P3-A）
3. 总工作量约 4-5 小时（按紧迫度分散执行，非一次性投入）
4. 每个阶段有明确回滚路径 + git snapshot 留底
5. 4 个决策点等总裁裁示（其中 P0-A 可一字"批准"立刻启动）

---

**结论一句话**：P0 路由问题简单（5 分钟修复），但完整治理需多日分阶段，期间所有变更入 git snapshot 留痕，任何阶段可独立回滚。

---

## 七、成功度量（验收标准）

各阶段完成后，以以下客观指标确认成功：

| 阶段 | 度量指标 | 通过阈值 |
|------|----------|----------|
| P0-A | 情报管线下次执行后 Slack 投递目标 | 100% 进入 #ai-agents-noti，0 条进 DM |
| P1-A | WF-09 编号唯一性 + WF-06/08 调用链 | n8n 中只有 1 条 WF-09；WF-06/08 内部无直接 Slack 节点 |
| P2-B | 47 条 workflow 健康度 | 从未运行率 ≤ 20%（当前 51%）；Active error 数 ≤ 1 |
| P3-A | 命名合规率 | 100% workflow 符合三段式命名规范 |

**整体目标**：47 条 workflow 全部满足"命名合规 + 路由统一 + 状态健康"三条件，n8n 后台一眼可读。

---

## 附录：阶段 1 关键事实索引

- 全量审计报告：`obs/06-daily-reports/2026-04-25-n8n-workflow-full-audit.md`（298 行）
- WF-09 根因诊断：`obs/06-daily-reports/2026-04-25-wf09-routing-diagnosis.md`（176 行）
- 47 workflow 健康度：Active 且 ≤7 天有 run = 20；Active 且从未运行 = 8；Inactive = 19；Active error = 4
- Slack 推送行为分类：A 直接 node = 1 / B HTTP 直推 = 18（含 2 条生产违规） / C 调 WF-09 = 7 / D 不发 = 21
