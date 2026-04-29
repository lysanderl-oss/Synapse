# LangToggle 修正候选方案（供评审）

**日期**：2026-04-23
**作者**：product_manager + ai_systems_dev（合并工）
**输入依据**：QA + 产品团队 LangToggle 全站走查报告
**受众**：评审团（Lysander + 智囊团 + 相关专家），用于方案筛选
**范围**：不含主站是否要英文版的战略决策——此为评审开放问题

---

## 摘要

基于走查报告确认的事实（类别 A：19 个非 Forge 页面点 EN 无条件跳 `/synapse/`；类别 B：`/synapse/beta` 缺双语白名单；以及 toggle 无跨页偏好记忆），本报告提出 **4 个结构性不同的修正方案**：

- **方案 A（Soft Disabled）**：最小代价，承认"非 Forge 无英文"的现状，视觉明确告知用户
- **方案 B（Hidden Toggle）**：最保守，非双语页面不展示 toggle，把"没得切"变成"看不见切换"
- **方案 C（Modal with Choice）**：最诚实对话式，询问用户意图后再跳转
- **方案 D（Mixed 分治 + 偏好记忆）**：最完整但最贵，按页型分治 + localStorage 记忆 + 补齐 `beta` 双语

**共性底线**：所有方案都必须修 `/synapse/beta` 类别 B 问题 —— 这是事实硬伤，不是选择题。

---

## 方案 A：Soft Disabled + Tooltip

### 1. 方案名
Soft Disabled + Tooltip（视觉置灰 + 悬停提示）

### 2. 核心行为改变
| 场景 | EN 按钮 | 中 按钮 | 说明 |
|------|---------|---------|------|
| 非 Forge 页面（主站 / Academy / Blog） | **disabled 样式**（置灰、`pointer-events: none`） | 保持当前高亮（视为当前语言） | EN 点击不触发跳转 |
| `/synapse/beta` | **disabled 或加入白名单**（二选一，见下） | 当前启用（会跳 `/synapse/zh/`，见类别 B） | 需决策：是否立即补 `/synapse/zh/beta` |
| Forge 7 个双语页 | 保持现有切换行为 | 保持现有切换行为 | 不改动 |

`/synapse/beta` 处理子选项：
- **A1**：beta 加入白名单 + 立即补 `/synapse/zh/beta`（代价小 + 修类别 B 根因）
- **A2**：beta 暂不加入白名单 + 中 按钮也 disabled（延后中文版工作）

### 3. 用户体验（UX）
- **视觉**：EN 按钮变浅灰色（opacity 0.4-0.5），`cursor: not-allowed`
- **点击反馈**：无跳转，无任何弹窗；hover 时显示 tooltip "This page isn't available in English yet"（或中文 "当前页面暂无英文版"）
- **预期心智**：用户立即明白"这里不能切英文"，不会产生"点了之后为什么跳到奇怪页面"的困惑
- **负面心智风险**：部分用户可能以为按钮坏了（需 tooltip 消解）

### 4. 技术实现
- **改动文件清单**：
  - `LangToggle.astro`（第 54-62 白名单，第 87 slug 判断，第 97 return fallback）
  - 新增 CSS `.lang-toggle--disabled` 样式
  - 新增 i18n 文案（EN / ZH 各一条 tooltip）
- **代码改动量**：**小**（~40 行）
- **新依赖**：无（Tooltip 可用原生 `title` 属性或 CSS `::after`，不需引入 UI 库）

### 5. 优点
1. **最诚实**：UI 直接反映"这里不支持英文"的事实，不制造虚假选择
2. **代价最低**：改动集中在单文件，无需补齐内容
3. **不破坏现有 Forge 行为**：Forge 7 页逻辑保持原样

### 6. 缺点 / 风险
1. **不解决"用户想看 Forge 英文门户"的入口发现问题**：原 fallback 的本意是把英文用户引导到 `/synapse/`，disabled 后这个引导消失
2. **视觉可能被误解为 bug**：尤其是国际用户第一次见到灰按钮
3. **Tooltip 移动端不友好**：手机无 hover，需额外设计移动端文案展示（或接受此缺陷）

### 7. 实施代价
- **开发工作量**：1-2 U（含 QA 回归 Forge 切换）
- **同步文档**：需更新站点 i18n 规范 1 条（"非双语页面 toggle 行为"）

---

## 方案 B：Hidden Toggle on Non-Bilingual

### 1. 方案名
Hidden Toggle on Non-Bilingual（非双语页面隐藏 toggle）

### 2. 核心行为改变
| 场景 | EN 按钮 | 中 按钮 | 说明 |
|------|---------|---------|------|
| 非 Forge 页面 | **不渲染** | **不渲染** | 整个 toggle 组件在页面上不存在 |
| `/synapse/beta` | 不渲染（除非加入白名单） | 不渲染 | 同方案 A，beta 处理需单独决策 |
| Forge 7 个双语页 | 正常渲染 + 切换 | 正常渲染 + 切换 | 不改动 |

### 3. 用户体验（UX）
- **视觉**：主站首页 / Academy / Blog 页面**完全看不到** EN|中 切换器
- **点击反馈**：无按钮可点
- **预期心智**：用户在 Forge 相关页面会看到 toggle，其他页面不会产生"可切换语言"的预期
- **负面心智风险**：英文用户根本不知道 Synapse Forge 有英文门户（缺乏发现性）

### 4. 技术实现
- **改动文件清单**：
  - `LangToggle.astro` 加入 `isBilingualPage(pathname)` 判断，若 false 则 `return null`
  - 检查 Header / Footer 中 `<LangToggle />` 使用位置，确保隐藏逻辑统一
- **代码改动量**：**小**（~20 行）
- **新依赖**：无

### 5. 优点
1. **最保守**：不新增任何 UX 概念，用户不会困惑
2. **代码最干净**：无 disabled 态、无 tooltip、无 modal，只有一个布尔判断
3. **不产生"坏按钮"视觉疑虑**

### 6. 缺点 / 风险
1. **完全失去发现性**：英文用户访问中文主站（如从外链进入 `/blog/xxx`）无任何途径进入 `/synapse/` 英文门户
2. **Header 视觉不一致**：Forge 页有 toggle、主站页没有，用户跨页浏览时会感觉"UI 不稳定"
3. **与现有 fallback 意图冲突**：原代码的 fallback 跳 `/synapse/` 本意是把英文用户往英文门户导，此方案直接废弃了这个意图

### 7. 实施代价
- **开发工作量**：1 U（最小）
- **同步文档**：需更新 Header 组件规范 1 条

---

## 方案 C：Explicit Modal with User Choice

### 1. 方案名
Explicit Modal with User Choice（显式 Modal 让用户选择）

### 2. 核心行为改变
| 场景 | EN 按钮 | 中 按钮 | 说明 |
|------|---------|---------|------|
| 非 Forge 页面，首次点 EN | **弹出 Modal** | 保持当前高亮 | Modal 内容："Our English content is focused on Synapse Forge. Would you like to visit our English product portal?" |
| 非 Forge 页面，已选过"Yes" | 直接跳 `/synapse/` | 保持当前高亮 | localStorage 记忆 |
| 非 Forge 页面，已选过"No" | 不跳转（静默 or 再次 Modal） | 保持当前高亮 | localStorage 记忆 |
| `/synapse/beta` | 同非 Forge 逻辑 or 加白名单 | 当前行为 | 需决策 |
| Forge 7 个双语页 | 保持现有切换行为 | 保持现有切换行为 | 不改动 |

### 3. 用户体验（UX）
- **视觉**：EN 按钮正常显示（不置灰）
- **点击反馈**：首次点击弹出轻量 Modal（非全屏，居中），含两个按钮 "Visit English Portal" / "Stay on this page"
- **预期心智**：用户理解"点 EN 不是简单切换当前页，而是跳到英文产品门户"；给用户决策权
- **负面心智风险**：Modal 在日常交互中被视为打扰；用户可能选 No 后仍困惑为何 EN 按钮还在

### 4. 技术实现
- **改动文件清单**：
  - `LangToggle.astro`（修改 click handler，改为触发 Modal）
  - 新增 `LangRedirectModal.astro` 组件（或 inline 到 Header）
  - 新增 Modal 相关 CSS
  - 新增 localStorage key: `lang_pref_ack`
  - 新增 i18n 文案（Modal title / body / button × EN+ZH）
- **代码改动量**：**中**（~120-180 行，含 Modal 组件 + 样式 + i18n）
- **新依赖**：无（Astro 原生 Modal 足够，不需要 Radix / Headless UI）

### 5. 优点
1. **最尊重用户意图**：不替用户决定跳不跳转
2. **保留发现性**：英文用户明确被告知"有英文门户可访问"
3. **Modal 文案可承载品牌声音**：有空间解释"Synapse Forge 是我们的英文产品线"

### 6. 缺点 / 风险
1. **交互打断**：Modal 是典型的 UX 反模式（尤其对已知情的回访用户，即使有 localStorage 也只覆盖同一浏览器）
2. **实现复杂度跳升**：一旦引入 Modal 组件，后续其他 UX 讨论都会想往里塞内容（范围蔓延风险）
3. **i18n 复杂度**：Modal 文案本身需要双语，若文案翻译不当会放大违和感

### 7. 实施代价
- **开发工作量**：3-4 U（Modal 组件 + 样式 + localStorage + QA + 移动端适配）
- **同步文档**：需更新 i18n 规范 + Modal 组件规范 + localStorage key 清单

---

## 方案 D：Mixed 分治 + 偏好记忆（最完整）

### 1. 方案名
Mixed by Page Type + localStorage Preference（按页型分治 + 偏好记忆）

### 2. 核心行为改变
| 场景 | EN 按钮 | 中 按钮 | 说明 |
|------|---------|---------|------|
| 主站非 Forge 页（`/`、`/services`、`/about` 等） | **disabled + tooltip**（方案 A 风格） | 当前高亮 | 诚实告知无英文版 |
| `/blog/*` | **若该文有英文版**：跳英文版 URL；**若无**：disabled + tooltip | 当前高亮 | 需文章 frontmatter 标记 `hasEnglish: true/false` |
| `/synapse/beta` | **加入双语白名单** | 跳 `/synapse/zh/beta`（需创建） | 首批补齐 `beta` 双语是硬要求 |
| `/academy/*` | disabled + tooltip | 当前高亮 | 同主站非 Forge |
| Forge 7 个双语页 | 保持现有切换行为 | 保持现有切换行为 | 不改动 |
| **跨页偏好记忆**（可选 feature flag） | 首次访问后记录用户偏好；偏好英文用户从 `/` 首次加载自动跳 `/synapse/` | 同左 | 独立 feature flag，默认关闭，A/B 可控 |

### 3. 用户体验（UX）
- **视觉**：按页型差异化 —— 主站 / Academy disabled、Blog 按文章有无英文版变化、Forge 保持现状、`beta` 变成双语
- **点击反馈**：disabled 页面同方案 A；博客有英文版时 EN 按钮高亮可点；Forge/beta 正常切换
- **预期心智**：用户从 toggle 状态能**读出当前页的双语支持程度**，逐步建立"Synapse Forge 是双语产品、主站和博客按内容而定"的心智
- **负面心智风险**：不同页面行为不一致，首次访问时需要学习；Blog 按文章变化的 EN 按钮需要清晰视觉区分

### 4. 技术实现
- **改动文件清单**：
  - `LangToggle.astro`（重构 slug 判断 + 白名单扩展 + 按页型分支）
  - Blog frontmatter schema 增加 `hasEnglish: boolean` 字段（`src/content/config.ts` 或等价位置）
  - 新增博客英文版 URL 生成规则（如 `/blog/en/<slug>`）
  - 新增 `/synapse/zh/beta` 页面（中文版 beta 内容，内容团队协作）
  - localStorage key: `lang_pref`（仅在启用 feature flag 时生效）
  - 新增 CSS disabled 样式 + tooltip
  - i18n 文案
- **代码改动量**：**大**（~250-350 行，含 blog schema + 中文 beta 页 + localStorage + 多处分支）
- **新依赖**：无（但需要内容团队协作创建 `/synapse/zh/beta`）

### 5. 优点
1. **最诚实且最完整**：按页型讲实话，而不是一刀切
2. **修复类别 B 根因**：`beta` 纳入白名单 + 补齐中文版，是真正的根因修复
3. **为未来博客双语留出扩展位**：`hasEnglish` frontmatter 让后续博客逐步双语变成低成本动作

### 6. 缺点 / 风险
1. **实施代价最高**：涉及代码 + 内容 + schema + QA 多方协作
2. **localStorage 偏好记忆是典型过度设计诱因**：若用户在公共电脑登录、或清 cookie，体验会回落到初次访问
3. **Blog 分支逻辑增加长期维护成本**：每篇博客需要决策是否出英文版 + 记在 frontmatter，若漏填会回退到 disabled

### 7. 实施代价
- **开发工作量**：6-8 U（拆 3 个子任务：核心 toggle 重构 + beta 中文版 + 偏好记忆 feature flag）
- **同步文档**：需更新 i18n 规范、博客写作规范、feature flag 清单、内容团队 SOP

---

## 方案对比矩阵

| 维度 | A (Soft Disabled) | B (Hidden) | C (Modal) | D (Mixed) |
|------|------|------|------|------|
| **UX 诚实度** | 高（视觉明示） | 中（隐藏=不承认有限制） | 高（对话式） | 最高（按页分治讲实话） |
| **实施代价** | 小（1-2 U） | 最小（1 U） | 中（3-4 U） | 大（6-8 U） |
| **引入新概念** | Tooltip | 无 | Modal + localStorage | 分治 + frontmatter + 可选偏好记忆 |
| **对现有 Forge 功能影响** | 无（Forge 逻辑不动） | 无 | 无 | 无（Forge 7 页保留） |
| **未来扩展性** | 低（disabled 是终态，难演进） | 低（隐藏后加回成本高） | 中（Modal 可承载更多信息） | 高（frontmatter 机制可扩展） |
| **破坏性变更** | 无 | 无（但 toggle 位置变化会影响 Header 视觉一致性） | 无 | 中（Blog frontmatter schema 变更） |
| **发现性**（英文用户找 Forge 英文门户） | 差（按钮不可点） | 最差（完全无提示） | 好（Modal 明示） | 中（主站仍 disabled，但 Blog/beta 场景改善） |
| **修复类别 B（beta）** | 需单独决策 A1/A2 | 需单独决策 | 需单独决策 | 内置修复 |
| **修复 toggle 无偏好记忆** | 不修 | 不修 | 部分（Modal 选择记忆） | 可选修（feature flag） |
| **移动端友好度** | 中（无 hover，tooltip 退化） | 高（无交互问题） | 中（Modal 需适配） | 中 |

---

## 共性：所有方案必须修复的最低项

无论评审选哪个方案，以下必须做：

1. **`/synapse/beta` 类别 B 问题**：`LangToggle.astro:54-62` 白名单必须加入 `beta` 或从 toggle 渲染列表明确排除。**决策点**：是否立即补 `/synapse/zh/beta` 中文版？
   - 若补 → 加入白名单，正常双语
   - 若不补 → 从 toggle 识别中排除，按方案 A/B/C/D 各自的非 Forge 页处理规则兜底
2. **博客 EN 按钮行为**：当前博客点 EN 跳 `/synapse/` 毫无合理性，必须从 4 个方案中择一改正
3. **移除类别 A 的 `return '/synapse/'` 无条件 fallback**（`LangToggle.astro:97`）：4 个方案都要求移除此行或改其语义

---

## 开放问题（评审需回答）

1. **非 Forge 页面的 EN 按钮是否该"提醒用户 Forge 英文门户存在"？** 
   - 这是方案 B（彻底不提）vs 方案 C（Modal 显式提）vs 方案 A（disabled，不提但也不阻断）的核心差异点
2. **主站首页 `/` 应该有英文版吗？** 
   - 若"有计划，半年内要做" → 倾向方案 D（为扩展留位）
   - 若"不做，Synapse Forge 是唯一英文产品面" → 倾向方案 A 或 B
3. **`/synapse/beta` 首期仅英文还是立即双语？** 
   - 这是共性底线里的必答题
4. **跨页偏好记忆是否值得做？** 
   - 仅在方案 D 可选；若评审团认为"偏好记忆只服务少数高频英文用户"，应砍掉以压缩范围
5. **博客双语策略**：
   - 是否要求每篇博客后续都出英文版？若否，Blog EN 按钮默认行为应该是什么？

---

## 推荐（product_manager + ai_systems_dev 综合视角）

**推荐第一选：方案 A（Soft Disabled + Tooltip）+ A1 子选项（补 `beta` 双语）**

理由 3 条：
1. **代价/收益比最优**：1-2 U 工作量即可消除 19 个页面的 UX 误导，类别 A 根因被直接切除
2. **避免过度设计**：Modal（方案 C）和 frontmatter 分治（方案 D）在当前阶段引入的长期维护成本超过了 UX 收益
3. **留有演进空间**：若未来决定博客双语或主站英文化，可以在 A 的基础上逐页"解封"（把页面加入白名单 + 补内容），不会被 A 锁死

**推荐第二选：方案 D（但延后到 Phase 2）**

理由：D 是最完整的长期方案，但现在做性价比不足。正确做法是先 A 止血 + 补 `beta` 双语，然后观察用户行为（是否真的有英文用户在主站乱点 EN），再决定是否升级到 D。

**明确不推荐：方案 C（Modal）**

理由：
1. Modal 是 UX 反模式，当前类别 A 的 19 个页面点击频率未必高到需要 Modal 级别的介入
2. Modal 文案的双语翻译质量要求高，若翻译不到位反而放大违和感
3. localStorage 记忆只能解决同浏览器问题，无法解决跨设备/清 cookie/隐私模式用户的重复 Modal 骚扰

**明确不推荐：方案 B（Hidden）**

理由：彻底隐藏 toggle 会导致英文用户在主站完全无法发现 Synapse Forge 英文门户的存在，这是**把已有的 UX 缺陷转化为发现性黑洞**，不是修复。

---

## 实施风险提示（所有方案共通）

1. **Forge 7 页白名单漂移**：无论选哪个方案，都需要保障 `BILINGUAL_FORGE_SLUGS` 列表与实际存在的双语页一一对应；未来新增 Forge 双语页时，这个列表必须被同步更新（否则类别 B 会以新形态复发）
2. **i18n 文案的双语一致性**：tooltip / Modal 文案的中英文必须在同一次 PR 内交付，不允许"先上英文，中文后补"
3. **Header 缓存策略**：若站点使用静态生成（Astro SSG），toggle 逻辑依赖 `window.location.pathname` 的客户端判断本身是合理的，但需在部署后 QA 验证 CDN 缓存不会导致 toggle 状态错位
4. **现有 `/synapse/` 门户流量监控**：无论哪个方案上线，都应在上线前后对比 `/synapse/` 的入站流量，防止意外砍掉了一个有效的英文用户入口而不自知
5. **移动端 hover 失效**：方案 A 依赖 tooltip，方案 D 部分页面也用 tooltip —— 移动端需额外处理（点击一次显示 tooltip，再点才跳转 or 放弃 tooltip 用其他视觉提示）

---

## 一句话给评审团

**先用方案 A 止血（含补齐 `/synapse/zh/beta`），观察真实用户行为一段时间后再决定是否升级到方案 D；方案 B 和 C 不推荐。**
