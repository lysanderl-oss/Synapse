---
title: Synapse 产品化架构方案 — Core/Ops 分离 + 订阅升级模型
date: 2026-04-12
author: Graphify 智囊团 + Growth 团队 + RD 团队
tags: [Synapse, 产品化, 架构, 商业模式, 版本管理]
decision_level: L3
---

# Synapse 产品化架构方案

## 一、商业模式

```
免费：初始化同步一次 Synapse Core → 永久使用 → 不收费
付费：持续订阅 Synapse Evolution → 每天/每周同步最新版 → $XX/月

总裁环境（上游）             用户环境（下游）
├── 每天自动进化              ├── 初始化 clone 一次
├── 情报+牛人+GAP分析         │   → 免费用户到此为止
├── 能力融合+Agent升级         │
├── 体系持续优化              ├── 订阅升级
└── 发布新版 Synapse Core     │   → 每天/每周同步最新Core
                              └── 用户自己的私有数据不受影响
```

## 二、架构分层

### 三层分离

- **Layer 1: Synapse Core（可分发）** — CLAUDE.md、organization.yaml、decision_rules.yaml、HR/personnel/*.md、*_experts.yaml、hr_base.py、scripts/*.py、方法论文档。版本化管理，免费用户获取初始版，付费用户持续同步。
- **Layer 2: Synapse Templates（Prompt模板）** — daily-intelligence-prompt.md、intelligence-action-prompt.md 等。随Core一起分发，用户可按行业定制。
- **Layer 3: User Private（用户私有，不分发）** — obs/00-daily-work/、active_tasks.yaml、credentials.mdenc、远程定时任务配置等。永远不进分发包。

### 文件归属分类

| 文件/目录 | 层级 | 升级时覆盖 |
|-----------|:----:|:----------:|
| CLAUDE.md | Core | ✅ 覆盖 |
| organization.yaml | Core | ✅ 覆盖 |
| HR/personnel/**/*.md | Core | ✅ 覆盖（能力进化） |
| hr_base.py | Core | ✅ 覆盖 |
| n8n_integration.yaml | Template | ❌ 不覆盖（环境绑定） |
| active_tasks.yaml | Private | ❌ 不碰 |
| obs/00-daily-work/ | Private | ❌ 不碰 |
| credentials.mdenc | Private | ❌ 不碰 |

## 三、版本管理机制

### 版本号规则

```
Synapse v{MAJOR}.{MINOR}.{PATCH}

MAJOR: 架构级变更（执行链重构、决策体系变更）
MINOR: 能力进化（新Agent、能力升级、新方法论）
PATCH: 小修复（描述优化、Bug修复）
```

### 版本文件

根目录 `VERSION` 文件保存当前版本号。`CHANGELOG.md` 记录每个版本变化。

## 四、用户升级流程

### 免费用户（初始化一次）

```
1. git clone https://github.com/lysanderl-glitch/synapse-core.git
2. 打开 CLAUDE.md，按顶部说明替换3个名字（3分钟）
3. 打开 Claude Code — Synapse 立即生效
```

### 付费用户（持续同步）

方式A（推荐）：在 Claude Code 中说"升级 Synapse" — CEO 自动拉取 Core 层更新、保留 Private 层、运行 HR 审计、报告变更。

方式B：手动 `git fetch upstream && git merge upstream/main --no-commit`

### 升级安全机制

升级前自动备份 → 拉取新版 Core → 运行 audit_all_agents()（确认分数≥90）→ 检查用户自定义是否被覆盖 → 通过则完成升级，失败则自动回滚。

## 五、收费模型

| 层级 | 内容 | 价格 |
|------|------|------|
| **Free** | 初始化同步 v1.0.0，永久使用 | $0 |
| **Evolution** | 持续同步最新 Core + 每周成长报告 | $99/月 |
| **Evolution Pro** | 上述 + 定制行业情报 + 优先新功能 | $299/月 |
| **Enterprise** | 上述 + 专属支持 + 定制Agent团队 | $999/月 |

## 六、实施路径

### 立即做

1. 创建 `VERSION` 文件（v1.0.0）
2. 创建 `CHANGELOG.md`
3. 确保 CLAUDE.md 顶部"个人化配置区"完整可用
4. 验证：新用户 clone → 改3个名字 → 打开 Claude Code → 体系生效

### 近期做

5. 创建 `synapse-core` 分发仓库（只含 Core 层）
6. 编写升级脚本（synapse upgrade 命令）
7. 设计付费验证机制

### 后续做

8. 建立自动化发布流程
9. 上线订阅支付（Stripe/LemonSqueezy）
10. 建立用户社区

## 七、评审

均分 5.0 → 推荐执行（strategist/gtm_strategist/decision_advisor/tech_lead/customer_insights_manager 全部评分5）
