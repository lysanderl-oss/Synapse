---
product_line: synapse_core
立项日期: 伴随 Synapse-PJ 体系诞生（PMO Auto V2.0 GA 前即为生产运行状态）
成熟度: 生产运行
产品线常委: 总裁刘子杨 + Lysander CEO 直管（内核体系不下放）
汇报链: N/A（内核产品线，其他产品线依赖它，不反向汇报）
战略依据: Harness Engineering — Agent = Model + Harness
---

# Synapse Core — 内核协作运营体系

## 产品线定义

Synapse Core 是 Synapse-PJ 体系的**基础内核产品线**，为其他 4 条产品线
（pmo_auto / content_marketing / janus_digital / enterprise_governance）
提供底层能力：治理框架 / 执行链 / Agent 协同 / 决策体系 / 跨会话状态管理。

Core 不面向外部市场销售，而是作为体系"神经中枢"支撑全部业务：
**知识(OBS) ←突触→ 决策(Harness) ←突触→ 执行(Agents)**。

## 四层架构

| 层 | 组件 | 功能 |
|----|------|------|
| 记忆层 | Obsidian 第二大脑（OBS）| 知识存储与检索 |
| 控制层 | Harness Engineering | 规则、约束、流程（Guides + Constraints + Sensors）|
| 执行层 | Multi-Agent 团队（44 人）| 专业分工执行 |
| 进化层 | 情报闭环管线 | 发现→评估→执行→报告 |
| 决策层 | 四级决策体系 | L1 自动 → L4 总裁 |

## 核心能力

1. **CEO Guard 架构**：PreToolUse hook P0 硬性约束，保证 CEO 主对话不直接执行高风险工具
2. **执行链四级决策（L1-L4）**：自动执行 / 专家评审 / Lysander 决策 / 总裁决策，清晰分层
3. **QA 三阶段门禁**：Alpha 集成测试 / Beta E2E 测试 / 发布评审，不可跳过
4. **Multi-Agent 协同**：44 人虚拟组织（含智囊团 + 8 个专业执行团队），Agent HR 管理制度
5. **跨会话状态管理**：active_tasks.yaml 保证任务不因会话切换丢失
6. **自动化编排层**：3 个定时远程 Agent（任务恢复 6:00 / 情报日报 8:00 / 情报行动 10:00 Dubai）
7. **价值对齐 memory 系统**：auto memory 持续沉淀用户偏好、反馈、项目上下文

## 与其他产品线的关系

Synapse Core 是**底座**，其他 4 条产品线均构建于其上：

| 产品线 | 依赖 / 外化关系 |
|--------|-----------------|
| **pmo_auto** | 构建**在** Core 之上的垂直业务自动化实例；同时反哺 Core（如 REQ-012-TC-01 升级了 QA 方法论）|
| **content_marketing** | 借力 Core 的 Agent 协同能力实现全自动博客流水线 |
| **janus_digital** | 把 Core 的 Multi-Agent 架构**产品化**对外销售 |
| **enterprise_governance** | 把 Core 的 CEO Guard + 执行链**咨询化**对外交付治理方案 |

**核心判断**：外化产品线的竞争力 = Core 的成熟度。Core 不稳，外化皆虚。

## 需求池分区

`product: synapse_core`

## 当前运行事实

- **Harness Configuration**：`CLAUDE.md`（~ 350 行内，受熵增预算约束）
- **根 VERSION**：1.0.0（需求池 meta.last_release 维护）
- **子系统独立版本**：pmo-auto 2.0.3 / infra 1.0.1
- **CEO Guard 审计日志**：`logs/ceo-guard-audit.log`（活跃）
- **熵增预算治理**：Phase 1 运行中，3 天定期审查
- **已支撑业务**：PMO Auto V2.0 GA 发布 + 情报管线 + 全自动博客管线

## 已交付的支撑业务

### 博客发布管线（OBJ-BLOG-PIPELINE-CLOUD shipped @ infra-1.0.6, 2026-04-26）

**类型**：基础设施管线（GitHub Actions cron 云端化）
**与情报管线同构**：参考 OBJ-Q2-INTEL-PIPELINE 模式

**组件**：
- `lysanderl-glitch/synapse-sessions` 私有 repo（本机 session 云端镜像）
- `scripts/sessions_watcher.py` 本机增量同步服务（每 5 分钟）
- `.github/workflows/blog-publish.yml` cron `0 18 * * *` UTC（Dubai 22:00）
- `.github/workflows/blog-heartbeat.yml` cron `0 19 * * *` UTC（Dubai 23:00）

**治理责任**：harness_engineer + integration_qa
**与 content_marketing 边界**：管线生产工具归 Core；产出的内容（lysander.bond 文章）归 content_marketing

**关联文档**：
- 完成报告：`obs/06-daily-reports/2026-04-26-obj-blog-pipeline-cloud-completion.md`
- SLA + 监控：`obs/06-daily-reports/2026-04-26-blog-pipeline-sla-and-monitoring.md`
- 归属评审：`obs/06-daily-reports/2026-04-26-blog-pipeline-product-line-attribution.md`

## 治理机制

- **日常优化**：harness_engineer + knowledge_engineer 主导（L2 专家评审）
- **架构决策**：总裁 + Lysander CEO 直管（L3-L4）
- **Phase 升级**：技术条件触发（非时间表），不按周期推进

## 下一步

- **Phase 2 触发条件**：`@import` 完整性校验机制就绪，或 Claude Code 官方修复静默失败 Bug
- **内容迁出**：CLAUDE.md 内容持续迁出至 `.claude/harness/` 参考模块（升级协议 / HR 评分细则 / 凭证使用说明）
- **熵增预算收紧**：Phase 2 完成后 CLAUDE.md 上限由 350 行收紧至 300 行
- **情报闭环深化**：持续通过情报管线驱动 Core 自我进化

---

**关联文件**：
- Harness Configuration: `CLAUDE.md`
- 决策体系: 定义于 CLAUDE.md 的"决策体系 v2.0"章节
- 审计日志: `logs/ceo-guard-audit.log`
- 跨会话状态: `agent-butler/config/active_tasks.yaml`
