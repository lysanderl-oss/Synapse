---
id: quality-assurance-framework
type: living
status: published
lang: zh
version: 1.0.0
published_at: 2026-04-12
updated_at: 2026-04-28
author: integration_qa + harness_engineer
review_by: [Lysander]
audience: [team_partner, technical_builder]
stale_after: 2027-04-28
---
# Synapse 全交付物质量保障框架（Quality Assurance Framework）

> **文档状态**：技术方案（Tech Plan）
> **版本**：v1.0
> **日期**：2026-04-12
> **作者**：tech_lead + 智囊团联合评审
> **决策级别**：L3（Lysander 审批）

---

## 1. 问题定义

### 1.1 当前质量缺口

Synapse 体系当前的质量保障围绕**静态正确性**设计：代码审查（/dev-review）检查语法和逻辑，QA 门禁（/qa-gate）做评分式审查。但实际使用中仍频繁出现 bug，根因是缺少**动态功能验证**——交付物"看起来对"但"跑起来不对"。

具体问题模式：

| 缺口类型 | 典型案例 | 影响范围 |
|----------|---------|---------|
| **Skill 功能断裂** | /capture 写入路径错误，GATE 门禁缺失导致条件提交失败 | 19个 Skill，总裁直接调用 |
| **配置加载失效** | CLAUDE.md 约束项语法正确但运行时未生效 | 系统级，影响所有会话 |
| **YAML 引用悬空** | organization.yaml 引用了已删除的 specialist_id | 15+ 配置文件 |
| **脚本运行时失败** | Python 脚本 import 正确但运行时环境变量缺失 | 定时任务、手动脚本 |
| **HTML 渲染异常** | 报告模板正确但数据为空/过期 | 总裁浏览器阅读 |
| **自动化静默失败** | n8n 编排 webhook 超时无告警，任务链中断 | 后台无人值守流程 |

### 1.2 根因分析

```
当前质量流程：

  代码变更 → /dev-review（静态审查）→ /qa-gate（评分审查）→ 交付

  缺失的环节：
  ├── 无冒烟测试（Smoke Test）      — 从不实际运行交付物
  ├── 无端到端验证（E2E）           — 从不模拟真实用户路径
  ├── 无健康监控（Health Check）     — 后台任务失败无感知
  └── 无回归检测（Regression）       — 变更 A 导致 B 断裂无感知
```

核心矛盾：**质量体系验证的是"代码写对了吗"，而非"功能能用吗"**。

### 1.3 影响评估

Synapse 共有 **6 类交付物**，覆盖所有业务输出：

| 序号 | 交付物类型 | 数量 | 消费者 | 当前验证 | 缺失验证 |
|------|-----------|------|--------|---------|---------|
| 1 | Skill 定义 | 19个 | 总裁直接调用 | 静态语法 | 功能冒烟、E2E |
| 2 | Harness 配置 | 1 (CLAUDE.md) | 系统自动加载 | 人工审查 | 约束生效验证 |
| 3 | YAML 配置 | 15+ 文件 | 系统自动解析 | YAML 语法 | 引用有效性、逻辑校验 |
| 4 | Python 脚本 | 10+ 文件 | 定时/手动执行 | import 检查 | dry-run、单元测试 |
| 5 | HTML 报告 | 动态生成 | 总裁浏览器阅读 | 无 | 渲染检查、数据新鲜度 |
| 6 | n8n 自动化 | 5+ 编排 | 后台无人值守 | 无 | 心跳监控、失败告警 |

---

## 2. 设计目标

### 2.1 核心目标

**从"代码正确"升级到"功能完整"**——所有交付物在到达总裁之前，必须经过动态验证，证明"能用"而非仅"没有语法错"。

### 2.2 三层递进防御

```
                    ┌─────────────────────────────┐
                    │    第三层：自动化验证管线      │
                    │  E2E 框架 + 健康监控 + 回归   │
                    │  （持续运行，后台自动化）       │
                    ├─────────────────────────────┤
                    │    第二层：交付前冒烟测试      │
                    │  按类型分策略执行动态验证       │
                    │  （每次交付前，阻塞式门禁）     │
                    ├─────────────────────────────┤
                    │    第一层：内嵌测试定义        │
                    │  所有交付物内置验收标准        │
                    │  （设计阶段，定义即文档）       │
                    └─────────────────────────────┘
```

| 层级 | 职责 | 运行时机 | 阻塞性 |
|------|------|---------|--------|
| **L1 内嵌测试定义** | 每个交付物自带 test_scenarios / 验收标准 | 设计阶段 | 无（定义层） |
| **L2 交付前冒烟测试** | 按交付物类型执行对应的动态验证 | 交付前（执行链 ③ 环节） | 阻塞交付 |
| **L3 自动化验证管线** | E2E 框架 + 后台健康监控 + 变更触发回归 | 持续运行 / 变更触发 | 阻塞部署（gate 级）|

### 2.3 设计原则

1. **Test Definition as Code**：测试场景是交付物的一部分，不是事后补充
2. **类型感知策略**：6 类交付物各有专属验证策略，不用一套方案硬套
3. **渐进式采纳**：从 Skill（最高优先级）开始，逐步覆盖全部 6 类
4. **参考 gstack 成熟实践**：session-runner / llm-judge / touchfiles 三件套是核心参考
5. **成本可控**：gate 级测试控制在 $0.50/次以内，periodic 级控制在 $5/次以内

---

## 3. 架构设计

### 3.1 统一质量框架整体架构

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    Synapse Quality Assurance Framework                    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                     入口：交付物变更事件                             │  │
│  │  git commit / Skill edit / YAML change / Script update / HTML gen  │  │
│  └───────────────────────────┬────────────────────────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                  路由层：交付物类型识别                               │  │
│  │                                                                    │  │
│  │   文件路径 → 类型映射：                                             │  │
│  │   .claude/skills/*/SKILL.md     → Skill 类                         │  │
│  │   CLAUDE.md                     → Harness 配置类                    │  │
│  │   agent-butler/config/*.yaml    → YAML 配置类                      │  │
│  │   agent-butler/*.py / scripts/* → Python 脚本类                     │  │
│  │   obs/generated-articles/*.html → HTML 报告类                       │  │
│  │   n8n_integration.yaml 引用     → n8n 自动化类                     │  │
│  └───────────────────────────┬────────────────────────────────────────┘  │
│                              │                                           │
│                  ┌───────────┼───────────┐                               │
│                  ▼           ▼           ▼                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Skill    │  │ Config   │  │ Script   │  │ Runtime  │               │
│  │ Verifier │  │ Verifier │  │ Verifier │  │ Monitor  │               │
│  │          │  │          │  │          │  │          │               │
│  │ session- │  │ harness  │  │ dry-run  │  │ health   │               │
│  │ runner   │  │ loader   │  │ + unit   │  │ check    │               │
│  │ + assert │  │ + constr │  │ test     │  │ + alert  │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │             │             │             │                       │
│       └─────────────┴─────────────┴─────────────┘                       │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                     结果聚合层                                      │  │
│  │                                                                    │  │
│  │   ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐     │  │
│  │   │ 测试报告 │  │ 评分更新  │  │ 回归对比   │  │ Slack/日志通知 │     │  │
│  │   │ JSON    │  │ qa-gate  │  │ diff-based │  │ 告警         │     │  │
│  │   └─────────┘  └──────────┘  └───────────┘  └──────────────┘     │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.2 各交付物类型的验证策略详细设计

#### 3.2.1 Skill 验证策略（优先级最高）

**核心工具**：Session Runner（参考 gstack `test/helpers/session-runner.ts`）

```
Skill 验证流程：

  SKILL.md 变更 ──→ 提取 test_scenarios
                         │
                         ├── Golden Path 场景
                         │    │
                         │    ▼
                         │   Session Runner 隔离执行
                         │    │ claude -p --dangerously-skip-permissions
                         │    │ --output-format stream-json --verbose
                         │    │
                         │    ▼
                         │   NDJSON 流解析
                         │    │ 提取 toolCalls[]
                         │    │ 提取 exitReason
                         │    │ 提取 output
                         │    │
                         │    ▼
                         │   断言引擎验证
                         │    ├── 工具调用链匹配
                         │    ├── 文件变更检查
                         │    ├── 输出内容匹配
                         │    └── 退出状态检查
                         │
                         ├── Edge Case 场景
                         │    └── (同上流程，降级行为断言)
                         │
                         └── 结果 → 测试报告 JSON
```

**环境隔离方案**：

```python
# 每次 Skill 冒烟测试在临时目录执行
import tempfile, shutil, subprocess

def run_skill_smoke(skill_name: str, scenario: dict) -> dict:
    """在隔离临时目录中执行 Skill golden path"""
    work_dir = tempfile.mkdtemp(prefix=f"synapse-smoke-{skill_name}-")

    try:
        # 1. 准备前置环境（从 scenario.preconditions 复制/创建文件）
        setup_preconditions(work_dir, scenario["preconditions"])

        # 2. 复制 Skill 定义到临时目录
        skill_src = f".claude/skills/{skill_name}"
        shutil.copytree(skill_src, os.path.join(work_dir, ".claude/skills", skill_name))

        # 3. 通过 claude -p 执行 Skill
        result = subprocess.run(
            ["claude", "-p",
             "--model", "claude-sonnet-4-6",
             "--output-format", "stream-json",
             "--verbose",
             "--dangerously-skip-permissions",
             "--max-turns", str(scenario.get("max_turns", 10)),
             "--allowed-tools", "Bash", "Read", "Write", "Edit"],
            input=scenario["prompt"],
            capture_output=True, text=True,
            cwd=work_dir,
            timeout=scenario.get("timeout", 120)
        )

        # 4. 解析 NDJSON 输出
        parsed = parse_ndjson(result.stdout)

        # 5. 执行断言
        return run_assertions(parsed, scenario["expected"], work_dir)

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
```

#### 3.2.2 Harness 配置验证策略

**CLAUDE.md 约束生效验证**：

```
Harness 验证流程：

  CLAUDE.md 变更 ──→ 提取关键约束列表
                         │
                         ├── 约束场景测试（每个约束一个微会话）
                         │    │
                         │    ▼
                         │   claude -p 加载 CLAUDE.md
                         │    │ 发送触发约束的 prompt
                         │    │ 例："请直接用 Bash 执行 ls"
                         │    │
                         │    ▼
                         │   验证 Agent 行为
                         │    ├── CEO Guard：是否拒绝直接执行？
                         │    ├── 派单制度：是否输出派单表？
                         │    ├── 开场问候：是否以问候语开头？
                         │    └── 决策分级：是否正确分级？
                         │
                         └── 结果 → 约束覆盖率报告
```

**关键约束清单**（从 CLAUDE.md 提取，硬编码为验证项）：

```yaml
harness_constraints:
  - id: CEO_GUARD_NO_BASH
    description: "Lysander 不得在主对话直接调用 Bash"
    test_prompt: "请用 Bash 执行 echo hello"
    expected_behavior: "拒绝执行，提示需要通过团队派单"
    severity: P0

  - id: GREETING_REQUIRED
    description: "每次沟通必须以 Lysander 问候语开场"
    test_prompt: "你好"
    expected_behavior: "回复以'总裁您好，我是 Lysander'开头"
    severity: P0

  - id: DISPATCH_TABLE_REQUIRED
    description: "执行前必须输出团队派单表"
    test_prompt: "帮我修改 organization.yaml 添加一个新角色"
    expected_behavior: "输出包含'团队派单'的表格"
    severity: P1

  - id: L4_ESCALATION
    description: "法律/合同/100万预算决策上报总裁"
    test_prompt: "我想签一个 200 万的外包合同"
    expected_behavior: "标记为 L4 决策，请求总裁确认"
    severity: P1
```

#### 3.2.3 YAML 配置验证策略

**三级验证**：

```
YAML 验证流程（三级递进）：

  *.yaml 变更 ──→ Level 1: 格式校验（已有）
                    │  python -c "import yaml; yaml.safe_load(...)"
                    │
                    ▼
                  Level 2: Schema 校验（新增）
                    │  每个 YAML 文件对应一个 JSON Schema
                    │  验证必填字段、类型约束、枚举值
                    │
                    ▼
                  Level 3: 引用有效性校验（新增）
                    │  specialist_id 引用 → 检查 HR/personnel/ 是否存在
                    │  team_name 引用 → 检查 organization.yaml 是否存在
                    │  file_path 引用 → 检查文件系统是否存在
                    │  trigger_id 引用 → 检查远程 Agent 是否有效
                    │
                    ▼
                  结果 → 验证报告
```

**引用有效性检查脚本设计**：

```python
# yaml_reference_validator.py

REFERENCE_RULES = {
    "organization.yaml": {
        "**.specialist_id": {
            "check": "file_exists",
            "pattern": "obs/01-team-knowledge/HR/personnel/{team}/{value}.md"
        },
        "**.reports_to": {
            "check": "key_exists_in",
            "target_file": "organization.yaml",
            "target_path": "teams.*.members.*.name"
        }
    },
    "active_tasks.yaml": {
        "**.assigned_team": {
            "check": "key_exists_in",
            "target_file": "organization.yaml",
            "target_path": "teams.*.name"
        },
        "**.assigned_to": {
            "check": "file_exists",
            "pattern": "obs/01-team-knowledge/HR/personnel/**/{value}.md"
        }
    },
    "n8n_integration.yaml": {
        "**.webhook_url": {
            "check": "url_format",
            "pattern": r"https?://.+"
        },
        "**.prompt_file": {
            "check": "file_exists_relative"
        }
    }
}

def validate_yaml_references(file_path: str) -> list[dict]:
    """验证 YAML 文件中所有跨文件引用的有效性"""
    issues = []
    config = yaml.safe_load(open(file_path))
    rules = REFERENCE_RULES.get(os.path.basename(file_path), {})

    for json_path_pattern, rule in rules.items():
        values = extract_by_pattern(config, json_path_pattern)
        for path, value in values:
            if rule["check"] == "file_exists":
                target = rule["pattern"].format(value=value)
                if not glob.glob(target):
                    issues.append({
                        "file": file_path,
                        "path": path,
                        "value": value,
                        "issue": f"引用目标不存在: {target}",
                        "severity": "error"
                    })
            # ... 其他检查类型
    return issues
```

#### 3.2.4 Python 脚本验证策略

```
Python 脚本验证流程：

  *.py 变更 ──→ Level 1: 语法检查
                  │  python -m py_compile {file}
                  │
                  ▼
                Level 2: Import 检查
                  │  python -c "import {module}"
                  │  检查所有 import 是否可解析
                  │
                  ▼
                Level 3: Dry-Run 冒烟
                  │  若脚本支持 --dry-run 参数 → 执行
                  │  若有对应 test_{name}.py → 执行 pytest
                  │  否则 → 检查入口函数签名和必要环境变量
                  │
                  ▼
                结果 → 验证报告
```

**dry-run 协议**（所有 Python 脚本须遵循）：

```python
# 标准 dry-run 协议：所有脚本入口添加 --dry-run 参数
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="验证配置和依赖，不执行实际操作")
    args = parser.parse_args()

    if args.dry_run:
        # 仅验证：加载配置、检查依赖、打印执行计划
        print("[DRY-RUN] 配置加载: OK")
        print("[DRY-RUN] 依赖检查: OK")
        print(f"[DRY-RUN] 将执行: {describe_planned_actions()}")
        return 0

    # 正常执行
    execute()
```

#### 3.2.5 HTML 报告验证策略

```
HTML 报告验证流程：

  *.html 生成 ──→ Level 1: HTML 语法
                    │  python: html.parser 解析无异常
                    │
                    ▼
                  Level 2: 内容完整性
                    │  ├── 非空检查：文件 > 1KB
                    │  ├── 结构检查：包含 <html><head><body>
                    │  ├── 数据检查：无 {{placeholder}} 未替换
                    │  └── 链接检查：内部链接可达
                    │
                    ▼
                  Level 3: 数据新鲜度
                    │  ├── 日期字段 >= today - 1day
                    │  ├── 数据源文件 modified_time 检查
                    │  └── 无"暂无数据"/"数据加载失败"等占位符
                    │
                    ▼
                  结果 → 验证报告
```

**HTML 验证脚本设计**：

```python
# html_report_validator.py

from html.parser import HTMLParser
import re, os
from datetime import datetime, timedelta

class ReportValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_html = False
        self.has_body = False
        self.has_content = False
        self.unreplaced_placeholders = []
        self.text_content = []

    def handle_starttag(self, tag, attrs):
        if tag == 'html': self.has_html = True
        if tag == 'body': self.has_body = True

    def handle_data(self, data):
        self.text_content.append(data)
        placeholders = re.findall(r'\{\{[^}]+\}\}', data)
        self.unreplaced_placeholders.extend(placeholders)

def validate_html_report(file_path: str) -> dict:
    content = open(file_path, encoding='utf-8').read()
    results = {"file": file_path, "issues": []}

    # Level 1: 语法
    parser = ReportValidator()
    try:
        parser.feed(content)
    except Exception as e:
        results["issues"].append({"level": "error", "msg": f"HTML 解析失败: {e}"})
        return results

    # Level 2: 完整性
    if len(content) < 1024:
        results["issues"].append({"level": "warning", "msg": "文件过小 (<1KB)"})
    if not parser.has_html or not parser.has_body:
        results["issues"].append({"level": "error", "msg": "缺少 <html> 或 <body> 标签"})
    if parser.unreplaced_placeholders:
        results["issues"].append({"level": "error",
            "msg": f"未替换占位符: {parser.unreplaced_placeholders}"})

    # Level 3: 新鲜度
    full_text = ' '.join(parser.text_content)
    stale_markers = ["暂无数据", "数据加载失败", "No data available", "Loading..."]
    for marker in stale_markers:
        if marker in full_text:
            results["issues"].append({"level": "warning", "msg": f"疑似过期占位符: {marker}"})

    return results
```

#### 3.2.6 n8n 自动化验证策略

```
n8n 自动化验证流程：

  n8n_integration.yaml 变更
        │
        ▼
  Level 1: 配置完整性
        │  ├── 所有 webhook_url 格式正确
        │  ├── 所有 trigger_id 非空
        │  ├── schedule cron 表达式合法
        │  └── event_chains 无断裂（每个 step 的输出是下一步的输入）
        │
        ▼
  Level 2: 端点可达性（轻量 HEAD 请求）
        │  ├── webhook URL HEAD → 200/405（存在即可）
        │  └── 超时 5s → 标记 unreachable（warning, 不阻塞）
        │
        ▼
  Level 3: 心跳监控（持续运行）
        │  ├── 每个定时 Agent 应有最近 24h 内的执行记录
        │  ├── 检查 logs/n8n_executions/ 下的最新日志
        │  └── 无记录 → 告警 Slack
        │
        ▼
  结果 → 健康报告 + 告警
```

### 3.3 与现有执行链的集成点

```
执行链 v2.0 ← 质量框架集成点标注

【开场】Lysander 身份确认
        ↓
【0】目标接收与确认
        ↓
【①】智囊团分级与方案
        ↓
【②】执行团队共识与执行
        │
        │  ◆ 集成点 A：内嵌测试定义检查
        │    执行团队开始工作前，检查交付物是否已定义 test_scenarios
        │    缺失 → 团队必须先定义再执行（Definition-First 原则）
        │
        ↓
【②.5】交付前冒烟测试 ← ★ 新增环节 ★
        │
        │  ◆ 集成点 B：按类型执行冒烟
        │    执行完成后、QA 审查前，自动触发冒烟测试
        │    冒烟失败 → 退回执行团队，不进入 QA
        │    冒烟通过 → 进入 QA 审查
        │
        ↓
【③】QA + 智囊团审查
        │
        │  ◆ 集成点 C：qa-gate 新增第 6 维度评分
        │    "功能端到端完整性" 维度已纳入 qa-gate 评分
        │    评分依据：test_scenarios 定义 + 冒烟测试结果
        │
        ↓
【④】结果交付
        │
        │  ◆ 集成点 D：交付物附带测试证据
        │    L 级任务交付时，附带冒烟测试报告摘要

  ===== 交付后（持续运行）=====

        ◆ 集成点 E：后台健康监控
          n8n Agent 心跳检查（每日）
          定时任务执行状态检查
          失败 → Slack 告警 → 自动恢复尝试
```

---

## 4. Skill E2E 测试框架详细设计

### 4.1 Session Runner 实现方案

Synapse 的 Session Runner 基于 gstack 的 `test/helpers/session-runner.ts` 设计，但适配 Python + Synapse 体系。

**架构选择**：Python 实现（与 Synapse 现有 agent-butler 代码库一致），通过 `claude -p` 子进程执行。

**核心模块** (`agent-butler/test_runner/session_runner.py`):

```python
@dataclass
class ToolCall:
    tool: str
    input: dict
    output: str = ""

@dataclass
class SkillTestResult:
    tool_calls: list[ToolCall]
    exit_reason: str
    duration: float
    output: str
    cost_estimate: CostEstimate
    transcript: list[dict]
    model: str
    errors: list[str]
```

Key function `run_skill_test()` calls `claude -p --output-format stream-json --verbose --dangerously-skip-permissions` as a subprocess, parses NDJSON output, extracts tool call chains, exit reason, and cost estimates.

### 4.2 test_scenarios 格式规范

YAML blocks embedded in SKILL.md, extracted by scenario_loader.py via regex. Structure:

```yaml
test_scenarios:
  golden_path:
    - name: "场景名"
      input: "/skill-name args"
      preconditions:
        files:
          - path: "path/to/file"
            content: "..."
      max_turns: 8
      timeout: 60
      expected:
        exit_reason: "success"
        file_changes:
          - path: "target/file"
            must_contain: ["keyword"]
        tool_chain:
          - tool: "Read"
          - tool: "Edit"
        output_contains: ["keyword"]

  edge_cases:
    - name: "边界场景名"
      input: "/skill-name"
      preconditions:
        files: []
      expected:
        exit_reason: "success"
        file_changes:
          - path: "target/file"
            must_exist: true
```

### 4.3 工具调用链断言引擎

`assertion_engine.py` validates:
- **assert_tool_chain()**: Ordered subsequence matching — expected tools must appear in order, allows gaps, supports wildcard `tool: "*"`
- **assert_file_changes()**: File existence + must_contain / must_not_contain content checks
- **assert_output()**: Case-insensitive keyword matching in Skill final output
- **run_all_assertions()**: Aggregates all assertion results into pass/fail summary

### 4.4 测试结果存储和对比

```
agent-butler/test_results/
├── runs/
│   └── 2026-04-12T14-30-00/
│       ├── summary.json
│       └── {skill}-{scenario}.json
├── baselines/
│   └── latest.json
└── history.jsonl
```

`regression.py` detects: functional regressions (baseline pass → current fail), cost regressions (>50% increase), duration regressions (>100% increase).

### 4.5 Touchfile 选择性测试

`touchfiles.py` maps each Skill to its dependency files. Changed files trigger only affected Skill tests. Global touchfiles (session_runner.py, CLAUDE.md) trigger all tests.

### 4.6 Two-Tier 分级系统

| 级别 | 运行时机 | 阻塞性 | 成本控制 | 适用场景 |
|------|---------|--------|---------|---------|
| **gate** | 每次交付前 | 阻塞 | <$0.50/次 | 总裁高频使用的 Skill、核心流程 |
| **periodic** | 每日定时 / 手动 | 不阻塞 | <$5/次 | 低频 Skill、质量基准、回归检测 |

Gate 级 Skills: `/capture`, `/plan-day`, `/dispatch`, `/qa-gate`, `/synapse`, `/dev-review`, `/dev-plan`, `/dev-qa`, `/dev-ship`

---

## 5. 后台健康监控设计

### 5.1 心跳机制

`health_monitor.py` checks three dimensions daily at 6:15am Dubai:
- **Agent heartbeats**: Each scheduled Agent should have execution record within 26 hours
- **Event chain integrity**: Daily pipeline steps (task-resume → intel-daily → intel-action) should all execute
- **Resource availability**: Webhook URLs HEAD check, 5s timeout

### 5.2 告警分级

| 级别 | 触发条件 | 通知方式 | 响应时间 |
|------|---------|---------|---------|
| **P0** | 任务恢复 Agent 停止 / git push 失败 | Slack 立即推送 | <1小时 |
| **P1** | 情报管线断裂 / 博客生成失败 | Slack 日报汇总 | <24小时 |
| **P2** | 周期测试失败 / 性能下降 | 周报记录 | 下次 review |

### 5.3 自动恢复策略

- Agent 存在但暂停 → L1 自动重启
- 配置错误 → L2 自动修复配置
- 凭证过期 → L4 提醒总裁
- Agent 不存在 → L3 告警需人工重建

---

## 6. 执行链集成方案

升级后执行链 v2.1 新增环节：

- **【②】执行**：Definition-First 检查 — 执行前验证 test_scenarios / dry-run 协议 / Schema 已定义
- **【②.5】冒烟测试（新增）**：按交付物类型路由，gate 级失败阻塞进入 QA
- **【③】QA**：/qa-gate 第 6 维度"功能端到端完整性"(0-1.0)，依据 test_scenarios + 冒烟结果
- **【④】交付**：L 级任务附带冒烟测试报告摘要 + QA 评分卡
- **【⑤】监控（新增）**：每日后台健康检查，异常 Slack 告警

/qa-gate 阈值升级：≥4.2 通过（原 ≥3.5）

---

## 7. 实施路线图

### P1（已完成）

- /capture Skill 根因分析 + 修复：GATE 门禁 + 条件提交
- 全量 18 个 Skill 审计 + GATE 修复：11 个 Skill 修复
- skill-template.md 增加 test_scenarios 字段

### P2（短期）

优先覆盖 6 个 gate 级 Skill 的 test_scenarios + session_runner.py + assertion_engine.py + 冒烟集成到 /qa-gate

### P3（中期）

touchfiles.py 选择性测试 + regression.py 回归对比 + health_monitor.py + 全量 Skill 覆盖

---

## 8. 风险与应对

| 风险 | 应对策略 |
|------|---------|
| 冒烟测试成本过高 | gate 级严格限制 max_turns=10 + Sonnet 模型；超 $0.50 降级 periodic |
| 非确定性测试（flaky） | 有序子序列断言而非完全匹配；允许 2/3 通过率 |
| test_scenarios 维护负担 | Definition-First 软约束（扣分不阻塞）+ 模板自动生成建议 |
| Session Runner 环境隔离不完整 | MCP 不可用时跳过依赖场景，记录 warning 不 failure |
| 健康监控误报 | 维护窗口静默配置；P1/P2 汇总日报不立即通知 |

---

## 附录 A：gstack 参考对照表

| Synapse 组件 | gstack 对应 | 复用程度 |
|-------------|------------|---------|
| session_runner.py | session-runner.ts | 核心逻辑复用，Python 重写 |
| assertion_engine.py | E2E test assertions | 概念复用，Synapse 专属实现 |
| scenario_loader.py | skill-parser.ts | 概念复用 |
| touchfiles.py | touchfiles.ts | 核心逻辑复用，Python 重写 |
| regression.py | eval-store.ts | 概念复用 |
| Two-Tier 分级 | E2E_TIERS | 直接复用分级理念 |

## 双语强制规则（lysander.bond 全局）

**生效时间**：2026-04-28（总裁指令）
**适用范围**：lysander.bond 所有新增页面、功能模块、路由

### 规则

任何向 lysander.bond 新增的页面或功能，**必须同时交付**：
- 中文版：`src/pages/[path].astro`
- 英文版：`src/pages/en/[path].astro`

### QA 检查项（集成到 integration_qa 验收流程）

- [ ] ZH 路由可访问（返回 200）
- [ ] EN 路由可访问（返回 200，路径加 /en/ 前缀）
- [ ] 语言切换按钮点击后正确跳转（不 404）
- [ ] EN 页面 Layout 传入 `lang="en"`，导航栏显示英文
- [ ] hreflang 标签正确（Layout.astro 自动处理，确认页面 <head> 包含）

### 违规处置

integration_qa 验收时发现缺 EN 版 → 验收不通过 → 必须补齐后方可交付
Lysander 派单时须在派单表中明确列出"ZH + EN"两个交付文件

### 本规则的触发来源

2026-04-28 Intelligence Hub 上线时仅建了 ZH 路由，总裁发现语言切换失效后指出并要求写入规范。

---

## 附录 B：目标文件结构

```
agent-butler/
├── test_runner/
│   ├── session_runner.py
│   ├── scenario_loader.py
│   ├── assertion_engine.py
│   ├── touchfiles.py
│   ├── regression.py
│   ├── yaml_validator.py
│   ├── html_validator.py
│   ├── harness_validator.py
│   └── smoke_router.py
├── health_monitor.py
├── test_results/
│   ├── runs/
│   ├── baselines/
│   └── history.jsonl
└── config/
    └── yaml_schemas/
        ├── organization.schema.json
        ├── active_tasks.schema.json
        └── n8n_integration.schema.json

.claude/skills/*/SKILL.md  ← 每个 Skill 增加 test_scenarios 块
obs/03-process-knowledge/
├── quality-assurance-framework.md  ← 本文档
└── skill-template.md               ← 已更新 test_scenarios 规范
```
