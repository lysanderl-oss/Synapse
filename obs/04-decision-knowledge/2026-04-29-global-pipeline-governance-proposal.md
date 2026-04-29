---
id: "2026-04-29-global-pipeline-governance-proposal"
type: reference
status: draft
lang: zh
version: 1.0.0
published_at: "2026-04-29"
updated_at: "2026-04-29"
author: product_ops
review_by: [strategy_advisor, harness_engineer, execution_auditor, integration_qa]
audience: [team_partner, knowledge_engineer]
stale_after: "2026-10-29"
---

# 全局产品管线治理提案 v1.0

## 执行摘要

当前 Synapse 旗下 5 条产品线中，3 条无产品档案、核心情报管线（intel-daily/intel-action）完全静默、pipeline-metrics 无锁定机制导致基线持续漂移。本提案针对上述问题，设计两项系统机制（每日 2:00 AM 全局同步 + PMC 治理前置），并补全三条缺失产品线档案，以实现"每天 8:00 AM 前所有管线信息状态已知可信"的治理目标。

---

## 一、现状审查结论

### 1.1 lysander.bond 管线健康状况

| 维度 | 当前状态 | 健康评分 |
|------|---------|---------|
| 内容生产自动化 | 85% 覆盖 | 良好 |
| 告警通知覆盖率 | 40%（9/10 GHA 有 Slack，intel-daily/intel-action 完全静默） | 差 |
| 治理文档同步 | 0%（PIPELINE.md Section 7 版本号滞后，显示 v1.1.0 实为 v1.2.0） | 极差 |
| 基线锁定 | 未锁定（pipeline-metrics yaml 随版本持续变化，blog 计数从基线 33 涨至实测 45） | 差 |

**核心风险**：每日 8:00 AM 情报窗口消费的数据，可能基于昨日甚至更早的过时状态，且无告警机制兜底。

### 1.2 全局产品线档案完整度

| 产品线 | 档案状态 | 关联 GHA | 问题 |
|--------|---------|---------|------|
| PMO Auto | 完整 | 有 | — |
| Synapse Core | 部分（需补全） | 有 | 缺委员会成员、核心约束 |
| Content Marketing | **无档案** | 有（2 条生产 GHA） | 最高风险：有生产管线无治理 |
| Janus Digital | **无档案** | 未知 | 占位档案缺失 |
| Enterprise Governance | **无档案** | 未知 | 占位档案缺失 |

### 1.3 核心问题清单（按优先级）

| 优先级 | 问题 | 影响范围 |
|--------|------|---------|
| P0 | intel-daily.yml + intel-action.yml 无 Slack 通知 | 情报管线失败无感知 |
| P0 | n8n-snapshot.yml 无任何告警 | n8n 备份失败静默 |
| P0 | Content Marketing 有生产 GHA 无产品档案 | 无治理边界 |
| P1 | pipeline-metrics 无锁定，基线持续漂移 | 度量失真 |
| P1 | PIPELINE.md Section 7 版本号 SSOT 漂移 | 文档不可信 |
| P2 | Synapse Core 档案不完整 | 治理盲区 |
| P2 | Janus Digital / Enterprise Governance 无占位档案 | 扩展困难 |

---

## 二、方案设计

### 2.1 机制一：每日 2:00 AM 全局产品管线同步（Global Pipeline Daily Sync）

**设计目标**：保证每天 8:00 AM 前，所有产品管线信息处于最新、可信、有告警的状态。

**触发时间**：每日 2:00 AM Dubai（= UTC 22:00 前一日）

**执行范围（按产品线）**：

| 产品线 | 更新内容 | 数据来源 | 责任 GHA 步骤 |
|--------|---------|---------|--------------|
| Content Marketing | blog 文章计数、pipeline-metrics/latest.yaml | lysander-bond src/content/ | Step 2: pipeline-metrics-refresh.py |
| Synapse Core | PIPELINE.md Section 7 版本号同步 | VERSION 文件 | Step 3: sed/Python 替换 |
| 全产品线 | Slack 状态通知（成功/失败） | GHA job 状态 | Step 5: Slack webhook |
| n8n 快照 | 失败告警补丁（现有 workflow 改造） | n8n-snapshot.yml job 状态 | 现有 workflow 补丁 |

#### 新建 GHA Workflow：pipeline-daily-sync.yml

```yaml
name: Pipeline Daily Sync

on:
  schedule:
    - cron: '0 22 * * *'   # 每日 UTC 22:00 = Dubai 2:00 AM
  workflow_dispatch:         # 手动触发入口

env:
  SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_N8N }}

jobs:
  pipeline-sync:
    name: Global Pipeline Daily Sync
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Step 1 — Checkout Synapse-Mini
        uses: actions/checkout@v4
        with:
          repository: lysanderl/Synapse-Mini
          token: ${{ secrets.GH_PAT }}
          path: synapse-mini

      - name: Step 2 — Run pipeline-metrics-refresh.py
        run: |
          cd synapse-mini
          python scripts/pipeline-metrics-refresh.py \
            --bond-repo ../lysander-bond \
            --output pipeline-metrics/latest.yaml
        env:
          BOND_REPO_PATH: ${{ github.workspace }}/lysander-bond

      - name: Step 3 — Update PIPELINE.md Section 7 version
        run: |
          cd synapse-mini
          CURRENT_VERSION=$(cat VERSION)
          python scripts/update-pipeline-doc.py \
            --file obs/PIPELINE.md \
            --section 7 \
            --version "$CURRENT_VERSION"

      - name: Step 4 — Checkout lysander-bond and push metrics
        uses: actions/checkout@v4
        with:
          repository: lysanderl/lysander-bond
          token: ${{ secrets.GH_PAT }}
          path: lysander-bond
      - name: Commit and push pipeline-metrics
        run: |
          cd lysander-bond
          git config user.name "Lysander Bot"
          git config user.email "bot@lysander.bond"
          git add pipeline-metrics/latest.yaml
          git diff --cached --quiet || git commit -m "chore: pipeline-metrics daily sync $(date -u +%Y-%m-%d)"
          git push

      - name: Step 5 — Slack 通知（成功）
        if: success()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "✅ *Pipeline Daily Sync* 完成 — $(date -u +%Y-%m-%d)\n管线状态已更新，8:00 AM 情报窗口就绪。",
              "username": "Lysander Bot",
              "icon_emoji": ":robot_face:"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ env.SLACK_WEBHOOK }}

      - name: Step 5 — Slack 通知（失败）
        if: failure()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "🚨 *Pipeline Daily Sync 失败* — $(date -u +%Y-%m-%d)\n需立即排查，8:00 AM 情报窗口数据可能过时。\n查看: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}",
              "username": "Lysander Bot",
              "icon_emoji": ":rotating_light:"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ env.SLACK_WEBHOOK }}
```

#### 同期改造（现有 workflow 补丁，不新建）

**intel-daily.yml** — 最后一步补充 Slack 通知：
```yaml
      - name: Slack 通知（成功）
        if: success()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: '{"text": "✅ intel-daily 完成 — ${{ github.run_id }}"}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_N8N }}

      - name: Slack 通知（失败）
        if: failure()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: '{"text": "🚨 intel-daily 失败 — 查看: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_N8N }}
```

**intel-action.yml** — 同上，payload 前缀替换为 `intel-action`。

**n8n-snapshot.yml** — 补充失败告警步骤（仅失败时发送，不发成功通知以降低噪音）：
```yaml
      - name: Slack 失败告警
        if: failure()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: '{"text": "🚨 n8n-snapshot 备份失败 — 查看: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_N8N }}
```

#### 新建 pipeline-metrics-refresh.py 核心逻辑

```python
#!/usr/bin/env python3
"""
pipeline-metrics-refresh.py
统计 lysander-bond 各 Content Collection 实际文件数，写入 pipeline-metrics/latest.yaml
generated_at 时间戳用于假成功验证：下次执行时检查是否在 26 小时内
"""
import argparse
import datetime
import os
import yaml
from pathlib import Path

def count_collection_files(bond_root: Path, collection: str, ext: str = ".md") -> int:
    collection_path = bond_root / "src" / "content" / collection
    if not collection_path.exists():
        return 0
    return len(list(collection_path.glob(f"**/*{ext}")))

def refresh_metrics(bond_repo: str, output: str):
    bond_root = Path(bond_repo)
    generated_at = datetime.datetime.utcnow().isoformat() + "Z"

    metrics = {
        "generated_at": generated_at,
        "schema_version": "1.1",
        "collections": {
            "blog":    count_collection_files(bond_root, "blog"),
            "project": count_collection_files(bond_root, "project"),
            "intel":   count_collection_files(bond_root, "intel"),
        }
    }

    # 假成功验证：检查上次生成时间是否超过 26 小时
    output_path = Path(output)
    if output_path.exists():
        with open(output_path) as f:
            prev = yaml.safe_load(f)
        prev_ts = datetime.datetime.fromisoformat(prev.get("generated_at", "").rstrip("Z"))
        age_hours = (datetime.datetime.utcnow() - prev_ts).total_seconds() / 3600
        if age_hours > 26:
            print(f"[WARN] 上次生成距今 {age_hours:.1f}h，超出 26h 阈值，本次更新视为恢复")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(metrics, f, allow_unicode=True, sort_keys=False)

    print(f"[OK] pipeline-metrics 已更新: {output}")
    for k, v in metrics["collections"].items():
        print(f"     {k}: {v} 篇")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bond-repo", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    refresh_metrics(args.bond_repo, args.output)
```

---

### 2.2 机制二：产品管线 PMC 治理前置制度（Product Pipeline PMC）

**核心原则**："What & Why 由 PMC 定义，How & When 由执行团队决定"

#### PMC 三角色映射

| PMC 角色 | Synapse Agent | 职责 |
|----------|--------------|------|
| 产品 Owner | Lysander CEO | 最终产品决策权，代理总裁执行 L3 决策 |
| 策略顾问 | strategy_advisor | Why & What 的专业分析，行业对标，成功指标定义 |
| 技术顾问 | harness_engineer | How 的可行性确认，风险评估，回滚方案设计 |

#### PMC 触发规则

**必须触发 PMC**：
- 新产品线启动或现有产品线下线
- 现有自动化功能的行为变更（输出格式、触发逻辑、发布目标改变）
- 数据 schema 变更（Content Collection 字段增删、pipeline-metrics 结构变更）
- 自动化管线逻辑变更（新增/删除 GHA step、cron 时间变更）
- 对外内容策略调整（语言、频率、受众定位改变）

**免于触发 PMC**：
- bug 修复（已知行为恢复，不改变预期功能）
- 样式微调（CSS、排版，不影响内容产出）
- 配置参数调整（超时时长、重试次数等数值微调）
- 内部工具优化（脚本性能提升，外部行为不变）
- 日志格式变更（不影响业务输出 artifact）

#### Product Brief 模板（Synapse 版，5 项）

```markdown
## Product Brief — [功能/变更名称]

**1. 问题陈述**
解决什么用户或业务问题？当前状态 vs 期望状态。

**2. 成功标准**（可量化）
- 指标 1：[具体数值目标，如"blog 计数误差 < 2%"]
- 指标 2：[...]
- 指标 3：[...]

**3. 范围边界**
In Scope（此次包含）：
- [ ] ...
- [ ] ...
- [ ] ...
Out of Scope（此次不含）：
- ...

**4. 风险与回滚**
主要风险：[...]
回滚方式：[具体操作步骤，不超过 3 步]
回滚耗时估算：[...]

**5. 决策级别**
[ ] L1 自动执行  [ ] L2 专家评审  [ ] L3 Lysander 决策  [ ] L4 总裁审批
```

#### 融入现有执行链

在【0.5】承接阶段新增判断节点：

```
【0.5】Lysander 承接与目标确认
  → 判断：是否符合 PMC 触发条件？
     ├── 是 → 输出 Product Brief（5 项）
     │         → PMC 异步确认（目标：5 分钟内）
     │         → 超时自动放行，记录"PMC-waived"
     │         → 再派单执行
     └── 否 → 直接派单（标注"PMC-exempt: [原因]"）
```

---

### 2.3 补全产品档案（3 条缺失线）

**优先级排序**：

| 优先级 | 产品线 | 理由 | 最小可行内容（MVP） |
|--------|--------|------|---------------------|
| P0 | Content Marketing | 已有 2 条生产 GHA，但无任何治理边界，最高风险 | 定位 + GHA 清单 + 委员会 3 人 + 约束 3 条 + 版本 |
| P1 | Synapse Core | 档案存在但不完整，缺委员会成员和核心约束 | 补全现有档案缺项 |
| P2 | Janus Digital | 无档案，需占位以便后续扩展 | 一句话定位 + 状态标注 placeholder |
| P2 | Enterprise Governance | 同上 | 同上 |

**MVP 档案结构（所有缺失线统一使用）**：

```yaml
# product-profile.md 最小可行结构
product_name: [名称]
one_liner: [一句话产品定位]
status: [active | placeholder | deprecated]
version: [x.x.x]

pipelines:
  - name: [GHA workflow 名称]
    file: .github/workflows/xxx.yml
    trigger: [schedule | push | manual]

committee:
  product_owner: Lysander CEO
  strategy_advisor: strategy_advisor
  tech_advisor: harness_engineer

constraints:
  - [约束 1]
  - [约束 2]
  - [约束 3]
```

---

## 三、实施 WBS

| 阶段 | 任务 | 执行团队 | 依赖 | 交付物 |
|------|------|---------|------|--------|
| Sprint 1（当日） | intel-daily.yml 补 Slack 通知（成功+失败） | harness_engineer | 无 | 已合并 commit |
| Sprint 1（当日） | intel-action.yml 补 Slack 通知（成功+失败） | harness_engineer | 无 | 已合并 commit |
| Sprint 1（当日） | n8n-snapshot.yml 补失败告警 | harness_engineer | 无 | 已合并 commit |
| Sprint 1（当日） | Content Marketing product-profile.md 创建（MVP） | knowledge_engineer | 无 | 档案文件入库 |
| Sprint 2（本周） | 新建 pipeline-daily-sync.yml | ai_systems_dev | Sprint 1 完成 | 可运行 GHA workflow |
| Sprint 2（本周） | 新建 pipeline-metrics-refresh.py | ai_systems_dev | Sprint 1 完成 | 可执行 Python 脚本 |
| Sprint 2（本周） | 写入 pmc-governance.md 到 .claude/harness/ | harness_engineer | 无 | 治理规则文件 |
| Sprint 3（下周） | Synapse Core product-profile 补全缺项 | knowledge_engineer | Sprint 1 | 完整档案 |
| Sprint 3（下周） | Janus Digital 占位档案 | knowledge_engineer | Sprint 2 | 占位档案文件 |
| Sprint 3（下周） | Enterprise Governance 占位档案 | knowledge_engineer | Sprint 2 | 占位档案文件 |

---

## 四、决策申请

**决策级别**：L4（总裁审批）

**理由**：本提案建立跨全产品线的治理制度，涉及修改 `.claude/harness/` 核心配置、新建生产 GHA workflow、变更全局执行链逻辑（【0.5】阶段新增 PMC 判断节点），属于体系级不可逆变更，须总裁确认后方可执行。

**申请事项**：

| # | 申请内容 | 影响范围 | 可逆性 |
|---|---------|---------|--------|
| 1 | 批准每日 2:00 AM 全局产品管线同步机制（新建 pipeline-daily-sync.yml） | lysander.bond + Synapse-Mini | 可逆（删除 workflow 即撤销） |
| 2 | 批准 PMC 治理前置制度（新建 .claude/harness/pmc-governance.md，修改执行链【0.5】说明） | 全产品线执行流程 | 可逆（删除文件+还原说明） |
| 3 | 批准补全三条产品线档案（Content Marketing / Janus Digital / Enterprise Governance） | 知识库 + 路由配置 | 可逆（删除档案文件） |
| 4 | 授权 Lysander 主导 Sprint 1–3 全程执行 | 团队执行授权 | — |

**执行授权范围**：总裁批准后，Lysander 全权按 WBS 自主调度 Sprint 1–3，无需逐任务请示。遇以下情况上报总裁：阻塞超过 24h 未解除 / 实际执行偏离 WBS > 30% / 出现新的 L4 级风险决策点。

**圆桌评审请求**：请 strategy_advisor / harness_engineer / execution_auditor / integration_qa 在批准前异步完成评审，将意见记录于本文档 `review_by` 成员对应的评审批注中。
