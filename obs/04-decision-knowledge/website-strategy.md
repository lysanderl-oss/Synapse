---
title: lysander.bond 网站战略重构方案
date: 2026-04-11
author: Graphify 智囊团 + Growth 团队 + RD 团队联合制定
tags: [网站, 战略, Synapse, 商业化, 内容运营]
decision_level: L3
status: 待执行
---

# lysander.bond 网站战略重构方案

## 一、战略定位

### 从"个人博客"到"商业平台"

| 维度 | 现状 | 目标 |
|------|------|------|
| 定位 | Lysander 的个人 AI 学习笔记 | Synapse by Janus Digital — AI Agent 运营体系 |
| 受众 | 同好/粉丝 | 企业管理者/技术负责人/AI架构师 |
| 目的 | 记录分享 | 获客+引流+品牌+内容资产 |
| 调性 | 随笔风格 | 专业+实践+有温度 |
| 变现 | 无 | 咨询获客入口+培训报名+品牌建设 |

网站使命：让潜在客户了解 Synapse + 通过专业内容建立行业影响力 + 将流量转化为咨询预约和培训报名。

## 二、信息架构（栏目结构）

```
lysander.bond/
├── / (首页)   Hero + 三大服务卡片 + 精选案例/数据 + 最新博客 + CTA
├── /about     Janus Digital介绍 + Synapse体系概述 + 刘子杨简介 + 联系方式
├── /services  Assessment($5K-$10K) + Implementation($30K-$80K) + 建筑AI增值 + CTA
├── /training  SCP课程介绍 + 大纲概要 + 认证说明 + 定价 + 报名CTA
├── /blog      方法论 / 技术指南 / 案例 / 行业洞察
└── /intelligence  最新AI情报日报（公开版）+ 历史归档 + 订阅入口
```

## 三、内容策略

### 现有内容处置

| 内容 | 决定 | 理由 |
|------|------|------|
| 9篇技术博客 | **保留** | 高质量技术内容，加标签重分类 |
| 4篇日记 | **删除** | 生活日记与商业定位不符 |
| /daily 栏目 | **删除** | 用 /intelligence 替代 |

### 内容发布节奏

- 每日：AI 情报日报（自动发布到 /intelligence）
- 每周：1篇深度博客（方法论 或 案例 或 技术指南）
- 每月：1篇行业洞察报告

## 四、品牌视觉规范

延续 Janus Digital 品牌色系：

| 色彩 | Hex | 用途 |
|------|-----|------|
| Gold | #FCAD2A | 品牌主色、CTA按钮、强调 |
| Deep Blue | #013A7D | 标题、导航、专业感 |
| Cyan | #028CDC | 链接、辅助强调、科技感 |
| Dark BG | #0A1628 | 页头/页脚深色背景 |

设计原则：极简、专业、大量留白，深色页头/页脚 + 白色内容区，卡片式布局，响应式（移动端优先）。

## 五、技术方案

技术栈保持不变：Astro + Tailwind CSS，服务器 43.156.171.107，定时构建部署。

需要修改：增加 /services /training /intelligence 页面，更新导航，替换品牌色，更新页头/页脚为 Synapse + Janus Digital 品牌，增加博客 tag 筛选，对接 daily-intelligence HTML 输出。

## 六、SEO 策略

核心关键词：Harness Engineering、AI Agent 团队管理、Multi-Agent 框架、AI 咨询服务、Synapse AI

每个页面添加 meta title + description + og:image；博客文章添加 schema.org 结构化数据；sitemap.xml 自动生成。

## 七、执行计划

**Phase 1（框架重构）**：备份现有网站 → 更新 Astro 结构 → 替换品牌色和页头/页脚 → 创建新页面 → 删除 /daily → 博客重分类 → 部署验证

**Phase 2（内容填充）**：发布 Harness Engineering 实战博客 → 上线服务/培训页面 → 配置情报日报自动发布

**Phase 3（持续运营）**：每日情报自动发布 + 每周博客更新 + SEO 监控和优化 + 转化率追踪
