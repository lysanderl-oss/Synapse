# Synapse Changelog

## [pmo-auto 2.4.0] - 2026-04-26

### Fixed
- BUG-V24-001: `_pending_*` 幽灵行清理 — 握手回调修复（反查真实 project_gid），新增 `POST /webhooks/asana/cleanup-pending` 端点，清理存量 39 条占位行
- BUG-V24-002: Archived 项目订阅同步下线 — 新增 `POST /webhooks/asana/sync-archived` 端点，将非活跃 Asana 项目的订阅标记 active=0
- BUG-V24-003: /health、/coverage、Dashboard 统计排除 pending 行 — active_subscriptions 从虚报 77 修正为真实活跃数
- BUG-V24-004: WF-09 IF 节点 Destination node not found — 节点重命名后 connections 引用未同步，已修复并同步 workflow_history 缓存

### Verified
- /coverage active 数字 = Asana 团队真实活跃项目数（±2）
- WF-09 Synapse-Audit-Webhook-Coverage 激活，下次触发：2026-04-27 05:05 Dubai

## [ops] - 2026-04-26

### 紧急运维修复（不构成 REQ shipped，仅运维变更归档）

**今日早些时候 Lysander 自主执行的 5 项紧急修复**，与 OBJ-BLOG-PIPELINE-CLOUD（infra v1.0.6）并行：

**A1 — Task Scheduler Operational 日志启用**
- 原计划：Lysander 自主执行 wevtutil set-log
- 实际：需 Administrator 权限，子 Agent 无法获得
- 总裁 2026-04-26 当日手动执行 `wevtutil set-log Microsoft-Windows-TaskScheduler/Operational /enabled:true`

**A2 — 04-25 work-log 补跑**
- 子 Agent 实证发现真凶：session-to-worklog.py 的 file mtime 过滤错误
- 跨日长会话 session 文件 mtime 是次日 → 全部被错误排除 → minimal log
- 修复：mtime 过滤 → 内部 timestamp 字段过滤；同时支持双账号扫描
- 04-25 真实 session = 4 长会话 / 3,410 条消息（不是 0）
- 04-25 三篇博客补发：`/blog/ai-session-time-awareness-illusion`、`/blog/fact-ssot-meta-rule-for-ai-agent-systems`、`/blog/n8n-unified-slack-notification-routing`
- 关联 commits: `08ad784`（mtime 修复）+ `fa664f6`（tracking JSON 对齐 _published/）

**B1 — heartbeat-check cron 时间调整**
- 原 `0 7 * * *` UTC（intel-action 漂移可能未完成时就告警）
- 改为 `0 9 * * *` UTC（容纳漂移）
- 关联 commit: `1a39aec`

**B2 — intel-daily.yml push 加 retry**
- 原 `git push ... || echo skip`（吃错）
- 改为 3 次 retry + pull rebase 兜底
- 关联 commit: `1a39aec`

**C1 — 删除 5 个 0x800700C1 长期失败 Windows Task**
- CalendarSync / DailyIntelligence / DailyReview / IntelligenceAction / TaskAutoResume
- 之前 P2-B 已确认从未成功，今日清理
- 关联 commit: `1a39aec`

**触发记录的 feedback memory（今日新增）**：
- `feedback_session_time_awareness.md`（会话连续 ≠ 时间连续）
- `feedback_dual_account_session.md`（双账号 session 扫描）

**不打 git tag**：以上属运维变更，无 REQ shipped。本段仅作运维日志归档。

---

## [infra v1.0.7] - 2026-04-26

### OBJ-INTEL-LOOP-CLOSURE shipped — 情报管线全自动闭环

**问题陈述**（总裁 2026-04-26 揭露）：
- "为什么只看到情报日报，没看到升级动作？"
- "80% 闭环什么意思？还需要我参与决策吗？"

**根因实证**：情报管线 4 步设计（发现→评估→执行→报告）实际只跑前 2 步：
- intel-action 只生成 markdown，从未写回 active_tasks.yaml
- 7 天内 12 条 INTEL 任务 ID 实际入库 = 0 条
- 闭环 L2→L3 完全断裂

**修复方案**（2 阶段）：

**阶段 1（commit 25d5b98）— 档 A3 基础闭环（80%）**
- action_agent.py 新增 append_intel_tasks_to_active_tasks_yaml + notify_intel_tasks_added
- 评估完成自动 append 到 active_tasks.yaml (status=approved-pending-dispatch)
- WF-09 Slack 通知 #ai-agents-noti
- 派单/执行权仍归 Lysander 主对话审查
- 验证：RUN 24959552361 写入 7 条 INTEL-20260427-001~007

**阶段 2（commits 7f50337 / dab3751 / b5e7f52）— D2 全自动消化（100%）**
- CLAUDE.md 【0.5】②.5 步：Pending-Dispatch INTEL 自动 review
- active_objectives.yaml dispatch_rules 5 规则 + 4 safeguards
- action_agent.py _normalize_rice 4 级 fallback（修 P0 数据契约缺陷）
- 7 条 INTEL backfilled rice.score
- D2 literal 模拟 = realistic 完全一致

**总裁参与度变化**：
- 修复前：100%（每条情报需主动 review）
- 阶段 1 后：50%（Lysander 主对话顺手处理）
- 阶段 2 后（infra-1.0.7）：**0%**（每次会话开场自动消化）

**关联 commits**：
- `25d5b98` action_agent 入池
- `1902496` workflow auto-commit
- `7f50337` D2 配置落地
- `dab3751` D2 模拟验证（暴露 P0 数据契约缺陷）
- `b5e7f52` 数据契约修复
- 本次 commit

**关联文档**：
- 闭环审计：`obs/06-daily-reports/2026-04-26-intel-pipeline-evolution-loop-audit.md`
- 全自动方案重评估：`obs/06-daily-reports/2026-04-26-intel-loop-full-auto-evaluation.md`
- D2 设计：`obs/06-daily-reports/2026-04-26-d2-auto-dispatch-design.md`
- D2 验证：`obs/06-daily-reports/2026-04-26-d2-simulation-verification.md`

**新增 feedback memory**（4 条今日累积反模式防线）：
- `feedback_doc_citation_must_verify` — 引用文档必须 Read 验证
- `feedback_silent_success_anti_pattern` — HTTP 200 ≠ 业务生效
- `feedback_session_time_awareness` — 会话连续 ≠ 时间连续
- `feedback_dual_account_session` — 双账号 session 扫描

**git tag**: `infra-1.0.7`

---

## [infra v1.0.6] - 2026-04-26

### OBJ-BLOG-PIPELINE-CLOUD shipped — 博客管线云端化

完整 4 stage 同日完成（约 6 小时），博客管线从本机 100% 锁定 → GitHub Actions 云端 cron。

**Stage 1 基础设施**（commits d4645e4 / 33149de / 614afdb）：
- 创建 `lysanderl-glitch/synapse-sessions` 私有 repo（534MB / 2057 jsonl 首次同步）
- `scripts/sessions_watcher.py` 本机增量同步（once / daemon / dry-run）
- `SESSIONS_REPO_TOKEN` 注入 synapse-ops

**Stage 2 GitHub Actions workflow**（commits 20cfb39 / e438006 / 08983a9 / e0ce771 / 273c9ec）：
- `.github/workflows/blog-publish.yml` cron 0 18 * * * UTC（Dubai 22:00）
- session-to-worklog.py / auto-publish-blog.py 云端化（env / CLI 重定向，本机向后兼容）
- 4 处真实 bug 修复（JSON 解析容错 / Py3.11 f-string backslash / inbox drain / Astro desc 换行）
- 端到端验证：RUN 24952227885 全成功，3 篇文章已发布 lysander.bond

**Stage 3 切流 + 监控**（本次 commit）：
- 旧 Synapse-WorklogExtractor Task：disabled（备份 _archive/，关停 0x80070002 噪音）
- 新 Synapse-SessionsWatcher Task：每 5 分钟同步本机 session
- `.github/workflows/blog-heartbeat.yml`：每日 23:00 Dubai 检查 last_sync 新鲜度

**Stage 4 收尾归档**（本次）：
- VERSION → 1.0.6
- active_objectives: OBJ-BLOG-PIPELINE-CLOUD completed
- 综合完成报告归档

**关机影响消解**：博客管线 cron 触发 / 抽取 / 发布 全部云端运行，本机仅 watcher 同步 session（关机时 session 暂存本机，下次开机 catch up）。

**自然消解的二级问题**：
- ✅ Synapse-WorklogExtractor 0x80070002 → 旧 Task 已 disable
- ✅ 博客双源不一致 → 云端版本只走 src/content/blog/ 路径（auto-publish-blog 已重构）
- ✅ 博客 index 列表更新 → 云端 build 自动处理
- ⏸ A1 wevtutil 仍需总裁手工（独立问题）

**git tag**: `infra-1.0.6`

## [pmo-auto 2.3.0] - 2026-04-25

### Fixed
- BUG-0425-001: WF-02 Docker DNS 隔离 — URL 从 `http://pmo-api:8088` 改为 `https://pmo-api.lysander.bond`，解决 n8n 容器无法解析内网 hostname 问题；同步更新 n8n SQLite workflow_history，确保执行快照与 workflow_entity 一致
- BUG-0425-002: WBS 导入 assignee 全角色映射 — wbs_to_asana.py/wbs_trigger.py 新增 DE/SA/CDE/Sales 角色 Asana GID 映射；pmo_api/main.py 修复 `_run_pipeline` 未传 DE/SA/CDE 邮箱给子进程

### Verified
- PRINCIPLE-001: WBS 正向链路任务粒度校验通过，L2/L3 assignee 覆盖率均为 100%（超过 80% Pass 标准）
- BUG-0425-001: WF-02 execution `11649` status=success（无 DNS 错误）
- BUG-0425-002: Asana 项目 `1214282511396882` L2=100% (13/13), L3=100% (67/67)

## [infra v1.0.5] - 2026-04-25

### OBJ-N8N-WORKFLOW-AUDIT 完整 shipped — n8n workflow 全量梳理 + Slack 通知路径统一

总裁要求按"分析→评估→方案评审→执行"流程，全 4 阶段完成。

**P0-A — Slack 路由修复**（commit `f455e1b`）：
- 问题：daily/action/resume 三个调用方默认 `SLACK_DEFAULT_RECIPIENT='U0ASLJZMVDE'` 走 WF-09 fallback → 总裁 DM
- 修复：默认改为 `'president'`，命中 WF-09 命名分支 → channel `C0AV1JAHZHB` (#ai-agents-noti)
- 验证：RUN `24924636231` / WF-09 Exec `11640` `recipient='president' channel=C0AV1JAHZHB ok=true`

**P1-A — WF-09 重命名 + WF-06/08 改造**（commit `42a4d9a`）：
- 重命名 `203fXfKkfqD1juuT`：WF-09 Webhook 未覆盖告警 → **Synapse-Audit-Webhook-Coverage**
- WF-06 / WF-08 直推 Slack 节点改为 HTTP→WF-09 Unified Notification
- WF-06/08 内部 per-user DM 逻辑保留（待 WF-09 扩展支持 `recipient='email:xxx'` 后再统一）

**P2-B — 垃圾债务处置 + 断裂调研**（commit `fa4f8f6`）：
- 类 1 自动删 6 条（test/My workflow 等明显废弃）→ archive 入 `harness/n8n-snapshots/_archive/`
- 类 2 [archived] 重命名 8 条（手工）+ 4 条 n8n 原生 isArchived=true
- 类 3 用途不明 6 条（含 Synapse-WF1/WF5 断裂态）→ 待呈报总裁决策
- 4 条 Active error 根因定位：WF-02 Notion filter / WF-04 WF-05 Notion 授权 / WF-06 Code Set 数据格式
- workflow 总数 47 → 41

**P3-A — 命名规范化**（commit `3cd4d50`）：
- 制定 `obs/03-process-knowledge/n8n-workflow-naming-conventions.md`
- 编号空间：WF-01~09 PMO / WF-10~29 业务副路 / 30~99 预留 / Synapse-*/Harness-* 不编号
- 5 个冲突 workflow 重命名（WF-02/04/05 副路改 WF-10~14）

**治理产出**：
- 47 → 41 workflow（-6 删除，-12 archived 标记）
- WF-09 前缀冲突解决
- WF-02/04/05 编号冲突解决
- 命名规范文档归档
- harness/n8n-snapshots/ 同步全部最新状态

**git tag**：`infra-1.0.5`

**关联 commits**：`f455e1b` + `42a4d9a` + `fa4f8f6` + `3cd4d50` + 本次

---

## [infra v1.0.4] - 2026-04-25

### REQ-INFRA-005 shipped — n8n WF-09 multiline body 治本 + 治理升级

**REQ-INFRA-005**：n8n WF-09 Unified Notification (`atit1zW3VYUL54CJ`) 处理含换行符 body 时 HTTP 500 "Bad control character"。

**Root Cause**（实证，非猜测）：
Send Slack 节点旧配置使用 raw JSON 模板模式，把 `{{ $json.body }}` 直接拼接进 JSON 模板字符串。body 含真实 `\n` (0x0A) 时违反 JSON 语法，触发 `Bad control character at position 126` 错误。

**Root Fix**（治本）：
2026-04-25 04:55:44 UTC 由**总裁本人**手动把 Send Slack 节点改为 **keypair 模式**。
keypair 模式下 n8n 自动 `JSON.stringify(value)` 安全转义 `\n` → `\\n`，根本消除 bug。
（验证：诊断子 Agent 8 次重放原失败 payload，全部 `status=200, ok=true`）

**Lysander 加固 + 治理升级**：

1. **方案 A — 恢复富文本 body**（commit `67d1498`）
   - 撤回 commit `8f3d354` 的过度防御简化
   - daily_agent / action_agent / resume_agent 恢复含 `\n` + 路径 + emoji 的富文本通知
   - 验证 RUN `24923619076` body_len=109 在 keypair 模式下成功送达

2. **方案 C — n8n workflow JSON 纳入 git 治理**（commit `1a3ba10`）
   - 新增 `scripts/n8n/export_workflows.py` 拉取所有 active workflow + 标准化
   - 47 个 workflow JSON 基线入库 `harness/n8n-snapshots/`
   - 新增 `.github/workflows/n8n-snapshot.yml` cron Dubai 05:00 每日 sync
   - 防止再次"会话外静默修改"导致审计漏洞

3. **方案 D — 术语统一**（commit `921733e`）
   - 项目文档 "WF-9" → "WF-09 Unified Notification (`atit1zW3VYUL54CJ`)" 全称
   - 避免与 `WF-09 Webhook 未覆盖告警` (`203fXfKkfqD1juuT`) 混淆
   - 15 个文件 / 69+ 处统一

4. **知识沉淀**：
   - `obs/03-process-knowledge/n8n-http-request-json-body-best-practice.md` — n8n HTTP Request 节点必用 keypair 模式（禁 raw JSON 模板）
   - `feedback_root_cause_first.md` memory — 反"猜测+绕过"模式
   - `feedback_canonical_naming.md` memory — 外部资源强制全名+ID 双重锚定

**git tag**：`infra-1.0.4`

**关联 commits**：`67d1498` + `1a3ba10` + `921733e` + 本次 commit

**版本号说明**：本周期与 `50a819b` (infra v1.0.3) 在同一日并行交付。v1.0.3 处理 HMAC/recipient/UTF-8 链路修复并已打 tag；本次 v1.0.4 为治理与知识沉淀升级，因此独立编号，避免覆盖既有发布。

---

## [infra v1.0.3] - 2026-04-25

### Fixed
- WF-09 HMAC Validate 节点：throw 改为 return error json，消除 HTTP 500 错误（P0）
- WF-01~WF-07 recipient 字段：`C0AJN5PN1G8` → `president`，通知正确路由至总裁 DM（P1）
- WF-09 Send Slack 节点：`specifyBody: json` expression 改为 `keypair` + `Content-Type: application/json; charset=utf-8`，消除中文乱码
- `scripts/planx_migrate.ps1`：`$CHANNEL` 更新为 `U0ASLJZMVDE`，脚本模板与生产配置对齐（P2）

### Changed
- WF-09 Parse Recipient：`president` → `C0AV1JAHZHB`（#ai-agents-noti 频道），替代 Bot DM
- PLAN-X-001 任务：已关闭（遗留自 2026-04-23）

**关键修复**：
- P0：HMAC 验证失败时 HTTP 500 → 200，消除 WF-09 调用链阻断
- P1：WF-01~07 全链路通知路由修复，解决历史 `channel_not_found` 误路由
- 中文编码：keypair 模式覆盖 n8n multiline body 处理 bug（见 REQ-INFRA-005）

**git tag**：`infra-1.0.3`

---

## [infra v1.0.2] - 2026-04-24

### P1 Slack 通知系统性修复

**扩展自 infra v1.0.1（REQ-INFRA-004）的系统性延伸**

**问题**：
infra v1.0.1 首次发现 n8n WF-09 Parse Recipient 节点期望标准 payload 契约 `{recipient, title, body, source, priority}`，但调用方发送 `{"text": "..."}` 导致 `recipient=''` → Slack channel_not_found。首次修复只处理了 `heartbeat_check.py`，其他 3 个情报管线 agent（daily / action / resume）同样缺陷未解决。

**根因**：
Slack 通知契约未作为共享规范，各 agent 自行实现，导致相同 bug 多处复现。

**修复**：
- `scripts/intelligence/shared_context.notify_slack()` 升级签名：
  - Old: `(webhook_url, message, channel=None)`
  - New: `(webhook_url, title, body, source, priority="info", recipient=None)`
- 响应体校验 `"ok":true`（防 HTTP 2xx + Slack not ok 假阳性）
- 3 个 agent 调用方全部迁移到标准契约：
  - daily_agent.py: source=intel-daily
  - action_agent.py: source=intel-action
  - resume_agent.py: source=task-resume
- 保留 `notify_slack_legacy()` shim 向后兼容

**验证**：
- py_compile 4 文件通过
- heartbeat-check（已用标准契约）Slack 实际送达总裁 DM（D0AUZENMGMS, ok:true）
- 其他 3 管线待下次 cron 触发验证

**关键 commits**：
- 644730f — heartbeat_check.py 首次修（REQ-INFRA-004 首次 shipped）
- 9739baa — 系统性扩展至 3 agent（REQ-INFRA-004 extended shipped）

**git tag**：`infra-1.0.2`

---

## [pmo-auto v2.0.3] - 2026-04-24

### P0 缺陷修复 — WF-05 批量分配 Assignee 崩溃

**问题**：WF-05 在 111 任务的 WBS 项目上触发 n8n task-runner disconnect（OOM），仅完成 44/111 分配即崩溃，Registry 未回写 `WF05已执行=true` 导致重入循环。

**发现路径**：
- REQ-012 WBS 专项验证今日从 2026-04-28 提前启动
- 总裁诊断：Test Copy 项目"团队信息维护"未标注导致 WF-05 未触发
- product_manager 标【已维护】后 WF-05 触发，暴露生产 OOM 缺陷

**修复方案**：n8n docker compose 注入环境变量
- `N8N_RUNNERS_MAX_OLD_SPACE_SIZE=4096`
- `NODE_OPTIONS=--max-old-space-size=4096`

**验证**：exec `10721` (2026-04-24T08:35 UTC) 成功处理 **111/111 items**，Asana 测试项目 13/13 顶层任务 100% assignee 分配。

**root cause**：Node.js 默认堆上限不足，非代码逻辑缺陷。SplitInBatches 降级为 P2 加固候选。

**紧急阻断历史**：07:40 UTC exec 10687 崩溃 → Lysander 派单 product_manager 回滚"团队信息维护"=未维护 → 重入阻断 → 修复部署后重新触发验证通过。

**证据**：
- 事件文档：`obs/06-daily-reports/2026-04-24-wf05-crash-incident.md`
- 测试计划：`obs/06-daily-reports/2026-04-24-req-012-wbs-test-plan.md`

**git tag**：`pmo-auto-2.0.3`

---

## [infra v1.0.1] - 2026-04-24

### P1 基础设施修复 — credentials.mdenc 凭证库重建

**问题**：主密码 `Liuzy****` 解密成功，但解密后 JSON 损坏（`"Google AI Studio"` key 末尾分隔符粘连：`"KEY:"VAL"` 应为 `"KEY": "VAL"`）。creds.py list/get 无法工作，子 Agent 依赖项目文档 Token fallback（安全隐患）。

**发现路径**：REQ-012 诊断过程中，product_manager 取 NOTION_TOKEN 失败，手动 fallback 发现凭证库损坏。

**修复动作**：
- 正则修复 JSON 分隔符粘连
- 新 iv/salt 重新加密
- 补录历史未入库 Token（NOTION_TOKEN / ASANA_PAT / N8N_API_KEY），Token 总数 11 → 13
- 清理 4 条明文 Token fallback 路径（n8n-wf-migration-status.md / plan-x-task-snapshot.md / GA 报告 v2 / planx_migrate.ps1）

**验证**：`creds.py list -p 'Liuzy****'` 返回 13 个 key，抽样 get 全部成功。

**遗留**：`logs/` 目录历史 commit 含 Token 痕迹（建议 REQ-INFRA-002 git history 清洗，非紧急）。

**git tag**：`infra-1.0.1`

---

## [pmo-auto v2.0.1] - 2026-04-24

### SSL 补丁

- REQ-010 shipped: pmo-api.lysander.bond DNS A 记录 + Let's Encrypt SSL 证书签发
- HTTPS 端点上线：https://pmo-api.lysander.bond/webhooks/asana/health
- 证书有效期至 2026-07-23，certbot 自动续期已启用
- DNS 由总裁在 DNSPod 控制台手动添加（价值选择路径）
- SSL 由 harness_engineer 子 Agent 通过 SSH certbot 签发

**证据：** `obs/06-daily-reports/2026-04-24-product-committee-execution-report.md`
**git tag：** `pmo-auto-2.0.1`

---

## [pmo-auto v2.0.0-ga] - 2026-04-23

### PMO Auto V2.0 正式发布（GA）

**验收结论：** 6/6 TC PASS（TC-A01~A06），总裁批准通过，进入生产运行。

**新增能力：**
- Webhook 全量活跃项目覆盖（72 活跃订阅 = 36 项目 × 2 事件类型），取代 60min 轮询
- Asana → n8n → pmo-api → WF-08 → Slack DM 端到端实时通知链路
- 项目 Hub 页面自动生成（Notion）

**缺陷修复：**
- D-01: WF-06/WF-08 Code 节点凭证 API 从 getCredentials 迁移至 requestWithAuthentication（n8n task runner sandbox 兼容）
- D-02: WF-01 Asana 项目 GID 字段清空修复（filter is_empty 正确触发）
- D-03: pmo-api nginx 反代配置（HTTP 就绪，SSL 待 DNS）
- D-04: WF-06 URL team GID 采用 $vars.ASANA_TEAM_GID || fallback 模式

**遗留项（V2.1 backlog）：**
- REQ-010 (P2): pmo-api.lysander.bond DNS + SSL
- REQ-011 (P3): WF-06 ASANA_TEAM_GID 迁至 n8n Variables
- REQ-012 (P1): WBS WF-02~WF-05 专项验证

**证据：** `obs/06-daily-reports/2026-04-23-pmo-v200-acceptance-report-ga.md`
**git tag：** `v2.0-ga`

---

## v1.0.0 — First Public Release (2026-04-12)

Synapse AI Team Operating System 正式发行版。
44 Agents × 14 Skills × 4-level decision system × CEO Guard enforcement。

### Core System
- **Harness Engineering 方法论**：5原则框架（Guides+Sensors双保险、执行链、角色分离、四级决策、能力审计）
- **CLAUDE.md Harness Configuration**：完整 CEO 约束 + 执行禁区 + 派单规范
- **四级决策体系**：L1 自动 → L4 总裁，95% 决策不上报
- **执行链 v2.0**：目标→方案→派单→执行→QA→交付 强制六步流程

### CEO Guard（对话控制机制）
- `.claude/settings.json`：PreToolUse/PostToolUse hooks 技术强制
- `scripts/ceo-guard-pre.js`：审计日志 + 上下文提醒注入
- `scripts/ceo-guard-post.js`：异步执行完成记录
- CLAUDE.md 违规模式识别表 + 工具白/黑名单

### 44 Agents × 7 Teams
- **Graphify**（6人）：战略分析、情报、进化引擎（evolution_engine）
- **Harness Ops**（4人）：Harness 配置、AI 系统开发、QA
- **RD**（5人）：研发、架构、数据
- **Content Ops**（6人）：内容生产、视觉设计
- **Growth**（4人）：增长、品牌
- **OBS**（4人）：知识库、文档
- **Butler**（7人）：PMO、交付、个人助理

### 14 Skills
`/dispatch` `/qa-gate` `/retro` `/knowledge` `/intel` `/graphify`
`/dev-plan` `/dev-qa` `/dev-review` `/dev-secure` `/dev-ship` `/daily-blog`
`/synapse` `/hr-audit`

### HR 管理系统
- Agent 入职审批流程（能力评分 ≥ 90 合格）
- 能力描述质量标准（A/B/C 三级，B 级以上合格）
- 定期自动审计 `audit_all_agents()`
- evolution_engine：自进化闭环协调 + GAP 分析

### 每日自动化管线
- 情报日报（搜索→分析→HTML→推送）
- 情报行动管线（建议评估→执行→报告）
- 任务恢复 Agent（active_tasks.yaml 跨会话续接）

### Distribution
- `build-distribution.py`：7类去个人化规则，0 残留验证
- `scripts/templates/`：个性化配置模板
- `synapse.config.yaml`：用户配置入口
- 升级机制：`升级 Synapse` 一句话完成，API：`https://lysander.bond/synapse/version.json`

---

*Built with Claude Code · Harness Engineering by Synapse-PJ*
