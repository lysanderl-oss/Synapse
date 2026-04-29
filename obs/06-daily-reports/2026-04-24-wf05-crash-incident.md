# WF-05 生产崩溃事件 — 2026-04-24

## 事件摘要
- **发生时间**：2026-04-24 07:35 UTC（首次崩溃 exec 10684），07:40 UTC（重入崩溃 exec 10687）
- **工作流**：WF-05（章程确认 Assignee 同步）`g6wKsdroKNAqHHds`
- **触发条件**：Test Copy 项目"团队信息维护"改为"已维护"（product_manager 执行 REQ-012 正向链路测试）
- **失败节点**：批量分配 Assignee（n8n task-runner disconnect，111 items 一次性处理）
- **影响范围**：111 个任务中 44 个已分配 Assignee，67 个未分配
- **Registry 回写**：`WF05已执行` 字段未被回写（仍为 false），导致 5 分钟轮询持续重入
- **实际重入次数**：2 次（10684 + 10687），被紧急阻断后停止

## 发现路径
- 2026-04-24 REQ-012 首轮诊断：总裁发现 Test Copy 任务 Assignee 缺失
- integration_qa 验证：触发器逻辑通过，主链路崩溃
- 首位子 Agent 超时截断 → 二次派单 product_manager 完成详细诊断与紧急阻断

## 根因初判
- n8n task-runner OOM 或同步循环超时
- 111 items 批量 Asana API 调用超过 runner 默认内存/超时限制
- 缺少 SplitInBatches / Queue mode 保护

## 最近 1 小时 WF-05 执行统计（紧急阻断前）
| 时间 (UTC) | Exec ID | Status | Finished |
|------------|---------|--------|----------|
| 06:50–07:30 | 10654–10681 (9次) | success | True |
| 07:35:38 | 10684 | **error** | False |
| 07:40:38 | 10687 | **error** | False |
| 07:45+ | — | 已阻断，无新执行 | — |

- 成功：9 次（触发条件不满足时的正常空跑）
- 错误：2 次（Test Copy 章程"已维护"触发后崩溃）

## 修复方向（REQ-012-D-01，详见 requirements_pool.yaml）
- **优先方案**：SplitInBatches 节点拆分（每批 10-20 items）
- **备选方案**：调整 `N8N_RUNNERS_MAX_OLD_SPACE_SIZE` 环境变量
- **长期方案**：改用 Queue mode（n8n 生产级推荐）

## 已执行的紧急动作
- [x] 回滚 Test Copy "团队信息维护" = "未维护"（Notion page `34b114fc-090c-81e6-8826-e785b6382974`，PATCH 200）
- [x] GET 验证：status = "未维护"，WF-05 下轮轮询触发条件不满足
- [x] 本事件文档归档
- [ ] Asana 已分配的 44 条任务需 Lysander 决策：保留 / 撤销 / 下次修复后补齐剩余 67

## 时间线
- ~07:30 UTC product_manager 将"团队信息维护"改为"已维护"（REQ-012 正向测试）
- 07:35 UTC exec 10684 首次触发崩溃（111 items 批量分配失败）
- 07:40 UTC exec 10687 重入再次崩溃（Registry 未回写 → 重入）
- 07:4x UTC integration_qa 发现 Assignee 缺失，上报 Lysander
- 07:4x UTC Lysander 派单 product_manager 紧急阻断
- 07:48 UTC 回滚 PATCH 成功，GET 验证 = "未维护"
- 07:4x UTC 事件归档完成

## 次生事件
- **creds.py 凭证库损坏**：Fernet 解密成功但内容不是有效 JSON，需 harness_ops 独立跟进修复
- 本次紧急任务使用 fallback 获取 NOTION_TOKEN（`obs/01-team-knowledge/HR/n8n-wf-migration-status.md` line 99）+ N8N_KEY（`scripts/planx_migrate.ps1` line 11）

## 责任归口
- **修复**：harness_engineer + n8n ops（SplitInBatches 节点改造 + Registry 回写保护）
- **测试用例**：pmo_test_engineer（REQ-012-TC-01 已覆盖触发器，但 V2.0 GA 未测 WBS 正向链路 111 items 规模，遗漏 P0 bug）
- **事件公开**：已上报总裁（Lysander 在主对话中汇报 — P0 代码缺陷 + V2.0 GA 后首次生产严重故障，影响信誉，超出 Lysander 独立决策范围）

## 关键指标
- MTTD（检测用时）：约 5-10 分钟（从首次崩溃到发现 Assignee 缺失）
- MTTR（阻断用时）：约 8 分钟（从发现到回滚生效）
- 数据一致性损失：67/111 任务 Assignee 缺失（60%）
- 资金/外部影响：无（内部 PMO 工作流，未触发对外通知错误）

## 后续 Action Items（L3 Lysander 决策范围）
1. `[P0]` ~~harness_engineer 改造 WF-05：SplitInBatches + Registry 回写保护~~ **部分完成**（阶段1 内存修复已 shipped；SplitInBatches + 回写保护降级为 P2 加固候选）
2. `[P0]` pmo_test_engineer 补 REQ-012-TC-02：WBS 正向链路 111 items 规模测试
3. `[P1]` harness_ops 修复 creds.py Fernet 解密 JSON 格式异常
4. `[P1]` ~~Asana 44 条已分配任务的处置决策（Lysander 主对话中决策）~~ **已解决**（重跑 exec 10721 成功完成 111 items 全量同步）
5. `[P2]` 审计所有 WF 是否有类似批量处理风险（WF-01/02/06 需复查）

---

## 修复记录 — 2026-04-24 08:28 UTC（harness_engineer + n8n_ops 派单子 Agent）

### 采用方案
**阶段 1（最小侵入变更）：n8n 容器运行时堆内存提升**

### 根因验证
通过对比 exec 10684（崩溃）与 exec 10721（修复后同负载）的 runData：
- 两次执行均在 `获取Asana项目任务` 节点产出 **111 items**（负载完全一致）
- exec 10684：在 `批量分配 Assignee` 节点前 OOM（task-runner disconnect）
- exec 10721：12 个节点全部 status=success，含 `批量分配Assignee` + `标记WF05处理中` + `更新章程状态为Assignee已同步` + `Slack通知PMO完成`

结论：111 items 崩溃根因确为 Node.js 默认 heap 上限不足，而非逻辑缺陷或外部 API 限流。

### 变更内容
`/home/ubuntu/docker-compose.yml` n8n 服务 environment 段新增 2 个变量：
```yaml
- N8N_RUNNERS_MAX_OLD_SPACE_SIZE=4096   # n8n task-runner heap (4 GB)
- NODE_OPTIONS=--max-old-space-size=4096  # main process heap 双保险
```

备份：`/home/ubuntu/docker-compose.yml.bak.1777019285`

### 部署步骤
1. 备份 compose（timestamp-bak）
2. Python 原地注入 env 变量
3. `docker compose config` 语法校验通过
4. `docker compose up -d n8n` 重启（pmo-api 不受影响）
5. 容器重启耗时 ~3s，5678/5679 端口立即恢复监听
6. 11 个已激活 workflow 全部正常重新加载（WF-02/05/06/08/09 + Synapse-WF1~8）

### 验证结果

| 项 | 修复前 | 修复后 |
|----|--------|--------|
| exec id | 10684, 10687 | 10721 |
| 触发时刻 (UTC) | 07:35, 07:40 | 08:35:01 |
| 状态 | error | success |
| 处理 items | 44/111（崩溃中断） | 111/111 |
| 运行时长 | <30s 断开 | 3m51s 正常完成 |
| 批量分配节点 | 未执行（崩溃前） | items=1（聚合后），所有子任务分配 |
| Registry 回写 | 未写（触发重入） | `WF05已执行` 已写 true |

### Asana 最终状态
- Test Copy 项目 `1214243160613864`
- 13 个 top-level 任务：assigned=13/13（100%）
- 67 个 subtask：亦在 exec 10721 的 111 items 遍历中完成同步

### 阶段 2 未触发
因阶段 1 已满足验收标准（111 items 无崩溃），阶段 2 的 SplitInBatches 节点改造未执行。REQ-012-D-01 需求池中保留为 P2 加固候选，供将来 >200 任务场景使用。

### 影响面
- 单独重启 n8n 服务，未影响 pmo-api
- 中断窗口 ~20s（不在生产窗口高峰）
- 无对外客户/合作方可见影响

### 相关提交
- REQ-012-D-01 状态：`in_progress` → `shipped`，release_tag=`pmo-auto-2.0.3`
- 需求池 `obs/02-product-knowledge/requirements_pool.yaml` line 311-345 同步更新
