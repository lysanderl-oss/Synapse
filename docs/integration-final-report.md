# Synapse 双目录整合 — 总裁决策报告

**日期**：2026-04-22
**报告密级**：内部 · 总裁可见
**三团队结论汇总**：Strategist + Decision Advisor + Execution Auditor

---

## 一、团队分析结论摘要

| 评估维度 | 结论 | 评级 |
|---------|------|------|
| 整合可行性 | **高** — 无致命冲突，路径清晰，n8n 已就绪 | ✅ |
| 共识吻合度 | **70%** — 智囊团报告存在3处关键失实 | 🟡 |
| 技术执行难度 | **整体低-中** — 约25个文件操作，约3小时 | 🟡 |
| 整合后价值提升 | Skills 8→14个 / Python 2→18模块 / 自动化管线解锁 | ✅ |
| 删除原目录风险 | **可行**（需完成TOP3前置迁移后） | ✅ |

---

## 二、共识校验：报告 vs 实际文件差异

### 智囊团报告3处关键失实

| 失实项 | 报告声称 | 实际情况 | 影响 |
|--------|---------|---------|------|
| Skills数量 | "当前版有20个" | 实际 14 个有效（.claude/ + skills/ 合计） | 夸大50% |
| PBS简报体系 | "Mini 无 PDG 团队" | PDG 团队已在 Mini 中配置，2张HR卡已就位 | 重复整合 |
| Growth团队 | "建议删除 Growth" | Growth 在 Mini 中**已启用且活跃** | 方向错误 |

### 实际缺失 TOP3（无争议）

| 优先级 | 缺失项 | 影响 |
|--------|--------|------|
| 🥇 P0 | 5个自动化 Agent Prompts（.md文件） | 情报管线自动化闭环缺失驱动 |
| 🥈 P0 | SPE 完整模块（OKR追踪+行为观察） | 总裁个人效率系统不完整 |
| 🥉 P0 | generate-article.py | daily-blog/retro Skill 执行依赖缺失 |

---

## 三、整合执行方案（建议立即执行）

### Phase 1：P0 脚本 + Prompts（预计 1 小时）

**harness_engineer 执行：**

| 序号 | 操作 | 来源 → 目标 |
|------|------|-----------|
| 1.1 | 迁移 generate-article.py | Multi-Agents/scripts/ → Synapse-Mini/scripts/ |
| 1.2 | 迁移 generate-daily-intelligence.py | Multi-Agents/scripts/ → Synapse-Mini/scripts/ |
| 1.3 | 创建 agent-CEO/config/prompts/ 目录 | — |
| 1.4 | 迁移 daily-intelligence-prompt.md | agent-butler/config/ → agent-CEO/config/prompts/ |
| 1.5 | 迁移 intelligence-action-prompt.md | agent-butler/config/ → agent-CEO/config/prompts/ |
| 1.6 | 更新 n8n_integration.yaml 中 trigger 路径 | 确认指向新位置 |

### Phase 2：Skills 迁移（预计 2 小时）

**迁移策略：**
- **11个低难度**：直接迁移（daily-blog, dev-*, graphify, hr-audit, intel, knowledge, qa-gate, retro）
- **4个中难度**：路径适配后迁移（dispatch, synapse, weekly-review, dev-ship）
- **gstack Skills**：不迁移（Mini 已通过 MCP server 集成）
- **Mini 已存在 Skills**：以 Multi-Agents 完整版替换或并存（dispatch, weekly-review）

**skills/ 目录结构（迁移后）：**

```
skills/
├── dispatch/          ← Multi-Agents 替换 Mini
├── capture/           ← Mini 保留
├── plan-day/          ← Mini 保留
├── time-block/        ← Mini 保留
├── weekly-review/    ← Multi-Agents 替换 Mini
├── daily-blog/        ← 新增（Multi-Agents）
├── dev-plan/         ← 新增
├── dev-qa/           ← 新增
├── dev-review/       ← 新增
├── dev-secure/       ← 新增
├── dev-ship/         ← 新增（路径适配）
├── graphify/         ← 新增
├── hr-audit/         ← 新增
├── intel/            ← 新增
├── knowledge/        ← 新增
├── qa-gate/          ← 新增
├── retro/            ← 新增
└── synapse/           ← 新增（路径适配）
```

### Phase 3：SPE 完整模块融入 CLAUDE.md（P1）

**整合内容：**
- 新增 SPE 章节（OKR目标设定/追踪/复盘）
- 迁移 personal_tasks.yaml → agent-CEO/config/
- 迁移 spe_intelligence.yaml → agent-CEO/config/
- **注意**：遵循熵增预算（350行），超出则先删减再添加

### Phase 4：QA 验证

**integration_qa 执行：**
- `/qa-gate` 全量检查迁移文件
- YAML 格式验证
- Skills 命令可用性测试
- n8n webhook 健康检查

---

## 四、删除 Multi-Agents System 目录决策

### 执行条件（完成以下后才能删除）

| 条件 | 状态 |
|------|------|
| Phase 1 完成（脚本 + Prompts 迁移） | 待执行 |
| Phase 2 完成（Skills 迁移） | 待执行 |
| Phase 3 完成（SPE 融入） | 待执行 |
| Phase 4 QA 验证通过 | 待执行 |
| Git commit 创建归档 checkpoint | 待执行 |

### 归档操作

```bash
# 归档 Multi-Agents System 完整历史
git bundle create synapse-archive-20260422.bundle --all

# 或直接删除前确认无遗留依赖
# 确认 n8n_integration.yaml 中 trigger 全部指向 Synapse-Mini 路径
```

### 不整合项（明确保留在归档中）

- Janusd 公司专属 WBS/PMO 脚本
- Growth / Stock / Janus 团队配置
- active_tasks.yaml 历史任务记录
- OBS 中的实际决策日志和会话快照

---

## 五、决策请求

**请总裁确认以下决策：**

| 决策项 | 选项 |
|--------|------|
| **是否批准立即执行 Phase 1（P0 脚本+Prompts 迁移）？** | A) 批准 / B) 暂缓 / C) 调整方案 |
| **是否批准 Phase 2（Skills 迁移）？** | A) 批准 / B) 暂缓 / C) 调整方案 |
| **删除 Multi-Agents System 目录的时间点？** | A) Phase 4 QA 通过后 / B) 等待一周观察 / C) 总裁另行通知 |

**建议决策**：A + A + A（全部批准，执行完成后删除）

---

## 六、三团队最终共识

**✅ 共识结论：整合方案可行，执行价值高，风险可控**

> Synapse-Mini 的技术架构（18个Python模块 + CEO Guard技术封锁 + P0合规三联动）代表演进方向；
> Multi-Agents System 的 Skills 和 Prompts 是经过验证的运营资产；
> 选择性单向整合后，Synapse-Mini 将成为集架构健壮性与运营丰富性于一体的完整体系。

---

*报告汇总：Lysander CEO | 三团队分析：Strategist + Decision Advisor + Execution Auditor | 2026-04-22*
*Synapse 体系 · 整合方案决策参考 · L3 决策：智囊团准备材料，Lysander 执行*
