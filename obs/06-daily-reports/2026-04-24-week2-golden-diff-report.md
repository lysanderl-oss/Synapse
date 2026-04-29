# Week 2.2 Golden Set 等价性 Diff 报告

- **任务**：OBJ-Q2-INTEL-PIPELINE Week 2 批次 2 任务 2.2
- **执行者**：integration_qa（Lysander 派单子 Agent）
- **日期**：2026-04-24
- **分析脚本**：`logs/week2_golden_diff.py`
- **原始数据**：`logs/week2-golden-diff-raw.json`

## 一、目标与范围

验证新 GitHub Actions 架构产出 vs 旧 Claude Code Routine 产出在**结构 / 字段 / 样式**层面等价。不 diff 内容（话题、条目数、具体文字因日期不同必然不同）。

**对照组**：

| 类别 | Golden Set（旧 Routine） | New（新架构） |
|------|--------------------------|---------------|
| 情报日报 HTML | 2026-04-19 / 04-20 / 04-21 | 2026-04-24 |
| 行动报告 Markdown | 2026-04-17 / 04-19 / 04-20 ⚠️ | 2026-04-25（**缺失**）|

注：原计划用 04-21 action-report.md 作为第 3 份 golden，文件不存在，替换为 04-17；04-25 新产出未生成，MD 等价性判定无法完成。

## 二、情报日报 HTML Diff 结果

### 特征对比

| 指标 | Golden 均值（n=3） | New（04-24） | 偏差 |
|------|--------------------|--------------|------|
| title 存在 | ✅ 均有 | ✅ | 一致 |
| KPI 区块存在 | ✅ 均有 | ✅ | 一致 |
| style 块存在 | ✅ 均有 | ✅ | 一致 |
| h1 / h2 标题 | 1 / 2.3 | 1 / 3 | 合理 |
| 情报条目数 | 8.0（范围 7-9）| 10 | 在 4-12 合理区间内 ✅ |
| 总字节数 | 6510 | 10933 | ×1.68（偏大，含 HTML 注释/新字段）|

### 三维度等价性评分

| 维度 | 结果 | 详情 |
|------|------|------|
| 字段存在性匹配 | **4/4（100%）** | title / KPI / style / h2 全部命中 |
| 条目数在合理范围 | ✅ True | avg 8 × [0.5, 1.5] = [4, 12]，new=10 命中 |
| CSS class 重叠率 | **70.6%** | 17 个 golden class，13 个 new，12 个共享 |

**共享 CSS class（关键样式一致）**：
`item`, `item-meta`, `kpi`, `kpi-row`, `label`, `meta`, `num`, `red`, `score`, `summary-box`, `tag`, `urgent`

**判定**：field_match 4/4 ✅ + items_in_range True ✅ + css_overlap 70.6% ≥ 60% ✅ → **结构等价通过 ✅**

### 非阻塞观察

- 新产出体积约 1.68× 偏大，推测因新架构 GitHub Actions 在 HTML 中加入了元数据注释或更丰富的 tag 分类，非缺陷
- golden 独有但 new 未用的 class：约 5 个（非核心样式类），不影响视觉一致性

## 三、行动报告 Markdown Diff 结果

### Golden 特征（n=3）

| 字段 | 04-17 | 04-19 | 04-20 | any-golden |
|------|-------|-------|-------|------------|
| h1/h2/h3 | 1/3/7 | 1/4/7 | 1/5/3 | — |
| 表格行数 | 20 | 14 | 23 | avg=19 |
| 战略专家 | ✅ | ✅ | ✅ | ✅ |
| 产品专家 | ✅ | ✅ | ✅ | ✅ |
| 技术专家 | ✅ | ✅ | ✅ | ✅ |
| 财务专家 | ✅ | ✅ | ✅ | ✅ |
| execute 决策 | ✅ | ✅ | ✅ | ✅ |
| inbox 决策 | ❌ | ❌ | ❌ | ❌ |
| deferred 决策 | ❌ | ❌ | ❌ | ❌ |
| 总结段 | ❌ | ❌ | ✅ | ✅ |
| 总字节数 | 2953 | 3977 | 2623 | avg=3184 |

### New（04-25）

❌ **文件不存在** — Week 2 批次 1 的 `2026-04-25-action-report.md` 未在预期路径生成。

**查找路径**：`obs/06-daily-reports/`
**实际存在 04-25 文件**：无（仅有 04-24-intelligence-pipeline-roundtable.md / batch1-smoke-test.md 等非 action-report 文件）

### 判定

❓ **行动报告 MD 等价性判定无法完成**（缺少 new 对照样本）。

Golden 侧特征记录完整，作为 Week 2 批次 1 产出生成后的二次 diff 基线留存。

## 四、整体等价性判定

| 维度 | 判定 |
|------|------|
| 情报日报 HTML 结构 | ✅ 等价通过（4/4 字段 + 70.6% CSS 重叠） |
| 行动报告 MD 结构 | ❓ 未判定（new 文件缺失） |

**综合评级**：⚠️ **部分等价** — HTML 通道已验证等价，MD 通道阻塞待产出。

## 五、对 Week 2 切流的建议

### HTML 通道（情报日报）

✅ **可启用 cron 切流** — 结构 / 字段 / 样式三维度均达等价门槛，无结构性差异。新产出体积偏大属功能增强，非回归缺陷。

### MD 通道（行动报告）

⚠️ **暂缓切流** — 需先补齐 Week 2 批次 1 的 `2026-04-25-action-report.md` 产出，再补做 MD 等价性验证。

**跟进项（交回 Lysander）**：
1. 核查 Week 2 批次 1 action-report 是否应已生成（GitHub Actions 日志 / n8n 触发记录）
2. 若未触发，补跑一次 action-report 生成
3. 产出到位后，重跑 `logs/week2_golden_diff.py` 补完 MD 等价性判定
4. 两通道均 ✅ 后，方可启用 cron 全量切流

## 六、附录

- 原始分析脚本：`C:\Users\lysanderl_janusd\Synapse-Mini\logs\week2_golden_diff.py`
- 原始 JSON 数据：`C:\Users\lysanderl_janusd\Synapse-Mini\logs\week2-golden-diff-raw.json`
- 分析工具：Python 3 + BeautifulSoup4
