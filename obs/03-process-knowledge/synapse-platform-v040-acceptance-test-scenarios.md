# Synapse Platform v0.4.0 — Acceptance Test Scenarios
# Synapse 平台 v0.4.0 — 验收测试方案

---

## 执行摘要 Executive Summary

**中文**
本文档定义 Synapse 平台 Boss + PM Agent 协作系统的验收测试方案，共 11 个测试场景，覆盖三大维度：核心协作流程、Agent 训练与记忆积累机制、边缘容错处理。测试目标是验证系统在真实业务场景中的端到端可靠性——从老板发出指令，到 PM Agent 起草、审批、交付，再到系统从反馈中持续学习优化，每一环节均须通过验证。

**English**
This document defines the acceptance test plan for the Synapse Platform Boss + PM Agent collaboration system. It covers 11 scenarios across three dimensions: core collaboration flow, agent training and memory accumulation, and edge-case resilience. The goal is to verify end-to-end reliability in real business contexts — from the Boss issuing a request, through PM Agent drafting and approval, to the system continuously learning from feedback.

---

## Suite A — 核心协作流程 Core Collaboration Flow

*验证 Boss → PM Agent → 审批 → 交付 的完整链路是否正常运转。*
*Verifies the complete Boss → PM Agent → Approval → Delivery pipeline.*

---

### A-01 周报端到端 Weekly Report End-to-End

| | 中文 | English |
|---|---|---|
| **测试内容** | Boss 用中文发送周报请求，PM Agent 起草中文报告，PM 审批通过后 Boss 收到英文结果 | Boss sends a weekly report request in Chinese; PM Agent drafts in Chinese; Boss receives English output after PM approval |
| **执行步骤** | 1. Boss 发送"帮我准备本周周报" 2. 确认 PM Agent 生成草稿 3. PM 点击审批通过 4. 验证 Boss 端收到英文版本 | 1. Boss sends "prepare this week's report" 2. Confirm PM Agent draft is generated 3. PM approves 4. Verify Boss receives English version |
| **通过标准** | 全流程 <60 秒完成；英文输出语义准确；无中间步骤丢失 | Full flow completes in <60s; English output is semantically accurate; no steps missing |


### A-02 会议准备端到端 Meeting Prep End-to-End

| | 中文 | English |
|---|---|---|
| **测试内容** | 与 A-01 相同的协作链路，验证系统在不同任务类型（会议准备）下的一致性 | Same collaboration chain as A-01, verifying consistent behavior across a different task type (meeting prep) |
| **执行步骤** | 1. Boss 发送会议议程请求 2. 验证 PM Agent 生成结构化议程草稿 3. PM 审批 4. Boss 收到双语会议简报 | 1. Boss requests meeting agenda 2. Confirm PM Agent generates structured draft 3. PM approves 4. Boss receives bilingual meeting brief |
| **通过标准** | 输出格式与周报有差异化（非套用同一模板）；流程稳定性与 A-01 一致 | Output format is appropriately distinct from weekly report; pipeline stability matches A-01 |

---

### A-03 PM 拒绝与系统恢复 PM Rejection & Recovery

| | 中文 | English |
|---|---|---|
| **测试内容** | PM 拒绝 Agent 草稿时，系统能否正确通知 Boss 并完成状态恢复 | When PM rejects the Agent draft, the system correctly notifies Boss and recovers gracefully |
| **执行步骤** | 1. 触发正常任务流程 2. PM 在审批环节点击"拒绝"并填写原因 3. 确认 Boss 收到拒绝通知 4. 验证任务状态回到待处理 | 1. Trigger normal task flow 2. PM clicks "Reject" with reason 3. Confirm Boss receives rejection notification 4. Verify task returns to pending state |
| **通过标准** | Boss 通知在 30 秒内到达；任务状态正确；系统无崩溃或卡死 | Boss notified within 30s; task state is correct; no crash or hung state |

---

## Suite B — Agent 训练层 Agent Training Layers

*验证 PM Agent 能否从人工反馈中持续学习，输出质量随使用次数提升。*
*Verifies that PM Agent can learn continuously from human feedback and improve output quality over time.*

---

### B-01 个人知识库注入 Personal KB Injection

| | 中文 | English |
|---|---|---|
| **测试内容** | 预加载个人知识库（写作偏好、术语表）后，验证 Agent 输出是否体现该风格 | Pre-load personal knowledge base (writing style, glossary); verify Agent output reflects the injected style |
| **执行步骤** | 1. 向个人 KB 写入风格规则（如"避免被动语态"） 2. 触发新任务 3. 对比注入前后的输出差异 | 1. Write style rules to personal KB (e.g., "avoid passive voice") 2. Trigger new task 3. Compare output before and after injection |
| **通过标准** | 注入后输出可见风格变化；规则未注入时输出不受影响 | Output shows visible style shift after injection; output without injection is unaffected |


### B-02 优质示例自动积累 Golden Example Auto-Accumulation

| | 中文 | English |
|---|---|---|
| **测试内容** | PM 审批通过后，该示例是否自动写入 Golden Example 数据库 | After PM approval, the example is automatically saved to the Golden Example database |
| **执行步骤** | 1. 完成一次完整的审批通过流程（参考 A-01） 2. 查询 Golden Example DB 记录 3. 确认新记录存在且字段完整 | 1. Complete a full approved flow (see A-01) 2. Query Golden Example DB 3. Confirm new record exists with complete fields |
| **通过标准** | 记录在审批后 10 秒内写入；包含任务类型、内容、时间戳 | Record written within 10s of approval; contains task type, content, timestamp |

---

### B-03 规则注入与生效验证 Rule Injection & Enforcement

| | 中文 | English |
|---|---|---|
| **测试内容** | 动态添加规则后，Agent 输出是否遵守该规则 | After dynamically adding a rule, verify Agent output complies with it |
| **执行步骤** | 1. 注入新规则（如"所有报告必须包含数据摘要部分"） 2. 触发任务 3. 检查输出是否包含规则要求的内容 | 1. Inject rule (e.g., "all reports must include a data summary section") 2. Trigger task 3. Check output includes rule-required content |
| **通过标准** | 规则注入后首次输出即生效；未注入该规则前的输出不包含此要求 | Rule takes effect on first output after injection; prior outputs do not contain the requirement |

---

### B-04 渐进记忆积累 Progressive Memory Accumulation

| | 中文 | English |
|---|---|---|
| **测试内容** | 每次审批通过后，`memory-seed.json` 是否正确更新 | After each approval, verify `memory-seed.json` is correctly updated |
| **执行步骤** | 1. 记录当前 `memory-seed.json` 的内容摘要 2. 完成一次审批通过 3. 重新读取文件，确认新增记忆条目 | 1. Note current `memory-seed.json` summary 2. Complete one approval 3. Re-read file and confirm new memory entry added |
| **通过标准** | 文件有新增条目；已有条目不被覆盖；格式合规（有效 JSON） | File has new entry; existing entries preserved; valid JSON format |


### B-05 多轮迭代质量提升 Output Quality Improvement Over Iterations

| | 中文 | English |
|---|---|---|
| **测试内容** | 经过 3 轮反馈循环后，Agent 输出质量是否可观测地提升 | After 3 feedback rounds, verify Agent output quality shows measurable improvement |
| **执行步骤** | 1. 执行相同类型任务 3 次，每次 PM 提供反馈并通过 2. 对比第 1 轮与第 3 轮输出 3. 评估相关性、格式符合度、个性化程度 | 1. Run the same task type 3 times, with PM feedback each round 2. Compare round-1 and round-3 outputs 3. Evaluate relevance, format compliance, personalization |
| **通过标准** | 第 3 轮输出在至少 2 个维度上优于第 1 轮（评审人主观评分 ≥4/5） | Round-3 output outperforms round-1 on at least 2 dimensions (reviewer score ≥4/5) |

---

## Suite C — 边缘容错 Edge Cases

*验证系统在异常输入、意外重启和并发压力下的健壮性。*
*Verifies system robustness under abnormal inputs, unexpected restarts, and concurrent load.*

---

### C-01 不支持消息处理 Unsupported Message Handling

| | 中文 | English |
|---|---|---|
| **测试内容** | 发送空消息或无关话题时，系统是否优雅拒绝而非崩溃 | When sending empty or off-topic messages, system declines gracefully without crashing |
| **执行步骤** | 1. 发送空消息 2. 发送与业务无关内容（如"今天天气如何"） 3. 确认系统返回友好提示而非错误堆栈 | 1. Send empty message 2. Send off-topic content (e.g., "what's the weather today") 3. Confirm system returns friendly prompt, not an error stack |
| **通过标准** | 两种输入均返回可读错误提示；无 500 错误；任务队列不受影响 | Both inputs return readable error message; no 500 errors; task queue unaffected |

---

### C-02 重启后状态恢复 State Recovery After Restart

| | 中文 | English |
|---|---|---|
| **测试内容** | 系统重启后，进行中的任务是否能恢复并继续执行 | After a system restart, in-progress tasks resume and continue correctly |
| **执行步骤** | 1. 创建一个任务并停留在"PM 审批中"状态 2. 模拟系统重启 3. 确认任务状态保留；PM 仍可正常审批 | 1. Create task and leave it in "awaiting PM approval" state 2. Simulate system restart 3. Confirm task state is preserved; PM can still approve |
| **通过标准** | 重启后任务状态与重启前完全一致；无数据丢失；PM 操作正常 | Task state identical before and after restart; no data loss; PM operations work normally |


### C-03 并发任务处理 Concurrent Task Handling

| | 中文 | English |
|---|---|---|
| **测试内容** | 同时提交多个任务时，系统是否独立处理每个任务而不相互干扰 | When multiple tasks are submitted simultaneously, each is processed independently without cross-contamination |
| **执行步骤** | 1. 同时发送 3 个不同类型的任务请求 2. 确认每个任务生成独立草稿 3. PM 分别审批，验证输出内容不混淆 | 1. Submit 3 different task requests simultaneously 2. Confirm each task generates an independent draft 3. PM approves each; verify outputs are not mixed |
| **通过标准** | 3 个任务全部独立完成；任务 ID 唯一；输出内容无交叉污染 | All 3 tasks complete independently; unique task IDs; no content cross-contamination |

---

## 验收追踪表 Pass/Fail Tracking

| 场景 ID | 场景名称 | 负责人 | 执行日期 | 结果 | 备注 |
|---------|----------|--------|----------|------|------|
| A-01 | 周报端到端 Weekly Report | | | ☐ Pass ☐ Fail | |
| A-02 | 会议准备端到端 Meeting Prep | | | ☐ Pass ☐ Fail | |
| A-03 | PM 拒绝与恢复 Rejection & Recovery | | | ☐ Pass ☐ Fail | |
| B-01 | 个人 KB 注入 KB Injection | | | ☐ Pass ☐ Fail | |
| B-02 | 示例自动积累 Auto-Accumulation | | | ☐ Pass ☐ Fail | |
| B-03 | 规则注入验证 Rule Injection | | | ☐ Pass ☐ Fail | |
| B-04 | 渐进记忆积累 Memory Accumulation | | | ☐ Pass ☐ Fail | |
| B-05 | 多轮质量提升 Quality Improvement | | | ☐ Pass ☐ Fail | |
| C-01 | 不支持消息处理 Unsupported Messages | | | ☐ Pass ☐ Fail | |
| C-02 | 重启后状态恢复 State Recovery | | | ☐ Pass ☐ Fail | |
| C-03 | 并发任务处理 Concurrent Tasks | | | ☐ Pass ☐ Fail | |

**验收通过标准 Acceptance Criteria:** Suite A 全部通过 + Suite B ≥ 4/5 通过 + Suite C 全部通过
**Release Gate:** All Suite A + ≥ 4/5 Suite B + All Suite C must pass before v0.4.0 ships.

---

*文档版本 Document Version: v0.4.0-rc1 · 创建日期 Created: 2026-04-29 · knowledge_engineer*
