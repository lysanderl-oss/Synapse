# PMO Auto V2.2 — 真实 E2E 测试报告

**测试执行时间：** 2026-04-25 05:02 — 05:38 (Dubai Time)
**测试工程师：** pmo_test_engineer
**测试标本：** Singapore Keppel Project [Test Copy - 0425]
**Notion 页面 ID：** `34d114fc-090c-81b3-8812-fc392c79765e`
**Asana Project GID：** `1214282123649966`
**Asana Webhook GID：** `1214282157104425`

---

## 执行摘要

| 测试用例 | 结果 | 备注 |
|---------|------|------|
| 前置：WF-01 激活状态 | PASS | AnR20HucIRaiZPS7 active=1 |
| TC-A01：Notion 页面创建 + WF-01 触发 | PASS | WF-01 在 5 分钟内自动触发 |
| TC-A02：WBS 同步到 Asana | PASS (备用路径) | WF-02 DNS Bug，备用 /run-wbs 成功 |
| TC-A03：Notion Hub 页创建 + Asana GID 回填 | PASS | WF-01 自动完成 |
| TC-A04：Webhook 批量注册 | PASS | 新项目注册成功 |
| TC-A05：幂等注册验证 | PASS | 第二次注册项目出现在 skipped |
| TC-A06：任务完成 Webhook → WF-08 通知 | PASS | 全链路 7 秒，WF-08 success |
| PRINCIPLE-001：WBS 正向链路任务粒度校验 | **FAIL** | L3 子任务 37/67（55%）assignee=null |

**验收结论：整体流程可运行，但存在 1 个 P1 Bug（WF-02 DNS）和 1 个已知 P1 Bug（REQ-012 assignee=null）。**

---

## 前置检查：WF-01 激活状态

**命令：**
```bash
ssh lysander-server "sudo sqlite3 /var/lib/docker/volumes/ubuntu_n8n_data/_data/database.sqlite \
  \"SELECT id, name, active FROM workflow_entity WHERE name LIKE '%WF-01%';\""
```

**实际输出：**
```
AnR20HucIRaiZPS7|WF-01 项目初始化|1
ykCSCyxue5zZImIs|WF-01 项目空间初始化|0
```

**判断：** PASS — 主 WF-01（AnR20HucIRaiZPS7）active=1，旧版本（项目空间初始化）inactive 不影响。
**时间戳：** 2026-04-25 05:04

---

## TC-A01：项目录入 + WF-01 触发

### 创建 Notion 页面

**命令：** `POST https://api.notion.com/v1/pages`（via SSH）

**关键参数：**
- parent.database_id: `ccb49243-a892-4691-bf0f-6adb3b1e576d`
- 项目名称: `Singapore Keppel Project [Test Copy - 0425]`
- 状态: `已签约`
- 团队信息维护: `已维护`（status 类型，非 select）
- 完整团队字段：PM/DE/SA/CDE/Sales 均已填写

**实际返回（截录）：**
```json
{
  "id": "34d114fc-090c-81b3-8812-fc392c79765e",
  "created_time": "2026-04-25T05:02:00.000Z",
  "properties": {
    "状态": {"select": {"name": "已签约"}},
    "团队信息维护": {"status": {"name": "已维护", "color": "green"}}
  }
}
```

**创建时间：** `2026-04-25T05:02:00.000Z`
**页面 ID：** `34d114fc-090c-81b3-8812-fc392c79765e`

### WF-01 触发验证

**命令：**
```bash
ssh lysander-server "sudo sqlite3 ... SELECT id, workflowId, startedAt, status FROM execution_entity WHERE workflowId='AnR20HucIRaiZPS7' AND id > 11564 ORDER BY startedAt DESC LIMIT 3;"
```

**实际输出：**
```
11585|AnR20HucIRaiZPS7|2026-04-25 05:10:35.038|success
11567|AnR20HucIRaiZPS7|2026-04-25 05:05:35.028|success
```

**判断：** PASS
- WF-01 在页面创建后 3 分 35 秒内自动触发（05:02 → 05:05）
- 执行 ID 11567，status=success

---

## TC-A03：Notion Hub 页创建 + Asana GID 回填

**验证时间：** 2026-04-25 05:10

**命令：** `GET https://api.notion.com/v1/pages/34d114fc-090c-81b3-8812-fc392c79765e`

**实际输出（关键字段）：**
```
WBS导入状态: 待导入
Asana项目GID: 1214282123649966
状态: 初始化中
项目Hub页链接: https://www.notion.so/Singapore-Keppel-Project-Test-Copy-0425-34d114fc090c81c39f4ce79ce0249b47
last_edited_time: 2026-04-25T05:05:00.000Z
```

**判断：** PASS
- WF-01 在 05:05 执行后：状态从「已签约」→「初始化中」
- Asana 项目 GID `1214282123649966` 已回填
- Notion Hub 页已创建

---

## TC-A02：WBS 同步到 Asana（备用路径）

### WF-02 DNS 故障（新发现 Bug）

**现象：**
```bash
# n8n event log 错误信息（execution 11584, 11587）：
"errorMessage": "The DNS server returned an error, perhaps the server is offline"
"lastNodeExecuted": "调用 PMO-API 执行导入"
"nodeType": "n8n-nodes-base.httpRequest"
```

**根因：** WF-02 配置的 PMO-API URL 为 `http://pmo-api:8088/run-wbs`（Docker 内网 hostname），
n8n 容器（ubuntu_pmo_net 网络，172.19.0.3）无法解析 `pmo-api`，
因为 pmo-api 容器在默认 bridge 网络（172.17.0.3），两容器不在同一 Docker 网络。

**受影响：** WF-02 在 05:05 正好在 WF-01 执行后出现 error 状态。

**备用方案：** 直接调用 localhost:8088/run-wbs

**命令：**
```bash
ssh lysander-server "curl -s -X POST 'http://localhost:8088/run-wbs' \
  -H 'Content-Type: application/json' \
  -d '{
    \"registry_page_id\": \"34d114fc-090c-81b3-8812-fc392c79765e\",
    \"title\": \"Singapore Keppel Project [Test Copy - 0425]\",
    \"asana_gid\": \"1214282123649966\",
    \"pm_email\": \"lysanderl@janusd.com\",
    \"de_email\": \"spikez@janusd.com\",
    \"sa_email\": \"rosaw@janusd.com\",
    \"cde_email\": \"suzyl@janusd.com\"
  }'"
```

**实际返回：**
```json
{"job_id": "4fd8a4e7", "status": "queued", "title": "Singapore Keppel Project [Test Copy - 0425]"}
```

**排队时间：** 2026-04-25 05:23:01
**完成时间：** 2026-04-25 05:32:23（耗时约 9 分钟）

**最终 job 状态：**
```json
{
  "job_id": "4fd8a4e7",
  "status": "completed",
  "wbs_success": true,
  "hub_success": true,
  "error": null,
  "completed_at": "2026-04-25T05:32:23.501655+00:00"
}
```

**Notion 导入状态变化：**
- 05:23 — 「待导入」→「导入中」（wbs_to_asana.py 启动后 Notion 回写）
- 05:32 — 「导入中」→「已完成」

**Asana 任务数验证（完成后）：**
```bash
ssh lysander-server "... 查询 Asana project 1214282123649966 任务数"
# 结果：顶层任务 13 个（与参考项目 0423 一致），L3 子任务 67 个
```

**判断：** PASS（通过备用路径）

**新发现缺陷：** BUG-0425-001（P1）— WF-02 Docker 网络隔离导致 DNS 解析失败

---

## PRINCIPLE-001：WBS 正向链路任务粒度校验

### 校验范围

基于 PRINCIPLE-001（测试档案 v1.4 强制原则），WBS 正向链路完成后必须通过 Asana API 验证任务粒度。

### L2 层（顶层任务）

| 字段 | 结果 |
|------|------|
| 任务数量 | 13（与参考项目一致）|
| assignee | 全部 null（13/13）|
| dependencies | 12/13 有前置依赖 |
| section | 归属「交付期」section |

### L3 层（子任务）

**命令（逐一查询 13 个顶层任务的子任务）：**
```bash
for each top-level task GID:
  curl .../tasks/{gid}/subtasks?opt_fields=gid,name,assignee...
```

**实际结果：**
| 指标 | 值 |
|------|-----|
| L3 子任务总数 | 67 |
| assignee 非 null | 30（45%）|
| **assignee = null** | **37（55%）** |

**样本（启动筹备 子任务）：**
```
编制项目章程及筹备工作 🏁 | assignee: {gid: 1213400756695149} ✓
补充收资 🏁              | assignee: {gid: 1213400756695149} ✓
收资资料整理阶段 🏁       | assignee: None ✗
```

**判断：** **FAIL — PRINCIPLE-001 违反**
- 37/67（55%）的 L3 任务 assignee=null
- 与 REQ-012 已知 Bug（Singapore Keppel Test Copy 项目 assignee 全部为 null）吻合
- 本次测试证实此 Bug 在 V2.2 中仍然存在（assignee 有部分设置但不完整）

**根因推测：** wbs_to_asana.py 中 assignee 映射逻辑存在条件覆盖不全的问题（部分任务类型未被正确映射到对应角色的 Asana GID）

---

## TC-A04：Webhook 批量注册

**命令：**
```bash
curl -s -X POST 'https://pmo-api.lysander.bond/webhooks/asana/register-team' \
  -H 'Content-Type: application/json' \
  -d '{"target_url": "https://pmo-api.lysander.bond/webhooks/asana"}'
```

**实际返回（截录）：**
```json
{
  "registered": [
    {
      "project_gid": "1214282123649966",
      "project_name": "Singapore Keppel Project [Test Copy - 0425]",
      "webhook_gid": "1214282157104425"
    }
  ],
  "skipped": [...36 projects with reason: already_exists...],
  "failed": []
}
```

**health 端点变化：** `active_subscriptions: 73 → 77`（+4，包括 0425 项目）

**判断：** PASS
- 新项目成功注册 webhook
- 已有项目正确 skip
- failed 列表为空
- health 端点 active_subscriptions 增加

**证据时间戳：** 2026-04-25 05:23:49（pmo-api 日志）

---

## TC-A05：幂等注册验证

**命令：** 与 TC-A04 相同请求（第二次调用）

**实际返回：**
```
Registered: 0
Skipped: 38（含 0425 项目，reason: already_exists）
Failed: 0
```

**0425 项目在 skipped 列表确认：**
```json
{
  "project_gid": "1214282123649966",
  "project_name": "Singapore Keppel Project [Test Copy - 0425]",
  "reason": "already_exists"
}
```

**判断：** PASS — 幂等机制正常工作

---

## TC-A06：任务完成 Webhook 通知验证

### 基线记录

| 指标 | 基线值 |
|------|-------|
| webhook_events_dedup 记录数 | 4 |
| notified_events 记录数 | 3 |

### 操作：完成 Asana 任务

**目标任务：** 「编制项目章程及筹备工作 🏁」(GID: 1214282244227772)
**选择原因：** L3 层任务，属于「启动筹备」下游，assignee 有值

**命令：**
```bash
curl -s -X PUT 'https://app.asana.com/api/1.0/tasks/1214282244227772' \
  -H "Authorization: Bearer [PAT]" \
  -d '{"data": {"completed": true}}'
```

**返回：**
```json
{"gid": "1214282244227772", "name": "编制项目章程及筹备工作 🏁", "completed": true, "completed_at": "2026-04-25T05:37:32.458Z"}
```

### Webhook 触发链路（实际 pmo-api 日志）

```
2026-04-25 05:37:36 [INFO] pmo_api.asana_webhook — [raw_body] {"events":[{"created_at":"2026-04-25T05:37:32.623Z","action":"changed","change":{"field":"completed","action":"changed"},"resource":{"gid":"1214282244227772","resource_type":"task"}}]}
2026-04-25 05:37:36 [INFO] pmo_api.asana_webhook — [webhook] received event: action=changed, resource_type=task, field=completed
2026-04-25 05:37:37 [INFO] pmo_api.asana_webhook — Asana API 回查 task_gid=1214282244227772 → completed=True
2026-04-25 05:37:37 [INFO] pmo_api.asana_webhook — 事件 accepted：Asana API 回查确认 completed=True
2026-04-25 05:37:37 [INFO] pmo_api.asana_webhook — 事件批次处理完成：accepted=1 skipped=0 duplicates=0
2026-04-25 05:37:39 [INFO] httpx — HTTP Request: POST https://n8n.lysander.bond/webhook/wf08-task-completed "HTTP/1.1 200 OK"
2026-04-25 05:37:39 [INFO] pmo_api.asana_webhook — 事件 c967521b4624 已转发 n8n WF-08
```

### WF-08 执行结果

```
sudo sqlite3 ... "SELECT id, workflowId, startedAt, status FROM execution_entity WHERE workflowId='ZCHNwHozL2Ib0urk' ORDER BY startedAt DESC LIMIT 1;"
11604|ZCHNwHozL2Ib0urk|2026-04-25 05:37:37.844|success
```

### 端到端延迟

| 节点 | 时间 |
|------|------|
| 任务完成（Asana） | 05:37:32.458 |
| pmo-api 收到 webhook | 05:37:36 |
| pmo-api accepted=1 + 转发 WF-08 | 05:37:39 |
| WF-08 执行成功 | 05:37:37.844 |
| **总延迟（任务完成 → WF-08 success）** | **约 5 秒** |

### dedup 表验证

```
sudo sqlite3 ... "SELECT id, event_key, task_gid, processed_at FROM webhook_events_dedup ORDER BY processed_at DESC LIMIT 1;"
5|wf08:1214282244227772:completed|1214282244227772|2026-04-25 05:37:37
```

**基线 4 → 5**（新增 1 条去重记录）

### notified_events 变化

基线 3 → 4（新增 1 条）

**判断：** PASS
- accepted=1 ✓
- WF-08 status=success ✓
- 端到端延迟 5 秒（SLA ≤60 秒）✓
- dedup 表新增记录 ✓
- notified_events 新增记录 ✓

---

## 缺陷清单

### BUG-0425-001（新发现）

| 项目 | 值 |
|------|-----|
| **ID** | BUG-0425-001 |
| **严重级别** | P1 |
| **标题** | WF-02 WBS导入触发 — Docker 网络隔离导致 DNS 解析失败 |
| **现象** | WF-02 每 5 分钟触发一次，调用 `http://pmo-api:8088/run-wbs` 时报错："The DNS server returned an error, perhaps the server is offline" |
| **根因** | n8n 容器在 `ubuntu_pmo_net`（172.19.0.3），pmo-api 在默认 `bridge`（172.17.0.3），两网络隔离，`pmo-api` hostname 无法解析 |
| **首次发现时间** | 2026-04-25 05:10（n8n execution 11584, 11587） |
| **影响范围** | WF-01 触发后 WBS 不会自动导入，需要人工调用 localhost:8088/run-wbs 备用路径 |
| **修复方案** | 方案A：将 n8n 和 pmo-api 容器加入同一 Docker 网络；方案B：WF-02 改用外网 URL `https://pmo-api.lysander.bond/run-wbs` |
| **临时绕过** | SSH 到服务器手动执行 `curl localhost:8088/run-wbs`，或通过外网 `https://pmo-api.lysander.bond/run-wbs` |

### BUG-0425-002（已知，REQ-012 延续）

| 项目 | 值 |
|------|-----|
| **ID** | BUG-0425-002 |
| **严重级别** | P1 |
| **标题** | WBS 正向链路 — L3 子任务 assignee 部分为 null（55%） |
| **现象** | wbs_to_asana.py 导入后，13 个顶层任务全部 assignee=null，67 个 L3 子任务中 37 个（55%）assignee=null |
| **根因** | 同 REQ-012 诊断结论（wbs_to_asana.py assignee 映射逻辑不完整） |
| **首次发现** | 2026-04-24 REQ-012 首轮诊断，本次测试重新确认仍存在 |
| **影响范围** | PRINCIPLE-001 校验 FAIL；无法正确向负责人发送 Slack DM |
| **修复状态** | 待修复（V2.2 未解决） |

---

## 测试数据明细

| 数据项 | 值 |
|--------|-----|
| Notion 页面 ID | `34d114fc-090c-81b3-8812-fc392c79765e` |
| Asana Project GID | `1214282123649966` |
| Asana Webhook GID | `1214282157104425` |
| WBS 导入 job_id | `4fd8a4e7` |
| WBS 导入耗时 | ~9 分钟（05:23:01 → 05:32:23）|
| Asana 顶层任务数 | 13 |
| Asana L3 子任务数 | 67 |
| Asana L3 null assignee | 37（55%）|
| 测试任务 GID（TC-A06）| `1214282244227772` |
| webhook_events_dedup | 4 → 5（+1）|
| notified_events | 3 → 4（+1）|
| WF-08 执行 ID | 11604 |
| WF-08 延迟 | ~5 秒 |
| active_subscriptions | 73 → 77（+4）|
| WF-01 执行 ID（触发） | 11567 |
| WF-02 错误执行 ID | 11584, 11587 |

---

## n8n API 密钥状态

**测试中发现：** 测试档案提供的 n8n API key（`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`）已过期，返回 `{"message":"unauthorized"}`。所有 n8n 验证通过 SSH + SQLite 直接读取数据库完成。

---

## 验收结论

**PMO Auto V2.2 核心功能可运行，但存在 2 个 P1 缺陷阻碍自动化完整性：**

**可用功能：**
- WF-01 项目初始化：✓（5 分钟内自动触发）
- Asana 项目创建 + Notion Hub 页：✓
- WBS 导入（备用路径）：✓（wbs_success=true）
- Webhook 注册 + 幂等：✓
- 任务完成 → Webhook → WF-08 通知链路：✓（5 秒内）

**待修复缺陷：**
1. **BUG-0425-001（P1）**：WF-02 DNS 隔离，WBS 无法自动触发（需修复 Docker 网络配置）
2. **BUG-0425-002（P1）**：55% L3 任务 assignee=null（REQ-012 延续，待 wbs_to_asana.py 修复）

**下一步建议：**
1. 修复 BUG-0425-001：将 n8n 加入 `ubuntu_pmo_net` 或 WF-02 改用外网 URL
2. 修复 BUG-0425-002：调查 wbs_to_asana.py assignee 映射逻辑，确保全部角色正确映射
3. 修复后重新执行 TC-A02 + PRINCIPLE-001 验证

---

*测试报告由 pmo_test_engineer 自动生成 — 2026-04-25*
