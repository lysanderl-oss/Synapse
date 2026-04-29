---
id: visual-qa-checklist
type: harness-fragment
parent: CLAUDE.md
extracted_at: 2026-04-27
moved_per: president decision ①A
---

# Visual QA 强制步骤（UI/前端变更必须执行）

> 触发场景：UI、前端、HTML 报告、Obsidian 视图变更
> 该 checklist 是 CLAUDE.md 执行链【③】QA 节点的必经子步骤

## 流程

1. 部署完成后截图目标页面（桌面端，必要时含移动端）
2. 视觉验收对照表：
   - [ ] 变更效果在截图中可见（非零差异）
   - [ ] 相关页面无明显布局破坏
   - [ ] 截图结果附入交付报告
3. 截图未通过 → 任务不得标记完成，必须返工

## 工具

- `mcp__Claude_in_Chrome`
- `mcp__Claude_Preview`

## 不通过举例

- 截图中找不到声称的变更点
- 文字溢出、按钮错位、配色错乱
- 移动端视图断裂
