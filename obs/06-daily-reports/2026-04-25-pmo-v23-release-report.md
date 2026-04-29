# PMO Auto V2.3 发布验收报告

**日期**: 2026-04-25  
**执行者**: harness_engineer + integration_qa 联合小组  
**版本**: pmo-auto-2.3.0  
**结论**: V2.3 PASS

---

## 1. Docker 重建结果

| 步骤 | 结果 |
|------|------|
| SCP wbs_to_asana.py | OK |
| SCP wbs_trigger.py | OK |
| SCP pmo_api/main.py（补丁：DE/SA/CDE 邮箱传参修复）| OK |
| `docker build -t ubuntu-pmo-api:v2.3` | OK — sha256:db27f799 |
| 容器重启（stop → rm → run） | OK — container ID: e017bb3b |
| `/health` 响应 | `{"status":"ok","active_jobs":0}` |
| `/dashboard` HTTP | 200 |

**镜像**: `ubuntu-pmo-api:v2.3`  
**挂载**: `/home/ubuntu/pmo-data:/data`  
**环境变量**: `PMO_API_DB_PATH=/data/pmo_api.db`

---

## 2. BUG-0425-001 验证 — WF-02 DNS 修复

**根因**: n8n workflow_history 中存储了旧版执行快照（URL: `http://pmo-api:8088/run-wbs`），
即使 workflow_entity.nodes 已更新，schedule trigger 仍使用缓存快照执行，导致 EAI_AGAIN DNS 错误。

**修复操作**:
1. 更新 workflow_entity.nodes → `https://pmo-api.lysander.bond/run-wbs` ✅
2. 通过 Python sqlite3 直接更新 n8n SQLite workflow_history.nodes（version `16ed82ac`）✅
3. 重启 n8n 容器（ubuntu-n8n-1）刷新内存缓存 ✅

**验证结果**:

| Execution ID | 时间 | Status |
|---|---|---|
| 11631 | 06:15 | error (DNS — 旧快照) |
| 11634 | 06:20 | error (DNS — 旧快照) |
| 11637 | 06:25 | error (DNS — 旧快照) |
| 11643 | 06:30 | error (DNS — n8n重启前) |
| 11646 | 06:35 | error (DNS — 数据库更新前) |
| **11649** | **06:40** | **success** ✅ |

**BUG-0425-001**: PASS — WF-02 execution 11649 status=success，URL=`https://pmo-api.lysander.bond/run-wbs`

---

## 3. BUG-0425-002 验证 — WBS Assignee 全角色映射

**修复范围**:
- `wbs_to_asana.py`: 新增 `--de-email / --sa-email / --cde-email / --sales-email` 参数，构建 role_to_gid 映射
- `wbs_trigger.py`: 新增从 Notion 页面属性提取 DE/SA/CDE 邮箱并传给子进程
- `pmo_api/main.py`: 修复 `_run_pipeline` 未将 de_email/sa_email/cde_email 传给 wbs_cmd（额外发现的缺陷）

**测试项目**: Singapore Keppel Project [Test Copy - 0425-fix-v2]  
**Notion Page ID**: `34d114fc-090c-81b7-bb2c-e141619bc616`  
**Asana Project GID**: `1214282511396882`

**角色 GID 映射验证**:
| 角色 | 邮箱 | Asana GID |
|------|------|-----------|
| PM | lysanderl@janusd.com | 1213400756695149 |
| DE | spikez@janusd.com | 1213899533220604 |
| SA | rosaw@janusd.com | 1213845226833073 |
| CDE | suzyl@janusd.com | （已找到） |

**Assignee 覆盖率**:

| 层级 | 总数 | 有 Assignee | 覆盖率 | Pass 标准 |
|------|------|-------------|--------|-----------|
| L2 任务 | 13 | 13 | **100%** | ≥80% ✅ |
| L3 子任务 | 67 | 67 | **100%** | ≥80% ✅ |

**BUG-0425-002**: PASS — L2/L3 assignee 覆盖率均为 100%（较修复前 0%/45% 大幅提升）

---

## 4. 版本锁定操作记录

### Synapse-Mini 仓库

| 文件 | 变更 |
|------|------|
| `pmo-auto/VERSION` | 2.2.0 → 2.3.0，新增 v2.3.0 历史注释 |
| `CHANGELOG.md` | 新增 `[pmo-auto 2.3.0] - 2026-04-25` 章节 |
| `obs/02-product-knowledge/requirements_pool.yaml` | REQ-012 status=shipped, last_release=pmo-auto-2.3.0 |

### PMO-AI Auto 仓库

| 文件 | 变更 |
|------|------|
| `wbs_to_asana.py` | BUG-0425-002: 新增 DE/SA/CDE/Sales 角色邮箱参数 |
| `wbs_trigger.py` | BUG-0425-002: 新增传递 de_email/sa_email/cde_email 给子进程 |
| `pmo_api/main.py` | 修复 `_run_pipeline` 未传 DE/SA/CDE 邮箱给 wbs_cmd |
| `n8n-workflows/WF-02_WBS导入.json` | BUG-0425-001: URL 从 `http://pmo-api:8088` 改为 `https://pmo-api.lysander.bond` |

Git commit hash 及 tag 见下文。

---

## 5. 最终结论

**V2.3 PASS**

| 验收项 | 结果 |
|--------|------|
| Docker 重建 ubuntu-pmo-api:v2.3 | PASS |
| /health 响应正常 | PASS |
| BUG-0425-001: WF-02 DNS 修复，execution success | PASS |
| BUG-0425-002: L2 assignee 覆盖率 100% | PASS |
| BUG-0425-002: L3 assignee 覆盖率 100% | PASS |
| VERSION 文件更新至 2.3.0 | PASS |
| CHANGELOG 更新 | PASS |
| requirements_pool.yaml REQ-012 shipped | PASS |
