---
id: ssot-i18n-president-decisions-2026-04-24
type: reference
status: published
lang: zh
version: "1.0"
decision_date: 2026-04-24
decision_level: L4
approved_by: 总裁刘子杨
author: Lysander
review_by: [execution_auditor]
audience: [team_partner, president]
---

# 总裁决策记录 — 2026-04-24 SSOT + i18n 战略

## 决策 ①：synapse-core 公开时机

- **选项**：A（立即 push）/ B（脱敏后）/ C（延迟）
- **总裁选择**：**A — 立即 push 公开**
- **Lysander 原建议**：A
- **含义**：阶段 1 内 synapse-core 必须公开，解除所有 SSOT 工作前置阻塞
- **附注**：实际仓库为 `lysanderl-glitch/synapse.git`（已存在 public），SSOT 沿用现有仓库无需新建

## 决策 ②：学院认证体系启动

- **选项**：A（仅徽章）/ B（正式认证）/ C（不做）
- **总裁选择**：**A — 首期仅做完成徽章**
- **Lysander 原建议**：A
- **含义**：学院课程完课 → 徽章；正式 SCP 认证如未来启动，单独 L4 上报

## 决策 ③：总裁个人 IP 参与学院课程

- **选项**：A（出镜 1 门）/ B（不出镜）/ C（延后）
- **总裁选择**：**B — 不出镜，纯 Multi-Agents 交付**
- **Lysander 原建议**：A（被否决）
- **含义**：学院开篇课由 Multi-Agents 完成；首期不建立"创始人视角"品牌锚
- **学习**：Lysander 过于追求"品牌势能"，总裁更看重"不依赖个人 IP 的可复制性"

## 授权范围

- 总裁授权 Lysander 组织执行阶段 1-5
- 后续 L1/L2/L3 决策由 Lysander + 智囊团 + 专家评审闭环
- 每阶段完成时简报总裁
- 未来认证商业化如启动，需独立 L4 上报

## 执行启动

阶段 1 止血动作（2026-04-24 总裁审批当夜启动）：
1. ✅ 决策留档
2. ✅ 四方案 + 综合评审留档到 OBS
3. ✅ synapse-core 已公开（沿用 synapse.git public）
4. 🟡 修复 Forge /synapse/get-started 错链接
5. 🟡 修复 Academy /academy/get-synapse 错链接
6. 🟡 synapse-core/docs/public/ 边界定义

---

## 决策修正（2026-04-24 深夜）

### 决策 ② 范围：A → B
- **原选择**：A（全站 80% 双语，博客 14 精选）
- **修正为**：**B（全站 100% 双语，含所有 33 篇博客）**
- **总裁原话**（2026-04-24 深夜）："② 范围刚才决策错误，应该是 B"
- **Lysander 判断**：此修正在 L4 决策范围内，总裁主动纠错无需 Lysander 审批
- **执行影响**：
  - `bilingual-blog-production-sop.md` 更新至 v1.1（新增存量博客条款）
  - `04-content-strategy.md` 追加"决策修正"小节
  - `SSOT-I18N-STRATEGY-2026-04-24` active_tasks 项更新范围字段
  - content_strategist 产能调整（+ 19 篇存量补译）

### 决策 ①③④ 保持不变
- ① A 立即全面启动
- ③ A 中文默认 + /en/ 英文
- ④ A 人工再创作

### 学习点
- Lysander 此前呈报方案时对决策 ②/③ 的选项描述不够直观，总裁凭直觉选 A 后发现与深层意图不符
- 教训：下次呈报选项时，除选项本身外，附上每个选项的"长远含义"和"排除什么"

---

**记录人**：Lysander
**归档日期**：2026-04-24
**决策级别**：L4（战略级不可逆）
