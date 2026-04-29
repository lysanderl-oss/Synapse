# WF-06 ASANA_TEAM_GID Fallback 永久化决策

**决策日期**：2026-04-24
**决策者**：总裁刘子杨
**承接人**：Lysander CEO
**执行者**：harness_engineer + knowledge_engineer
**关联需求**：REQ-011（`obs/02-product-knowledge/requirements_pool.yaml:216-231`）
**状态**：wontfix（永久）

---

## 一、决策背景

V2.0 GA 验收遗留项 D-04：WF-06 Asana 团队 GID 使用
`$vars.ASANA_TEAM_GID || '1213938170960375'` 的 fallback 表达式，
本意在未来升级 n8n 付费套餐后切换到 n8n Variables（`$vars`）托管，
移除硬编码 fallback。

REQ-011 原计划在 n8n Variables 功能授权（付费套餐）后执行迁移。

## 二、决策内容

**总裁 2026-04-24 明确决策**：
1. **不升级 n8n 付费套餐**
2. WF-06 的 `$vars.ASANA_TEAM_GID || '1213938170960375'` fallback
   表达式 **永久保留**
3. `'1213938170960375'` 作为最终生产值，不再视为"临时硬编码"
4. REQ-011 标记 **wontfix**，不再进入任何版本 Backlog

## 三、技术影响与维护指引

### 3.1 表达式保留原因
- 技术上 fallback 分支仍能正确工作（n8n 社区版不支持 `$vars` 时
  左操作数为 undefined，自动走 fallback 字符串）
- 保持表达式形式而非裸字符串，便于未来如有变动时最小改动
- 不构成功能缺陷，无性能/安全影响

### 3.2 不应再提出的改进项
- ❌ "移除硬编码改用 n8n Variables"
- ❌ "REQ-011 重新排期"
- ❌ "升级 n8n 套餐以启用 $vars"

除非总裁显式撤销本决策，否则上述建议视为无效 noise，不纳入评估。

### 3.3 如 Asana 团队 GID 变更
直接在 n8n UI 中编辑 WF-06 对应 Code 节点，替换
字符串 `'1213938170960375'` 即可。无需动迁架构。

## 四、本地仓库与远程实例状态

- **本地仓库**：无 WF-06 JSON 副本（n8n workflow 仅托管于远程 n8n 实例）
- **远程 n8n 实例**：WF-06 Code 节点需手动通过 n8n UI 追加 notes 说明
- **替代记录位置**：本决策记录 + `requirements_pool.yaml` REQ-011 条目

## 五、可粘贴的 n8n 节点 Notes 文本

> 维护者后续登录 n8n UI 后，请打开 WF-06 工作流，定位使用
> `ASANA_TEAM_GID` 或 `1213938170960375` 的 Code 节点，
> 在其 **Notes** 字段（节点设置面板底部）粘贴以下文本：

```
[2026-04-24 总裁决策] 不升级 n8n 付费套餐，$vars 表达式保留但永久走 fallback 分支。
维持 '1213938170960375' 硬编码为最终生产值。
REQ-011 已标记 wontfix。参考 requirements_pool.yaml。
```

## 六、审计索引

| 项目 | 位置 |
|------|------|
| 需求池条目 | `obs/02-product-knowledge/requirements_pool.yaml:216-231` |
| 本决策记录 | `obs/03-process-knowledge/wf06-fallback-permanent-2026-04-24.md` |
| V2.0 GA 验收报告 | `obs/06-daily-reports/2026-04-23-pmo-v200-acceptance-report-ga.md` |
| PRD 原始需求 | `obs/02-product-knowledge/prd-pmo-auto.md` |

---

**本决策永久生效，除非总裁显式撤销。**
