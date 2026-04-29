---
id: strategic-overhaul-approval-package-2026-04-26
type: core
status: pending_approval
lang: zh
version: "1.0"
decision_date: 2026-04-26
decision_level: L4
review_panel: [strategy_advisor, execution_auditor, decision_advisor]
author: Lysander
audience: [president, team_partner]
related: [website-strategy, synapse-monetization-strategy, synapse-product-architecture]
scope: [website_overhaul, gtm_strategy, license_governance]
supersedes: []
---

# 战略审批包：网站内容整体性改造 + 推广策略调整 + 复用授权策略

## BLUF（4 行给总裁）

- 三大议题（产品/市场/治理）已闭环综评，三方案高度一致、无方向性冲突
- 推荐战略：锁定"开源体系 + 咨询服务"主线 + 内部 Dogfooding 优先 + B+D 授权分阶段落地
- 整合 P0 立即执行 16 项（约 3-5 工作单元，跨产品/市场/治理三团队并行）
- 等待总裁对 **7 个 L4 决策点** 裁决；其余 9 项 L3 已由 Lysander 自决闭环

---

## 一、共识（三方案高度一致，6 条）

1. **现状不可持续**：网站叙事混乱（Synapse / Forge / Academy 三套品牌叠加）+ 推广早于产品成熟度 + 复用没有法律护栏，三处缺口同时暴露
2. **主线必须单一**：Janus Digital 提炼 Synapse 开源体系 → 咨询服务复刻；这条主线同时解决产品、市场、治理三方案的根因
3. **内部先于外部**：Dogfooding（B 层 Janus 部门 + C 层早期种子）必须先于公开推广，反馈闭环数据是对外重启的硬扳机
4. **法律护栏先行**：阶段 0 LICENSE/Terms/Banner 必须在公开推广恢复前落地（不可让推广扩大与法律真空叠加）
5. **删减优先于新增**：所有方案的第一动作都是"暂停 / 删除 / 合并"，不是"新增功能 / 新增页面 / 新增推广渠道"
6. **可观测可回滚**：每个动作都有北极星指标 + 回滚预案（NPS、DAU/WAU、可公开案例数、扳机条件）

---

## 二、综合方案要点

### 2.1 网站主线故事（产品方案核心）

> **Janus Digital（公司主体）** 在自身运营中提炼出 **Synapse**（AI 协作运营体系，开源），通过 **咨询服务** 帮助客户复刻这套体系。Lysander 是 Synapse 体系内的 AI CEO 角色（demo 而非产品）。

主导航 8 项 → 5 项：**产品 / 上手 / 博客 / 定价 / 关于**。删除/合并 5 页：services（并入定价）、training（并入上手）、intelligence（并入博客）、academy/dashboard、academy/course。

### 2.2 推广策略调整（市场方案核心）

- **暂停**：12 项对外资产（PH/HN 草稿、社交推广、公开 Beta 招募）
- **扩大**：A 层 Lysander 自身、B 层 Janus 部门试点、C 层早期种子（约 20 人）
- **Advocate 4 级**：L1 Active → L2 Contributor → L3 Advocate → L4 Co-creator
- **对外重启硬扳机**（同时满足 4 条）：
  - 内部 NPS ≥ 50
  - DAU/WAU ≥ 0.5
  - 可公开案例 ≥ 3
  - L3+ Advocate ≥ 5

### 2.3 复用授权（治理方案核心）

- **阶段 0（立即，1 工作日）**：BSL-1.1 LICENSE + USAGE_TERMS.md + README Banner + workspace/ 脱敏
- **阶段 1（推广扳机触发后）**：可选注册 + tokenized download
- **阶段 2（远期）**：分层架构（core 公开 / pro 受控 / enterprise 闭源）

### 2.4 三方案的协同关系

```
网站改造（A）── 锁定主线故事 ──┐
                             ├──→ 给市场推广提供单一信息（消除叙事冲突）
推广策略（B）── 内部反馈闭环 ──┤
                             ├──→ 验证产品改造方向（NPS / 案例反哺 IA）
治理护栏（C）── 法律 + 脱敏 ──┘
                             └──→ 让推广可放心扩大（无法律真空）
```

三方案不是并列三件事，而是一个 **"叙事-验证-护栏"** 闭环。

---

## 三、跨方案冲突 + 评审团裁决（4 项）

### 冲突 ①：方案 A 删除 academy 部分页面 vs 方案 B 暂停 /synapse/beta 公开

- **方案 A**：删除 academy/dashboard、academy/course，academy/index 部分保留
- **方案 B**：暂停 /synapse/beta 公开访问页面
- **裁决**：合并处理 — academy/dashboard、academy/course 直接删除（A 主张），academy/index 保留但加 "内部测试中" Banner（B 主张），/synapse/beta 在阶段 0 加 USAGE_TERMS Banner 并降权（不删除，留作 L3 Advocate 入口）。**统一在网站改造批次执行**

### 冲突 ②：方案 A 改名 "Synapse Forge → Synapse" vs 方案 C 仓库名 lysanderl-glitch/synapse

- **方案 A**：建议品牌统一为 Synapse
- **方案 C**：仓库已经是 synapse（不是 synapse-forge）
- **裁决**：**无实质冲突，反而互证** — GitHub 已是 synapse，网站层面改名只是去掉一层 Forge 包装层，与现状对齐。**建议总裁批准 A 选项**（决策点 ③）

### 冲突 ③：方案 C 阶段 0 BSL-1.1 vs 方案 A 主线故事 "开源 + 服务"

- **争议**：BSL 不是 OSI 认证开源，是否影响"开源叙事"
- **方案 A**：主线故事强调"开源"
- **方案 C**：BSL-1.1 是 source-available + 4 年自动转 Apache-2.0
- **裁决**：**叙事调整 + 选型保留** — 网站文案使用 **"source-available, open by 2030"** 或 **"开源（4 年延迟 Apache-2.0）"** 的精确表述，不使用裸"开源"二字误导用户；BSL-1.1 选型保留（商业护栏更重要）。如果总裁选 C 选项（完全开源），叙事可改为裸"开源"

### 冲突 ④：方案 B 扳机 NPS≥50 vs 方案 A IA 重构后才能测内部 NPS

- **争议**：NPS 测量需要相对稳定的产品形态
- **裁决**：**依赖关系明确** — 方案 A 的 P0 网站改造（约 1-2 工作单元）必须先于方案 B 的内部 NPS 测量启动；NPS 首次测量节点定在网站改造完成后 + 内部 Dogfooding 运行 2-3 周。**纳入整合执行计划的串行依赖**

---

## 四、整合 P0 立即执行清单（16 项，3-5 工作单元）

### 治理批次（最高优先级，1 工作日完成，不阻塞其他批次）

1. 添加 LICENSE 文件（BSL-1.1，待总裁批准选型）— harness_engineer
2. 创建 USAGE_TERMS.md 商用条款 — harness_engineer
3. README 顶部添加 LICENSE Banner — knowledge_engineer
4. workspace/ 目录脱敏（删除真实客户名 / API key / 凭证）— integration_qa

### 网站改造批次（2-3 工作单元）

5. 主导航 8 项 → 5 项重构 — product_designer
6. 删除 academy/dashboard、academy/course 页面 — frontend_dev
7. 合并 services → 定价、training → 上手、intelligence → 博客 — content_strategist
8. /synapse/beta 加 "内部测试 + USAGE_TERMS" Banner — frontend_dev
9. 全站文案统一为"Janus Digital 提炼 Synapse 开源体系，咨询服务复刻" — content_strategist
10. 品牌名替换 "Synapse Forge" → "Synapse"（待总裁批准）— content_strategist + frontend_dev

### 推广暂停批次（与治理批次并行，0.5 工作日）

11. 暂停 PH 草稿 / HN 计划 / 社交推广日程 — growth_lead
12. 公开 Beta 招募页改为 Waitlist 形式 — growth_lead
13. 内部 Dogfooding 启动文档 + Advocate 4 级机制上线 — knowledge_engineer

### 测量基线批次（网站改造完成后启动）

14. 内部 NPS 测量工具部署（首次测量在网站改造后 2-3 周）— growth_lead
15. DAU/WAU 看板 + 反馈闭环率追踪 — ai_systems_dev
16. 对外重启扳机仪表盘（4 条扳机条件可视化）— ai_systems_dev

---

## 五、需要总裁裁决（7 个 L4 决策点）

### 决策点 ①：网站主体身份

**选项**：
- A. 引入 "Janus Digital" 为公司主体（背书 + 法律实体）+ Synapse 为产品名 + Lysander 为 AI CEO 角色
- B. 不公开 Janus Digital，保持 Synapse 为唯一品牌
- C. 沿用现状（Synapse / Forge / Academy 三套品牌混乱不变）

**Lysander 建议**：**A**
**理由**：法律实体显性化是治理护栏的前置条件；商业咨询需要法律主体背书；"提炼-复刻"叙事需要公司+产品两层结构

### 决策点 ②：Academy 商业模式存废

**选项**：
- A. 删除 $99/$999 SaaS 订阅，统一回 "开源体系免费 + 咨询服务付费"
- B. 保留 SaaS 订阅作为另一商业路径
- C. 暂时保留页面但标 "Coming Soon"，本期不主推

**Lysander 建议**：**A**
**理由**：与开源叙事冲突；SaaS 自助模式需要重投入产品化；当前阶段商业焦点应是高客单咨询而非 LTV 不明的订阅

### 决策点 ③：品牌名（Synapse vs Synapse Forge）

**选项**：
- A. 统一为 "Synapse"（GitHub 仓库已是 synapse，简化品牌）
- B. 保持 "Synapse Forge" 作为产品品牌（Synapse 体系 + Forge 产品）
- C. 双品牌共存（当前现状）

**Lysander 建议**：**A**
**理由**：访客理解成本低；GitHub repo 已是 synapse；删除一层 Forge 包装层；与方案 A、C 自动对齐

### 决策点 ④：LICENSE 选型

**选项**：
- A. **BSL-1.1**（4 年自动转 Apache-2.0，业界已被 Sentry/CockroachDB 验证）
- B. 自定义 "Synapse Source-Available License"
- C. 完全开源（Apache-2.0 / MIT，无商用限制）

**Lysander 建议**：**A**
**理由**：商业护栏（4 年内禁竞品复用）+ 社区信任锚（4 年后保证开源）+ 业界先例多；自定义协议法律风险高且社区接受度低；完全开源放弃商业护栏

### 决策点 ⑤：C 层种子用户 "终身 Pro" 承诺

**选项**：
- A. 已发承诺继续兑现，未来不再发
- B. 全部改口为 "早期访问 + 6 个月 Pro 试用"
- C. 完全去掉权益承诺

**Lysander 建议**：**A**
**理由**：信用最高；契约边界清晰（已发的兑现，未来不再发）；C 层人数有限（约 20 人），财务影响可控

### 决策点 ⑥：B 层 Janus 部门 Dogfooding 覆盖

**选项**：
- A. 全员铺开（4 个部门同时启动）
- B. 试点 1 个部门（建议 PMO，离 Synapse 应用场景最近）
- C. 部门 Lead 自愿报名

**Lysander 建议**：**B**
**理由**：风险低 + 能拿到试点数据 + 不影响其他部门正常运营；试点成功后再扩展是更稳妥的扩张路径

### 决策点 ⑦：扳机触发后对外重启节奏

**选项**：
- A. 全开（PH+HN+社交+Beta 同步）
- B. 分段开放（先 Waitlist + GitHub 公开 → 1 个月后 PH → 再 HN）
- C. 触发时再决定

**Lysander 建议**：**B**
**理由**：可控可观测；Waitlist 阶段可继续收集数据；分段开放降低单点失败风险（如某渠道反馈不佳可暂停）

---

## 六、Lysander 自主决策项（L3，已闭环，9 条）

1. **网站主导航精简到 5 项的具体名字**：产品/上手/博客/定价/关于（已定）
2. **academy/dashboard、academy/course 直接删除**（产品+治理一致，无叙事影响）
3. **/synapse/beta 加 Banner 而非删除**（保留 Advocate 入口，加 USAGE_TERMS 护栏）
4. **workspace/ 脱敏方式**：保留目录结构，删除真实客户名/凭证/API key（integration_qa 执行）
5. **注册强制 vs 可选**：阶段 1 默认可选注册（不强制阻碍试用），强制注册留到阶段 2 分层架构时
6. **specialist 卡是否脱敏**：人员名实化保留（Lysander/Janus 等 AI 角色名），删除真实合作伙伴名
7. **PH/HN 草稿暂停具体执行**：草稿存档不删除（扳机触发后可复用）
8. **内部 Dogfooding 反馈闭环工具**：使用现有 OBS 笔记 + 周会反馈表，不新增 SaaS 工具
9. **测量基线启动节奏**：网站改造完成后立即启动 NPS 工具部署，2-3 周后首次正式测量

---

## 七、执行授权请求

请总裁对以上 **7 个 L4 决策点** 回复 A/B/C 选项（或综合选项 + 备注）。

Lysander 收到决策后，将按 **整合 P0 清单 16 项** 立即组织执行：
- 治理批次（4 项，1 工作日）+ 推广暂停批次（3 项，0.5 工作日）并行启动
- 网站改造批次（6 项，2-3 工作单元）紧随其后
- 测量基线批次（3 项）在网站改造完成后启动
- 每批次完成后向总裁简报，发现问题随时升级

---

## 八、跨方案风险综合（5 条）

1. **三批次叠加**：网站改造期间双轨运行 + 推广暂停期 + LICENSE 引入，访客可能困惑 → 治理批次先行 1-2 天，让 Banner 在改造期间已有效
2. **内部 Dogfooding 不达扳机**：可能拖延对外重启 → 设置 8 周中检点，如未达扳机由智囊团评审是否调整产品方向
3. **BSL-1.1 社区接受度**：可能引发"伪开源"批评 → README 显性说明"4 年自动转 Apache-2.0"+ 提供商用咨询通道
4. **品牌改名遗漏**：Synapse Forge 在历史博客/外链中仍有引用 → 不强制全量替换，新内容统一用 Synapse 即可
5. **Janus 部门试点抵触**：Lead 可能不愿试点 → Lysander 直接对接 PMO Lead，提供"零投入快速试用"承诺

---

## 九、附：原始 3 份方案位置

- 方案 A 产品视角：`obs/04-decision-knowledge/website-strategy.md` + 网站审计报告
- 方案 B 市场视角：`obs/02-product-knowledge/` 内 GTM 策略文档（推广暂停清单）
- 方案 C 治理视角：`obs/04-decision-knowledge/synapse-monetization-strategy.md` + LICENSE 选型分析

（具体文件名待 OBS 团队归档时确认；本审批包独立可读，无需溯源即可决策）

---

## 十、评审团签字

- **strategy_advisor**：三方案战略一致，建议总裁批准 7 项 L4 决策点
- **execution_auditor**：执行链完整（智囊团评审 → Lysander 整合 → 总裁决策 → 执行批次），P0 清单可立即派单
- **decision_advisor**：决策边界清晰（7 L4 + 9 L3），不存在 Lysander 越权或上报过度

**评审日期**：2026-04-26
**待总裁回复**：7 个 L4 决策点 A/B/C 选项 + 备注
