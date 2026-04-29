# gstack Skills — Synapse 项目层封装

## 说明

gstack 是一套 AI 工程师工作流技能集（由 Garry Tan / YC 社区维护）。
本目录是 gstack 在 **Synapse 项目层**的封装入口。

源仓库位置（全局层，仅作更新源，不注册为 Skills）：
`C:\Users\lysanderl_janusd\.claude\skills\gstack\`

## 已封装技能

| 指令 | 目录 | 功能 |
|------|------|------|
| `/review` | `../gstack-review/` | PR 预着陆代码审查，分析 diff、安全、SQL 安全等 |
| `/qa` | `../gstack-qa/` | 系统性 QA 测试 + Bug 修复，输出健康分报告 |
| `/ship` | `../gstack-ship/` | 完整发布流程：测试 → bump VERSION → CHANGELOG → PR |

## 架构决策

**方案 B（Synapse 项目层）被选用**，理由：
- gstack 本就是 Synapse rd 团队专用工具，无需跨项目共享
- SKILL.md 随 Synapse git 管理，版本可追溯
- 随 Synapse 迁移时一并携带，不依赖全局环境

## 更新方式

当 gstack 全局仓库有新版本时，由 harness_engineer 执行：
```bash
cp ~/.claude/skills/gstack/review/SKILL.md  Synapse/.claude/skills/gstack-review/SKILL.md
cp ~/.claude/skills/gstack/qa/SKILL.md      Synapse/.claude/skills/gstack-qa/SKILL.md
cp ~/.claude/skills/gstack/ship/SKILL.md    Synapse/.claude/skills/gstack-ship/SKILL.md
```

版本信息参见全局仓库：`~/.claude/skills/gstack/VERSION`
