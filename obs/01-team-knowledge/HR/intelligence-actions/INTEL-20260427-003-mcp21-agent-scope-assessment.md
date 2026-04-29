---
id: intel-20260427-003-mcp21-agent-scope-assessment
type: private
status: published
lang: zh
version: 1.0.0
published_at: 2026-04-27
updated_at: 2026-04-27
author: harness_engineer
review_by: [ai_ml_engineer]
audience: [knowledge_engineer]
---

# INTEL-20260427-003：MCP 2.1 Agent Scope 落地评估

**日期**：2026-04-27
**执行人**：harness_engineer
**任务级别**：P1
**来源**：情报行动管线 2026-04-27（综合评分 17/20）

---

## 核心结论

MCP 2.1 Agent Scope + Context Integrity Hash 组合可将 Synapse P0 执行禁区从"文档约定"升级为"协议层强制"，**可行性评级：部分可行（近期 80% + 中期 100%）**。最高价值落地点：在现有 PreToolUse hook 中嵌入 Agent Scope 语义校验（无需等待官方支持，本周可落地），同时准备 `.claude/mcp_agent_scope.json` 配置文件，MCP 2.1 就绪后一键激活协议层强制。

---

## 1. P0 禁区 → Agent Scope 映射

### 1.1 现有禁区规则（来源：CLAUDE.md § CEO 执行禁区）

| 禁区类型 | 禁止对象 | 触发场景 |
|---------|---------|---------|
| 工具黑名单 | `Bash`、`Edit`、`Write`、`WebSearch`、`WebFetch` | CEO 主对话直接调用 |
| 流程约束 | 跳过【0.5】承接直接派单 | 任何级别任务 |
| 伪装绕过 | 贴标签冒充、先斩后奏、伪派单 | 所有模式 |

### 1.2 当前技术防护层（来源：settings.local.json）

- PreToolUse hook：每次工具调用注入审计提醒（CEO Guard 已激活）
- 日志路径：`logs/ceo-guard-audit.log`
- 当前权限白名单：仅含 Bash/PowerShell 特定命令，非系统级 deny

### 1.3 MCP 2.1 Agent Scope 映射表

```json
// 文件：.claude/mcp_agent_scope.json
{
  "agent_scope_version": "2.1",
  "scope_id": "synapse-ceo-lysander",
  "description": "Synapse CEO Lysander P0 执行禁区 — 协议层强制",
  "context": {
    "role": "ceo",
    "persona": "Lysander",
    "conversation_type": "main_dialog"
  },
  "denied_tools": [
    {
      "tool": "bash",
      "reason": "CEO 主对话禁止直接执行 shell 命令，必须通过 Agent 子任务执行",
      "error_code": "P0_CEO_GUARD_VIOLATION",
      "remediation": "通过 Agent 工具创建子 Agent，由子 Agent 执行 Bash"
    },
    {
      "tool": "edit",
      "reason": "CEO 主对话禁止直接编辑文件",
      "error_code": "P0_CEO_GUARD_VIOLATION",
      "remediation": "派单 harness_engineer 子 Agent 执行 Edit"
    },
    {
      "tool": "write",
      "reason": "CEO 主对话禁止直接写文件",
      "error_code": "P0_CEO_GUARD_VIOLATION",
      "remediation": "派单对应执行团队子 Agent 执行 Write"
    },
    {
      "tool": "web_search",
      "reason": "CEO 主对话禁止直接网络搜索，需通过情报管线",
      "error_code": "P0_CEO_GUARD_VIOLATION",
      "remediation": "派单 intel_analyst 或通过情报行动管线执行"
    },
    {
      "tool": "web_fetch",
      "reason": "CEO 主对话禁止直接抓取网页",
      "error_code": "P0_CEO_GUARD_VIOLATION",
      "remediation": "派单子 Agent 执行 WebFetch"
    }
  ],
  "allowed_tools": [
    "read",
    "glob",
    "grep",
    "skill",
    "agent"
  ],
  "workflow_constraints": [
    {
      "constraint": "require_stage_0_5_before_dispatch",
      "description": "任何派单前必须完成【0.5】Lysander 承接与目标确认",
      "enforcement": "pre_dispatch_check"
    },
    {
      "constraint": "require_dispatch_table_before_execution",
      "description": "调用任何 Edit/Write/Bash 之前必须输出团队派单表",
      "enforcement": "pre_tool_audit"
    }
  ]
}
```

### 1.4 映射对照：P0 规则 → Agent Scope 字段

| P0 规则（CLAUDE.md） | Agent Scope 字段 | 强制级别 |
|---------------------|-----------------|---------|
| `tool_blacklist: [Bash]` | `denied_tools[].tool: "bash"` | 协议层拦截 |
| `tool_blacklist: [Edit]` | `denied_tools[].tool: "edit"` | 协议层拦截 |
| `tool_blacklist: [Write]` | `denied_tools[].tool: "write"` | 协议层拦截 |
| `tool_blacklist: [WebSearch]` | `denied_tools[].tool: "web_search"` | 协议层拦截 |
| `tool_blacklist: [WebFetch]` | `denied_tools[].tool: "web_fetch"` | 协议层拦截 |
| `tool_whitelist: [Read, Skill, Agent, Glob, Grep]` | `allowed_tools: [...]` | 协议层允许 |
| 流程约束（Stage 0.5）| `workflow_constraints[].constraint` | 语义声明（需 hook 执行） |

**注**：`denied_tools` 和 `allowed_tools` 为 MCP 2.1 协议层字段，由 MCP runtime 在工具分发前自动拦截；`workflow_constraints` 为 Synapse 扩展字段，需 PreToolUse hook 读取执行。

---

## 2. Context Integrity Hash 集成可行性

### 2.1 结论：**部分可行**

| 场景 | 可行性 | 理由 |
|------|-------|------|
| CLAUDE.md 规则完整性锁定 | 可行 | 对 CLAUDE.md 全文计算 SHA-256，在每次会话初始化时由 hook 验证 hash |
| 防止规则被覆盖注入 | 部分可行 | 可防止文件篡改，但无法防止 system prompt 注入（需 MCP runtime 支持） |
| 跨会话 hash 持久化 | 可行 | 将 hash 写入 `.claude/harness/claude_md.hash`，每次启动校验 |
| 实时 context 完整性 | 不可行（近期） | 需 MCP 2.1 runtime 原生支持，Claude Code 当前版本尚未实现 |

### 2.2 可行理由（近期方案）

MCP 2.1 Context Integrity Hash 的核心价值是在 context window 中声明一个 `context_hash`，runtime 在每次工具调用前验证 CLAUDE.md 等核心 Harness 文件未被篡改。在官方支持到来前，可通过 **PreToolUse hook 手动实现等效机制**：

```python
# .claude/hooks/ceo_guard_enhanced.py（近期落地方案）
import hashlib, json, os

HARNESS_FILES = [
    "CLAUDE.md",
    ".claude/harness/execution-chain-stage-0.5.md",
]

def compute_hash(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def verify_context_integrity() -> bool:
    """PreToolUse hook 调用：校验 Harness 文件完整性"""
    hash_store = ".claude/harness/context_integrity.json"
    if not os.path.exists(hash_store):
        return True  # 首次运行，初始化 hash
    with open(hash_store) as f:
        stored = json.load(f)
    for fpath in HARNESS_FILES:
        current = compute_hash(fpath)
        if stored.get(fpath) != current:
            raise RuntimeError(
                f"Context Integrity Violation: {fpath} has been modified. "
                f"Expected: {stored[fpath][:16]}... Got: {current[:16]}..."
            )
    return True
```

### 2.3 不可行场景说明

- **System prompt 注入攻击**：恶意 prompt 在 context 层面覆盖规则，不触发文件级 hash，需 MCP 2.1 runtime 的 `context_integrity_mode: strict` 才能防护（中期目标）。
- **子 Agent context 隔离**：当前 Claude Code 子 Agent 共享部分 parent context，MCP 2.1 的 Agent Scope 可在子 Agent 级别重新声明 scope，实现真正的隔离（中期目标）。

---

## 3. 落地路径

| 时间 | 行动 | 具体内容 | 价值 |
|------|------|---------|------|
| **立即（本周）** | 增强 PreToolUse hook | 在现有 CEO Guard hook 中加入：① `denied_tools` 列表硬编码校验；② context integrity hash 文件级校验；③ 违规时输出结构化 `P0_CEO_GUARD_VIOLATION` 错误码 | 80% 的协议层强制效果，无需等待官方支持 |
| **立即（本周）** | 创建 `mcp_agent_scope.json` | 创建 `.claude/mcp_agent_scope.json`（本文 §1.3 配置示例），作为 MCP 2.1 就绪后的一键激活文件；同时将 `allowed_tools` 和 `denied_tools` 列表注入 CLAUDE.md 旁注 | 零边际成本，MCP 2.1 支持后立即生效 |
| **立即（本周）** | context_integrity.json 初始化 | 在 `.claude/harness/` 目录生成 `context_integrity.json`，记录 CLAUDE.md + 关键 harness 文件的 SHA-256 hash；hook 启动时自动验证 | 防止 Harness 文件意外篡改 |
| **中期（MCP 2.1 就绪）** | 激活协议层 Agent Scope | Claude Code 官方支持 `mcp_agent_scope.json` 后，P0 禁区由 MCP runtime 拦截，不再依赖 hook 的自律性 | 100% 强制，绕过路径在协议层关闭 |
| **中期（MCP 2.1 就绪）** | 启用 `context_integrity_mode: strict` | 在 `mcp_agent_scope.json` 中开启严格模式，防止 system prompt 注入覆盖规则 | 防御恶意 context 注入 |
| **中期（MCP 2.1 就绪）** | 子 Agent scope 继承规则 | 定义子 Agent scope 模板（harness_engineer / butler 等角色各自的 allowed_tools），防止子 Agent 越权 | 全栈 Agent 权限边界 |

---

## 4. 建议优先级

### 优先级排序（P0 → P2）

1. **[P0 立即] PreToolUse hook 增强**
   - 现有 CEO Guard hook 仅有"审计提醒"语义，无硬性拦截
   - 加入 `denied_tools` 硬编码拦截，工具调用失败并返回 `P0_CEO_GUARD_VIOLATION`
   - 估算工作量：1-2小时，harness_engineer 可独立完成

2. **[P1 本周] `mcp_agent_scope.json` 预置**
   - 按 §1.3 配置示例创建文件，MCP 2.1 就绪后零摩擦激活
   - 同时将 `denied_tools` 列表同步至 CLAUDE.md `## ⛔ CEO 执行禁区` 节，确保 SSOT

3. **[P1 本周] context_integrity.json 初始化**
   - 生成 CLAUDE.md + 关键 harness 文件的 SHA-256 baseline
   - 将 hash 验证逻辑合并入 PreToolUse hook

4. **[P2 中期] MCP 2.1 协议层激活**
   - 跟踪 Claude Code 官方 MCP 2.1 支持公告（目前装机量 9700 万，标准化进度快）
   - 触发条件：Claude Code 发布 `mcp_agent_scope` 支持时，由 harness_engineer 执行激活

### 技术债风险

- 当前 CEO Guard 的"文档约定"防护存在被 Auto Mode 或 context 注入绕过的理论风险
- MCP 2.1 协议层强制是将该风险从"依赖模型自律"降级为"依赖协议拦截"的关键升级
- **核心价值**：P0 约束的执行成本从"每次 token 消耗"降为"协议层零成本"

---

## 参考背景

- 情报来源：情报行动管线 2026-04-27
- 关联任务：INTEL-20260420-001（MCP 9700万装机量审计），INTEL-20260421-001（OpenAI SDK 对比）
- 相关文件：
  - `CLAUDE.md` §CEO 执行禁区
  - `.claude/settings.local.json`（当前 hook 权限配置）
  - `.claude/harness/ceo-guard-tests.md`（P0 规则测试场景）
