---
id: astro-content-layer-pitfalls
type: reference
status: published
lang: zh
version: 1.0.0
published_at: 2026-04-28
updated_at: 2026-04-28
author: knowledge_engineer
review_by: [Lysander, integration_qa]
audience: [technical_builder]
stale_after: 2027-04-28
---

# Astro Content Layer API 踩坑记录

## Bug：post.render() 在 Astro 6 中已废弃

**发现时间**：2026-04-28  
**影响范围**：所有使用 Content Collections 的动态路由页面  
**严重程度**：P0（构建失败，导致所有新部署无法上线）

### 根因

Astro 6 引入 Content Layer API 后，`post.render()` 实例方法被移除。
必须从 `astro:content` 导入独立的 `render` 函数。

### 错误写法（Astro 5 及以前）

```astro
import { getCollection } from 'astro:content';
const { Content } = await post.render();
```

### 正确写法（Astro 6+）

```astro
import { getCollection, render } from 'astro:content';
const { Content } = await render(post);
```

### 受影响的文件（本次修复）

- `src/pages/intelligence/daily/[date].astro`
- `src/pages/intelligence/decisions/[id].astro`  
- `src/pages/intelligence/results/[date].astro`

### 防复发检查

新增任何使用 Content Collections 的动态路由页面时，必须：
1. import 时包含 `render`：`import { getCollection, render } from 'astro:content'`
2. 调用时使用函数式：`const { Content } = await render(entry)`
3. 不得使用 `entry.render()` 实例方法调用形式

---

## Bug：astro.config.mjs redirect 覆盖实际路由

**发现时间**：2026-04-28

### 根因

`astro.config.mjs` 中的 `redirects` 配置优先级高于 `src/pages/` 下的实际文件。
如果 redirect 指向了一个已建立实际页面的路由，该页面将永远不可达。

### 教训

- 每次新建路由（尤其是 /intelligence/、/academy/ 等）前，先检查 astro.config.mjs redirects
- IA 重构时删除旧 redirect 后，若后续重建该路由，需同步删除 redirect 条目
- 本次案例：/intelligence → /synapse/intelligence（2026-04-26 遗留）覆盖了 /intelligence/ Hub

### 检查命令

```bash
grep -n "intelligence\|academy\|synapse" astro.config.mjs | grep redirects -A 20
```
