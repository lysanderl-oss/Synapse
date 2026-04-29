# Synapse 双目录整合 — 技术整合路径报告

**日期**：2026-04-22
**执行团队**：execution_auditor（执行审计师）
**报告类型**：技术路径分析
**分析基础**：synapse-integration-evaluation-20260422.md

---

## 一、Skills 迁移可行性矩阵

### 1.1 来源与目标对照

| Multi-Agents Skill | 目标路径 | 适配难度 | 关键依赖 | 风险项 |
|-------------------|---------|---------|---------|-------|
| daily-blog | `skills/daily-blog/` | **低** | generate-article.py | 硬编码路径（见下方） |
| dev-plan | `skills/daily-blog/dev-plan/` | **低** | 无 | 目录结构不同 |
| dev-qa | `skills/daily-blog/dev-qa/` | **低** | 无 | — |
| dev-review | `skills/daily-blog/dev-review/` | **低** | 无 | — |
| dev-secure | `skills/daily-blog/dev-secure/` | **低** | 无 | disable-model-invocation 标记需验证 |
| dev-ship | `skills/daily-blog/dev-ship/` | **中** | 无 | 硬编码路径需适配 |
| dispatch | `skills/dispatch/` | **中** | organization.yaml | 路径引用需更新 |
| graphify | `skills/graphify/` | **低** | 无 | 路径引用需更新 |
| hr-audit | `skills/hr-audit/` | **低** | 无 | — |
| intel | `skills/intel/` | **低** | 无 | — |
| knowledge | `skills/knowledge/` | **低** | 无 | — |
| qa-gate | `skills/qa-gate/` | **低** | 无 | — |
| retro | `skills/retro/` | **低** | 无 | — |
| synapse | `skills/synapse/` | **中** | organization.yaml, active_tasks.yaml | 路径需更新 |
| weekly-review | `skills/weekly-review/` | **中** | personal_tasks.yaml, memory/ | 依赖 Mini 缺失模块 |
| **gstack*** | Mini 已有 `.claude/skills/` | **不迁移** | MCP | gstack MCP 已通过 Skill 注册 |

> *注：gstack、gstack-qa、gstack-review、gstack-ship 在 Multi-Agents 中为 gstack MCP 的 wrapper 脚本，Mini 已通过 MCP server 直接集成，无需迁移。

### 1.2 Mini 已有 Skills（检查重复）

| Mini Skill | 来源 | 与 Multi-Agents 重复 | 评估 |
|-----------|------|---------------------|------|
| capture | `skills/capture.md` | 部分（与 daily-blog 流程相关） | Mini 已有，保留；检查是否可与 daily-blog 链接 |
| dispatch | `skills/dispatch.md` | 完全同名 | Mini 较简单，以 Multi-Agents 完整版替换 |
| plan-day | `skills/plan-day.md` | 部分（与 weekly-review 共享 OKR 逻辑） | 保留；补充 personal_tasks.yaml 依赖说明 |
| time-block | `skills/time-block.md` | 部分 | 保留；补充 Google Calendar MCP 依赖 |
| weekly-review | `skills/weekly-review.md` | 完全同名 | Multi-Agents 版功能更完整，以其替换 |

### 1.3 适配难度说明

#### 低适配难度（直接迁移）
**daily-blog, dev-plan, dev-qa, dev-review, dev-secure, graphify, hr-audit, intel, knowledge, qa-gate, retro**

这 11 个 Skills 均为**独立功能模块**，不依赖 Mini 缺失的模块：
- 不依赖 `personal_tasks.yaml`
- 不依赖 `memory/` 目录（行为观察文件）
- 不依赖 `/c/Users/.../ai-team-system` 等硬编码路径
- 不依赖特定 organization.yaml 结构

迁移操作：复制 SKILL.md → 目录结构对齐 → 路径引用全局替换。

#### 中适配难度（需路径适配）
**dev-ship, dispatch, synapse, weekly-review**

| Skill | 适配问题 | 解决方案 |
|-------|---------|---------|
| dev-ship | Step 4 硬编码路径 `/c/Users/lysanderl_janusd/Claude Code/ai-team-system` | 替换为 `$SYNAPSE_ROOT` 环境变量或相对路径 |
| dispatch | Step 2 读取 `agent-butler/config/organization.yaml` | 替换为 `agent-CEO/config/organization.yaml` |
| synapse | Step 3 引用 `agent-butler/config/` | 替换为 `agent-CEO/config/` |
| weekly-review | Step 2c 读取 `personal_tasks.yaml`；Step 2e 读取 `memory/` 目录 | personal_tasks.yaml 需从 Multi-Agents 一并迁移；memory/ 目录需创建（可空目录，weekly-review 会跳过不存在的数据源） |

---

## 二、Agent Prompts 迁移优先级

### 2.1 完整迁移清单

| Prompt | 优先级 | 依赖 n8n | 依赖脚本 | Mini 现状 |
|--------|-------|---------|---------|---------|
| daily-intelligence-prompt.md | **P0** | 是 | generate-daily-intelligence.py | 无（缺失） |
| intelligence-action-prompt.md | **P0** | 是 | 无（Python调用） | 无（缺失） |
| task-auto-resume-prompt.md | P1 | 是 | 无 | Mini 无独立 Prompt，但 harness_fsm.py 已覆盖部分逻辑 |
| calendar-sync-prompt.md | P2 | 是 | 无 | Mini 无此模块 |
| retro-blog-prompt.md | P2 | 是 | generate-article.py | Mini 无此模块 |

### 2.2 优先级说明

**P0（必须迁移）：**
- `daily-intelligence-prompt.md` + `generate-daily-intelligence.py`：**两者必须同时迁移**，否则情报日报自动化管线无法运行
- `intelligence-action-prompt.md`：情报行动管线的核心 Prompt，与 daily-intelligence 成对使用

**P1（建议迁移）：**
- `task-auto-resume-prompt.md`：任务自动恢复 Prompt。Mini 的 `harness_fsm.py` 已覆盖任务状态恢复逻辑，但无独立 Prompt 文件。如需要定时任务 Agent，将此 Prompt 与 harness_fsm 结合使用。

**P2（可选迁移）：**
- `calendar-sync-prompt.md` 和 `retro-blog-prompt.md`：属于细粒度自动化，当前 Mini 无此需求可不迁移。

### 2.3 n8n 依赖说明

| Prompt | n8n webhook | Mini n8n_integration.yaml 状态 |
|--------|-----------|-------------------------------|
| daily-intelligence | trig_01Lp7Q1Nn36JQAw4FEEJmKQX | 已存在于 Mini 的 n8n_integration.yaml |
| intelligence-action | trig_017vgQox9JUcwvnx43ucLRPd | 已存在于 Mini 的 n8n_integration.yaml |
| task-auto-resume | trig_01RJJoy4v8TLj2HyHRnABKJb | 已存在于 Mini 的 n8n_integration.yaml |

**重要发现**：Mini 的 `agent-CEO/config/n8n_integration.yaml` 已包含全部 3 个 live trigger IDs，无需重新配置 n8n 工作流。迁移时仅需确认 trigger IDs 的执行目标（Prompt 文件路径）正确。

---

## 三、Python 模块冲突检查

### 3.1 文件级冲突（同名文件）

| 文件名 | Multi-Agents | Mini | 冲突类型 | 处理方案 |
|--------|------------|------|---------|---------|
| hr_base.py | `agent-butler/hr_base.py` | `agent-CEO/hr_base.py` | **同名不同版本** | **保留 Mini 版本**（v3.0，功能更丰富含 QA 引擎）；Multi-Agents 版的功能子集已由 Mini 版覆盖 |
| hr_watcher.py | `agent-butler/hr_watcher.py` | 无 | 缺失 | Mini 无对应模块；**不迁移**（文件监控对日常运行非必需） |

### 3.2 Mini 独有模块（Mini 架构优势）

以下 Mini 模块在 Multi-Agents 中无对应文件，属于 **v3.0 架构升级**，不可被降级：

| 模块 | 功能 | 说明 |
|------|------|------|
| `harness_fsm.py` | 执行链状态机 | 自动管理执行链状态流转 |
| `capability_router.py` | 能力路由 | Agent 能力智能路由 |
| `evolution_dashboard.py` | 进化仪表板 | 自进化追踪 |
| `lysander_interceptor.py` | CEO 拦截器 | 执行链合规审计 |
| `opc_cfo.py` / `opc_coo.py` | CFO/COO Agent | 运营控制 |
| `visual_qa.py` | 视觉 QA | UI 变更自动截图验证 |
| `intelligence_fanout.py` / `intelligence_forecaster.py` | 情报扩展/预测 | 情报管线增强 |
| `dispatch_auditor.py` / `dispatch_weekly_audit.py` | 派单审计 | 派单质量追踪 |
| `self_improvement.py` | 自改进 | 体系自我优化 |

### 3.3 路径差异对比

| 路径概念 | Multi-Agents | Mini |
|---------|------------|------|
| Python 模块根目录 | `agent-butler/` | `agent-CEO/` |
| 配置文件 | `agent-butler/config/` | `agent-CEO/config/` |
| 组织配置 | `agent-butler/config/organization.yaml` | `agent-CEO/config/organization.yaml` |
| 活跃任务 | `agent-butler/config/active_tasks.yaml` | `agent-CEO/config/active_tasks.yaml` |
| n8n 配置 | `agent-butler/config/n8n_integration.yaml` | `agent-CEO/config/n8n_integration.yaml` |
| HR 知识库根 | `obs/01-team-knowledge/HR` | `obs/01-team-knowledge/HR`（相同） |
| 人员卡片格式 | `.md`（YAML frontmatter） | `.yaml`（纯 YAML） |
| Skills 根目录 | `.claude/skills/` | `skills/`（非 MCP） |

### 3.4 hr_base.py 功能差异

| 功能 | Multi-Agents | Mini |
|------|------------|------|
| 卡片格式 | `.md` frontmatter | `.yaml` 纯格式 |
| 团队字段 | `specialists[]` | `members[]`（兼容 `specialists`） |
| QA 引擎 | 无 | 内置 qa_auto_review（85/100 体系） |
| Visual QA 集成 | 无 | qa_auto_review 内置调用 |
| 决策日志 | 部分 | 完整（decision_log.json 集成） |
| 环境变量 | OBS_KB_ROOT | SYNAPSE_ROOT + OBS_KB_ROOT |

**结论**：Mini 的 hr_base.py v3.0 是 Multi-Agents 的超集，迁移时无需合并，仅需在 organization.yaml 中对齐字段名（`members` vs `specialists`）。

---

## 四、完整整合执行步骤（含顺序）

### Phase 0：准备（执行审计师）
```
[ ] 确认 docs/ 目录存在（用于存放报告）
[ ] 备份 Mini 当前状态（git commit checkpoint）
[ ] 创建 skills/ 子目录结构
```

### Phase 1：脚本迁移（P0，必须）
```
[ ] 1.1 迁移 generate-article.py → scripts/generate-article.py
      - 检查相对路径引用是否需要更新
      - 验证：python scripts/generate-article.py --help
[ ] 1.2 迁移 generate-daily-intelligence.py → scripts/generate-daily-intelligence.py
      - 验证：python scripts/generate-daily-intelligence.py --help
```

### Phase 2：Prompts 迁移（P0，必须）
```
[ ] 2.1 创建 agent-CEO/config/prompts/ 目录
[ ] 2.2 迁移 daily-intelligence-prompt.md → agent-CEO/config/prompts/
[ ] 2.3 迁移 intelligence-action-prompt.md → agent-CEO/config/prompts/
[ ] 2.4 更新 n8n_integration.yaml 中 trigger 的 Prompt 路径指向新位置
[ ] 2.5 验证：n8n webhook 调用时文件路径正确
```

### Phase 3：Skills 迁移（核心工作）
```
[ ] 3.1 直接迁移（11个，低难度）
      - 创建 skills/daily-blog/ 子目录
      - 迁移 dev-plan, dev-qa, dev-review, dev-secure
      - 迁移 graphify, hr-audit, intel, knowledge, qa-gate, retro

[ ] 3.2 路径适配迁移（4个，中难度）
      - dev-ship：全局替换硬编码路径
      - dispatch：替换 organization.yaml 路径
      - synapse：替换路径并适配 v3.0 身份说明
      - weekly-review：同时迁移 personal_tasks.yaml + 创建 memory/ 目录

[ ] 3.3 Mini 已存在 Skills 处理
      - capture：保留 Mini 版本（功能完整）
      - dispatch：Multi-Agents 完整版替换 Mini 简化版
      - plan-day/time-block：保留 Mini 版本
      - weekly-review：Multi-Agents 完整版替换
```

### Phase 4：organization.yaml 扩充（P1）
```
[ ] 4.1 对比两版本 organization.yaml 团队配置
[ ] 4.2 将 Multi-Agents 中缺失的团队（如 Product Ops、Content_ops）
      补充到 Mini 的 organization.yaml
[ ] 4.3 字段统一：specialists → members（对齐 Mini v3.0）
[ ] 4.4 更新 agents.yaml 中各 Agent 的能力描述（B 级标准）
```

### Phase 5：验证与 QA 门禁
```
[ ] 5.1 运行 /qa-gate 检查所有迁移文件语法
[ ] 5.2 YAML 格式验证（python -c "import yaml; yaml.safe_load(open(f))"）
[ ] 5.3 Skills 注册测试（执行 /daily-blog help 等简单命令）
[ ] 5.4 n8n webhook 健康检查
[ ] 5.5 执行链合规检查（/synapse status）
```

### Phase 6：知识沉淀
```
[ ] 6.1 将本报告移入 obs/03-process-knowledge/
[ ] 6.2 创建整合执行 SOP 文档 → obs/03-process-knowledge/integration-sop.md
[ ] 6.3 更新 CLAUDE.md Skills 引用列表
```

---

## 五、整合后技术风险清单

### 5.1 高风险（可能阻断）

| 风险 | 描述 | 缓解方案 |
|------|------|---------|
| **R1：人员卡片格式不兼容** | Multi-Agents 人员卡片为 `.md` frontmatter，Mini 使用纯 `.yaml`。直接迁移后 hr_base.py 无法读取卡片 | hr_base.py 已支持 YAML 格式；迁移人员卡片时需转换格式或运行格式转换脚本 |
| **R2：n8n trigger 目标路径错误** | n8n_integration.yaml 中的 trigger IDs 已指向 Mini 文件路径，但如果 Prompt 迁移位置不对应，自动化管线失效 | Phase 2.4 中更新 n8n_integration.yaml 的 trigger 配置 |
| **R3：hardcoded 路径导致脚本失效** | daily-blog 的 generate-article.py 调用和 dev-ship 的路径硬编码 | Phase 3.2 中全局替换；统一使用环境变量 `$SYNAPSE_ROOT` |

### 5.2 中风险（需监控）

| 风险 | 描述 | 缓解方案 |
|------|------|---------|
| **R4：personal_tasks.yaml 缺失** | weekly-review 依赖 personal_tasks.yaml，但 Mini 无此文件 | Phase 3.2 中从 Multi-Agents 迁移；如不存在则创建空文件 |
| **R5：memory/ 目录缺失** | weekly-review 读取 memory/ 目录的行为观察文件 | Phase 3.2 中创建空 memory/ 目录；Skill 代码已处理文件不存在时跳过 |
| **R6：disable-model-invocation 标签兼容性** | dev-secure 使用 `disable-model-invocation: true`，需确认 Mini 的 Claude Code 版本支持此标签 | 迁移后运行 /dev-secure full 测试 |
| **R7：organization.yaml 字段名不一致** | Multi-Agents 用 `specialists[]`，Mini 用 `members[]` | Phase 4.3 中统一使用 `members[]`（Mini v3.0 兼容两种） |

### 5.3 低风险（可接受）

| 风险 | 描述 | 缓解方案 |
|------|------|---------|
| **R8：gstack MCP 重复注册** | Multi-Agents 的 gstack skills 与 Mini 的 MCP server 功能重叠 | 迁移时跳过 gstack skills；保留 MCP 集成 |
| **R9：CLAUDE.md 行数熵增** | 新增 Skills 可能使 CLAUDE.md 超过 350 行熵增预算 | 遵循熵增规则：超出时先删减再添加 |
| **R10：Skills 数量激增** | 迁移后 Mini Skills 从 8 个增至 20+，用户可能不知如何选择 | 更新 README/QUICKSTART 中的 Skills 索引说明 |

### 5.4 无风险项（已确认安全）

| 项 | 说明 |
|---|------|
| Python 模块命名冲突 | Mini 与 Multi-Agents 无同名 Python 模块（除 hr_base.py，已分析） |
| n8n webhook 配置 | Mini n8n_integration.yaml 已包含全部 live trigger IDs，无需重建 |
| gstack 依赖 | gstack MCP 已通过 MCP server 集成，不依赖任何 Skill 文件 |
| 执行链合规 | Mini 的 CEO Guard（技术封锁）比 Multi-Agents 更严格，迁移后合规性只会提升 |

---

## 六、核心结论

### 6.1 技术可行性：**高**

- **无致命冲突**：Python 模块无真正冲突（hr_base.py 为版本差异，Mini 已是超集）
- **路径清晰**：两套系统的目录结构一一对应，迁移路径明确
- **n8n 已就绪**：trigger IDs 已存在于 Mini 的 n8n_integration.yaml，无需重建自动化管线

### 6.2 整合策略：**单向移植**

遵循 synapse-integration-evaluation-20260422.md 的结论，选择性单向整合：
- **移植层**：Skills（16个）、Prompts（5个）、Scripts（2个）、OBS 结构补充
- **保留层**：Mini 全套 Python 架构（v3.0 状态机/CFO/COO/Visual QA/进化体系）
- **禁止项**：不替换 Mini 的 hr_base.py（v3.0 功能更完整）、不覆盖独有模块

### 6.3 执行顺序要点

```
Phase 1（脚本）先于 Phase 2（Prompts）先于 Phase 3（Skills）
原因：daily-blog Skill 依赖 generate-article.py；
      intelligence prompts 依赖 generate-daily-intelligence.py；
      路径依赖关系决定顺序。
```

### 6.4 工作量估算

| Phase | 工作量 | 复杂度 |
|-------|--------|--------|
| Phase 1 脚本迁移 | 小（2个文件） | 低 |
| Phase 2 Prompts 迁移 | 小（2个文件） | 低 |
| Phase 3 Skills 迁移 | 大（16个目录） | 中（路径适配） |
| Phase 4 organization 扩充 | 中 | 中 |
| Phase 5 QA 验证 | 中 | 低 |
| **总计** | **约 25 个文件操作** | **整体低-中** |

---

*报告生成：execution_auditor | 审查：Lysander CEO | 2026-04-22*
