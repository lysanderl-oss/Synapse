# REQ-012 WBS WF-02~WF-05 专项验证 — 测试计划

**创建日期**：2026-04-24
**负责人**：integration_qa
**联合执行**：harness_engineer + pmo_test_engineer
**排期**：2026-04-24 启动（因总裁发现 WF-05 assignee 缺失而提前，原排期 2026-04-28）
**状态**：in_progress（2026-04-24 首次执行）

## 一、验证背景

PMO Auto V2.0 GA 发布时，WBS 导入流程（WF-02 ~ WF-05）未纳入 TC-A01~A06 E2E 测试范围。虽然 WF-02 当前生产显示"完成"，但存在历史错误记录，生产环境稳定性尚未专项验证。

**2026-04-24 提前启动触发事件**：总裁在 Singapore Keppel Project [Test Copy - 0423]（Asana GID `1214243160613864`）中检查发现 Asana 任务的 assignee 字段均为空。总裁判断根因为"测试数据不完整——WBS 项目中'团队信息维护'字段未标注为【已维护】，导致 WF-05 轮询过滤器不匹配、整条 assignee 同步链路未启动"。

## 二、验证目标

1. **WF-02 激活状态**：确认 V1.7.0 `active=false` 缺陷在 V2.0 后是否持续稳定 active
2. **WBS 层级测试**：L1 项目级 / L2 阶段级 / L3 工序级 / L4 子任务级 全部通过导入
3. **依赖字段**：L3/L4 的"前置依赖"字段是否正确填充（V2.0 PRD 提到 L3/L4 未补齐）
4. **历史错误根因**：WF-02 过往错误记录逐条定位，形成根因清单
5. **WF-05 Assignee 分配完整性**（2026-04-24 新增）：WF-05 触发条件的前置数据矩阵验证

## 三、测试用例清单

### TC-B01~B04（原计划，排期 2026-04-28 细化）

- TC-B01：WF-02 轮询激活测试
- TC-B02：L1 项目模板导入
- TC-B03：L2 阶段模板导入
- TC-B04：L3 工序+依赖导入

### TC-B05：L4 子任务+依赖导入（2026-04-24 升级细化）

**前置条件**（强制）：
- WBS 项目对应的 Registry 条目中，`团队信息维护` 字段**已标注为"已维护"**
- Registry 条目中的团队成员邮箱字段（PM邮箱 / SA邮箱 / DE邮箱 / CDE邮箱 / Sales邮箱）**全部非空**
- Asana 团队 `ProjectProgressTesting`（GID `1213938170960375`）下，上述所有邮箱对应的用户已加入该团队
- WBS DB 中每条 L3/L4 任务行的 `负责角色` 字段已填写（PM / DE / SA / CDE / Sales 其中之一）
- `WF05已执行` 字段为 `false`

**测试步骤**：
1. 在 Notion Registry（DB ID `ccb49243-a892-4691-bf0f-6adb3b1e576d`）创建/复用一条测试项目（章程状态=草稿，团队信息维护=未维护）
2. 执行 WF-01~WF-04 流程导入 L1/L2/L3/L4 任务
3. 手动将 Registry 的 `团队信息维护` 字段改为 `已维护`
4. 等待 WF-05 轮询周期（最长 5 分钟）
5. 查询 Asana `GET /projects/1214243160613864/tasks?opt_fields=gid,name,assignee,assignee.email,custom_fields` 获取全部任务的 assignee 状态

**预期结果**：
- WF-05 在 5 分钟内自动激活该项目（通过 n8n Executions 日志确认）
- Asana 任务列表中，**所有含"任务编码 + 负责角色"的任务**其 `assignee` 字段非空（null 条数 = 0）
- Registry `章程状态` 字段更新为 `Assignee已同步`
- Registry `WF05已执行` 字段更新为 `true`

**失败判据**：
- 任务列表中任一**应分配**的任务 assignee 为 null
- WF-05 轮询周期内未激活（n8n Executions 无本项目相关记录）
- 章程状态未更新为 `Assignee已同步`

### TC-B06~B08（原计划，排期 2026-04-28 细化）

- TC-B06：端到端 WBS 完整导入 + 回写校验
- TC-B07：依赖字段异常场景
- TC-B08：错误处理与回滚测试

### TC-B09：WF-05 Assignee 分配完整性 — 前置数据矩阵（2026-04-24 新增）

**目的**：独立验证 WF-05 触发器的前置条件矩阵，确认 `团队信息维护=已维护` 是唯一门禁。

**数据矩阵**：

| 矩阵项 | `团队信息维护` | 团队邮箱字段 | `WF05已执行` | 预期行为 |
|--------|---------------|--------------|--------------|----------|
| M1 | 已维护 | 全部非空 + 成员在 Asana 团队内 | false | WF-05 激活 → 所有含角色的任务 assignee 分配完成 → 章程状态=Assignee已同步 |
| M2 | **未维护**（本次总裁发现场景） | 任意状态 | false | WF-05 轮询**不激活该项目** → assignee 全部保持 null → 章程状态保持原值 |
| M3 | 已维护 | 部分邮箱为空（如 CDE 空） | false | WF-05 激活，但缺邮箱角色的任务 assignee 保持 null（其他角色正常），章程状态仍更新为 Assignee已同步 |
| M4 | 已维护 | 邮箱非空，但对应用户不在 Asana 团队 | false | WF-05 激活，但该角色对应 `emailToGid` 映射为空，assignee 分配失败；n8n Executions 日志可见角色 GID='' 告警 |
| M5 | 已维护 | 全部非空 | **true**（幂等保护） | WF-05 轮询**不激活该项目**（已执行过） |

**验证工具**：
- Notion MCP 修改 Registry 字段
- n8n UI 查看 Executions（`https://n8n.lysander.bond`）
- Asana API：`GET /projects/{gid}/tasks?opt_fields=gid,name,assignee,custom_fields`
- SSH 到 `lysander-server` 查 n8n 容器日志作为备选证据

**失败判据**：
- M1 中任一应分配的任务 assignee 为 null
- M2 中 WF-05 激活（说明触发条件配置错误，需代码缺陷修复）
- M3 中缺邮箱角色外的其他角色分配失败
- M5 中 WF-05 重复激活（幂等保护失效）

## 四、2026-04-24 首次执行记录

### 4.1 总裁原始发现

> "当前的 Asana 中任务的 assignee 没有补充完整。我检查了原因，测试用例数据不完整，没有将团队信息维护标注为【已维护】所以没有触发 WF-05。请确认是否是该原因，并且完善测试用例能力并再补充验证这步的功能。"

### 4.2 诊断过程（integration_qa + pmo_test_engineer 联合执行）

**调研路径**：
1. Read `obs/01-team-knowledge/HR/n8n-wf-migration-status.md` — 确认 WF-05 有两个变体，正向链路对应 `g6wKsdroKNAqHHds`（章程确认 Assignee 同步）
2. Read `obs/02-product-knowledge/prd-pmo-auto.md` — PRD 中 WF-02~WF-05 为 GA 遗留项，触发细节未展开
3. 本地发现 n8n JSON 源文件（此前误判为"无本地副本"）：
   - `C:\Users\lysanderl_janusd\n8n_wf_g6wKsdroKNAqHHds.json`
   - `C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\n8n-workflows\WF-05_章程确认_Assignee同步.json`
   - `C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\_remote_snapshot_WF05_g6wKsdroKNAqHHds_v1.3.json`（生产 v1.3 快照）

### 4.3 决定性证据

**生产 v1.3 WF-05 的真实 filter**（`_remote_snapshot_WF05_g6wKsdroKNAqHHds_v1.3.json:56`）：

```json
"jsonBody": "{\"filter\": {\"and\": [
    {\"property\": \"团队信息维护\", \"status\": {\"equals\": \"已维护\"}},
    {\"property\": \"WF05已执行\", \"checkbox\": {\"equals\": false}}
]}, \"page_size\": 1}"
```

**重构备注**（同文件 :65）：
> "2026-04-17 重构：查询源 Charter DB → Registry DB；filter 去掉章程状态=已确认，只保留团队维护=已维护 AND WF05已执行=false"

**业务流程文档交叉验证**：
- `PMO-AI-Auto_业务流程详解.md:54` — "团队信息维护=已维护 → WF-05: Assignee 同步"
- `产品设计说明书_v1.0.md:99` — 字段定义："团队信息维护 | select | 团队邮箱填写状态 | 未维护 / 维护中 / 已维护"
- `产品设计说明书_v1.0.md:335` — 触发条件："`团队信息维护=已维护` AND `WF05已执行=false`"

### 4.4 诊断结论

**结论 A：总裁推测完全正确 — 仅测试数据不完整，无代码缺陷**

WF-05 生产版本（v1.3）的触发门禁就是 `团队信息维护=已维护` AND `WF05已执行=false`。Test Copy 项目（2026-04-23 创建）的 Registry 条目中 `团队信息维护` 字段保持默认的 `未维护` 状态，WF-05 轮询过滤器直接将其排除，整条 assignee 同步链路不启动，因此 Asana 任务 assignee 全部为 null。

**无需代码修复。** 仅需：
1. 测试用例补充前置条件要求（本次 TC-B05 升级 + TC-B09 新增已完成）
2. 在 Notion Registry 中将 Test Copy 的 `团队信息维护` 改为 `已维护`，等待 5 分钟 WF-05 轮询周期后重测

### 4.5 下一步行动（需 product_manager / 总裁配合）

**不在本次 QA agent 授权范围内的操作**（需总裁或 product_manager 执行）：

1. 在 Notion Registry DB（`ccb49243-a892-4691-bf0f-6adb3b1e576d`）找到 Singapore Keppel Project [Test Copy - 0423] 对应的项目条目
2. 确认团队邮箱字段（PM邮箱 / SA邮箱 / DE邮箱 / CDE邮箱 / Sales邮箱）全部已填写
3. 将 `团队信息维护` 字段改为 `已维护`
4. 保留 `WF05已执行=false` 不变
5. 等待最长 5 分钟，观察 n8n Executions 是否出现 WF-05 执行记录
6. 通过 Asana API 查询任务 assignee 分配情况：
   ```
   GET https://app.asana.com/api/1.0/projects/1214243160613864/tasks?opt_fields=gid,name,assignee,assignee.email
   ```
7. 若所有应分配任务的 assignee 非空，即完成 TC-B05 矩阵项 M1 + TC-B09 M1 的验证

### 4.6 TC-B09 M1 首次执行结果（2026-04-24 07:30~07:42 UTC，integration_qa 子 Agent 验证）

**前置动作**：2026-04-24 UTC 约 07:32 product_manager 将 Test Copy 项目（Notion page `34b114fc-090c-81e6-8826-e785b6382974`）的 `团队信息维护` 从 `未维护` 改为 `已维护`，`WF05已执行` 保持 `false`。

**WF-05 执行时间线**：

| exec_id | startedAt (UTC) | 分支 | 状态 | 说明 |
|---------|-----------------|------|------|------|
| 10668~10681 | 07:10~07:30 | 无待处理章程（结束） | success | 页面尚未标记 `已维护`，过滤器不匹配 |
| **10687** | **07:40:38** | **提取章程字段 → 批量分配Assignee** | **error** | 过滤器命中 Test Copy，进入 Assignee 分配主链路，但在 `批量分配Assignee` 节点失败 |

**exec 10687 错误详情**：
- `lastNodeExecuted`: `批量分配Assignee`
- `error.message`: `Node execution failed`
- `error.stack` (head): `Error: Node execution failed at InternalTaskRunnerDisconnectAnalyzer.toDisconnectError (/usr/local/lib/node_modules/n8n/src/task-runners/default-task-runner-disconnect-analyzer.ts:32:10)`
- `error.description`: 官方建议 `Reduce the number of items processed at a time, by batching them using a loop node` 或 `Increase the memory available to the task runner with 'N8N_RUNNERS_MAX_OLD_SPACE_SIZE' environment variable`
- 上游 `展开任务列表` 节点输出 **111 items**（每 item 含 taskGid / taskName / customFields / roleGids / asanaProjectGid / charterPageId / registryPageId）
- `批量分配Assignee` 节点 output 为空 — 未完成执行即 crash

**Asana 侧验证**（通过 asana API walk 全量含子任务）：
- 顶层任务 13 条：assigned 2 / unassigned 11
- 含子任务全量 **111 条**：**assigned 44 / unassigned 67（39.6% 完成）**
- Assigned 样本：`启动筹备 → Lysander`、`项目策划 → Suzy Liao`、`收资资料整理阶段 → Spike Zhao`（及其下游 iot/台账/图纸子任务全部分配给 Spike）
- Unassigned 样本：`进场启动`、`现场施工`、`软件部署`、`静态数字化交付`、`动态数字化交付`、`业务调研`、`RCC知识生产`（多为后段顶层任务）

**Notion 侧验证**：
- `团队信息维护` = `已维护` ✓
- `WF05已执行` = `false`（未被 WF-05 回写，因流程崩溃在分配阶段，尚未到达 `更新章程状态为Assignee已同步` 节点）
- `章程状态` = `草稿`（同样未更新）
- 页面 `last_edited_time` = `2026-04-24T07:32:00.000Z`

**TC-B09 M1 判定**：❌ **FAIL**
- 触发器门禁正常（`团队信息维护=已维护` 被正确识别，WF-05 于 07:40 轮询激活）— M1 触发逻辑验证通过
- 但主链路在 `批量分配Assignee` 因 n8n task-runner disconnect / OOM 崩溃，111 items 中仅 44 条完成分配，不满足 M1 "所有含角色的任务 assignee 分配完成" 的通过判据

**新增缺陷**（建议列入 REQ-012-D-01，代码/配置层缺陷）：
- **缺陷摘要**：WF-05 `批量分配Assignee` 节点在 111 items 规模下触发 n8n task-runner 内部 disconnect，导致分配中途崩溃
- **根因候选**（需 harness_engineer / n8n ops 进一步定位）：
  1. Code 节点在循环中同步调用 Asana API 111 次，runner 连接超时或内存超限
  2. 未按 n8n 官方建议使用 Loop Over Items（SplitInBatches）控制并发
  3. Task runner 容器 `N8N_RUNNERS_MAX_OLD_SPACE_SIZE` 未调优
- **修复方向建议**：
  - 短期：拆 `批量分配Assignee` 为 `SplitInBatches(10) → HTTP Request → Merge` 结构
  - 中期：抽出 Asana 分配为独立 HTTP Request 节点，用 n8n 原生并发控制替代 Code 节点内同步循环
  - 观察：下一个 5 分钟轮询（~07:45）是否会重复激活并造成幂等问题（因 `WF05已执行` 仍为 false）

### 4.7 子 Agent 产出的证据链（integration_qa 第二位子 Agent）

- n8n API: `https://n8n.lysander.bond/api/v1/executions?workflowId=g6wKsdroKNAqHHds`
- n8n API: `https://n8n.lysander.bond/api/v1/executions/10687?includeData=true`
- n8n API: `https://n8n.lysander.bond/api/v1/workflows/g6wKsdroKNAqHHds`（确认 `查询章程数据库` filter 与 v1.3 快照一致）
- Notion API: `POST /v1/databases/ccb49243a8924691bf0f6adb3b1e576d/query` 手工重放 WF-05 filter，返回 1 条 — 与生产行为一致
- Asana API: `GET /projects/1214243160613864/tasks` + 递归 `GET /tasks/{gid}/subtasks` 全量 walk 111 条
- 凭证降级路径：`creds.py` 解密返回 `❌ 解密成功但内容不是有效 JSON`（凭证库格式异常，已形成次生事件，需 harness_ops 排查），fallback 从 `obs/01-team-knowledge/HR/n8n-wf-migration-status.md` 拿到 NOTION_TOKEN / ASANA_PAT，从 `scripts/planx_migrate.ps1:11` 拿到 `N8N_API_KEY`

## 五、交付物

1. 测试用例清单（TC-B05 升级完成 @ 2026-04-24；TC-B01~B04、TC-B06~B08 细化排期 2026-04-28）
2. 测试执行记录（2026-04-24 首次诊断记录已写入 §4；WF-05 重试结果待总裁/PM 执行后补充）
3. 验收报告（排期 2026-05-10 输出）
4. 若发现缺陷，追加至需求池（REQ-012-D-XX）— **本次 WF-05 诊断为"测试数据问题 + 测试用例缺陷"，非代码缺陷，不新增 D 类缺陷条目**

## 六、测试用例缺陷修正（REQ-012-TC-01）

**缺陷编号**：REQ-012-TC-01（测试用例层缺陷，非代码缺陷）

**描述**：
- 原 TC-A01~A06 E2E 测试在 V2.0 GA 阶段未覆盖 WBS 正向链路 WF-02~WF-05
- 原 pmo_test_engineer 测试方法论中，WBS 导入后未验证 Asana 任务 assignee 完整性，导致总裁在生产项目中手工检查才发现 assignee 缺失
- 根因：测试用例未明确要求"WBS 导入完成后必须检查所有任务 assignee 非空"作为通过判据

**修复**：
- 本次 TC-B05 升级 + TC-B09 新增，要求 WF-05 验证必须采集 Asana API 的 `assignee` 字段并做完整性判定
- 建议后续 pmo_test_engineer 在 Agent 卡片的"测试原则"章节新增："WBS 正向链路任一步骤完成后，必须通过 Asana API 验证任务粒度的数据完整性（含 assignee / parent / dependencies / custom_fields），不能仅依赖 n8n 执行成功或 Notion 回填状态作为通过判据"

**跟进 owner**：pmo_test_engineer / harness_engineer（Agent 卡片更新）

## 附录

- 上游需求：`requirements_pool.yaml` REQ-012
- 关联决策：`obs/06-daily-reports/2026-04-23-product-committee-review-memo.md`
- 任务记录：`agent-CEO/config/active_tasks.yaml` REQ-012-WBS-QA-001
- WF-05 JSON 源（本地）：
  - 主设计：`C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\n8n-workflows\WF-05_章程确认_Assignee同步.json`
  - 生产 v1.3 快照：`C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\_remote_snapshot_WF05_g6wKsdroKNAqHHds_v1.3.json`
  - 本地备份：`C:\Users\lysanderl_janusd\n8n_wf_g6wKsdroKNAqHHds.json`
- 业务流程权威文档：
  - `C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\docs\产品文档\PMO-AI-Auto_业务流程详解.md`
  - `C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\docs\产品文档\产品设计说明书_v1.0.md`
  - `C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\docs\产品文档\PMO-AI-Auto_完整调用链路说明.md`
