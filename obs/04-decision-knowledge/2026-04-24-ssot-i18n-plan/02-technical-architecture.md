---
id: ssot-i18n-technical-architecture
type: core
status: published
lang: zh
version: "1.0"
published_at: 2026-04-24
author: ai_systems_dev
audience: [team_partner]
---

# 方案 ②：技术架构方案 — Build-time Extract + Astro 原生 i18n

## BLUF

**SSOT 推荐方案 C：Build-time Clone + Extract 脚本，工程量 8U。**
**i18n 推荐 Astro 原生 i18n + Content Collections locale 分离，工程量 22U，全站统一 URL 策略：`/` 中文默认 + `/en/` 英文前缀。**
**总工程量：30U，4 阶段执行。**
**通过 build-time 内容组装 + Content Collections 一次性清理博客 + 学院债务。**

## 一、SSOT 技术路径对比

### 1.1 五方案矩阵

| 方案 | 工程量 | 同步延迟 | 发布解耦 | 版本锁定 | 开发者体验 | 维护成本 |
|------|--------|----------|----------|----------|-----------|----------|
| A. 直接复制 | 2U | 手动 | 无 | 无 | 差 | 最高 |
| B. Git Submodule | 5U | commit 级 | 弱 | 强 | 中 | 中 |
| **C. Build-time Extract** | **8U** | **build 级** | **强** | **强** | **好** | **低** |
| D. npm Package | 15U | 版本级 | 中 | 强 | 好 | 高 |
| E. Headless CMS | 30U | 实时 | 最强 | 弱 | 差 | 最高 |

### 1.2 方案 C 核心设计

**触发链路：**
```
synapse-core.main push → GitHub webhook → Astro site rebuild →
  scripts/extract-synapse-content.mjs 运行 →
  git clone/pull synapse-core 到 .cache/synapse-core/ →
  读取 docs/public/_manifest.yaml →
  按 manifest 复制 md 文件到 src/content/synapse/ →
  注入 frontmatter: source_commit, synced_at, source_path →
  Astro build → deploy
```

**契约文件 `synapse-core/docs/public/_manifest.yaml`：**
```yaml
version: "1.0"
publish_targets:
  - id: harness-101
    source: docs/public/harness-101.md
    target_site: forge
    target_path: learn/harness-101
    required_lang: [zh, en]
  - id: ceo-guard-spec
    source: docs/public/ceo-guard.md
    target_site: synapse-main
    target_path: academy/ceo-guard
    required_lang: [zh]
```

Manifest 是 **公开 API 契约**，非 manifest 列出的文件即使存在于 synapse-core 也不被发布。

**Extract 脚本核心逻辑：**
```javascript
// scripts/extract-synapse-content.mjs
import { execSync } from 'child_process'
import { readFile, writeFile } from 'fs/promises'
import { parse } from 'yaml'

const CACHE_DIR = '.cache/synapse-core'
const MANIFEST_PATH = `${CACHE_DIR}/docs/public/_manifest.yaml`

// 1. 克隆或拉取
await ensureSynapseCoreCache()
const commit = execSync(`git -C ${CACHE_DIR} rev-parse HEAD`).toString().trim()

// 2. 读 manifest
const manifest = parse(await readFile(MANIFEST_PATH, 'utf-8'))

// 3. 逐个 target 提取
for (const entry of manifest.publish_targets) {
  const content = await readFile(`${CACHE_DIR}/${entry.source}`, 'utf-8')
  const injected = injectFrontmatter(content, {
    source_commit: commit,
    synced_at: new Date().toISOString(),
    source_path: entry.source,
    synapse_version: manifest.version
  })
  await writeFile(`src/content/synapse/${entry.id}.md`, injected)
}
```

**缓存策略：**
- `.cache/synapse-core/` 不进 git（.gitignore），但 CI 环境缓存该目录以加速构建
- 每次 build 前 `git pull`，失败则回退到上次成功的缓存
- 本地开发支持 `SYNAPSE_CORE_LOCAL=/path/to/local/repo` 环境变量，绕过 clone 直接指向本地路径

### 1.3 为何不选 B（Submodule）

- Submodule 对内容编辑者不友好：非程序员贡献 synapse-core 内容时需理解 submodule 概念
- Submodule 的 detached HEAD 状态容易产生"修改丢失"困惑
- build-time 组装比 submodule 更灵活：可在构建时注入元数据、按 manifest 过滤、生成 TOC

## 二、i18n 架构

### 2.1 技术选型

- **Astro 6（原生 i18n stable）**：`astro.config.mjs` 中 `i18n: { defaultLocale: 'zh', locales: ['zh', 'en'], routing: { prefixDefaultLocale: false } }`
- **Content Collections locale 分离**：`src/content/blog/zh/` 与 `src/content/blog/en/`，collection schema 统一
- **翻译状态字段**：frontmatter 添加 `translation_of` 指向原文 id，`translation_status` 取值 untranslated/in-progress/review/published/out-of-sync

### 2.2 URL 策略

**推荐：全站统一 `/` 中文默认 + `/en/` 英文前缀。**

理由：
- 用户跨栏目跳转时语言切换行为一致（从 Forge 切到主站不会意外从英文变中文）
- hreflang 标签配置简单，SEO 友好
- 语言选择器实现成本低（同一组件全站复用）

**URL 示例：**
```
synapse.janusd.com/                → 主站中文首页
synapse.janusd.com/en/             → 主站英文首页
synapse.janusd.com/academy/harness-101 → 中文课程
synapse.janusd.com/en/academy/harness-101 → 英文课程
synapse-forge.com/                 → Forge 中文首页
synapse-forge.com/en/              → Forge 英文首页
```

### 2.3 Content Collections Schema

```typescript
// src/content/config.ts
import { defineCollection, z } from 'astro:content'

const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    id: z.string(),
    title: z.string(),
    lang: z.enum(['zh', 'en']),
    translation_of: z.string().optional(),
    translation_status: z.enum([
      'untranslated', 'in-progress', 'review', 'published', 'out-of-sync'
    ]).default('published'),
    published_at: z.date(),
    updated_at: z.date().optional(),
    author: z.string(),
    tags: z.array(z.string()).default([]),
    audience: z.array(z.string()).default([]),
  })
})

export const collections = { blog: blogCollection }
```

### 2.4 语言切换 UX

- 每页右上角语言切换器
- 切换逻辑：当前页有对应翻译 → 跳转翻译；无对应翻译 → 跳转目标语言首页 + toast 提示
- localStorage 记录用户偏好，首次访问按 Accept-Language 头智能重定向

## 三、4 阶段执行计划

### 阶段 1：止血（P0）

- 修复学院/Forge 现存所有错链接（手动扫 30% 错链逐个修）
- synapse-core 公开到 GitHub（依赖总裁决策）
- 建立 `docs/public/` 目录 + 初版 `_manifest.yaml`（7 条核心条目）
- 工程量：3U

### 阶段 2：SSOT 地基

- 实现 `scripts/extract-synapse-content.mjs`
- 配置 GitHub webhook → Astro 重建触发
- Content Collections schema 定义
- frontmatter 注入规范落地
- 工程量：8U

### 阶段 3：学院重构 + Forge 同源

- 学院页面按新 IA 重建（课程 + 认证徽章 + 下载中心）
- Forge get-started 5min/30min 双版本拆分
- 全部中文内容通过 Extract 脚本同步
- 工程量：10U

### 阶段 4：全站 i18n 升级

- 启用 Astro i18n
- 商业页（pricing/about/contact/privacy/terms）双语
- Forge 全站骨架双语
- 学院核心 5 页双语
- 博客 14 篇精选双语（与内容方案联动）
- 工程量：9U

**总计：30U**

## 四、关键技术细节

### 4.1 synapse-core 公开边界

- `docs/public/` 目录下所有 md 文件视同公开 API
- 非 `docs/public/` 的任何文件不得被 Extract 脚本引用
- PR 模板增加 checkbox："本次修改是否涉及 docs/public/ 下文件？若是，请附带影响范围说明。"

### 4.2 frontmatter 注入

Extract 脚本在每个目标文件 frontmatter 顶部注入：
```yaml
source_commit: abc123def
synced_at: 2026-04-24T10:00:00Z
source_path: docs/public/harness-101.md
synapse_version: "1.0"
```

学院/Forge 页面底部显示 "来源：synapse-core @ abc123d · 同步时间：2026-04-24 10:00 UTC"，点击可跳转 GitHub 查看原文。

### 4.3 博客双语渐进迁移

不强制翻译存量博客。新文章发布时按以下流程：
1. 中文版本发布
2. 打 `translation_status: untranslated` 于对应英文 stub
3. 若该文进入 P1 精选池 → content_creator 再创作英文版
4. 英文版 published → 更新 `translation_status: published`
5. 中文版下次重大更新时，英文版自动标记 `out-of-sync`，触发二次翻译任务

## 五、依赖与风险

### 5.1 依赖

- **synapse-core 公开**（L4 总裁决策）
- **Astro 6 i18n stable**（当前 6.2 已 stable，满足）
- **Node 22+**（现服务器 Node 20，需升级）
- **GitHub webhook → build server 连通性**（需配置 Secret Token）

### 5.2 风险

- synapse-core 公开后内容审计成本（见版本管理方案）
- Extract 脚本失败时的 fallback（缓存回退机制已设计）
- 双语内容的 out-of-sync 漂移（依赖版本管理方案的告警机制）

---

**作者**：ai_systems_dev
**日期**：2026-04-24
**审阅**：strategy_advisor + execution_auditor
