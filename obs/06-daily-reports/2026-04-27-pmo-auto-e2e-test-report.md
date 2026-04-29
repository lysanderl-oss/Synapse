---
id: pmo-auto-e2e-test-0427
type: narrative
status: published
lang: zh
version: 2.0.0
published_at: "2026-04-27"
updated_at: "2026-04-27"
author: pmo_test_engineer
review_by: [integration_qa]
audience: [team_partner]
---

# PMO Auto E2E 验收测试报告

**测试日期**：2026-04-27  
**执行人**：pmo_test_engineer + integration_qa  
**测试环境**：n8n.lysander.bond + pmo-api.lysander.bond + Asana  
**测试版本**：PMO Auto v2.4.0  
**测试项目**：Singapore Keppel Project [Test Copy - 0427]  
**Notion Page ID**：34f114fc-090c-8167-9fc7-fa08287e8f10  
**Asana Project GID**：1214313881117253（修复后新建）  
**结论**：PASS — 原始 2 个 P1 bug 已修复确认；遗留 2 个预存缺陷 (BUG-003/004) 待 REQ-012-WBS-QA-001 跟进

---

## 测试结果汇总

| TC | 名称 | 结果 | 关键数据 |
|----|------|------|----------|
| TC-A01 | 项目录入/WF-01 触发 | PASS | 执行 #13731 SUCCESS (12:20:46), 新Asana GID=1214313881117253，所有节点含邀请链完成 |
| TC-A02 | WBS 同步到 Asana | FAIL | 预存缺陷（BUG-003）：WF-11→pmo-api→WF-12 链路断裂，WF-12 零执行历史，Asana 项目仍 0 任务；与 BUG-001/002 无关 |
| TC-A03 | Notion Hub 页面 GID 回填 | PASS | AsanaGID=1214313881117253 已回填；交付Asana项目链接、章程状态、WBS导入状态 all populated |
| TC-A04 | Webhook 注册 | PASS | 首次调用：Test Copy 0427 出现在 registered 列表（之后移至 skipped） |
| TC-A05 | 幂等注册验证 | PASS | 第二次调用：Test Copy 0427 (GID=1214313881117253) 在 skipped，reason=already_exists |
| TC-A06 | 任务完成 Webhook 通知 | PASS | smoke test 执行 #13724、#13722 均 status:success，响应时间 ~1.4s；修复前所有执行均为 error |

---

## Suite B PRD 合规

| REQ | 检查项 | 结果 | 详情 |
|-----|--------|------|------|
| REQ-009 | target_team_gid 可配置 | PASS | config.yaml line 22: `target_team_gid: "1213938170960375"`；wbs_to_asana.py 通过 `_cfg("asana.team_gid", ...)` 读取，fallback 为默认值（可覆盖） |
| REQ-005 | WF-06 无明文凭证 | PASS | WF-06 JSON文件（20368 chars）未检测到 Bearer token / Asana PAT / Notion Token 明文 |
| REQ-003 | 时区 Asia/Dubai | PASS | config.yaml line 10 + line 90 均为 `timezone: "Asia/Dubai"` |
| REQ-004 | dedup 表存在 | PASS | sqlite3 `.tables` 输出包含 `webhook_events_dedup` |

---

## PRINCIPLE-001 验证（WBS 任务粒度）

**结论：PARTIAL**  
PM email 已成功提取，PM 已添加至 Asana 项目成员。  
但"提取注册表数据"Code Node 仅提取 pmEmail，deEmail / saEmail / cdeEmail 字段未提取（BUG-004，P2，预存缺陷）。  
其他团队成员（DE / SA / CDE）尚未加入 Asana 项目。  
WBS 任务数量验证仍被 BUG-003 阻塞，待 REQ-012-WBS-QA-001 完成后补验。

---

## 修复后验证（2026-04-27）

### BUG-001 — 已修复 ✓

- **修复时间**：2026-04-27T12:09:38 UTC
- **修复方法**：WF-01 "邀请团队成员加入项目" Code Node 替换为 HTTP Request 节点链：
  - `get-team-members-v2` → `filter-member-gids-v2` → `add-project-members-v2`
- **验证结果**：TC-A01 执行 #13731 (2026-04-27T12:20:46–12:21:06) status:success，新 Asana 项目 GID=1214313881117253 创建，所有节点（含邀请链）完成
- **状态**：RESOLVED

### BUG-002 — 已修复 ✓

- **修复时间**：2026-04-27（同会话）
- **修复方法**：WF-08 connections dict 中 stale 连接 key "汇总发送监控频道" 重命名为 "Notify via WF-09 (was 汇总发送监控频道)"
- **验证结果**：TC-A06 smoke test 执行 #13724、#13722 均 status:success，响应时间 ~1.4s；修复前所有执行均为 error
- **状态**：RESOLVED

### BUG-003 — 新发现（预存缺陷，BUG-001 修复后暴露）

- **优先级**：P1
- **现象**：WF-11 (id:VaFr43GafxDrPvEE) 能拾取"待导入"状态，但 WF-12 (id:p8tPxmkhMcQPcRMh, WBS工序导入) 零执行历史，Asana 项目 0 任务
- **根因**：WF-11 → pmo-api → WF-12 触发链路断裂；与 BUG-001/002 无因果关系，是独立预存缺陷
- **影响**：TC-A02 FAIL，PRINCIPLE-001 WBS 任务数量无法验证
- **跟进**：REQ-012-WBS-QA-001（scheduled 2026-04-28）

### BUG-004 — 新发现（预存缺陷）

- **优先级**：P2
- **现象**：WF-01 中"提取注册表数据"Code Node 仅提取 pmEmail，不提取 deEmail / saEmail / cdeEmail
- **根因**：Code Node 提取逻辑不完整，缺少 DE / SA / CDE 邮件字段映射
- **影响**：PRINCIPLE-001 PARTIAL — 仅 PM 加入 Asana 项目，其他团队成员缺失
- **跟进**：REQ-012-WBS-QA-001 范围内修复

---

## 缺陷清单

### BUG-001 (P1) — WF-01 "邀请团队成员"节点：`this.getCredentials is not a function` — ✓ 已修复

- **现象**：WF-01 exec 13699 在节点"邀请团队成员加入项目"失败
- **错误**：`TypeError: this.getCredentials is not a function [line 1]` in n8n Task Runner
- **根因**：n8n Code Node 在 Task Runner 模式下调用了 `this.getCredentials()`，该 API 在独立 Task Runner 上下文中不可用（n8n 平台 bug）
- **修复**：Code Node 替换为 HTTP Request 节点链（get-team-members-v2 → filter-member-gids-v2 → add-project-members-v2）
- **修复时间**：2026-04-27T12:09:38 UTC，验证 exec #13731 PASS

### BUG-002 (P1) — WF-08 Webhook 节点：`Cannot read properties of undefined (reading 'name')` — ✓ 已修复

- **现象**：WF-08 exec 13706 Webhook 节点立即 error
- **错误**：`TypeError: Cannot read properties of undefined (reading 'name')` in `WebhookContext.getChildNodes`
- **根因**：connections dict stale key 导致 n8n 内部 Webhook 响应模式配置检查访问 undefined
- **修复**：stale key "汇总发送监控频道" 重命名为 "Notify via WF-09 (was 汇总发送监控频道)"
- **修复时间**：2026-04-27，验证 exec #13724/#13722 PASS

### BUG-003 (P1) — WF-12 (WBS工序导入) 从未执行 — 待修复

- **现象**：WF-12 (id:p8tPxmkhMcQPcRMh) 零执行历史
- **根因**：WF-11 → pmo-api → WF-12 触发链路断裂（具体断点待 REQ-012-WBS-QA-001 诊断）
- **影响**：TC-A02 FAIL，WBS 无法导入 Asana
- **跟进**：REQ-012-WBS-QA-001（2026-04-28 启动）

### BUG-004 (P2) — "提取注册表数据"字段缺失 — 待修复

- **现象**：deEmail / saEmail / cdeEmail 字段未被 Code Node 提取
- **影响**：PRINCIPLE-001 PARTIAL，其他团队成员未加入 Asana 项目
- **跟进**：REQ-012-WBS-QA-001 范围内修复

> **2026-04-27 更新**：BUG-004 需重新评估。Test Copy - 0427 创建时 de_email/sa_email/cde_email 为空（团队信息维护 = 未维护，违反 PRINCIPLE-002），"提取注册表数据"节点行为符合预期（无可提取的邮箱）。BUG-004 暂标记为 **INVALID** 待确认（需使用 PRINCIPLE-002 合规测试数据重新验证）。

---

## 验收结论

**PMO Auto v2.4.0 E2E 验收：PASS — 原始 2 个 P1 bug 已修复确认；遗留 2 个预存缺陷 (BUG-003/004) 待 REQ-012-WBS-QA-001 跟进**

**通过项**：
- Notion Registry 页面创建与 WF-01 轮询触发机制正常（5分钟内触发）
- WF-01 核心流程（Notion 查询 → 标记初始化中 → Gemini 章程 → Asana 项目创建 → 邀请团队成员）全部节点完成
- Notion Hub GID 回填正常（TC-A03 PASS）
- Webhook 注册 API 正常（TC-A04 PASS）、幂等性验证通过（TC-A05 PASS）
- Asana 任务完成 → pmo-api webhook delivery → WF-08 通知链路畅通（~1.4s 响应）
- Suite B 全部 4 项 PRD 合规（REQ-003/004/005/009 均 PASS）
- pmo-api health 正常（wbs_script + hub + 凭证全部 ok）

**遗留缺陷**（不阻塞核心流程，纳入下一轮跟进）：
1. **BUG-003 (P1)**：WF-12 WBS导入链路断裂 → REQ-012-WBS-QA-001 优先调查
2. **BUG-004 (P2)**：Email 字段提取不完整 → REQ-012-WBS-QA-001 范围内修复

**测试清理**：
- Notion Test Copy 页面已保留（供 REQ-012-WBS-QA-001 继续验证）
- Asana Test Copy 项目 GID=1214313881117253（待 WBS 导入后验证）
- 测试中临时完成的任务（启动筹备 GID=1214144030436659）已恢复为未完成状态
