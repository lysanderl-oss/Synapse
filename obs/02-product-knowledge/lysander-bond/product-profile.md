---
title: lysander.bond — 品牌内容平台
product_id: lysander_bond
status: published
profile_version: 1.0.0
created: 2026-04-29
updated: 2026-04-29
approved_by: 总裁刘子杨
decision_ref: D-2026-04-29-001
governance: pipeline_product_governance
routing_active: true
split_from: content_marketing
---

# lysander.bond — 品牌内容平台

**产品代号**：lysander_bond  
**状态**：Published  
**Profile 版本**：1.0.0  
**生效日期**：2026-04-29  
**从 Content Marketing 独立拆出**

---

## 一、产品定位

lysander.bond 是 Synapse-PJ 的**对外品牌内容平台**，技术上为独立 git 仓库（Astro 框架），承载博客、情报、产品展示等全部对外内容资产的发布与展示。

**与 Marketing 产品线的关系**：Marketing 负责内容生产与叙事策略，lysander.bond 负责内容发布与站点运营。两者上下游关系：Marketing 生产 → lysander.bond 发布。

---

## 二、技术架构

```
内容生产（Synapse-Mini）
    ↓
GHA 管线（intel-daily / blog-publish / pipeline-daily-sync）
    ↓
lysander-bond git 仓库（lysanderl-glitch/lysander-bond）
    ↓
Cloudflare Pages（主站 lysander.bond）
    └── Volcano Engine（镜像站 synapsehd.com）
```

**关键组件**：
| 组件 | 说明 |
|------|------|
| 框架 | Astro 6（静态站点生成） |
| 主域名 | lysander.bond（Cloudflare Pages） |
| 镜像域名 | synapsehd.com（Volcano Engine，ICP 备案中） |
| 内容集合 | intelligence-daily / decisions / results / blog/zh / blog/en |
| 自动发布管线 | intel-daily.yml / intel-action.yml / pipeline-daily-sync.yml |

---

## 三、版本管理

遵循 **Pipeline Product Governance 三层版本制**（总裁 2026-04-26 批准）：

| 层级 | 规则 | 决策者 |
|------|------|--------|
| MAJOR（x.0.0）| 全站架构重组 | L4 总裁 |
| MINOR（x.y.0）| 新功能/新页面/策略变更 | L3 Lysander |
| PATCH（x.y.z）| Bug 修复/样式微调 | L2 harness_engineer |

**当前版本**：v1.2.0-intelligence-hub  
**版本历史**：v1.0-bilingual → v1.1.0-strategic-overhaul → v1.2.0-intelligence-hub

---

## 四、关键约束（PRINCIPLE）

| # | 约束 | 说明 |
|---|------|------|
| LB-P1 | **main 分支非 PATCH 变更必须关联 tag** | 未打 tag 直接 push 到 main 视为违规，触发 Lysander 复盘 |
| LB-P2 | **MINOR+ 变更须双轮 UAT** | 功能变更必须在测试环境验证后再合并 main |
| LB-P3 | **双语覆盖强制** | 所有新增页面必须同时提供 zh + en 版本，集成 QA 检查 |
| LB-P4 | **synapsehd.com 镜像同步** | 每次 main 分支 push 自动触发 deploy-volcano.yml，保持双站同步 |

---

## 五、委员会成员

| 角色 | Synapse Agent | 职责 |
|------|--------------|------|
| 产品 Owner | Lysander CEO | 版本发布决策（L3） |
| 技术维护 | harness_engineer | GHA 管线、站点架构、部署 |
| 内容发布 | ai_systems_dev | 发布脚本、内容集合 schema |
| 质量门禁 | integration_qa | UAT 验证、双语检查、构建验证 |

---

## 六、关键约束（技术）

| 约束 | 说明 |
|------|------|
| **禁止生成 .astro 博客文件** | 只能输出 Content Collections .md，否则 esbuild 崩溃 |
| **使用 render(post)** | Astro 6 breaking change，post.render() 已移除 |
| **双语同步** | 新增页面必须同时有 ZH + EN 版本 |
| **QA 评分 ≥85** | integration_qa 审查通过后才允许发布 |

---

## 七、快速恢复

| 资源 | 路径/地址 |
|------|---------|
| git 仓库 | `lysanderl-glitch/lysander-bond`（GitHub） |
| 本地路径 | `C:/Users/lysanderl_janusd/lysander-bond/` |
| Cloudflare 部署 | Cloudflare Pages dashboard |
| Volcano 部署脚本 | `.github/workflows/deploy-volcano.yml` |
| 管线治理文档 | `PIPELINE.md`（仓库根目录） |
| 版本基线快照 | `pipeline-metrics/` 目录 |
| synapsehd.com 激活 Runbook | `obs/03-process-knowledge/synapsehd-com-activation-runbook-2026-04-30.md` |

---

**编制**：knowledge_engineer · **生效**：2026-04-29 · **下次审查**：每次 MINOR 版本发布时
