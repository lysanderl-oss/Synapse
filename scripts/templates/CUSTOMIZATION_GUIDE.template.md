# Synapse 定制指南

本指南帮助你根据自己的业务场景深度定制 Synapse 体系。

---

## 快速个性化（3分钟）

打开 `CLAUDE.md`，使用编辑器全局替换（Ctrl+H）完成以下3处替换：

| 搜索内容 | 替换为 | 说明 |
|---------|-------|------|
| `Lysander` | 你的 AI CEO 名字 | 如 "Alex"、"Aurora"、"助手" |
| `{{PRESIDENT_NAME}}` | 你的名字 | AI 以此称呼你 |
| `{{COMPANY_NAME}}` | 你的公司/团队名 | 出现在组织描述中 |

替换后保存，打开 Claude Code，AI CEO 会立即以你的名字问候你。

---

## 定制团队结构

### 增加 Agent

在 `agent-butler/config/organization.yaml` 中找到对应团队，添加新角色 ID。  
然后在 `obs/01-team-knowledge/HR/personnel/` 创建对应人卡文件（参考现有人卡格式）。

**人卡质量标准（合格线 90 分）**：
- ✅ A 级（优秀）："基于 pytest + Playwright 的端到端测试框架搭建与维护"
- ✅ B 级（合格）："SWOT分析、PEST分析、波特五力模型应用"
- ❌ C 级（不合格）："项目管理"、"知识沉淀" ← 禁止这类模糊描述

### 创建行业定制团队

参考 `docs/OPTIONAL_EXTENSIONS/janus-team-example.yaml` 了解如何为特定行业（如建筑、金融、零售）创建专属团队。

---

## 定制决策规则

编辑 `agent-butler/config/decision_rules.yaml` 调整决策阈值：
- 修改 L4 上报条件（默认：>100万预算 / 法律合同 / 公司存续）
- 调整 L1 自动执行范围
- 新增业务特定决策规则

---

## 定制 Skills 工作流

Skills 位于 `.claude/skills/` 目录，每个 Skill 是一个 `SKILL.md` 文件。

参考现有 Skill 格式，为你的业务场景创建新的工作流：
- 定制行业情报来源（修改 `daily-intelligence-prompt.md`）
- 创建业务特定的执行流程（如销售 CRM 跟进、研发 Sprint 回顾）

---

## 可选扩展（Synapse Ops 层）

以下功能需要特定工具/服务支持，属于可选增强：

| 扩展 | 说明 | 参考文档 |
|------|------|---------|
| n8n 自动化 | 定时触发情报管线、任务恢复 | `docs/OPTIONAL_EXTENSIONS/n8n-integration-guide.md` |
| Slack 通知 | 任务完成/阻塞时通知 | `docs/OPTIONAL_EXTENSIONS/slack-setup-guide.md` |
| 博客自动发布 | 每日自动生成并发布文章 | `docs/OPTIONAL_EXTENSIONS/blog-publish-guide.md` |

---

## 升级体系

当 Synapse 发布新版本，对你的 AI CEO 说：**"升级 Synapse"**

CEO 会自动：
1. 检查远程仓库最新版本
2. 拉取 Core 层文件更新（不影响你的个人配置）
3. 运行 HR 审计确认体系健康（≥90分）
4. 报告升级了什么

---

*Synapse — 让每个人都能拥有一支 AI 专家团队*  
*出品：[lysander.bond](https://lysander.bond)*
