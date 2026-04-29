# Synapse 可选扩展（Synapse Ops 层）

Synapse Core 体系开箱即用，零外部依赖。  
以下扩展功能需要特定工具/服务支持，按需启用。

---

## 扩展列表

### 1. n8n 自动化编排

**功能**：定时触发情报管线、自动恢复阻塞任务、任务状态变更通知  
**需要**：n8n 实例（本地 localhost:5678 或云端）  
**参考**：`docs/OPTIONAL_EXTENSIONS/n8n-integration-guide.md`（即将推出）

> 无此扩展时：你的 AI 团队仍可手动执行所有功能，只是需要手动触发。

### 2. Slack / 企业微信通知

**功能**：任务完成/阻塞/升级时主动推送通知  
**需要**：Slack Workspace 或企业微信 API  
**参考**：`docs/OPTIONAL_EXTENSIONS/slack-setup-guide.md`（即将推出）

### 3. 博客/内容自动发布

**功能**：每日自动生成复盘文章 + 发布到指定平台  
**需要**：目标发布平台的 API（WordPress、Ghost、微信公众号等）  
**参考**：`docs/OPTIONAL_EXTENSIONS/blog-publish-guide.md`（即将推出）

### 4. 行业定制团队示例

针对特定行业的 Agent 团队配置示例：

- `janus-team-example.yaml` — 建筑数字化行业团队（IoT、BIM、PMO）
- `stock-team-example.yaml` — 量化交易/金融分析团队（即将推出）
- `saas-team-example.yaml` — SaaS 产品团队（即将推出）

使用方法：将对应文件内容复制到 `agent-butler/config/organization.yaml` 中对应的团队区块。

---

## 自行开发扩展

Synapse 体系是完全开放的框架。你可以：
- 创建新 Agent（在 `obs/01-team-knowledge/HR/personnel/` 添加人卡）
- 创建新 Skill（在 `.claude/skills/` 添加工作流）
- 修改决策规则（编辑 `agent-butler/config/decision_rules.yaml`）
- 创建新的 Harness 自动化（参考现有 n8n 集成模式）

扩展建议：先问 → "这个功能离开远程服务还能不能用？"
- 能用 → 纳入 Core，对所有用户生效
- 不能用 → 归入 Ops，保持 Core 的可移植性

---

*如需帮助构建行业定制方案，欢迎访问 [lysander.bond/academy](https://lysander.bond/academy)*
