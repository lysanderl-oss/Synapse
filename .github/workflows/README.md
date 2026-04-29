# GitHub Actions Workflows — Synapse 情报管线

本目录承载 Synapse Q2 情报管线的 **GitHub Actions 编排层**。Week 1 为骨架阶段（`workflow_dispatch` 手动触发），Week 2 验证通过后启用 `schedule` cron 自动编排。

## Workflow 清单

| 文件 | 用途 | 触发方式（Week 1） | 触发方式（Week 2） | 超时 |
|------|------|------------------|------------------|------|
| `intel-daily.yml`  | 生成每日情报日报 HTML → commit `obs/06-daily-reports/YYYY-MM-DD-intelligence-daily.html` | workflow_dispatch | cron `0 4 * * *`（UTC 04:00 = Dubai 08:00） | 15 min |
| `intel-action.yml` | 从日报提取建议 → 4 专家评估 → 行动报告 → commit `obs/06-daily-reports/YYYY-MM-DD-action-report.md` | workflow_dispatch | cron `0 6 * * *`（UTC 06:00 = Dubai 10:00） | 20 min |
| `task-resume.yml`  | 读 `active_tasks.yaml` → 评估阻塞解除 → 回写续接状态 | workflow_dispatch | cron `0 2 * * *`（UTC 02:00 = Dubai 06:00） | 10 min |

## 手动触发（Week 1）

```bash
gh workflow run intel-daily.yml -f date_override=2026-04-23
gh workflow run intel-action.yml -f target_date=2026-04-22
gh workflow run task-resume.yml
```

或在 GitHub UI：Actions tab → 选择 workflow → `Run workflow`。

## 依赖 Secrets（待 Week 1 Secrets 注入 job 完成）

- `ANTHROPIC_API_KEY` — Claude API 调用
- `N8N_SLACK_WEBHOOK_URL` — 成功/失败通知（待加）
- `OBS_PUSH_TOKEN`（可选）— 若跨仓库 commit 需要

## Week 1 → Week 2 切换流程

1. Week 1：所有 step 为 `echo PLACEHOLDER`，Python glue 由 `ai_ml_engineer` 另派单实现
2. Week 1 收尾：`harness_engineer` 另派单注入 GitHub Secrets
3. Week 2：手动 `workflow_dispatch` 端到端跑通 3 次以上
4. Week 2 验证通过后：在 3 份 yaml 中 uncomment `schedule:` 块启用 cron
5. Week 2 结束：监控连续 7 天成功率 ≥ 95%

## 生产 SLA（Week 2 后目标）

- **intel-daily**：成功率 ≥ 95%，失败 → n8n Slack 告警 < 10 min
- **intel-action**：成功率 ≥ 90%（依赖日报），失败回退人工
- **task-resume**：成功率 ≥ 99%（轻量），失败告警但不阻塞

## 设计原则

- `permissions: contents: write` 最小化（仅 commit 权限，无 PR/issue）
- `concurrency` 防止同一 workflow 并行执行污染产物
- 无 token 明文，全部走 `${{ secrets.XXX }}`
- `timeout-minutes` 硬性上限防止卡死消耗额度
