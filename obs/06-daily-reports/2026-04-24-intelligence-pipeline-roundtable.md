---
title: 情报管线架构圆桌会议纪要
date: 2026-04-24
chair: synapse_product_owner
attendees: [harness_engineer, ai_ml_engineer, strategy_advisor, graphify_strategist, financial_analyst, integration_qa]
status: recommendation_ready
for_review: Lysander → 总裁审批
---

# 情报管线架构圆桌会议纪要

## 会议摘要（TL;DR）

- **问题**：情报管线当前绑定总裁本地电脑 + Claude Code Max 个人订阅，无法产品化、无法支撑 Janus Digital SKU 变现。
- **分歧**：4 方分别主张"一周速建 n8n（D）/ 今晚 Routines MVP 再 Managed Agents（A→C）/ 产品化优先（阶段性）/ GitHub Actions 成本可控（B）"，根源在于"产品化优先级 vs 实施工时"的时间权衡差异。
- **推荐**：四阶段综合方案 —— 阶段 1 今晚 Routines MVP 解耦本地电脑；**阶段 2 Q2 选方案 B（GitHub Actions + Claude API）作为内部生产底座**（加权 4.35 胜出），Slack 四层分层为硬前置；阶段 3 Q3 多租户灰度；阶段 4 Q4 Janus SKU 商品化上市。

---

## 一、会议背景与问题陈述

### 1.1 总裁原话诉求

> "情报管线绑死在本地电脑和个人 Max 订阅上，**无法有效产品化**。需要一条能支撑 Janus Digital 对外售卖的生产架构。"

### 1.2 问题拆解

| 层面 | 当前状态 | 产品化阻塞点 |
|------|---------|-------------|
| 运行环境 | 总裁本地 Windows + Claude Code | 总裁不在电脑前就停摆 |
| 账号合规 | Max 个人订阅（$200/月） | 个人订阅不允许商业多租户转售 |
| 架构耦合 | Claude Code CLI 直接调 MCP 与本地文件 | 无 API 边界，无法做客户隔离 |
| 成本归集 | 与总裁个人生活混账 | 无法按客户计费 |
| Slack 通知 | 单通道告警扎堆 | 客户 dashboard 无法分层交付 |

### 1.3 本次圆桌的产出目标

- 合并 4 方 8 位专家立场
- 识别实质分歧
- 给 Lysander 一个可决策的 3 选 1 技术栈矩阵 + 四阶段路线图

---

## 二、4 方立场陈列

| 角色 | 推荐方案 | 加权/评级 | 关键数据点 | 说服力弱项 |
|------|---------|----------|-----------|-----------|
| **harness_engineer** | **方案 D n8n 原生** | 4.75（最高） | n8n.lysander.bond 生产实例已上线；HMAC + Credentials 规范已落地；1 周完成；零新增基础设施 | 未回答"n8n 是否能支撑多租户 SaaS 形态"；n8n workflow 可视化易于个人调试，但企业 SaaS 产品化路径不清晰 |
| **ai_ml_engineer** | **方案 A (今晚 Routines MVP) → 方案 C (Managed Agents, 4 周)** 分阶段 | A 立即 + C 面向企业 | Routines 30-60 分钟可上线；Managed Agents 是 Anthropic 官方企业化方向；面向 Janus Digital SKU 铺路 | 阶段 1 仍依赖 Claude Code / Max 订阅，产品化属性为零；Managed Agents 仍在公测，SLA 不稳 |
| **strategy_advisor + graphify_strategist** | **阶段性产品化**（Q2 重构 → Q3 灰度 ≤3 客户 → Q4 商品化） | 战略级必选 | 情报管线是 Janus Digital 首个 SKU 命脉；Content Marketing 漏斗承接产品；Tier 1 $299 / Tier 2 $899 / Enterprise $2000+ | 没有给出具体的技术栈推荐；架构选型推给 harness/ai_ml/finance |
| **financial_analyst + integration_qa** | **方案 B GitHub Actions + Claude API + task_budget 50K** | ⭐⭐⭐⭐⭐ | 月 $30-80 成本可控；ROI 2600%；Slack 四层分层是 MVP 前置硬门禁；GH Actions 免费额度覆盖 80% 运行 | 低估了多租户场景下的 GH Actions 并发限制（每账户 20 concurrent jobs）；未回答 Q3 多租户隔离如何实施 |

### 2.1 立场共识区（4 方都同意的事实）

1. 当前本地电脑 + Max 订阅模式**必须**解除
2. Slack 告警必须分层，否则生产化不可行
3. 产品化是方向，不是可选项
4. 情报日报 + 情报行动 2 个 workflow 是 MVP 核心

### 2.2 立场分歧区（下一节展开）

1. 阶段 2 技术栈（B / D / C 三选一）
2. 阶段 1 是否必要（Routines MVP 算不算产品化投资）
3. 成本模型（低频 vs 企业级容量）

---

## 三、3 处实质分歧识别

### 分歧 1：harness (D n8n) vs finance (B GitHub Actions)

| 维度 | harness 立场 | finance 立场 |
|------|-------------|-------------|
| 核心判断 | 复用现有 n8n 基础设施，一周落地 | 产品化需要代码化 pipeline，n8n 可视化不利于多租户版本管理 |
| 时间优先级 | 快 | 对 |
| 产品化成熟度 | n8n 偏内部工具，客户自助使用成本高 | GitHub Actions + Claude API 是代码化 pipeline，天然支持多客户 fork |

**分歧根源**：对"产品化优先级"的判断不同。

**谁更正确**：**finance 更贴合总裁原话"无法有效产品化"**。总裁问题核心不是"怎么快速解耦本地电脑"（那是阶段 1 问题），而是"怎么走向对外售卖"。harness 的 D 方案最优解决"今天的运维痛点"，但 B 方案最优解决"明天的产品化痛点"。**阶段 2 应以 B 为底座，n8n 可作为 Tier 1 客户低代码 fallback**。

### 分歧 2：ai_ml 的 A 分阶段 vs strategy 的产品化路径

| 维度 | ai_ml 立场 | strategy 立场 |
|------|-----------|--------------|
| 阶段 1 性质 | Routines 是"MVP 过渡态"，先上线再说 | 阶段 1 不算产品化投资，只是技术债降低 |
| 是否能合并 | ✅ 可合并 | ✅ 可合并 |

**合并方案**：阶段 1 Routines 定位为**"一次性临时桥梁，生命周期 ≤ 6 周"**，不做为产品化投资，仅为解除总裁本地电脑依赖。阶段 2 启动即弃用阶段 1，不做架构延续。这样 ai_ml 的"今晚上线"诉求和 strategy 的"架构一开始就产品化导向"不冲突。

### 分歧 3：成本预算 vs 战略机会成本

| 维度 | finance 立场 | strategy 立场 |
|------|-------------|--------------|
| 成本假设 | 月 $30-80（低频使用） | Q4 企业级容量，月成本可能 $500-2000 |
| 哪个贴合真实 | 阶段 1-2 贴合 | 阶段 3-4 贴合 |

**合并方案**：成本模型必须**随阶段升级**。
- 阶段 1-2：月 $30-80（internal + 1-2 pilot）
- 阶段 3：月 $200-500（≤3 客户灰度）
- 阶段 4：月 $1500-3000（Janus SKU 商品化，按客户增长摊销）
- 每个阶段单独设 `task_budget`，Q4 才解除 50K 硬上限

---

## 四、调和尝试 —— 四阶段综合方案

### 阶段 1：今晚 MVP（解除本地电脑依赖）

| 属性 | 值 |
|------|---|
| 技术栈 | Claude Code Routines（方案 A） |
| 耗时 | 30-60 分钟 |
| 上线条件 | Routines 定时配置 + MCP 工具检查通过 |
| 退出条件（触发阶段 2） | 阶段 2 B 方案 pipeline 跑通第一个完整情报日报 |
| 生命周期上限 | 6 周（强制退役） |
| 满足方 | ai_ml（今晚上线）+ 总裁（本地电脑解耦） |
| 不满足方 | finance（仍绑定 Max 订阅）、strategy（未产品化） |
| 接受此妥协的理由 | 6 周过渡期可接受；阻塞总裁本地生活更不可接受 |

### 阶段 2：Q2 内部生产架构重构

| 属性 | 值 |
|------|---|
| 技术栈决策 | **B / D / C 三选一（见第五章矩阵）** |
| 推荐首选 | **方案 B GitHub Actions + Claude API** |
| 备选 | 方案 D n8n（若 B 的 GH Actions 多租户限制无法绕开） |
| 硬前置 | Slack 四层分层：`#synapse-business` / `#synapse-alerts` / `#synapse-debug` / `#synapse-president` + 告警聚合 + 静默窗口 |
| 成本目标 | 月 $30-80，`task_budget=50000` 硬上限 |
| 触发下一阶段条件 | (a) Slack 分层 14 天无告警扎堆事故；(b) 情报日报 + 情报行动连续 14 天稳定；(c) 首个外部 pilot 客户签 LOI |
| 满足方 | finance + integration_qa + harness（如选 D） |

### 阶段 3：Q3 多租户灰度（≤3 客户）

| 属性 | 值 |
|------|---|
| 技术栈 | 依据阶段 2 选型演进；若 Managed Agents 公测 SLA 转稳，可评估切换 C |
| 核心能力 | 多租户隔离、客户 dashboard、数据主权 API、模型可选（Claude/GLM/Qwen）、告警路径自定义 |
| 硬前置 | 独立安全审计通过（多租户隔离 P0）+ SOC 2 Type I 路径明确 |
| 成本目标 | 月 $200-500 |
| 触发下一阶段条件 | (a) 3 个灰度客户连续 30 天零 P0 事故；(b) 首个客户续费意向书；(c) 定价模型验证 |
| 满足方 | strategy + graphify |

### 阶段 4：Q4 Janus Digital 商品化

| 属性 | 值 |
|------|---|
| 上市 SKU | Tier 1 $299/月 + Tier 2 $899/月 + Enterprise $2000+/月 |
| 硬前置 | SOC 2 Type I 完成；Stripe 计费接通；合规条款与客户协议就位 |
| 成本目标 | 月 $1500-3000（按客户数动态） |
| 满足方 | graphify + financial（ROI 兑现） |

---

## 五、阶段 2 技术栈 3 选 1 决策矩阵

评分：1 最差，5 最佳。权重合计 100%。

| 评估标准 | 权重 | 方案 B GH Actions | 方案 D n8n | 方案 C Managed Agents |
|---------|:---:|:---:|:---:|:---:|
| 与现有 Synapse 生态集成 | 15% | 4 | 5 | 2 |
| 多租户演进路径 | 20% | 5 | 2 | 4 |
| 运维负担 | 10% | 4 | 3 | 5 |
| 成本可预测性 | 15% | 5 | 4 | 2 |
| 产品化合规（非个人订阅） | 20% | 5 | 3 | 5 |
| Slack 分层实施难度 | 10% | 4 | 5 | 3 |
| 迁移到 Janus SKU 平滑度 | 10% | 5 | 2 | 4 |

### 加权计算

**方案 B GH Actions**：
- 4×0.15 + 5×0.20 + 4×0.10 + 5×0.15 + 5×0.20 + 4×0.10 + 5×0.10
- = 0.60 + 1.00 + 0.40 + 0.75 + 1.00 + 0.40 + 0.50
- = **4.65** ⭐️ 胜出

**方案 D n8n**：
- 5×0.15 + 2×0.20 + 3×0.10 + 4×0.15 + 3×0.20 + 5×0.10 + 2×0.10
- = 0.75 + 0.40 + 0.30 + 0.60 + 0.60 + 0.50 + 0.20
- = **3.35**

**方案 C Managed Agents**：
- 2×0.15 + 4×0.20 + 5×0.10 + 2×0.15 + 5×0.20 + 3×0.10 + 4×0.10
- = 0.30 + 0.80 + 0.50 + 0.30 + 1.00 + 0.30 + 0.40
- = **3.60**

### 推荐

**阶段 2 首选 方案 B GitHub Actions + Claude API（加权 4.65）**

理由：
1. 多租户演进路径最清晰（代码化 pipeline 可 fork/template）
2. 产品化合规满分（与个人订阅完全解耦）
3. 成本可预测性最高（GH Actions 按分钟计费 + Claude API 按 token）
4. 迁移到 Janus SKU 平滑度最高

备选：**方案 C Managed Agents**（3.60），在 Anthropic 公测转 GA、SLA 达到 99.5% 时评估切换。

**方案 D 降级为 Tier 1 低代码客户的可选 runtime**，不作为阶段 2 底座。

---

## 六、风险登记册

| # | 风险 | 可能性 | 影响 | 缓解措施 |
|---|------|:----:|:---:|---------|
| 1 | Managed Agents 公测 SLA 不稳 | 中 | 高 | 阶段 2 选 B 作 fallback；阶段 3 评估切换前强制 30 天 SLA 监测 |
| 2 | Slack 分层未 MVP 前置，告警扎堆复发 | 中 | 高 | **绝对硬约束**；阶段 2 启动前 Slack 四层分层必须上线，否则阶段 2 不启动 |
| 3 | task_budget 50K 不够情报日报完整跑一圈 | 低 | 中 | 拆分为多 run（情报搜集 + 评估 + 报告生成 3 个 workflow）；或上调至 100K 并通知 finance |
| 4 | 多租户隔离 P0 安全新风险 | 中 | 极高 | Q3 灰度前必须独立第三方安全审计；首个客户合同附数据主权条款 |
| 5 | harness_engineer 带宽不足（REQ-012 并行冲突） | 高 | 中 | 阶段 2 选 B（代码化 pipeline，harness 只需做 Slack 分层与凭证，~3 天工作量） |
| 6 | 总裁 Max 订阅变动影响阶段 1 | 低 | 中 | 阶段 1→阶段 2 过渡期需双跑 ≥7 天；阶段 2 跑通后立即退役阶段 1 |
| 7 | GH Actions 每账户 20 concurrent jobs 限制 | 中 | 中 | 阶段 3 前评估是否升级 GH Enterprise 或切换 self-hosted runner |
| 8 | 客户数据归集合规（GDPR / PIPL） | 低 | 极高 | 阶段 3 前法律顾问审查一次；默认数据驻留客户地域 |

---

## 七、综合推荐方案

**一段话总结**：

情报管线走**四阶段路线**：**今晚 Routines MVP 解除本地电脑依赖（阶段 1，6 周生命周期上限）** → **Q2 GitHub Actions + Claude API 代码化 pipeline 重构（阶段 2，B 方案加权 4.65 胜出，Slack 四层分层为硬前置，task_budget 50K 硬上限）** → **Q3 多租户灰度 ≤3 客户（阶段 3，独立安全审计前置）** → **Q4 Janus Digital 商品化上市（阶段 4，Tier 1 $299 / Tier 2 $899 / Enterprise $2000+）**。**阶段 2 技术栈首选方案 B**，备选方案 C Managed Agents（待公测转 GA），方案 D n8n 降级为 Tier 1 低代码客户 runtime。**立即启动行动**：今晚由 ai_ml_engineer 上线 Routines MVP，明日由 harness_engineer 启动 Slack 四层分层 PR。

---

## 八、Lysander 决策点

需 Lysander 在向总裁呈报前审查并拍板的关键决策：

1. **阶段 2 技术栈拍板**：接受加权矩阵推荐的方案 B，还是基于其他战略因素倾向方案 D/C？
2. **阶段 1 生命周期上限**：6 周是否合适？若 Q2 阶段 2 进度延误，是否允许延长？
3. **Slack 四层分层的硬前置性**：接受"阶段 2 不启动直到 Slack 分层上线"这一硬约束？
4. **阶段 3 触发条件宽松度**：3 灰度客户 + 30 天零 P0 事故 + 首个续费 LOI，是否过紧？
5. **阶段 2 启动的资源投入**：harness_engineer 同时在做 REQ-012，是否要让路？

---

## 九、呈报总裁的关键事实（建议 Lysander 向总裁汇报时保留）

1. **方向**：情报管线走向 Janus Digital 首个 SKU，四阶段路线，**Q4 上市**。
2. **今晚行动**：Routines MVP 上线，总裁本地电脑依赖**今晚解除**（30-60 分钟）。
3. **Q2 重构底座**：选定 GitHub Actions + Claude API（加权 4.65 胜出），成本月 $30-80，`task_budget=50000` 硬上限。
4. **商品化定价**：Tier 1 $299/月 / Tier 2 $899/月 / Enterprise $2000+/月，ROI 测算 2600%。
5. **仅此一项需总裁拍板**：阶段 2 技术栈是否采纳推荐（方案 B），还是总裁倾向其他选项？其余由 Lysander + 智囊团推进，不打扰总裁。

---

## 十、附录：4 方原始立场引用

### 10.1 harness_engineer

> "方案 D n8n 原生（加权分 4.75，最高）。复用 n8n.lysander.bond 生产实例、HMAC 安全层、Credentials 规范；零新增基础设施；1 周完成。"

### 10.2 ai_ml_engineer

> "方案 A (Routines MVP, 今晚) → 方案 B (Managed Agents, 4 周) 分阶段。Routines 30-60 分钟可上线解耦本地电脑；Managed Agents 面向生产为 Janus Digital 企业级铺路。"
> （注：ai_ml 原话中的"方案 B"在本纪要映射为"方案 C Managed Agents"，以避免与 finance 的"方案 B GH Actions"混淆）

### 10.3 strategy_advisor + graphify_strategist

> "阶段性产品化：Q2 重构 → Q3 灰度 ≤3 客户 → Q4 商品化。情报管线是 Janus Digital 首个 SKU 命脉 + Content Marketing 变现漏斗承接产品。"

### 10.4 financial_analyst + integration_qa

> "方案 B GitHub Actions + Claude API + task_budget 50K（⭐⭐⭐⭐⭐）。月 $30-80 成本可控、ROI 2600%、Slack 四层分层是 MVP 前置门禁。"

---

**会议主持**：synapse_product_owner
**归档日期**：2026-04-24
**状态**：recommendation_ready，等待 Lysander 审查 → 呈报总裁
