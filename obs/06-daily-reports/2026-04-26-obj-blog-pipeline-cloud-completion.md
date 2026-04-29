---
title: OBJ-BLOG-PIPELINE-CLOUD 完成报告
date: 2026-04-26
objective_id: OBJ-BLOG-PIPELINE-CLOUD
status: completed
release_tag: infra-1.0.6
---

# OBJ-BLOG-PIPELINE-CLOUD 完成报告

## 一、Objective 总览

- **启动**：2026-04-26（总裁观察 Synapse-WorklogExtractor 持续报错 0x80070002，引出博客管线本机锁定问题）
- **完成**：2026-04-26（同日 4 stage 全部完成）
- **流程**：策划 → 基础设施 → workflow 云端化 → 切流监控 → 收尾归档
- **总工作量**：约 6 小时（合并 4 stage 同日 ship）
- **批准权来源**：总裁批准 Lysander 推荐方案 A（参考情报管线 GitHub Actions 模式）后，按 `feedback_goal_driven_authorization` 自主调度执行
- **版本锁定 tag**：`infra-1.0.6`

## 二、战略动机回顾

博客管线启动时 100% 锁本机：

| Layer | 修复前 | 影响 |
|-------|--------|------|
| L1 触发 | Windows Task Scheduler | 仅本机开机时跑，关机即停 |
| L2 抽取 | 本机 Python 扫 .claude/projects/ | 关机无 session 抽取 |
| L3 发布 | 本机 git push | 关机无文章发布 |

**根因**：博客发布是天级 cron，但触发器、抽取器、发布器全部驻留本机。一旦关机，当日博客即丢失。

**解法**：复制情报管线（已在 GitHub Actions cron 上稳定运行）模式，把博客管线的触发 + 处理迁移到 GitHub Actions，本机仅保留轻量 watcher 把 session 同步到云端。

## 三、4 Stage 成果

### Stage 1 — 基础设施（synapse-sessions repo + watcher）

实证基建，先把"session 上云"打通，否则后续 cron 无原料。

| 产物 | 形态 | 关键证据 |
|------|------|----------|
| `lysanderl-glitch/synapse-sessions` 私有 repo | 534MB / 2057 jsonl 首次同步 | commit `d4645e4` |
| `scripts/sessions_watcher.py` | once / daemon / dry-run 三模式 | commit `33149de` |
| `SESSIONS_REPO_TOKEN` 注入 synapse-ops | GitHub Secrets | commit `614afdb` |

**关键决策**：私有 repo（session 含敏感对话）+ GitHub Secrets 隔离访问。

### Stage 2 — GitHub Actions workflow（脚本云端化）

把本机 session-to-worklog + auto-publish-blog 改造成云端可运行版本，同时保持本机向后兼容。

| 产物 | 行数 | 关键改造 |
|------|------|----------|
| `.github/workflows/blog-publish.yml` | cron `0 18 * * *` UTC（Dubai 22:00） | commit `20cfb39` |
| `session-to-worklog.py` 重构 | env / CLI 重定向 | commit `e438006` |
| `auto-publish-blog.py` 重构 | 云端路径 + 本机兼容 | commit `08983a9` |

**真实 bug 修复（4 处，均上线后实测发现）**：

| Commit | Bug | 根因 |
|--------|-----|------|
| `e0ce771` | JSON 解析容错 | 部分 jsonl 含 BOM |
| 同上 | Py3.11 f-string backslash | `\n` 在 f-string 内不允许 |
| `273c9ec` | inbox drain 逻辑 | watcher 重复同步未清理已发布 |
| 同上 | Astro desc 换行 | YAML frontmatter 多行未转义 |

**端到端验证**：
- RUN `24952227885` 全成功
- 3 篇文章已发布 lysander.bond（云端 build + git push 链路打通）

### Stage 3 — 切流 + 监控（本次）

旧 Task 关停 + 新 watcher Task + heartbeat workflow。

| 产物 | 状态 | 证据 |
|------|------|------|
| `Synapse-WorklogExtractor` Task | **disabled**（保留 90 天可回滚） | 备份 `harness/n8n-snapshots/_archive/Synapse-WorklogExtractor_pre-disable.xml` |
| `Synapse-SessionsWatcher` Task | **registered** + Ready | 每 5 分钟跑 `python sessions_watcher.py --once`，python 用绝对路径（避开 0x80070002 PATH 根因） |
| `.github/workflows/blog-heartbeat.yml` | 59 行 | cron `0 19 * * *` UTC（Dubai 23:00），仅 warning/critical 才发 Slack |

**关键决策**：旧 Task 是 disable 不是 delete，保留 90 天可回滚（防止云端管线突发故障无后路）。

### Stage 4 — 收尾归档（本次）

| 产物 | 状态 |
|------|------|
| `VERSION` | infra 1.0.5 → 1.0.6 |
| `CHANGELOG.md` | 新段位置：顶部第 3 行（infra v1.0.6） |
| `agent-CEO/config/active_objectives.yaml` | OBJ-BLOG-PIPELINE-CLOUD status → completed，4 milestones → completed |
| 综合完成报告 | 本文件 |
| git tag | `infra-1.0.6` |

## 四、量化变化

### 关机影响（最核心的指标）

| 维度 | 修复前 | 修复后 |
|------|--------|--------|
| 关机时博客发布 | ❌ 中断 | ✅ 云端正常 cron |
| 关机时 session 同步 | ❌ 中断 | ⏸ 暂存本机，下次开机 catch up |
| 关机时心跳监控 | ❌ 无 | ✅ 云端独立 cron |

**结论**：博客管线 cron 触发 / 抽取 / 发布 100% 云端化。本机仅承担 session 同步（关机时 session 暂存本机，开机后 watcher 一次性 catch up 到 cloud，云端下个 cron 周期自动消费）。

### 工作量

| Stage | 投入时间 | 主要消耗 |
|-------|----------|----------|
| Stage 1 | ~1.5h | repo 初始化 + watcher 写作 + 首次 534MB 同步 |
| Stage 2 | ~3h | workflow + 脚本云端化 + 4 bug 修复 |
| Stage 3 | ~0.5h | 旧 Task disable + 新 Task 注册 + heartbeat |
| Stage 4 | ~1h | 版本锁定 + 综合报告 |
| **总计** | **~6h** | 同日 ship |

### 自动化率

| 链路 | 修复前 | 修复后 |
|------|--------|--------|
| 触发自动化 | 本机 Task（依赖开机） | GitHub Actions cron（独立） |
| 抽取自动化 | 本机 Python（依赖开机） | GitHub Actions runner（独立） |
| 发布自动化 | 本机 git push（依赖开机） | GitHub Actions runner（独立） |
| 监控自动化 | 无 | heartbeat workflow（独立） |
| **本机依赖** | 100% | 仅 session 同步层 |

## 五、二级问题自然消解

OBJ shipped 后，以下 3 个二级问题自然消失：

| 二级问题 | 状态 | 消解方式 |
|----------|------|----------|
| Synapse-WorklogExtractor 0x80070002 | ✅ 消解 | 旧 Task 已 disable，错误日志噪音消失 |
| 博客双源不一致（src/content/blog vs blog/） | ✅ 消解 | 云端版本只走 `src/content/blog/{zh,en}/` 单一路径 |
| 博客 index 列表更新不及时 | ✅ 消解 | 云端 build 自动重生成 index |
| A1 wevtutil 仍需总裁手工 | ⏸ 独立 | 与本 OBJ 无关，独立任务 |

## 六、待您裁示的剩余事项

1. **double-account 扩展（可选）**：
   - 当前 watcher 仅监听 `lysanderl_janusd` 用户的 `.claude/projects/`
   - 若需扩展到 `lysanderl@janusd.com` 账号，需在另一台/同一台机器再装一个 watcher
   - 建议：观察当前单账号稳定 1 周后再决定

2. **A1 wevtutil 命令**（独立问题）：
   - 仍需总裁手工执行（系统级权限，AI 无法代理）
   - 建议：下次会话时执行 `Action Required` checklist 提示

3. **观察期建议**：
   - 接下来 7 天观察 blog-publish.yml cron 实际跑通率
   - heartbeat 若连续 3 天 critical → 触发应急方案：临时恢复旧 Task

## 七、关联 Memory 应用

本次执行严格按以下 memory 准则推进：

| Memory | 应用点 |
|--------|--------|
| `feedback_goal_driven_authorization` | 4 stage 自主推进，仅 stage 完成后向总裁汇报 |
| `feedback_root_cause_first` | 0x80070002 根因实证为 PATH 问题，新 Task 直接用 python 绝对路径 |
| `feedback_req_shipped_version_lock` | 5 步流程：VERSION → CHANGELOG → Objective → 报告 → tag |
| `feedback_secondary_issue_natural_resolution` | 3 个二级问题在 OBJ shipped 时自然消解，未单独立项 |

## 八、完整 Commit 链

| Commit | Stage | 摘要 |
|--------|-------|------|
| `d4645e4` | 1 | synapse-sessions 私有 repo 初始化 |
| `33149de` | 1 | sessions_watcher.py 三模式实现 |
| `614afdb` | 1 | SESSIONS_REPO_TOKEN 注入 |
| `20cfb39` | 2 | blog-publish.yml workflow |
| `e438006` | 2 | session-to-worklog 云端化 |
| `08983a9` | 2 | auto-publish-blog 云端化 |
| `e0ce771` | 2 | bug 修复（JSON BOM + Py3.11 f-string） |
| `273c9ec` | 2 | bug 修复（inbox drain + Astro desc） |
| **本次** | 3+4 | 旧 Task disable + 新 Task 注册 + heartbeat + 版本锁定 |

## 九、版本锁定证据

```
VERSION:
  - infra: 1.0.6 (2026-04-26) — 博客管线云端化（OBJ-BLOG-PIPELINE-CLOUD）

git tag: infra-1.0.6
```

---

**Lysander 总结**：

OBJ-BLOG-PIPELINE-CLOUD 同日 ship，博客管线从本机 100% 锁定 → GitHub Actions 云端 cron。关机不再影响发布，3 个二级问题自然消解，监控 + 回滚通道齐备。infra v1.0.6 锁定，Objective 归档完成。
