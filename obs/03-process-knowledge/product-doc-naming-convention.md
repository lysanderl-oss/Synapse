# 产品文档命名规范

**制定日期**：2026-04-26
**制定人**：knowledge_engineer
**触发背景**：prd-v200-pmo-auto.md 文件名含版本号，持续追加内容后与文件名脱节，引发混淆。

---

## 核心原则

**PRD 及产品规格文档使用产品名称命名，不含版本号。**

| 错误示例 | 正确示例 |
|------------|------------|
| `prd-v200-pmo-auto.md` | `prd-pmo-auto.md` |
| `spec-v1-janus-digital.md` | `spec-janus-digital.md` |
| `requirements-v3-synapse-core.md` | `requirements-synapse-core.md` |

---

## 规则细则

### R1 — 文件命名格式

```
{文档类型}-{产品名称}.md
```

- 文档类型：`prd` / `spec` / `requirements` / `roadmap`
- 产品名称：小写短横线分隔，与产品线编码一致（`pmo-auto` / `janus-digital` / `synapse-core`）
- **禁止**在文件名中出现版本号（`v200` / `v2` / `v1.0` 等）

### R2 — 版本历史跟踪位置

版本演进通过文件**内部 §7（版本里程碑）章节**追踪，不通过文件名区分。

### R3 — knowledge_engineer 触发检查

每次向 PRD/规格文档追加新版本章节时，knowledge_engineer 必须执行：

1. 确认文件名不含版本号
2. 确认文件名与当前产品线编码一致
3. 如有不符，立即提出重命名建议（不等待总裁发现）

### R4 — 历史文件迁移

发现不符合规范的历史文件时：

- 使用 `git mv` 重命名（保留 git 历史）
- 同步更新所有引用
- commit message 注明：`refactor: 文件重命名，符合产品文档命名规范`

---

## 适用范围

- `obs/02-product-knowledge/` 下所有产品文档
- `obs/02-project-knowledge/` 下的项目规格文档

**不适用**：会议纪要、日报（含日期）、验收报告（含日期+版本）——这类文档的日期/版本是关键索引信息，应保留。
