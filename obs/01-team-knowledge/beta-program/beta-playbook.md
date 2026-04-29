# Synapse Forge — Closed Beta Playbook

> 阶段 B（Closed Beta）运营手册。
> Owner: growth_lead + Lysander
> Last updated: 2026-04-23
> Status: Active (launching now)

## 0. 目标与成功指标

**阶段 B 核心目标**：在 Founding 30 位置上招募 10–30 个精选团队，形成首批可公开引用的真实案例与付费意愿信号。

**Exit Criteria（进入阶段 C Commercial Launch 的条件）**：
- ≥ 10 founding 团队完成初次部署并在使用中
- ≥ 3 付费意愿信号（书面/口头承诺 Pro tier 购买）
- ≥ 2 可公开署名或匿名引用的真实案例
- 30 天滚动 Churn < 20%
- 加权 NPS ≥ 40

---

## 1. 招募渠道清单

### 1.1 高优先级（主力渠道）

| 渠道 | 操作 | Owner | 频率 |
|------|------|-------|------|
| **Twitter / X** | Lysander 个人账号发布 Founding 30 招募推文，锚定 Harness Engineering 博客链接 | Lysander 本人 | 每周 1 条 Thread + 3 条短推 |
| **LinkedIn** | CEO 身份 Post + 定向发 DM 给建筑数字化 / Claude Code 活跃用户 | Lysander 本人 | 每周 1 Post + 5 DM |
| **朋友推荐** | 向 5–10 位已知友好同行直发邀请函（advocate-list.md） | Lysander 本人 | 一次性铺开 + 每周补新 |
| **门户 Waitlist** | `/synapse/beta` 页面被动收件 | 自动运行 | 无需主动运营 |

### 1.2 次优先级（辅助渠道）

| 渠道 | 操作 | 备注 |
|------|------|------|
| GitHub Discussions / Issues | Synapse 开源仓库的活跃贡献者转化 | 阶段 B 中期启动 |
| 小众垂直社区 | 建筑数字化圈子、量化交易圈 | 通过现有 Janus/Stock 模块切入 |
| 已公开博文的读者 | Harness Engineering 博客下方 CTA 指向 `/synapse/beta` | 被动 |

### 1.3 暂不启用

- 付费广告（阶段 C 再考虑）
- 冷发 Email 大规模群发（违背"精选"基调）
- Hacker News 主动 Show HN（保留弹药到阶段 C Launch Day）

---

## 2. 准入评估 Checklist

> 每一位申请者走完以下流程。评分细则见 `application-review-rubric.md`。

1. **初步筛选（T+0）**
   - 邮件内容完整度：Team / Size / AI Tools / Why / Contact 五项缺一项即回邮追问
   - 明显不匹配者（如营销群发、与 AI 无关业务）礼貌拒绝，不进入评分

2. **Rubric 评分（T+1 日内）**
   - 5 维度 × 5 分 = 25 分总分（见 rubric 文档）
   - ≥ 16 进入 Beta
   - 13–15 列入观察名单（等阶段 C 或二批）
   - ≤ 12 礼貌拒绝并保留联系方式

3. **接受后发欢迎邮件（T+2 日内）**
   - 使用 `beta-welcome-email-template.md` 模板
   - 同时发出 Slack/Discord 邀请链接
   - 分配 Founding Number（按接受顺序 #001, #002, ...）

---

## 3. 新成员 Onboarding SOP

### 3.1 接受后 24 小时内

| 步骤 | 操作 | 交付物 |
|------|------|--------|
| 1 | 发欢迎邮件（中/英择一，按申请语言） | 邮件已送达 |
| 2 | 发 Slack/Discord 邀请链接 | 新成员已加入频道 |
| 3 | 发 Resource Pack（GitHub 链接 + CLAUDE.md 模板 + 快速上手文档） | 资源包链接可点 |
| 4 | 在 advocate-list.md 标记状态为 `已接受` | 名单更新 |

### 3.2 Resource Pack 内容（一封邮件 + 一个链接）

```
1. Synapse Forge 开源仓库链接（GitHub）
2. Synapse Forge 文档入口（/synapse/how-it-works）
3. CLAUDE.md 模板文件（含 Harness 基础配置）
4. Quick Start 视频或 5 分钟 Getting Started 文档
5. Founding 30 专属 Slack/Discord 频道链接
6. Lysander 联系方式（每季度 1h 咨询预约入口）
7. 首次部署 72 小时 Check 表单链接
```

### 3.3 72 小时首次部署 Check

- 发一封轻量问卷：
  - [ ] 是否完成 CLAUDE.md 个人化配置（3 个字段替换）
  - [ ] 是否完成首次会话识别（Lysander 开场问候出现）
  - [ ] 是否跑通至少 1 次派单流程
  - [ ] 遇到的第一个阻塞点是什么
- 如果未完成，Lysander 主动发一封诊断邮件（不是销售）

### 3.4 第 1 周 30 分钟视频 Onboarding

- 日程：接受后 7 天内由 Lysander 安排
- 议程：
  1. 观察新成员的真实首次 dispatch（5–10 min）
  2. 为其场景微调 CLAUDE.md（10 min）
  3. 答疑 + 收集首次反馈（10 min）
- 记录：每次视频后在 advocate-list.md 更新 `last_contact` 和 `notes`

---

## 4. 每周五增长站会议程（Lysander Slack Thread 模板）

> 每周五 Dubai 时间 14:00 发布，Founding 30 频道置顶。

```markdown
# Founding 30 — Weekly Sync (Week NN)

## 本周 Synapse 进展
- 新增/修复：[列 3 项最关键变更]
- 新模块/新规则：[如有]
- 文档/知识库更新：[如有]

## 数据速览
- 活跃 founding 团队：X / 30
- 本周新增加入：X
- 本周结构化反馈：X 条
- 本周阻塞工单：X 条（已关闭 Y）

## 本周 Ask（需要你们的输入）
1. [具体问题 1]
2. [具体问题 2]

## 下周预告
- [即将发布项]

回帖格式建议：
- 我是 Founding #XXX，本周用了 Synapse 做了 ___，遇到 ___，建议 ___。
```

---

## 5. 反馈分级 SOP

### 5.1 三分类

| 分类 | 定义 | 响应 SLA | Owner |
|------|------|----------|-------|
| **Bug** | 系统行为违背文档约定，阻塞工作 | 24 小时内响应，3 天内修复或给出绕过 | ai_systems_dev |
| **UX** | 能用但笨拙，摩擦大 | 1 周内响应与评估 | harness_engineer |
| **功能请求** | 新能力/新模块 | 每月一次集中评审，纳入 roadmap | Lysander + 智囊团 |

### 5.2 收集入口

1. 专属 Slack/Discord 频道 `#founding-feedback`
2. 每月 1 次结构化反馈邮件（模板在欢迎邮件中给）
3. 每周五站会回帖
4. 视频 onboarding 即时口头

### 5.3 处理链路

```
feedback 进入
  ↓
ai_systems_dev 分类（Bug / UX / Feature）
  ↓
Bug → 立即立工单 → 修复 → 通知反馈人
UX  → 进 backlog → 每周分流
Feature → 月度评审 → roadmap 或拒绝（给理由）
```

### 5.4 反馈人关怀

- 每条 feedback 必须有人回复（哪怕是 "已看到，排期中"）
- 被采纳的 feature 在 CHANGELOG 里署名感谢
- 连续 3 个月无反馈的 founding 团队：Lysander 亲自发一封轻量关怀邮件

---

## 6. 阶段 B → C 退出清单

> 以下 5 条全部满足才宣布进入阶段 C。由 growth_lead + execution_auditor 每月 15 日联合评估。

- [ ] ≥ 10 founding 团队完成初次部署并在使用中（active = 最近 30 天有 commit 或对话证据）
- [ ] ≥ 3 付费意愿信号（书面 Email / Slack 明确表态购买 Pro）
- [ ] ≥ 2 可公开引用的真实案例（已获得使用方明确授权）
- [ ] 30 天滚动 Churn < 20%（定义：30 天内 last_activity 无更新的 founding 数 / 总 active founding 数）
- [ ] 加权 NPS ≥ 40（最近一次月度 NPS 调查结果）

满足后提交 L3 决策给 Lysander，由 Lysander 启动阶段 C 准备工作。

---

## 7. 风险与对策

| 风险 | 发生概率 | 影响 | 对策 |
|------|----------|------|------|
| 申请量过少（< 10/月） | 中 | 阶段 B 拖长 | 增加朋友推荐直发 + Lysander 个人渠道加码 |
| 申请量过多（> 50/周） | 低 | 评估积压 | 临时暂停 Waitlist 页面 CTA，专心处理队列 |
| 首批申请者普遍完成不了部署 | 中 | 口碑风险 | 同步完善 Get Started 文档 + 视频 |
| 反馈频道冷清 | 中 | 判断失真 | Lysander 每周主动抛具体问题激活讨论 |
| Founding 成员要求超出合理范围的定制 | 中 | 资源消耗 | 明确 Founding 权益清单，超出项走咨询服务 |
| 竞品模仿 | 低 | 中期差异化压力 | 保持 Harness 方法论深度文档化优势 |

---

## 8. Owner 与问责

| 职责 | Owner | 备份 |
|------|-------|------|
| 招募渠道运营 | Lysander 本人 | growth_lead |
| 申请 Rubric 打分 | growth_lead | Lysander |
| Onboarding 欢迎邮件 | growth_lead（模板） | Lysander（签名） |
| 视频 Onboarding | Lysander 本人 | — |
| 反馈分类与派工 | ai_systems_dev | harness_engineer |
| 每周五站会 | Lysander 本人 | growth_lead |
| 月度退出条件评估 | growth_lead + execution_auditor | — |
| advocate-list 维护 | growth_lead | — |

---

## 9. 附录：关键链接

- Waitlist 页面：https://lysander.bond/synapse/beta
- Founding Rubric：`./application-review-rubric.md`
- 欢迎邮件模板：`./beta-welcome-email-template.md`
- Advocate 名单：`./advocate-list.md`
- 方法论博客：https://lysander.bond/blog/harness-engineering-guide
- Synapse 公开仓库：https://github.com/[TBD - 填入 Synapse 开源仓库地址]
