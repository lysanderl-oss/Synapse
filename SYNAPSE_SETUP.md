# Synapse 快速接入指南

**5分钟上手，拥有属于你自己的 AI CEO 团队。**

> 获取邀请码或申请加入：[lysander.bond/academy](https://lysander.bond/academy)

---

## 什么是 Synapse？

Synapse 是一套运行在 Claude Code 上的 **AI 公司操作系统**。

接入后，你拥有：
- 一位 **AI CEO**（替你统筹调度，你只需提目标）
- **44 位 AI 专家**分10支团队（研发/运营/战略/内容/情报等）
- **四级决策体系**（小事自动执行，大事才问你）
- **每日自动化流水线**（情报→分析→执行→汇报，全自动运转）

> 你只需要：**提出目标 → 等待结果 → 验收交付**

---

## 接入步骤（三步完成）

### 第一步：获取 Synapse 配置包

**方式 A（推荐，零门槛）**：
访问 [lysander.bond/academy](https://lysander.bond/academy) → 填写你的 CEO 名称和你的名字 → 下载个性化配置包（已自动完成个人化，跳过第二步）

**方式 B（技术用户，GitHub）**：
打开 PowerShell，粘贴运行：
```powershell
Invoke-WebRequest -Uri 'https://github.com/lysanderl-glitch/ai-team-system/archive/refs/heads/main.zip' -OutFile "$env:USERPROFILE\Downloads\synapse.zip"
Expand-Archive -Path "$env:USERPROFILE\Downloads\synapse.zip" -DestinationPath "$env:USERPROFILE\Claude Code" -Force
Rename-Item -Path "$env:USERPROFILE\Claude Code\ai-team-system-main" -NewName 'ai-team-system' -ErrorAction SilentlyContinue
```
完成后，文件位于：`C:\Users\你的用户名\Claude Code\ai-team-system`

---

### 第二步：个人化配置（仅方式 B 需要，2分钟）

打开文件夹中的 `CLAUDE.md`，按顶部说明做三处全局替换（Ctrl+H）：

| 替换内容 | 说明 |
|---------|------|
| `Lysander` → 你的 AI CEO 名字 | 如 "Alex"、"Aurora"、"助理" |
| `刘子杨` → 你的名字 | AI 会以此称呼你 |
| `Synapse-PJ` → 你的公司/团队名 | 出现在组织描述中 |

替换后保存文件。

---

### 第三步：用 Claude Code 打开，发送任意消息

1. 打开 **Claude Code**
2. 点击 **Open Folder** → 选择 `ai-team-system` 文件夹（含 `CLAUDE.md` 的那个）
3. 在对话框发送任意内容

收到 AI CEO 的问候语，说明接入成功：
> **"[你的名字]您好，我是 [CEO名称]，Multi-Agents 团队为您服务！"**

> ⚠️ **如果没有出现问候语**：确认 Claude Code 打开的是含 `CLAUDE.md` 的根目录。

---

## 如何升级体系

当 Synapse 发布新版本，直接对你的 AI CEO 说：

> **"升级 Synapse"**

CEO 会自动获取最新版本、展示变更内容，确认后完成升级。你的个人化配置（CEO名/你的名字）不受影响。

---

## 进阶资源

- 📖 **Multi-Agents 学院**：[lysander.bond/academy](https://lysander.bond/academy)
- 🔧 **核心配置**：`CLAUDE.md`（Harness 配置，修改团队规则）
- 👥 **团队结构**：`agent-butler/config/organization.yaml`（增删 Agent）
- 📋 **任务状态**：`agent-butler/config/active_tasks.yaml`（跨会话任务追踪）
- 🔄 **升级日志**：`VERSION`（当前体系版本）

---

## 常见问题

**Q：数据安全吗？**
Synapse 完全运行在你本地，数据不经过任何第三方（除 Anthropic Claude API）。

**Q：需要付费吗？**
Synapse 配置包本身免费开放。运行需要 Claude Code 订阅（由 Anthropic 提供）。

**Q：可以定制团队结构吗？**
可以。通过学院的定制工具，或直接编辑 `agent-butler/config/organization.yaml`。

**Q：如何获得邀请？**
前往 [lysander.bond/academy](https://lysander.bond/academy) 申请。

---

*Synapse — 让每个人都能拥有一支 AI 专家团队*
*出品：[lysander.bond](https://lysander.bond)*
