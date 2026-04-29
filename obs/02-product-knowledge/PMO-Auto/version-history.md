---
id: pmo-auto-version-history
type: living
status: published
lang: zh
version: 2.6.0
published_at: "2026-04-27"
updated_at: "2026-04-27"
author: knowledge_engineer
review_by: [synapse_product_owner]
audience: [team_partner]
product: PMO Auto
maintainer: synapse_product_owner
---

# PMO Auto — 版本历史

## 版本总览

| 版本 | 日期 | 类型 | 核心内容 | 验收结论 |
|------|------|------|----------|---------|
| **v2.6.0** | 2026-04-27 | 修复 | BUG-003：WF-12 激活，WBS 导入链路全通 | GA ✓ E2E 全 PASS |
| v2.5.0 | 2026-04-27 | 修复 | BUG-005+006：DE/SA/CDE 邮箱提取 + 团队信息维护回归修复 | GA ✓ 0427C 验收通过 |
| v2.4.0 | 2026-04-27 | 修复 | BUG-001+002：WF-01 邀请成员节点 + WF-08 Webhook 修复 | GA ✓ TC-A01/A03/A04/A05/A06 PASS |
| v2.0.3 | 2026-04-24 | 修复 | WF-05 OOM 修复（n8n runner 堆内存 4096MB）| GA ✓ |
| v2.0.1 | 2026-04-24 | 修复 | SSL 补丁 — pmo-api.lysander.bond HTTPS 上线 | GA ✓ |
| **v2.0.0** | 2026-04-22 | 大版本 | V2 首个 GA — Webhook 全量覆盖 / HMAC 修复 / 幂等去重 | GA ✓ TC-A01~A06 PASS |
| v1.7.0 | 2026-04-22 | 里程碑 | V1 最终版本 — 源码审计差异清零（15条 → 0条）| V1 GA ✓ |

---

## 详细版本记录

### v2.6.0 — 2026-04-27（锁定包：2026-04-28）

**类型**：Bug Fix（P1）
**核心修复**：BUG-003 WF-12 激活

**变更内容**：
- WF-12 (p8tPxmkhMcQPcRMh) 从 inactive → active，webhook path `pmo-wf02-wbs-import` 重新注册生效
- WBS 导入链路全通：WF-01 → WF-11 → pmo-api /run-wbs → wbs_to_asana.py V1.4 → Asana 任务

**验收数据**：
- 测试项目：Singapore Keppel Project [Test Copy - 0427C]
- Notion Page ID：34f114fc-090c-818a-ad76-cae03ff05a89
- Asana GID：1214320092268919
- WBS 导入结果：80 节点（13 主任务 + 67 子任务）
- WF-11 exec：13897，pmo-api job：731503d8

**关联文档**：
- 验收报告：`obs/06-daily-reports/2026-04-27-pmo-auto-bug003-tc-a02.md`
- 锁定包：`C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\_LOCKED_v2.6.0_FULL_20260428\`
- 发布说明：[releases/v2.6.0.md](releases/v2.6.0.md)

---

### v2.5.0 — 2026-04-27

**类型**：Bug Fix（P1 × 2）
**核心修复**：BUG-005 + BUG-006

**变更内容**：
- BUG-005：WF-01 "提取注册表数据" Code Node 补充 deEmail/saEmail/cdeEmail 提取
- BUG-006（回归）：删除 WF-01 "回填注册表链接"节点中 `团队信息维护` 的错误覆写操作

**验收数据**：
- E2E 0427C (2026-04-27T16:05:28Z) 验收通过
- Asana 项目成员：4人（PM + DE + SA + CDE 全部加入）
- 团队信息维护：执行前后均保持"已维护"

**关联文档**：
- 测试报告：`obs/06-daily-reports/2026-04-27-pmo-auto-e2e-rerun-0427C.md`
- 锁定包：`C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\_LOCKED_v2.5.0_20260427\`

---

### v2.4.0 — 2026-04-27

**类型**：Bug Fix（P1 × 2）
**核心修复**：BUG-001 + BUG-002

**变更内容**：
- BUG-001：WF-01 "邀请团队成员加入项目" Code Node 替换为 HTTP Request 节点链（get-team-members-v2 → filter-member-gids-v2 → add-project-members-v2）
- BUG-002：WF-08 connections dict stale key 重命名修复

**关联文档**：
- 测试报告：`obs/06-daily-reports/2026-04-27-pmo-auto-e2e-test-report.md`

---

### v2.0.3 — 2026-04-24

**类型**：Hot Fix（OOM）
**关联需求**：REQ-012-D-01
**修复**：n8n runner 堆内存从默认值提升至 4096MB，解决 WF-05 执行时 OOM Crash
**关联文档**：`obs/06-daily-reports/2026-04-24-wf05-crash-incident.md`

---

### v2.0.1 — 2026-04-24

**类型**：Security Patch
**关联需求**：REQ-010
**修复**：pmo-api.lysander.bond 启用 HTTPS（Let's Encrypt SSL，有效期至 2026-07-23）

---

### v2.0.0 — 2026-04-22（V2 首个 GA）

**类型**：大版本 GA
**关联需求**：REQ-001 / 005 / 009

**核心能力**：
- Asana Webhook 全量覆盖（73 活跃订阅：36 项目 × 2 事件类型）
- HMAC 签名验证修复（36 项目各有独立 secret，多重验证）
- WF-06/WF-08 共享幂等去重机制（webhook_events_dedup 表）
- REQ-009：Asana 目标团队范围可配置化（target_team_gid 写入 config.yaml）
- REQ-001：`POST /webhooks/asana/register-team` 端点
- 凭证集中管理：n8n Credentials Store（httpHeaderAuth），杜绝硬编码
- 子域名独立：pmo-api.lysander.bond

**验收**：TC-A01~A06 全部 PASS
**锁定包**：`C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\_LOCKED_v2.0.0_20260422\`
**关联文档**：`obs/06-daily-reports/2026-04-23-pmo-v200-acceptance-report-ga.md`

---

### v1.7.0 — 2026-04-22（V1 最终版本）

**类型**：里程碑版本（V1 终结）
**关键成就**：V1.7.0 遗留 15 条源码审计差异全部清零，完成从作坊式研发到双轨制的转型
**锁定包**：`C:\Users\lysanderl_janusd\PMO-AI Auto\PMO-AI Auto\_LOCKED_v1.7.0_20260422_102155\`

---

## 版本跳号说明

- **v2.0.2**：跳号保留给 REQ-012-TC-01 方法论升级（无代码变更，未独立打 tag）
- **v2.1.0 ~ v2.3.0**：内部迭代批次，在 v2.4.0/2.5.0/2.6.0 的修复过程中消耗

## 下一里程碑（v2.7.0 候选）

- REQ-012-WBS-QA-001：WBS 全面验证（Notion 表单 → WBS 任务映射完整性验证）
- REQ-002 / 003 / 004：V2.1 backlog 重新评估
- TC-A04 Webhook 注册改善：新项目即时纳入 register-team 覆盖范围
