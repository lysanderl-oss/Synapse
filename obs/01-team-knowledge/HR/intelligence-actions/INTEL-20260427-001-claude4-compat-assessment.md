---
id: intel-20260427-001-claude4-compat-assessment
type: private
status: published
lang: zh
version: 1.0.0
published_at: 2026-04-27
updated_at: 2026-04-27
author: ai_ml_engineer
review_by: [harness_engineer]
audience: [knowledge_engineer]
---

# INTEL-20260427-001：Claude 4 API 迁移兼容性评估

**日期**：2026-04-27
**执行人**：ai_ml_engineer
**任务级别**：P1
**关联任务**：INTEL-20260419-002、INTEL-20260420-007

---

## 评估结论

| 维度 | 结论 | 风险等级 |
|------|------|----------|
| Prompt Caching 兼容性 | **ATTENTION** | 低-中 |
| Harness P0 约束稳定性 | **PASS** | 极低 |
| API 版本切换预案 | **PASS** | 极低 |

**总体评级：ATTENTION（局部关注点，整体可控）**

核心发现：Synapse 架构对 Claude 4 迁移整体风险极低，但存在 3 个硬编码模型 ID 点（`scripts/` 层）及 Prompt Caching `ephemeral` TTL 行为待验证，需在 Claude 4 GA 前预处理。

---

## 1. Prompt Caching 兼容性

### 扫描结果

全库扫描关键词：`anthropic`、`claude-`、`cache_control`，发现以下 API 调用文件：

| 文件 | 模型引用方式 | cache_control 用法 | 风险等级 |
|------|-------------|-------------------|----------|
| `scripts/intelligence/shared_context.py` | 变量 `DEFAULT_MODEL = "claude-sonnet-4-6"` / `OPUS_MODEL = "claude-opus-4-6"` | `{"type": "ephemeral"}` system block caching（第 163 行） | **中** |
| `scripts/notion_daily_sync.py` | 硬编码 `model="claude-sonnet-4-6"`（第 121 行） | 无 cache_control | **中** |
| `scripts/auto-publish-blog.py` | `DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")`（第 50 行） | 无 cache_control | **低**（env 可覆盖） |
| `scripts/session-to-worklog.py` | `DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")`（第 272 行） | 无 cache_control | **低**（env 可覆盖） |
| `agent-CEO/` Python 文件 | 无直接 Anthropic API 调用（`anthropic` 字符串仅出现在评分权重 + 示例数据中） | — | 无风险 |
| `synapse.yaml` | 无模型引用 | — | 无风险 |
| `agent-CEO/config/n8n_integration.yaml` | 无模型引用 | — | 无风险 |

### Prompt Caching 风险分析

**现有用法**：`shared_context.py` 中对 `system` 消息使用 `cache_control: {"type": "ephemeral"}`，TTL 5 分钟。这是标准用法，符合 Anthropic 官方规范。

**Claude 4 变化风险评估**：

1. **`ephemeral` cache_control API**：根据 Anthropic 公开文档，`ephemeral` 类型是稳定 API 而非 beta 特性，预计在 Claude 4 中保持兼容。风险：**低**。

2. **`cache_creation_input_tokens` / `cache_read_input_tokens` 用量字段**：`shared_context.py` 第 216-219 行读取这两个字段监控缓存命中。若 Claude 4 更名或重构 usage 字段结构，监控日志会静默失效（不影响功能，但失去观测性）。风险：**低-中**，需在 Claude 4 上线后验证。

3. **硬编码模型 ID `notion_daily_sync.py`**：唯一硬编码（无 env 覆盖），Claude 4 GA 后若 `claude-sonnet-4-6` 停服（参见 INTEL-20260419-002，停服截止 2026-06-15），此处将直接 API 报错。风险：**中（时间窗口内可接受，需在 6 月前修复）**。

### 修复行动项

| # | 文件 | 修复方式 | 优先级 | 建议截止 |
|---|------|----------|--------|----------|
| F-01 | `scripts/notion_daily_sync.py:121` | 将 `model="claude-sonnet-4-6"` 改为 `model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")` | P1 | 2026-06-01 |
| F-02 | `scripts/intelligence/shared_context.py:60-61` | 将 `DEFAULT_MODEL`/`OPUS_MODEL` 改为 env 变量兜底 | P1 | 2026-06-01 |
| F-03 | `shared_context.py` usage 字段读取 | 添加 `hasattr` 防御，避免字段缺失导致崩溃 | P2 | Claude 4 GA 后 2 周内 |

---

## 2. Harness P0 约束稳定性

### CEO Guard 机制分析

**保护架构**：CEO Guard 通过 PreToolUse hook（`.claude/hooks/ceo_guard_pre.js`）在协议层实施工具调用拦截，**与模型无关**——无论 Claude 4 模型能力多强，hook 均在 Claude Code 运行时层触发，先于模型输出执行。

**关键设计特性**（代码验证）：

| 特性 | 实现方式 | Claude 4 影响 |
|------|----------|--------------|
| 工具黑名单 | `['Edit', 'Write', 'Bash', 'WebSearch', 'WebFetch', 'MultiEdit']` — 硬编码在 hook 中 | 无影响，黑名单由 hook 维护 |
| 子 Agent 豁免 | `CLAUDE_SUBAGENT === 'true'` 环境变量判断 | 无影响，仍走子 Agent 路径 |
| 自动化时间窗口豁免 | Dubai 22:00–08:00 UTC+4 时间范围判断 | 无影响，逻辑在 Node.js hook 层 |
| Override 机制 | `settings.json` 中 `ceo_guard_override: false` | 无影响 |
| 审计日志 | `audit/ceo_guard.jsonl`，fail-open（hook 错误不阻断正常操作） | 无影响 |

**结论**：CEO Guard 是**协议层约束**（Claude Code 运行时层），不依赖模型行为。即使 Claude 4 具备更强的自主性或工具调用能力，只要尝试直接调用黑名单工具，PreToolUse hook 仍会在调用前拦截并返回 `{ "decision": "block" }`。**P0 约束在 Claude 4 下稳定性评级：PASS（高置信度）**。

**潜在注意点**：Claude 4 若引入新的工具类型（如 `MultiEdit` 的变体或新原生工具），需检查黑名单是否完整覆盖。建议在 Claude 4 GA 时审查 Claude Code Release Notes 中的工具列表变更。

---

## 3. API 版本切换预案

### 配置文件扫描结论

延续 INTEL-20260420-007（rd_devops 2026-04-22 全库扫描）结论，并针对 Claude 4 场景补充验证：

| 配置文件 | 模型引用 | 切换难度 |
|----------|----------|----------|
| `synapse.yaml` | 无 | 零改动 |
| `agent-CEO/config/n8n_integration.yaml` | 无 | 零改动 |
| `agent-CEO/config/decision_rules.yaml` | 无 | 零改动 |
| `agent-CEO/config/organization.yaml` | 无 | 零改动 |
| `agent-CEO/config/active_tasks.yaml` | 仅 notes 字段文本 | 可选清理 |
| `.claude/settings.json` | 无 | 零改动 |

### 最小改动切换方案

**改动点清单（共 2 个核心文件）**：

```
改动 1：scripts/notion_daily_sync.py — 第 121 行
  前：model="claude-sonnet-4-6"
  后：model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-7")
  影响范围：notion 日报 AI 摘要生成（单文件，低风险）

改动 2：scripts/intelligence/shared_context.py — 第 60-61 行
  前：DEFAULT_MODEL: str = "claude-sonnet-4-6"
      OPUS_MODEL: str = "claude-opus-4-6"
  后：DEFAULT_MODEL: str = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-7")
      OPUS_MODEL: str = os.environ.get("ANTHROPIC_OPUS_MODEL", "claude-opus-4-7")
  影响范围：情报管线所有 API 调用（主路径，中优先级测试）
```

**无需改动**（env 覆盖已就绪）：
- `scripts/auto-publish-blog.py`：`DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", ...)` — 设置 env 变量即切换
- `scripts/session-to-worklog.py`：同上

**切换执行步骤**（预计 < 30 分钟）：

```
步骤 1：修改上述 2 个文件的硬编码 fallback 值
步骤 2：在运行环境设置 ANTHROPIC_MODEL=claude-sonnet-4-7
步骤 3：运行 shared_context.py 单次测试调用，确认 usage 字段正常
步骤 4：验证 notion_daily_sync.py 单次摘要生成（非破坏性）
步骤 5：情报管线下一次定时触发后确认正常输出
```

---

## 行动建议

| # | 行动项 | 执行者 | 截止日期 | 优先级 |
|---|--------|--------|----------|--------|
| A-01 | 修复 `notion_daily_sync.py:121` 硬编码模型 ID（F-01） | ai_ml_engineer | 2026-06-01 | P1 |
| A-02 | 将 `shared_context.py` DEFAULT_MODEL/OPUS_MODEL 改为 env 变量兜底（F-02） | ai_ml_engineer | 2026-06-01 | P1 |
| A-03 | Claude 4 GA 后：审查 Claude Code 新工具类型，更新 CEO Guard 黑名单（如需） | harness_engineer | Claude 4 GA 后 2 周 | P2 |
| A-04 | Claude 4 GA 后：验证 `cache_creation_input_tokens`/`cache_read_input_tokens` 字段兼容性 | ai_ml_engineer | Claude 4 GA 后 2 周 | P2 |
| A-05 | 在 `.env` / GitHub Actions secrets 中预配置 `ANTHROPIC_MODEL=claude-sonnet-4-7` | harness_engineer | 2026-06-08（停服前 1 周） | P1 |

**总结**：Synapse 体系整体迁移风险极低，核心架构（配置文件层、自动化管线配置层）无任何硬编码模型 ID。唯一需要主动处理的是 `scripts/` 层的 3 处硬编码（2 处已有 env 覆盖，1 处需代码修改）。P0 约束（CEO Guard）在 Claude 4 下完全不受影响——协议层 hook 独立于模型版本。建议在 2026-06-01 前完成 A-01、A-02，即可实现停服前零风险切换。

---

*报告生成：ai_ml_engineer（INTEL-20260427-001）*
*审查：harness_engineer（协助 CEO Guard 稳定性评估）*
*下次更新：Claude 4 GA 发布后 2 周内*
