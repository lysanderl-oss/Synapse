# Notion Hub 操作 SOP

**版本**：v1.0
**生效日期**：2026-04-27
**维护者**：notion_architect
**适用范围**：所有涉及 Lysander-AI Hub 的 Notion 操作

---

## 核心原则

> "每次 Notion 操作都是产品迭代，不是临时任务。"

1. **先读后写**：操作前必须读取 `agent-CEO/config/notion_pipeline_config.yaml`
2. **位置确认**：不得猜测页面 ID，必须从配置文件查找或 API 核查
3. **附件真实**：任何"下载链接"必须是真实可访问的 URL，禁止假链接
4. **操作后更新**：完成后更新配置文件的 known_pages 和 change_log

---

## 操作前检查清单

- [ ] 已读取 notion_pipeline_config.yaml，了解当前页面树
- [ ] 确认目标页面 ID（非猜测）
- [ ] 确认新内容的层级位置（parent page）
- [ ] 如涉及附件，确认使用 approved_methods 中的方案
- [ ] 如需新建页面，已在 planned_pages 中登记

---

## 附件上传标准流程

### 方案A：GitHub Raw URL（推荐）

1. `git add <文件路径>`
2. `git commit -m "docs: add downloadable artifact <名称>"`
3. `git push origin main`
4. 获取 Raw URL：`https://raw.githubusercontent.com/<owner>/<repo>/main/<path>`
5. 在 Notion 中创建 bookmark block 或 pdf embed block（使用 Raw URL）

### 方案B：手动上传（备选）

1. 在 Notion 页面点击 + → Upload file
2. 上传完成后，Notion 自动生成下载链接
3. 将下载链接记录到 notion_pipeline_config.yaml 的对应页面条目中

---

## Notion 高级功能速查

| 功能 | 方式 | 注意 |
|------|------|------|
| 模板导入 | Notion UI → Settings → Import | 不支持 API import |
| 页面复制 | API：duplicate page | 复制含所有 blocks |
| PDF 预览 | API：pdf block + external URL | 需要公开 URL |
| 数据库关联 | Relation property | 只能关联同 workspace 的数据库 |
| 同步 block | Notion UI 手动操作 | API 不支持创建 synced block |
| 分栏布局 | API：column_list + column blocks | 每列最多 100 个 blocks |

---

## 常见错误及预防

| 错误 | 原因 | 预防 |
|------|------|------|
| 写入错误页面 | 使用了缓存的旧 ID | 每次从 pipeline_config 读取，或 API 重新查询 |
| 附件不可下载 | 使用本地路径或假 URL | 只使用 approved_methods |
| 页面树失控 | 操作后未更新配置 | 强制 after_any_operation checklist |
| 内容重复 | 不了解现有内容 | 操作前读取 known_pages |

---

## 管线管理策略（Plan B 全自动，2026-04-27 生效）

### 三层内容架构

| 层级 | 内容 | 自动化方式 | 频率 |
|------|------|-----------|------|
| Layer 1 自动层 | 工作日志 DB | notion_daily_sync.py | 每日 22:00 Dubai |
| Layer 2 事件层 | 成果物 Dashboard + 可下载文档 | OBJ 完成时 Lysander 触发 | 事件驱动 |
| Layer 3 同步层 | 资产全景 / 产品线 / 团队体系 | hub-weekly-sync.yml | 每周日 20:00 Dubai |

### 里程碑触发检查清单（OBJ completed 时执行）

- [ ] 是否有新 PDF/报告？→ `diff-to-notion.py` + 上传到可下载文档
- [ ] Agent 数量是否变化？→ 触发资产全景更新
- [ ] 是否有新产品线？→ 手动更新产品线详情页

### 周度健康报告

每周日 20:00 Dubai 自动发送 Slack 通知，包含：
- 工作日志最近7天条目数
- 各页面可访问性
- 资产数字变化
- 未入 Hub 的新成果物候选列表

### 内容价值过滤器

**进入 Hub**: 可对外展示成果物 | 体系里程碑 | 战略方向 | 资产变化>5
**不进入 Hub**: 过程文件 | 内部技术决策 | 例行工作日志
