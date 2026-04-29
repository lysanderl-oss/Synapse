---
title: 博客管线稳定运行保障方案（SLA + 监控 + 灾难恢复）
date: 2026-04-26
objective_id: OBJ-BLOG-PIPELINE-CLOUD
status: review
release_baseline: infra-1.0.6
authors: integration_qa + harness_engineer
---

# 博客管线稳定运行保障方案

> 上下文：OBJ-BLOG-PIPELINE-CLOUD 已 shipped @ infra-1.0.6（云端化、本机仅保留 watcher）。
> 总裁问：之后如何保障稳定运行？
> 本报告 = 实证盘点 + 失效场景识别 + SLA + 监控加固 + 灾难恢复 + 优先级。
> **本报告只评审产出方案，不实际部署任何监控**（按派单约束）。

---

## 一、现有稳定保障盘点（实证）

| # | 类别 | 现有机制 | 文件锚点 | 评估 |
|---|------|---------|---------|------|
| 1 | GitHub Actions cron 触发 | `0 18 * * *` UTC（Dubai 22:00） | `.github/workflows/blog-publish.yml:17` | 漂移 1-3h 是 GH 常态，对天级博客可接受 |
| 2 | Worklog/Publish 重试 | 3 次 retry × 30s sleep | `blog-publish.yml:78-91` | 应对临时 API/网络抖动 |
| 3 | Push 冲突处理 | `pull --rebase` 兜底 + 3 次 push 重试 | `blog-publish.yml:110-117, 133-140` | 已实证（Stage 2 阶段触发过） |
| 4 | 心跳监控（博客） | `blog-heartbeat.yml` Dubai 23:00（publish + 1h） | `.github/workflows/blog-heartbeat.yml:7` | 检查 last_sync 24h 新鲜度，warning/critical 才发 Slack |
| 5 | 心跳监控（情报） | `heartbeat-check.yml` Dubai 13:00 | `.github/workflows/heartbeat-check.yml:6` | 检查 daily.html / action-report.md 产出 |
| 6 | Slack 通知（成功+失败+告警） | WF-09 Unified Notification + `recipient='president'` | `blog-publish.yml:144-172` | 已实证（infra-1.0.6 验收链路打通） |
| 7 | sessions_watcher 增量同步 | 本机 Task Scheduler 每 5 分钟 once 模式 | `scripts/sessions_watcher.py` | 关机时无法跑（场景 A 失效点） |
| 8 | 旧 Task 备份 | `Synapse-WorklogExtractor` XML 留底 | `harness/n8n-snapshots/_archive/` | 90 天可回滚 |
| 9 | concurrency lock | `group: blog-publish, cancel-in-progress: false` | `blog-publish.yml:22-24` | 防并行污染 |
| 10 | timeout 兜底 | publish=30min / heartbeat=5min | 各 workflow | 防 hang 死耗 GH 配额 |

**结论**：**容错栈已经相当完整**，明显缺口集中在"本机 watcher"和"长尾失效场景"两类。

---

## 二、剩余的 6 类失效场景（实证识别）

### 场景 A：本机长期关机（>1 天）
- watcher 不跑 → session 不上传 synapse-sessions
- blog-publish cron 跑了，但 sessions 是旧的 → worklog 空跑（正常退出）
- **当前覆盖**：✅ heartbeat 24h 后 Slack warning（last_sync 陈旧）
- **缺口**：仅 24h 阈值，期间总裁可能不知 worklog 已经空跑了 1-2 天

### 场景 B：本机开机但 watcher Task 失败
- 类似昨日 0x80070002 ENOENT 问题（PATH 不全 / Python 路径漂移）
- last_sync.json 不更新 → heartbeat 24h 后告警
- **缺口**：发现晚（最少 24h），且无 Task 退出码反馈通道

### 场景 C：synapse-sessions 仓库膨胀（GitHub 5/100 GB 限制）
- 当前 727MB（本机副本，云端实测 534 MB）/ 2057 jsonl
- 每日新增估算 ~10-30 MB（假设每天 5-10 个 session × 几 MB）
- **缺口**：触达 GitHub 软上限（5 GB warning / 100 GB hard limit）需要约 X 月，但目前无大小检测，会撞墙才发现

### 场景 D：GitHub Actions 配额耗尽（私有 repo 月 2000 min 免费）
- 当前 cron 估算用量：blog-publish ~10 min × 30 = 300 min；intel-daily/action 各 ~5 min × 60 = 300 min；heartbeat ×2 ~150 min；总和 ~750 min/月，距上限有余裕
- **缺口**：未来加 monitor / build / 多次重试时可能逼近上限，目前无配额监控告警

### 场景 E：lysander-bond Astro 构建失败
- 触发因素：Astro 升级 / 依赖冲突 / 文章 frontmatter 语法错（已在 Stage 2 触发过 desc 换行 bug）
- 用户无感（旧站仍在 Cloudflare Pages 上），但新文章发不出
- **缺口**：lysander-bond 的 build/deploy 失败当前不会回灌到 synapse-ops 的 Slack 通道

### 场景 F：Anthropic API 长时间故障 / Key 失效
- worklog 生成 + publish QA 都依赖 Anthropic API
- 当前 3 次 retry，但 API 长时间宕机仍会失败 → blog-publish 任务红 → Slack critical
- **缺口**：无主动 API 健康预检，每天直接到 cron 时刻才发现

---

## 三、SLA 设计（4 项指标）

按"博客管线作为内部产品"对齐 SLA：

| 指标 | 目标 | 测量方法 | 数据源 |
|------|:---:|---------|--------|
| **每日发布率** | ≥ 95% | `(有候选 day 中实际成功发布的 day 数) / (有候选 day 数)` 30 天滚动 | `scripts/.blog-published.json` + `obs/00-daily-work/` |
| **发布延迟** | < 6 h after Dubai 22:00 | cron 触发到文章 commit lysander-bond 的间隔 | GitHub Actions run timestamp |
| **数据完整性** | 100% | session-to-worklog 覆盖所有 jsonl（无 silent skip） | `scripts/.worklog-processed.json` 对比 sessions repo jsonl 列表 |
| **站点可用性** | ≥ 99.9% | uptime 监控 lysander.bond / 7 天均值 | 外部 uptime 服务（待引入） |

**SLA 不达标响应**：
- 单日异常 → Slack warning（已有）
- 连续 3 日发布率 < 95% → Lysander 触发根因审查
- 数据完整性 < 100% → P0，立刻挂起后续 publish 直至修复

---

## 四、监控加固（4 项）

### 加固 1：watcher 健康自检 + Task 退出码回灌
- **当前缺口**：watcher Task 失败仅本机 Event Log 可见，云端不知
- **加固方案**：
  - watcher 启动时附加 `--ping-on-success` 选项，成功后写 `last_sync.json` 同时（可选）轻量 ping GH Actions repository_dispatch
  - 或更简单：让 heartbeat 阈值从 24h 降到 12h（catch up 周期变快），critical 阈值降至 36h
- **工作量**：1-2 h（仅调阈值）/ 4-6 h（含 ping endpoint）

### 加固 2：synapse-sessions 容量监控
- **当前缺口**：撞墙才发现
- **加固方案**：在 `blog-heartbeat.yml` 内加一步 `du -sh` 检查
  - > 4 GB → warning（GitHub 5GB 软线）
  - > 50 GB → critical（远早于 100GB 硬线，留 P1 处理时间）
  - 同时记录月增长率
- **工作量**：1 h（1 个 step + 1 段 jq 阈值判定）
- **延伸**：超阈值时自动归档老 session 到独立 bucket（P2）

### 加固 3：GitHub Actions 配额监控
- **当前缺口**：用量信息不可见
- **加固方案**：新增 `quota-check.yml` 月初跑一次
  - 调用 `gh api /repos/{owner}/{repo}/actions/cache/usage` + billing API
  - 用量 > 70% → warning，> 90% → critical
- **工作量**：2-3 h（API + Slack 接入）

### 加固 4：Astro build 失败告警（lysander-bond → synapse-ops Slack）
- **当前缺口**：lysander-bond 自己的 build/deploy 失败 silent
- **加固方案**：在 `lysander-bond` 仓库新增（或修改）`build.yml` 末尾加 `if: failure()` 步骤，调用同一 `SLACK_WEBHOOK_N8N` 推 critical
- **工作量**：1-2 h（含 secrets 注入 lysander-bond）

**总工作量估算**：5-12 h（视加固 1 选哪种实现），可在 1-2 个工作日内完成。

---

## 五、灾难恢复手册（4 类故障）

| 故障类别 | 检测信号 | 恢复步骤 | RTO |
|---------|---------|---------|:---:|
| **A. watcher 完全失败 / 本机长期关机** | heartbeat 12-24h 告警 | 1) 远程提醒总裁开机；2) 手动 trigger `Synapse-SessionsWatcher` Task；3) 必要时本机 `python scripts/sessions_watcher.py --once` 一次补齐；4) 手动 `gh workflow run blog-publish.yml` 补当日 | 30 min |
| **B. synapse-sessions 仓库损坏 / 误删** | publish 失败 + Slack critical（checkout 异常） | 1) 本机 `~/.claude/projects` 仍有副本；2) 重新 init repo + force push；3) re-run blog-publish | 1 h |
| **C. blog-publish cron 长期失败（>3 日）** | 连续 Slack critical | 1) Lysander 召集 ai_systems_dev + harness_engineer；2) 看 GH run log 定位根因；3) 修代码 / 升降级依赖 / 调 secrets；4) workflow_dispatch 手动重跑 | 取决于根因（典型 2-6 h） |
| **D. Astro 构建失败 / lysander-bond 站点崩** | 加固 4 后 Slack critical / 总裁手动发现 | 1) `git revert` lysander-bond 到上一 healthy commit；2) Cloudflare Pages 自动重建；3) 后台修真问题；4) 修好后 cherry-pick 文章 | 5 min |

**总裁可在阅读时直接看到 RTO，无需进一步追问。**

---

## 六、推荐执行优先级

### P0（紧急加固，本周内）
- **加固 1（轻量版）**：heartbeat 阈值降至 12h warning / 36h critical（1 h）
- **加固 4**：lysander-bond Astro build 失败告警（1-2 h）
> 理由：这两项目前暴露面最大（watcher 失败、Astro 失败），成本最低。

### P1（本月内）
- **加固 2**：synapse-sessions 容量监控（1 h）
- **加固 1（完整版）**：watcher Task 退出码回灌 / GH repository_dispatch ping（4-6 h）
> 理由：风险曲线随时间上升，但短期不会爆。

### P2（季度内）
- **加固 3**：GitHub Actions 配额监控（2-3 h）
- 站点 uptime 外部监控接入（独立子项目，非本管线 scope）
- session 老归档机制（容量超阈值时自动迁移到 archive bucket）
> 理由：当前距上限有余裕，先完成 P0/P1 性价比更高。

---

## 七、与情报管线 SLA 一致性

博客管线和情报管线本就是"同模式异 payload"，SLA 应保持镜像：

| 维度 | 情报管线 | 博客管线 | 一致性 |
|------|---------|---------|:------:|
| 心跳频率 | 每日 1 次（Dubai 13:00） | 每日 1 次（Dubai 23:00） | ✅ |
| 心跳脚本 | `scripts/intelligence/heartbeat_check.py` | `blog-heartbeat.yml` 内联 jq | ⚠️ 异构（建议 P2 统一） |
| Slack 通道 | `recipient='president'` | `recipient='president'` | ✅ |
| 重试次数 | （查 daily/action workflow） | 3 次 × 30s | ⚠️ 待对齐 |
| 容量监控 | 无（产出小） | 待加（产出大） | N/A |
| timeout | 15 min | 30 min | 合理（payload 不同） |

**建议**：P2 阶段统一心跳脚本到 `scripts/heartbeat_check.py` 通用形态，避免双份维护。

---

## 八、给 Lysander 的一行

✅ 稳定运行方案：**6 失效场景识别 / SLA 4 项 / 加固 4 项（P0×2 + P1×2 + P2×3）/ DR 4 类（最长 RTO 6h）**，待 Lysander 综合后呈报总裁。
