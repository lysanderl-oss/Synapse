---
id: product-routing
type: harness-reference
status: active
lang: zh
version: 1.0.0
published_at: "2026-04-28"
updated_at: "2026-04-28"
author: harness_engineer
review_by: [knowledge_engineer, execution_auditor]
audience: [lysander, team_partner]
title: 产品管线路由规则
---

# 产品管线路由规则
# [ADDED: 2026-04-28]
# 触发场景：Lysander 在【0.5】承接阶段识别到产品线关键词时读取本文件

## 产品线路由表

| 关键词 | 产品线 | 知识文件路径 | 委员会成员 |
|--------|--------|-------------|-----------|
| PMO Auto / pmo-api / WF-01~WF-14 / WBS导入 / Asana项目初始化 | PMO Auto | obs/02-product-knowledge/PMO-Auto/product-profile.md | synapse_product_owner, pmo_test_engineer, ai_systems_dev, integration_qa |
| Synapse / CLAUDE.md / Harness / 执行链 / Agent团队 / 体系升级 | Synapse 体系 | obs/02-product-knowledge/Synapse/product-profile.md | harness_engineer, knowledge_engineer, execution_auditor |

## Lysander 路由执行步骤（强制嵌入【0.5】）

当总裁提出需求时，【0.5】承接阶段必须执行：

1. **产品线检测**：扫描总裁输入中的关键词，匹配上方路由表
2. **读取产品知识卡**（如有匹配）：Read `{知识文件路径}`，获取产品当前状态
3. **构建产品上下文摘要**：从 product-profile 中提取：版本 / 关键组件 / 注意事项 / 最近变更
4. **注入派单 prompt**：在每个子 Agent 派单 prompt 的开头加入 `[产品上下文]` 区段
5. **委员会路由**（如适用）：将涉及产品分析的任务优先派给对应委员会成员

## 无关键词匹配时的降级行为（P1-02）

当总裁输入不包含路由表中任何关键词时：
- **直接跳过**产品知识卡读取步骤（步骤 2~5 全部略过）
- **不询问**总裁"请问您说的是哪个产品线"
- **不阻塞**【0.5】承接流程，正常继续任务分析
- 派单 prompt 中不注入任何 `[产品上下文]` 区段

> 判断原则：宁可漏注入产品上下文，也不因产品线识别而打断总裁节奏。

## 派单 Prompt 产品上下文注入模板

当识别到产品线时，在子 Agent 派单 prompt 开头附加：

```
[产品上下文]
产品线：{产品线名称}
当前版本：{版本号}（来自 product-profile.md）
关键组件：{关键组件列表}
最近变更：{最近变更摘要}
注意事项：{约束/PRINCIPLE 列表}
委员会：{相关成员}
详细产品档案：{知识文件路径}（如需更多上下文请 Read 此文件）
```

## Read 失败降级规则（P1-04）

当 `product-profile.md` 不存在或 Read 工具返回错误时：
1. **不阻塞执行**：跳过产品上下文注入，继续执行任务
2. **在派单 prompt 中输出降级标记**，替代完整 `[产品上下文]` 区段：

```
[产品上下文：不可用，请委员会从源系统获取当前状态]
```

3. **不向总裁上报**此技术异常（属于 L1 自动降级，不触发 L4）
4. knowledge_engineer 应在下一个【④】交付阶段补建缺失的 product-profile.md

## 知识卡更新 Checklist（P1-03：【④】交付阶段强制）

每次以下事件发生后，在执行链【④】交付前，knowledge_engineer 必须确认对应 product-profile.md 是否需要更新：

- [ ] 版本发布（VERSION 文件变更）→ 更新 `version` + `profile_version` + 添加 releases/ 发布说明
- [ ] 架构变更（新增/删除关键组件）→ 更新"系统拓扑"和"核心工作流"章节
- [ ] PRINCIPLE 变更（P0/P1 规则修订）→ 更新"关键约束"章节
- [ ] 重大 Bug 修复（P1+ Bug 关闭）→ 更新"委员会快速入职摘要"中的约束点

**未更新视为交付不完整**，integration_qa 在【③】QA 环节检查 `profile_version` 与产品 `version` 是否同步。

## 产品知识卡标准结构（新增产品线时参考）

每个 product-profile.md 必须包含：
1. 系统拓扑（组件、URL、ID）
2. 核心工作流/模块清单
3. 关键约束（PRINCIPLE 列表）
4. 快速恢复（恢复命令/路径）
5. 委员会成员

新增产品线：在路由表添加一行，创建对应目录和 product-profile.md，更新 _index.md。

## 验收测试用例（P1-04）
# [ADDED: 2026-04-28]

| ID | 输入示例 | 预期行为 | 通过标准 |
|----|---------|---------|---------|
| TC-R01 | "PMO Auto WF-11 没有触发" | 关键词命中 `PMO Auto`，【0.5】承接后读取 product-profile.md | 派单 prompt 包含 `[产品上下文]` 区段，委员会成员为 `synapse_product_owner` |
| TC-R02 | "帮我写一篇文章" | 无关键词匹配，跳过读取步骤，直接进入任务分析 | 派单 prompt 中无 `[产品上下文]`，【0.5】不增加延迟，不询问产品线 |
| TC-R03 | "升级 Synapse" | 关键词命中 `Synapse`，读取 `obs/02-product-knowledge/Synapse/product-profile.md` | 若文件为 draft 占位，产品上下文注入 `[产品上下文：不可用，请委员会从源系统获取当前状态]` |
