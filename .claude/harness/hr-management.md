# Agent HR 管理制度 — 参考模块
# [ADDED: 2026-04-12]
# 本文件由 CLAUDE.md 提取。按需读取，非会话启动时自动加载。
# 触发场景：新增 Agent、Agent 能力审计、HR 入职审批

### Agent HR 管理制度（强制）

**新增 Agent 必须经过 HR 审批**：
1. 任何新增 Agent 必须提交给 `hr_director` 入职审批
2. 卡片必须符合强制 Schema（详见 `obs/03-process-knowledge/agent-hr-management-system.md`）
3. 能力描述必须达到 B 级（具体到方法论/框架），C 级（仅活动名）不合格
4. 新 Agent 默认 `status: probation`，通过评审后 `capability_architect` 升级为 `active`
5. 与现有角色能力重叠 >30% 的不予批准

**能力描述质量标准**：
- A级（优秀）："基于 pytest + Playwright 的端到端测试框架搭建与维护" ← 目标水平
- B级（合格）："SWOT分析、PEST分析、波特五力模型应用"
- C级（不合格）："项目管理"、"知识沉淀" ← 禁止出现

**审计评分标准**（合格线 90 分）：
- **≥90分**：合格，保持 active
- **80-89分**：需优化，限期提升能力描述至 A 级
- **60-79分**：不合格，立即修订
- **<60分**：严重不合格，降级 inactive 或退役

**定期评审**：每周一由 HR 审计 Agent 自动运行 `audit_all_agents()`，<90 分的 Agent 自动触发能力升级。
