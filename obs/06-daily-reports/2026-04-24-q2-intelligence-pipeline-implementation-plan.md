---
title: Q2 情报管线产品化架构 — 详细实施计划
date: 2026-04-24
status: approved_by_president
approved_decisions:
  - 跳过 Q1 MVP，直接进 Q2
  - 阶段 2 技术栈：GitHub Actions + Claude API + task_budget 50K + prompt caching
  - Slack 分层延后，复用 n8n slack 通知流
for_execution: harness_engineer + ai_ml_engineer
timeline: 2-4 周（Q2 前半）
---

# Q2 情报管线产品化架构 — 详细实施计划

## 总览

**目标**：将情报管线（情报日报 / 情报行动 / 任务自动恢复）从总裁本地电脑 Claude Code Routines 迁移至 GitHub Actions + Claude API 驱动的独立服务，实现脱离总裁本地依赖、7×24 自动运行、可观测、可预算。

**技术栈**：GitHub Actions（定时编排）+ Claude API（推理）+ task_budget 50K（成本硬上限）+ prompt caching（降本）+ Python asyncio（多 Agent 编排）。

**交付物**：3 个 GitHub Actions workflow、3 个 Python glue script（daily / action / resume）、Jinja2 HTML 模板、版本化 prompt 文件、GitHub Secrets 凭证集、n8n slack 通知复用。

**时间**：2-4 周（Q2 前半），Week 1 骨架、Week 2 等价切流、Week 3 观测、Week 4 预留扩展骨架。

**预算**：$30-80/月（Claude API token，含 prompt caching 节省 50-70%）。GitHub Actions 免费额度覆盖。

## 一、WBS 工作拆解（Week-by-Week）

### Week 1：前置准备 + 架构骨架

- [ ] 1.1 从历史情报日报 / 行动报告 golden set 中抽取模板
  - 负责人：ai_ml_engineer
  - 输入：`obs/06-daily-reports/2026-04-XX-intelligence-daily.html`（多份）
  - 输出：`agent-CEO/templates/intelligence-daily.html.j2`、`intelligence-action.html.j2`
- [ ] 1.2 抽取情报管线 prompt 到版本化文件
  - 负责人：ai_ml_engineer
  - 输出：`agent-CEO/prompts/intelligence-daily.md`、`intelligence-action.md`、`task-resume.md`
- [ ] 1.3 创建 GitHub Actions workflow 骨架（3 个 cron）
  - 负责人：harness_engineer
  - 输出：`.github/workflows/intel-daily.yml`、`intel-action.yml`、`task-resume.yml`
- [ ] 1.4 创建 Python glue code（multi-agent 编排）
  - 负责人：ai_ml_engineer
  - 输出：`scripts/intelligence/daily_agent.py`、`action_agent.py`、`resume_agent.py` + `shared_context.py`
- [ ] 1.5 凭证接入 GitHub Secrets
  - 负责人：harness_engineer
  - 内容：ANTHROPIC_API_KEY / NOTION_TOKEN / N8N_API_KEY / SLACK_WEBHOOK（复用现有 n8n webhook）
- [ ] 1.6 task_budget 和 prompt caching 的代码实现
  - 负责人：ai_ml_engineer
  - 目标：每 run ≤ 50K token 硬上限 + 跨 run caching（system prompt + golden context）

### Week 2：单管线验证 + 迁移

- [ ] 2.1 单独跑情报日报（非生产）验证输出等价性
- [ ] 2.2 与历史 golden set diff 比较（≤5% 差异视为等价）
- [ ] 2.3 切流：GitHub Actions cron 接管生产（原 3 个 Routine 保持停用不恢复）
- [ ] 2.4 观察 3 天稳定性

### Week 3：可观测性 + 成本验证

- [ ] 3.1 n8n slack 通知流复用（总裁审批 3 决定）
- [ ] 3.2 心跳监控（每日检查前日产出文件是否存在）
- [ ] 3.3 成本报告（token 实际消耗 vs 预算 ≤$80/月）
- [ ] 3.4 failed run 处理策略（GH Actions retry + Slack 告警）

### Week 4（可选）：加固 + 产品化骨架预留

- [ ] 4.1 多租户隔离骨架（预留 Q3 扩展）
- [ ] 4.2 数据主权导出 API 骨架（预留 Q4 商品化）
- [ ] 4.3 Q3/Q4 路线图回填 requirements_pool.yaml

## 二、技术细节

### GitHub Actions 定时编排

```yaml
# .github/workflows/intel-daily.yml
name: Intelligence Daily
on:
  schedule:
    - cron: '0 4 * * *'  # 08:00 Dubai = 04:00 UTC
  workflow_dispatch:
jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r scripts/intelligence/requirements.txt
      - run: python scripts/intelligence/daily_agent.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
          TASK_BUDGET_TOKENS: '50000'
```

另外 2 个 workflow（`intel-action.yml` 10:00 Dubai、`task-resume.yml` 06:00 Dubai）同构。

### Claude API 调用模式

```python
# prompt caching + task_budget
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=4096,
    system=[
        {"type": "text", "text": SYSTEM_PROMPT,
         "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": GOLDEN_CONTEXT,
         "cache_control": {"type": "ephemeral"}},
    ],
    messages=[{"role": "user", "content": user_input}],
    extra_headers={"anthropic-beta": "token-budget-2024-12"},
    metadata={"task_budget": os.environ["TASK_BUDGET_TOKENS"]},
)
```

关键约束：system / golden context 块打 `cache_control`；task_budget 硬封顶；跨 run cache TTL 5 分钟 → 调度节奏需让同类 run 近邻触发或接受 cache miss。

### 多 Agent 编排（发现 → 评估 → 执行 → 报告）

```python
# scripts/intelligence/shared_context.py
class PipelineState:
    discovered: list       # Agent 1 产出
    evaluated: list        # Agent 2 筛选
    executed: list         # Agent 3 动作
    report_html: str       # Agent 4 渲染

async def run_pipeline():
    state = PipelineState()
    await discovery_agent(state)
    await evaluation_agent(state)
    await execution_agent(state)
    await report_agent(state)  # Jinja2 → HTML
    await git_commit_and_push(state.report_html)
    await slack_notify_via_n8n(state)
```

每个 Agent 是一次 Claude API 调用，state 在内存 dict 中流转；失败时整个 workflow 失败并触发 n8n slack 告警。

### 凭证管理

GitHub Secrets 清单：
- `ANTHROPIC_API_KEY`（已由 harness_engineer 入凭证库并同步）
- `NOTION_TOKEN`
- `N8N_API_KEY`
- `SLACK_WEBHOOK`（指向 n8n 现有 webhook，复用通知流）
- `GITHUB_TOKEN`（GH Actions 内置，用于 commit report）

本地 Python 脚本通过 `os.environ` 读取，不落盘。

### 失败处理

- GH Actions `retry: max-attempts: 2` on transient errors
- 失败触发 `on-failure` step → POST n8n webhook → 现有 slack 通道（聚合 + throttle ≥5 min）
- 连续 2 天失败 → 升级为 L3 事件，Lysander 介入排障

## 三、成本与预算

| 项 | 估算 |
|---|-----|
| GitHub Actions（分钟配额）| $0（免费额度 2000 min/月）|
| Claude API token（50K × 3 run × 30 天）| $30-80 |
| prompt caching 节省 | 50-70% input cost |
| 合计 | **$30-80/月** |

假设：Opus 输入 $15/Mtok、输出 $75/Mtok。50K × 3 × 30 = 4.5M token/月，若 80% 命中 cache（$1.5/Mtok）+ 20% miss + 少量输出 → 上限约 $80。实际 cache 命中率 Week 3 验证。

## 四、里程碑与验收

| 里程碑 | 验收标准 |
|-------|---------|
| Week 1 末 | 3 个 GH Actions workflow 可手动触发且成功跑通一次 |
| Week 2 末 | 情报日报产出与历史 golden set diff < 5% |
| Week 3 末 | 成本 < $80/月确认，心跳监控就绪 |
| Week 4 末 | Q3/Q4 骨架预留 |

## 五、新增 REQ 条目（待入需求池）

- REQ-INFRA-003: Q2 情报管线产品化架构
  - product: synapse_core
  - priority: P0
  - status: in_progress
  - rice: 25.0（见 requirements_pool.yaml）
  - 验收：以上里程碑

## 六、Slack 通知策略（按总裁审批 3）

复用现有 n8n slack 通知流。具体：
- 成功事件：n8n webhook → 现有默认 channel
- 失败事件：GH Actions → n8n webhook → 现有默认 channel（聚合 + throttle）
- **不新增 channel，不做分层**

Slack 四层分层（`#synapse-business` / `#synapse-alerts` / `#synapse-debug` / `#synapse-president`）记录为 tech-debt，Q3 或之后评估。

## 七、风险与缓解

| 风险 | 缓解 |
|------|------|
| 情报管线停摆 3-5 周的业务影响 | 接受（总裁跳过 Q1 决定）；Content Marketing 博客管线不受影响 |
| Slack 噪音问题继续存在 | 记录为 tech-debt REQ，Q3 或之后处理 |
| prompt caching 5 分钟 TTL 需调度节奏配合 | Week 1.6 实现时严格测试跨 run cache hit rate |
| task_budget 50K 不够 | Week 2 如验证不够，升至 70K，但需重新核算预算 |
| 历史 golden set 样本不足 | Week 1.1 从近 30 天情报日报抽取 ≥10 份，多样性覆盖 |
| GH Actions 冷启动延迟 | 非紧急任务可接受；每次 checkout + setup-python 约 30-60s |

## 八、后续里程碑（Q3/Q4）

- Q3：多租户灰度（≤3 客户）
- Q4：Janus Digital SKU 商品化
- 进入 Q3 前需独立安全审计

---

**计划批准**：总裁于 2026-04-24 批准
**执行授权**：Lysander 全权统筹
**首次 Week 1 启动**：待 Lysander 指示（或本次会话继续）
