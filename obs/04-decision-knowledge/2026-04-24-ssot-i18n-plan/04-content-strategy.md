---
id: synapse-content-strategy-plan
type: core
status: published
lang: zh
version: "1.0"
published_at: 2026-04-24
author: content_strategist
review_by: [decision_advisor, style_calibrator]
audience: [team_partner]
stale_after: 2026-10-24
---

# 方案 ④：内容策略方案 — 学院重构 + 双语无情优先级

## BLUF

**学院从"聚合页"重构为"课程 + 认证徽章 + 个性化下载中心"。**
**双语战略：英文版少而精（Forge 全 + 学院 5 门 + 博客 14 篇），中文版全量保留。**
**再创作 > 直译**：博客 5 篇英文再创作 > 9 篇双语翻译 > 19 篇保留中文。
**onboarding 双版本同源**：Forge 5min 快速 + Academy 30min 深度，共享 `synapse-core/onboarding-steps.yaml`。

## 一、学院重构蓝图

### 1.1 现状诊断

| 维度 | 现状 | 问题 |
|------|------|------|
| 页数 | 7 页 | 只够放"聚合目录"，深度不足 |
| 语言 | 全中文 | 国际用户 0 触达 |
| 定位 | "使用手册 + 社区" | 与 Forge 严重重叠 |
| 转化 | 无认证、无徽章、无下载追踪 | 流量无沉淀 |

### 1.2 新定位：课程 + 认证徽章 + 个性化下载中心

| 维度 | Forge | Academy（学院） |
|------|-------|-----------------|
| 角色 | 产品门户（what + how-to-buy） | 学习门户（how-it-works + 能力证明） |
| 内容 | 落地页、功能、定价、下载 | 课程、徽章、自定义配置生成器 |
| 受众 | 新访客（决策期） | 已注册用户（学习期 + 能力沉淀） |
| KPI | 注册转化率 | 完课率 + 徽章颁发数 |

### 1.3 新 IA（信息架构）

```
/academy/
  /                      ← Academy 首页：课程地图 + 我的徽章
  /courses/              ← 5 门核心课
    /onboarding/         ← 30min 深度入门
    /harness-101/        ← 45min Harness 基础
    /multi-agent-ops/    ← 60min Agent 团队运营
    /intelligence-pipeline/ ← 45min 情报闭环
    /customization/      ← 60min 自定义扩展
  /certification/        ← 完成徽章墙（P1：仅徽章；P2+：SCP 正式认证）
  /bundle/               ← 个性化配置下载中心（首期 onboarding 定制包）
  /community/            ← P2 再说，首期不做
```

### 1.4 与 Forge 分工

- Forge 用户看到"有 onboarding 课程吗？" → 跳转 Academy
- Academy 用户看到"这个功能怎么用？" → 内嵌 Forge reference 链接
- **onboarding 双版本**：同源于 `synapse-core/onboarding-steps.yaml`，Forge 渲染为 5 步快速摘要，Academy 渲染为 30min 分章节课程

## 二、5 门核心课程

| # | 课程 | 时长 | 受众 | 学习目标 |
|---|------|------|------|---------|
| 1 | **onboarding** | 30min | 首次用户 | 10 分钟跑通第一个 Agent 任务，理解 CEO/团队/执行链基本概念 |
| 2 | **harness-101** | 45min | 想理解原理的用户 | Harness Engineering 三层（Guides/Workflow/Constraints）掌握 |
| 3 | **multi-agent-ops** | 60min | 团队管理者 | Agent HR、派单、评审、决策四级体系落地 |
| 4 | **intelligence-pipeline** | 45min | 进阶用户 | 配置情报发现-评估-执行-报告闭环 |
| 5 | **customization** | 60min | 深度用户 | 新增 Agent、改执行链、自定义 Harness 约束 |

**完成即徽章**（首期不做考试，仅追踪完课）。

## 三、双语优先级（无情选择）

### 3.1 P0（阶段 4 之前必须英文上线）

| 资产 | 理由 |
|------|------|
| 站点骨架（导航、footer、元数据） | 没有骨架就没有 /en/ |
| Forge 全部 7 页 | 产品门户必须双语 |
| Academy 首页 | 学院入口必须国际化 |
| **onboarding 课** | 国际用户第一触点 |
| 商业页（pricing、contact） | 涉及销售转化 |

### 3.2 P1（阶段 5 前期）

| 资产 | 理由 |
|------|------|
| 博客 **5 篇再创作**（见 3.5） | 代表作英文版，SEO + 品牌 |
| harness-101 + multi-agent-ops | 学院核心课双语 |
| SCP 产品页 | 商业化重点 |

### 3.3 P2（阶段 5 后期）

| 资产 | 理由 |
|------|------|
| 博客 **9 篇翻译** | 次优先博客 |
| intelligence-pipeline + customization 课 | 深度课双语 |

### 3.4 P3（暂不英文化）

- 剩余 **19 篇博客**保留中文原版
- Academy 社区、SOP 内部文档不对外

### 3.5 博客 33 篇分级

| 分级 | 数量 | 处理策略 |
|------|------|---------|
| **骨架页**（Forge/Academy 内嵌的博客引用） | — | P0 随站点一起双语 |
| **P1 再创作** | 5 篇 | 英文版重写（非翻译），质量 ≥ 85/100 |
| **P2 翻译** | 9 篇 | AI 翻译 + style_calibrator 校准 |
| **P3 保留** | 19 篇 | 仅中文，不翻译 |

**P1 5 篇再创作选择标准**：
- SEO 潜力（关键词对应英文搜索量）
- 品牌代表性（体现 Synapse 独特方法论）
- 可再创作度（不是时效性新闻）

## 四、翻译质量标准

### 4.1 再创作 > 直译原则

- **P1 再创作**：允许改标题、重组结构、本地化案例。中英文各自是"最好版本"，不追求一一对应
- **P2 翻译**：保持结构，但术语/文风按英文读者习惯调整

### 4.2 双审流程

```
草稿（AI 生成或作者直写）
    ↓
style_calibrator 风格审（词汇/语气/文化）
    ↓
integration_qa 事实审（技术准确 + frontmatter 合规）
    ↓
综合评分 ≥ 85/100 才发布
```

### 4.3 不合格处理

- 60-84：返工一次
- <60：退回选题环节，不发布

## 五、翻译产能估算（AI Agent 非人类）

| 内容类型 | 每周产能 |
|---------|---------|
| 再创作（P1） | 2 篇 |
| 翻译（P2） | 3 篇 |
| 站点静态（UI 字符串） | 1 次全量 |
| 学院课程 | 1 门 / 周 |

**总体估算**：阶段 5（博客迁移期）约 7 周完成 P1+P2 全部。

## 六、SEO 关键词矩阵（14 条核心双语对照）

| 中文关键词 | 英文关键词 | 目标页 |
|-----------|-----------|-------|
| AI CEO | AI CEO | Forge 首页 |
| 多智能体运营 | multi-agent ops | Forge how-it-works |
| Harness 工程 | Harness Engineering | harness-101 课 |
| AI 协作体系 | AI collaboration system | Forge how-it-works |
| AI 执行链 | AI execution chain | multi-agent-ops 课 |
| AI 派单 | AI task dispatch | multi-agent-ops 课 |
| AI 决策体系 | AI decision framework | Forge how-it-works |
| 个人 AI 团队 | personal AI team | Forge 首页 |
| AI 智囊团 | AI advisory team | Forge how-it-works |
| 情报自动化 | intelligence automation | intelligence-pipeline 课 |
| Agent 人力 | Agent HR | multi-agent-ops 课 |
| Claude Code harness | Claude Code harness | harness-101 课 |
| Obsidian 第二大脑 | Obsidian second brain | customization 课 |
| SCP 服务 | SCP (Strategic Co-Pilot) | SCP 产品页 |

## 七、Harness 101 课程大纲（示例完整设计）

### L1. 什么是 Harness Engineering（5min）
- Agent = Model + Harness 公式
- 为什么模型不够用
- 三大支柱：Guides / Workflow / Constraints

### L2. Guides（前馈控制）（8min）
- 什么是"前馈"
- CLAUDE.md 的角色锚定
- 派单制、执行者声明

### L3. Workflow（结构化流程）（10min）
- 执行链 v2.0 六步（含 0.5 承接）
- 分级标准 S/M/L
- QA 硬门禁

### L4. Constraints（约束系统）（10min）
- CEO 执行禁区
- hook 级防护
- 工具白黑名单

### L5. 动手：给你的 Harness 加一条规则（12min）
- 实操：编辑 CLAUDE.md 加约束
- 测试：触发规则
- 审计：查看日志

**完课 → 徽章 `harness-apprentice`**。

## 八、内容运营节奏

### 8.1 学院重构期（阶段 3）
- **停新博客**：全部产能投入学院课程
- **保留情报日报**（自动化，不占人工）

### 8.2 双语并行期（阶段 4-5）
- 每周发 1 门学院课（先中后英）
- 每周发 2 篇 P1 再创作 + 3 篇 P2 翻译
- 博客暂停中文新增，存量消化

### 8.3 商业化期（阶段 5 后）
- SCP 产品页上线
- 学院徽章驱动注册
- 博客恢复中英双语日常节奏（2 篇 / 周）

## 九、与其他团队的接口

| 我方依赖 | 责任方 | 交付物 |
|---------|-------|--------|
| 学院课程视频制作 | product_ops | 课程录制 + 剪辑 |
| 课程技术验证 | integration_qa | 每门课实操步骤可跑通 |
| 术语表维护 | knowledge_engineer | glossary.yaml |
| frontmatter 合规 | harness_engineer | frontmatter_lint |
| onboarding-steps.yaml 单一源 | product_manager | 双版本同源数据 |

## 十、BLUF 收束

**学院收敛**：从 7 页聚合 → 5 门课程 + 徽章 + 下载中心。
**双版本同源**：onboarding 在 Forge（5min）和 Academy（30min）共享 YAML 数据源，不写两次。
**无情优先级**：英文版少而精，26 篇博客做 P1+P2 = 14 篇双语，19 篇保留中文。
**英文版少而精**：再创作 > 翻译，双审 ≥85/100 才发布。

---

## 2026-04-24 决策修正（Stage 4/5 范围扩展）

总裁于 2026-04-24 深夜追加决策：范围选 **B（全站 100% 双语）**，覆盖原 P3 "保留中文" 归档类博客。

### 新策略
- P0 站点骨架 + Forge + Academy：无变化，必双语
- P1 博客精选 5 篇：无变化，full 再创作
- P2 博客 9 篇：无变化，full 翻译
- **P3 博客 19 篇**：从"保留中文"改为"**摘要式英文版**（300-500 字精华 + 中文原文链接）"
- **Changelog / 情报日报历史**：仍视为 "living 内容"，不做回溯翻译（总裁"100% 双语"指人工创作内容，living 数据流由 Lysander 自主判定）

### 产能影响
- 存量英文博客数：14 → **33**
- 产能：P1+P2 按原计划 14 周；P3 批量摘要加速至 4-6 周
- 总计全量补译约 18-20 周可达"全站 100% 双语"指标

---

**作者**：content_strategist
**审阅**：decision_advisor, style_calibrator
**归档日期**：2026-04-24
