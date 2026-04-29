---
id: stage4-i18n-architecture
type: core
status: review
lang: zh
version: 1.0
published_at: 2026-04-24
author: ai_systems_dev
review_by: [harness_engineer, execution_auditor, Lysander]
audience: [technical_builder]
stale_after: 2026-07-24
---

# 阶段 4：全站 i18n 架构升级方案

## 目标状态

- **中文版（默认，无前缀）**：`/`、`/services`、`/training`、`/intelligence`、`/about`、`/synapse/`、`/academy/`、`/blog/<slug>`
- **英文版（`/en/` 前缀）**：`/en/`、`/en/services`、`/en/training`、`/en/intelligence`、`/en/about`、`/en/synapse/`、`/en/academy/`、`/en/blog/<slug>`
- 所有页面自动生成 `<link rel="alternate" hreflang="...">`
- 301 重定向保护现有 Forge SEO（`/synapse/*` 英文老链接 → `/en/synapse/*`）
- 中文成为品牌第一语言（与总裁定位一致）

## 现状分析

### 当前技术栈
- Astro `^6.1.3`，`output: 'static'`
- 无 `@astrojs/i18n`、无 `@astrojs/sitemap`
- Forge 双语采用"方案 C 双文件路由"手动维护：
  - `src/pages/synapse/*.astro`（英文默认，7 页）
  - `src/pages/synapse/zh/*.astro`（中文备用，7 页）
- `Layout.astro` 基于 prop `lang` 切换文案（zh-CN / en），已支持双语 header/footer
- `SynapseLayout.astro` 接受 `currentLang` + `altLang` props，手工输出 hreflang

### 需要迁移的资产（未来破坏性）

#### Forge（双语重组 — 破坏性，本次不做）

**选项 1（推荐）**：目录互换
- `src/pages/synapse/zh/*.astro` 7 个文件 → 重命名移动到 `src/pages/synapse/*.astro`（覆盖原英文）
- 原 `src/pages/synapse/*.astro` 7 个文件 → 移动到 `src/pages/en/synapse/*.astro`
- 301 重定向：`/synapse/zh/* → /synapse/*`（旧中文路径归位）；`/synapse/<old-en>/* → /en/synapse/*`（由 _redirects 一条规则处理）

**选项 2**：保留两份，改 Layout 默认语言指向
- 不动文件位置，在 `Layout.astro` / `SynapseSubNav.astro` 层改默认路由
- 缺点：URL 与文件名不直觉，后续维护心智负担大
- **不推荐**

#### 主站 + Academy + Blog（单语 → 双语，本次不做）
- 主页 `/`: 创建 `/en/index.astro`
- `/services`: 创建 `/en/services.astro`
- `/training`: 创建 `/en/training.astro`
- `/intelligence`: 创建 `/en/intelligence.astro`
- `/about`: 创建 `/en/about.astro`
- `/academy/*` 7 页: 创建 `/en/academy/*` 7 页
- `/blog/*` 33 页: 迁移到 Content Collections + 精选 14 篇加英文版

## 架构决策

### 选项 A：Astro 6 原生 i18n（**选择此方案**）

Astro 6 已内置 `i18n` 配置（无需额外 integration）：

```javascript
// astro.config.mjs
export default defineConfig({
  site: 'https://lysander.bond',
  output: 'static',
  i18n: {
    defaultLocale: 'zh',
    locales: ['zh', 'en'],
    routing: {
      prefixDefaultLocale: false  // 中文默认无前缀
    }
  }
});
```

- 路由约定：`src/pages/<file>.astro` → `/`；`src/pages/en/<file>.astro` → `/en/*`
- 内置 helper：`Astro.currentLocale`、`getRelativeLocaleUrl()`、`getAbsoluteLocaleUrl()`
- **未来扩展**（加日语等）成本线性

### 选项 B：手动 `/en/` 目录（不用 i18n 配置）
- 零依赖，完全靠目录约定
- 缺点：失去 Astro 的 i18n helpers，硬编码路径多，易漂移

### 最终选择：**选项 A**
Astro 6 已内置 i18n，零依赖成本；helpers 减少硬编码；与现有 `Layout.astro` 的 `lang` prop 正交，不破坏现有结构。

## 迁移计划（6 步，分批）

### Step 1（**本次会话，无破坏性**）
- 安装 `@astrojs/sitemap`
- `astro.config.mjs` 加 `i18n` 配置（`prefixDefaultLocale: false`）+ `sitemap()` integration
- 本地 build 验证现有 60+ 页不受影响
- 不动 `src/pages/` 下任何内容
- commit + push

### Step 2（**下次会话，破坏性，需 Lysander 审核**）
- Forge URL 互换：
  - 移动 `src/pages/synapse/zh/*.astro` （7 文件）到 `src/pages/synapse/*.astro`（覆盖）
  - 移动原 `src/pages/synapse/*.astro`（7 文件）到 `src/pages/en/synapse/*.astro`
  - 注意 `src/pages/synapse/index.astro`（Forge 首页）特殊处理，index 既是入口也是路由
- 更新 SynapseLayout/SynapseSubNav 中所有硬编码 `/synapse/zh/*` 和 `/synapse/*` 的链接

### Step 3（下次会话）
- 301 重定向配置
- Astro 静态站无原生 301，可选方案：
  - **A. Cloudflare Pages `_redirects` 文件（推荐）**：lysander.bond 托管在 Cloudflare，`public/_redirects` 会被原样发布
  - B. Nginx 配置（若有自管服务器）
  - C. SPA 路由层 JS 302（临时应急）
- 示例 `_redirects`：
  ```
  /synapse/zh/* /synapse/:splat 301
  /synapse/capabilities /en/synapse/capabilities 301
  /synapse/methodology /en/synapse/methodology 301
  ...（7 条 Forge 英文旧链）
  ```

### Step 4（下次会话）
- LangToggle 升级：
  - 重写 `computeTargetUrl()` 以支持全站路由（当前仅支持 Forge 内）
  - 全站所有页 disabled 状态解除（因有英文版了）
  - hreflang 自动化：`Layout.astro` 根据 `Astro.currentLocale` 自动生成 `<link rel="alternate">`

### Step 5（内容并行，不是工程）
- content_strategist + bilingual_editor 产出主页 + Academy + services 英文版
- 博客迁移到 Content Collections + 精选 14 篇加英文

### Step 6
- `@astrojs/sitemap` 自动生成含 hreflang 的 sitemap
- 提交 Google Search Console 变更通知

## 破坏性变更影响评估

### SEO 影响
- `/synapse/*` 英文版迁至 `/en/synapse/*`：SEO 权重暂时分散，301 + hreflang 应缓解
- 过渡期（Google 重索引）：预估 4-8 周
- 风险级别：**中**

### 外部链接
- GitHub README、社交媒体引用、名片等：需手动更新
- Lysander 统筹 growth_lead 做一次全量审计，先搜集所有对外链接清单

### 用户书签
- 现有英文用户书签 `/synapse/capabilities` 等会 301 跳到 `/en/synapse/capabilities`
- 风险级别：**低**（301 透明处理）

## 本次会话实施（Step 1）

1. 安装 `@astrojs/sitemap`
2. `astro.config.mjs` 添加 i18n 配置 + sitemap integration
3. 本地 `npm run build` 验证现有 60+ 页不受影响
4. 不动 `src/pages/` 下任何文件
5. commit + push

**关键验证点**：Astro 6 的 i18n 配置在 `output: 'static'` 下，若 `src/pages/en/` 目录不存在，不应对现有路由有任何影响。Build 产出页数应与上次相同。

## 下次会话实施（Step 2-6）

Lysander 在新会话开始时审核本方案，批准后执行。预估总工程量（U = unit 约半小时工作）：
- Step 2（URL 迁移）：3U
- Step 3（301 redirects）：1U
- Step 4（LangToggle + hreflang）：2U
- Step 5（内容，content_strategist）：内容产能，不计工程 U
- Step 6（sitemap 调优）：0.5U
- 合计：约 **7U 代码** + 大量内容产能

## 风险清单

1. **Astro 6 i18n 在 static output 下的 caveat**：需本次 build 验证；特别是 `prefixDefaultLocale: false` + `src/pages/en/` 是否会触发 Astro 对原有路径的重写
2. **Cloudflare `_redirects` 规则上限**：若超 1000 条需优化（目前不会触及）
3. **LangToggle 过渡期不一致**：Step 2 完成但 Step 4 未完成时，LangToggle 会指错
4. **结构对称性**：`/en/academy` 等子路径必须与中文结构完全对应，否则 404
5. **`prefixDefaultLocale: false` 的已知 Astro caveat**：静态输出下可能与 `src/pages/zh/` 目录冲突；确保不创建该目录

## 回滚策略

- **Step 1 若失败**：revert `astro.config.mjs`；卸载 `@astrojs/sitemap`
- **Step 2 若失败**：`git revert` 相关 commit，恢复 `/synapse/zh/` 目录结构
- **Step 3 若 301 错**：从 `_redirects` 删除或替换为 302（安全版）

## 关键决策点（Lysander 下次会话审核）

1. Forge URL 迁移方式：**选项 1（移动目录，推荐）** vs 选项 2（Layout 改默认）
2. 301 方案：**Cloudflare `_redirects`（推荐）** vs Nginx vs SPA JS
3. 内容优先级：先做 Forge+主页 双语，还是同步推进博客迁移

## 一句话

本会话完成 Step 1（i18n config 预留 + sitemap 安装），下次会话 Lysander 审核本方案后实施 Step 2-4 破坏性迁移。
