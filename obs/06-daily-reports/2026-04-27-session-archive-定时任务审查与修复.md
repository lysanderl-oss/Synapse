# 会话归档：定时任务审查与修复
**日期**：2026-04-27
**会话类型**：M 级运营审查 + 多项修复执行
**验收状态**：26/26 PASS

---

## 本次会话完成事项

### 一、定时任务时间偏差审查
- 确认情报管线（6am/8am/10am Dubai）已迁移至 GH Actions，Claude Code Routines 全部 disabled 为预期状态
- 发现 n8n_integration.yaml 中 3am/4am 为迁移前残留文档，已修正

### 二、信息修正（原则落地）
- `n8n_integration.yaml`：workflow_mapping 时间（3am/4am→8am/10am）、event_chains trig_* 标注 deprecated、情报管线归属更新为 GH Actions
- n8n 架构纠正：lysander.bond = Synapse 生产主实例；janusd.io = PMO Monday Auto 专用副本（非迁移替代）
- `PMO-MIGRATION-PHASE1-001` 标题及 notes 纠正为"副本部署"
- `n8n_integration.yaml` 全站域名更新（14 处 lysander.bond→janusd.io，production_base_url 独立字段）

### 三、新建 GH Actions Workflow
| Workflow | 调度 | 职责 |
|---|---|---|
| `hub-daily-sync.yml` | UTC 18:00 = Dubai 22:00 每日 | Notion 工作日志 DB 日报同步（恢复断路的 NotionDailySync）|
| `hr-weekly-audit.yml` | UTC 19:00 Sunday = Dubai 23:00 周日 | HR 周度能力审查（6维度，恢复 disabled Routine）|

### 四、代码修复
- `notion_daily_sync.py`：REPO_ROOT 硬编码 Windows 路径 → `Path(__file__).parent.parent`（P1 修复）
- `notion_daily_sync.py`：Slack webhook URL 硬编码 → `os.environ.get("SLACK_WEBHOOK_N8N", "")`
- `hub-daily-sync.yml`：补入 `SLACK_WEBHOOK_N8N` 环境变量

### 五、产品管线治理
- `hub-daily-sync.yml` 归入 Notion 产品管线（`notion_pipeline_config.yaml` 更新，`hub-health-check.py` 新增日报新鲜度检查）
- `automation-event-chain.md` 新增 GH Actions 调度 SLA 节（4 个 workflow 实际窗口明确标注）

### 六、Backlog 登记
- `INFRA-GHA-NODEJS20-001`：5 个 GH Actions workflow Node.js 20 退役升级，deadline 2026-08-01
- `INFRA-NOTION-SYNC-001`：已 completed（NotionDailySync 迁移至 hub-daily-sync.yml）

### 七、n8n PMO 通知审计
- 全量 Slack 通知点梳理：每日最多 8 条（6am/8am/10am×2/1pm/10pm/10pm/11pm）+ 周日健康报告
- 所有通知均经 WF-09（atit1zW3VYUL54CJ）路由至总裁 DM
- PMO Bot 消息来源确认：WF-01 项目初始化（正常业务通知）

### 八、架构文件
- Memory 新增：`project_n8n_architecture.md`（n8n 双实例架构）

---

## 遗留待办（跨会话跟踪）

| ID | 内容 | 状态 |
|---|---|---|
| INFRA-GHA-NODEJS20-001 | Node.js 20 退役升级（5个workflow）| backlog，2026-08-01 |
| Phase 2 credentials | 总裁自行复制 credentials.mdenc + creds.py 至 Synapse-Mini | pending |
| Multi-Agents System 旧克隆归档 | 待总裁完成 credentials 复制后执行 | pending |
| n8n.lysander.bond WF-10/11/13/14 | Phase 2 迁移（PMO Monday Auto 副本）| 待 Phase 1 稳满 5 工作日后 |
| WF-12 BUG-003 | 另一会话处理中 | in_progress |
