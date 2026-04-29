---
id: pmo-auto-migration-plan-2026
type: living
status: published
lang: zh
version: 1.1.0
published_at: 2026-04-26
updated_at: 2026-04-27
author: synapse_product_owner
review_by: [Lysander]
audience: [knowledge_engineer]
stale_after: 2026-10-27
---

# PMO Auto 迁移方案 — n8n + Asana→Monday

**文档状态**：已批准，执行中
**版本**：v1.0
**日期**：2026-04-26
**主持**：synapse_product_owner
**专家评审**：execution_auditor + strategy_advisor
**决策级别**：L4（总裁审批）

---

## 战略修正记录（2026-04-27）

**原误解**：Phase 1 完成后立即暂停旧实例，切换至新实例。  
**正确理解**：采用"副本并行建设"策略——  
- **原体系（PMO Auto）**：n8n.lysander.bond + Asana，持续稳定运行，不受迁移影响  
- **新体系（PMO Monday Auto）**：n8n.janusd.io + Monday.com，从零建设，完全验收后再切换  

两套体系并行存在，直至 PMO Monday Auto 完整验收通过。原体系关闭时间由总裁决定。

**已执行的修正操作（2026-04-27）**：
- n8n.lysander.bond 9个WF 已恢复 active（原体系运行正常）
- pmo-api N8N_WF08_URL 已恢复指向 lysander.bond
- n8n.janusd.io 9个WF 设为 inactive（建设中，暂不运行）

---

## 总裁批准记录

**批准日期**：2026-04-27  
**批准人**：总裁 刘子杨  
**决策级别**：L4

| 决策点 | 总裁决策 |
|--------|---------|
| 1. Monday Pro 采购 | 授权采购 Pro 方案 |
| 2. Asana 保留期限 | 90 天只读后存档关闭 |
| 3. pmo-api 域名 | 两步走：Phase 1 保持 lysander.bond，Phase 2 迁移至 janusd.io |
| 4. WF-01 PAT 轮换 | 授权，约束：不影响现有体系稳定运行 |
| 5. 切换时间窗口 | 随时可启动（测试环境，无需审批窗口） |

---

## 执行摘要

### 迁移目标

| 迁移项 | 现状 | 目标 |
|--------|------|------|
| n8n 实例 | n8n.lysander.bond（自托管） | n8n.janusd.io（新实例） |
| 项目管理工具 | Asana | Monday.com |

PMO Auto 是 Synapse 体系的自动化运营核心，承载 9 个关键工作流（WF-01~WF-09），日常处理情报收集、WBS 生成、任务同步、Slack 通知等高频自动化任务。迁移目标是在不中断核心业务的前提下，完成基础设施和工具层的双重升级。

### 方案概述

迁移分两个独立阶段串行执行：

- **阶段 1（n8n 迁移）**：副本优先策略。在 janusd.io 新实例建立全部工作流副本，逐个激活验证，通过后统一切换，旧实例保留作为回滚保障。预计执行周期：5~7 个工作日（含双轨稳定期）。
- **阶段 2（Asana→Monday）**：历史数据存档不迁移，双轨 72 小时观察后切换。阶段 1 稳定运行满 5 个工作日后方可启动。预计执行周期：7~10 个工作日。

两个阶段之间设强制间隔期，禁止并行启动。

### 关键决策点（需总裁确认，共 5 项）

1. **Monday.com Pro 方案授权**：生产环境必须使用 Pro 或 Enterprise 方案（Automation Actions 配额要求），当前 Free/Basic/Standard 仅 250 次/月，无法满足生产需要。需总裁授权预算采购 Pro 方案。
2. **Asana 账号保留期限**：历史数据不迁移，Asana 账号需保留只读访问多久？推荐 90 天，到期后存档关闭。需总裁确认。
3. **迁移期间业务中断接受度**：阶段 1 切换窗口约 1~2 小时（工作流暂停期）。阶段 2 双轨期 72 小时内存在数据双写风险。总裁是否接受此窗口？
4. **WF-01 明文 PAT 安全修复授权**：WF-01 Code 节点含明文 Asana PAT（已在 git 历史中暴露），修复需要轮换此 PAT 并更新 Asana 凭证配置。需确认是否立即执行凭证轮换（会短暂影响 Asana 相关 WF）。
5. **pmo-api DNS 切换决策**：`pmo-api.lysander.bond` 在多个 WF 中硬编码，迁移完成后是否同步迁移至 janusd.io 域名，还是保留 lysander.bond 继续使用？不同选择影响后续维护成本。

### 整体风险评级

**阶段 1：中等风险**（主要风险：回滚速度 + 安全修复时序）
**阶段 2：较高风险**（主要风险：Webhook 安全架构重设计 + Pro 方案依赖）

---

## 专家评审结论

### execution_auditor 评审意见

#### 1. 阶段 1 副本方案可执行性和风险控制

**结论：ACCEPT（附条件）**

方案 C（副本先行，全量导入后逐个激活验证，通过后统一切换）逻辑清晰，回滚路径明确。可执行性评分：4/5。

附加条件（必须写入执行约束）：
- 双轨期内旧 n8n 实例不得关闭，必须保持 active 状态直至阶段 1 验收全部通过
- 新旧实例切换通过修改 pmo-api 环境变量和相关 WF URL 实现（非 DNS 切换），确保回滚速度

#### 2. WF-01 明文 PAT 修复时机

**结论：CONCERN — 必须迁移前修复，不可推迟至迁移中同步处理**

WF-01 Code 节点含明文 Asana PAT（`2/1213400756695149/...`），这是 P0 安全风险。如果推迟至"迁移中同步修复"，等于将安全漏洞原样复制到新环境，风险加倍。

**强制执行顺序**：
1. 在旧 n8n 上将 WF-01 改为从 Credential Store 读取（停止使用明文），同时轮换被暴露的 PAT
2. 验证 WF-01 在旧实例正常运行
3. 导出已修复的 WF-01 到新实例

此步骤是 Step 0 的第一优先任务，阻塞后续所有工作流迁移工作。

#### 3. 切换回滚方案速度（< 5 分钟目标）

**结论：CONCERN — 原方案 DNS 回滚路径不满足要求，需替换为 URL 切换方案**

如依赖 DNS 切换（n8n.lysander.bond 指向新实例），DNS 传播时间无法保证 < 5 分钟，极端情况可达 1 小时以上。

**推荐替代回滚方案**：
- 新实例使用 n8n.janusd.io，旧实例保持 n8n.lysander.bond 不变
- 切换机制：修改 pmo-api 的 `N8N_WF08_URL` 环境变量，以及各 WF 中的 URL 引用
- 回滚时间目标：< 2 分钟（环境变量修改 + 重启 pmo-api 服务）
- 需预先准备新旧两套环境变量值，写入运维手册

#### 4. WF-05 staticData 清理对时间线的影响

**结论：ACCEPT（不阻塞，但需记录业务影响）**

WF-05 的 staticData 迁移时不可携带，新实例需重新初始化，接受状态归零。此问题不阻塞整体时间线，但执行前必须确认：
- WF-05 去重逻辑依赖的历史状态归零后，是否会在短期内出现重复推送
- 建议在低流量时段执行 WF-05 迁移，并在激活后人工观察 24 小时

---

### strategy_advisor 评审意见

#### 1. 先迁 n8n、再迁 Monday 的顺序

**结论：ACCEPT**

顺序合理，符合系统依赖链逻辑。n8n 是编排执行层，Monday 是数据承载层；先稳定执行层再切换数据层，避免双重变更叠加造成故障溯源困难。

**关键约束**：两阶段之间必须设置强制稳定期（最少 5 个工作日），确认阶段 1 全部 WF 运行正常后，方可启动阶段 2。禁止在阶段 1 切换窗口期内同步启动阶段 2 准备工作中的任何数据层变更。

#### 2. Monday Webhook HMAC 缺失是否为战略级风险

**结论：CONCERN — 战略级风险，不可接受技术折衷后跳过，必须在方案中明确替代安全方案**

PMO Auto 的 Webhook 管道是整个自动化体系的指令通道。Monday 标准 Webhook 无 HMAC 签名验证意味着：任何获取到 Webhook URL 的主体都可伪造事件触发 PMO 流程，包括伪造任务完成通知、WBS 生成触发等高权限操作。

对于 PMO 这类管理核心系统，"无签名验证"不是可接受的技术折衷，而是必须设计替代方案的架构缺口。

**推荐替代安全方案（详见阶段 2 技术架构章节）**：
- IP 白名单：Monday.com Webhook 出口 IP 固定，在 pmo-api 层做入口过滤
- 时间戳窗口验证：每次请求携带时间戳，服务端拒绝 5 分钟以外的请求，防止重放攻击
- 两种机制叠加，在无 HMAC 条件下提供合理的安全保障

此替代方案必须作为阶段 2 的交付验收标准之一，不得以"功能先上线，安全后补"的方式绕过。

#### 3. 历史 Asana 数据"存档不迁移"策略的业务风险

**结论：ACCEPT（附 3 个执行条件）**

存档不迁移策略战略上合理，历史数据迁移的实施复杂度和 ROI 不成正比。但以下条件缺一不可：

1. **Asana 账号保留只读访问最少 90 天**：切换后不得立即关闭 Asana，确保历史数据可查阅，具体期限需总裁确认（详见执行摘要决策点 2）
2. **进行中任务必须手动在 Monday 中重建**：任何跨越切换时间节点仍在进行中的 Asana 任务，必须在切换前手动迁移至 Monday，不能留在 Asana 中遗忘
3. **用户通知**：需明确告知相关用户"历史数据可在 Asana 只读查阅至 XX 日期"，到期后的存档方案（导出格式）需提前确定

---

### synapse_product_owner 综合结论

**整体方案决策：APPROVE（附 4 项强制前置条件）**

| 前置条件 | 责任方 | 阻塞性 |
|----------|--------|--------|
| WF-01 明文 PAT 必须在 Step 0 修复，PAT 同步轮换 | harness_engineer | 硬性阻塞 |
| 回滚方案改为 URL/环境变量切换，非 DNS 切换 | harness_engineer | 硬性阻塞 |
| 阶段 2 方案文档必须包含 Webhook 替代安全方案 | ai_systems_dev | 硬性阻塞 |
| Monday Pro 方案采购完成后方可启动阶段 2 | 总裁授权 | 硬性阻塞 |

**两项 CONCERN 处置**：
- WF-01 PAT 修复：提升为 Step 0 第一优先级，阻塞后续步骤
- Monday Webhook 安全：升级为阶段 2 验收必要条件，不允许降级处理

---

## 阶段 1：n8n 迁移方案（详细）

### 推荐方案及理由

**采用方案 C：副本先行 + 逐个激活验证 + 一次性切换**

理由：
- 旧实例在整个迁移期间保持运行，业务连续性有保障
- 每个 WF 在新实例单独验证，问题隔离，不影响其他 WF
- 验证通过后统一切换，切换动作原子化，避免混乱
- 旧实例可随时作为回滚目标，不存在数据丢失风险

备选方案 A（直接停机迁移）和方案 B（逐个切换）均因回滚复杂度高或中断时间长被排除。

### 前置条件（4 项，全部满足方可开始）

| # | 条件 | 验证方式 |
|---|------|----------|
| 1 | SSH 访问旧 n8n 实例（n8n.lysander.bond） | `ssh user@n8n.lysander.bond` 测试通过 |
| 2 | 凭证明文可获取（5 类：Slack Bot Token、Asana PAT、Notion API、Fireflies API、Gemini API） | 逐一验证可登录 n8n Credential Store 导出 |
| 3 | n8n.janusd.io 实例已部署并可访问，版本与旧实例一致 | 访问 n8n.janusd.io 登录成功 |
| 4 | pmo-api 有权修改环境变量 `N8N_WF08_URL`（部署或配置访问权） | 验证 pmo-api 配置文件可写 |

### 分步执行清单

#### Step 0：安全修复（强制前置，执行其余步骤前必须完成）

| 任务 | 说明 | 验收标准 |
|------|------|----------|
| 0.1 修复 WF-01 明文 PAT | 将 Code 节点中 `2/1213400756695149/...` 替换为从 Credential Store 读取 | WF-01 在旧实例执行一次完整运行，无报错 |
| 0.2 轮换被暴露的 Asana PAT | 在 Asana 开发者设置中撤销旧 PAT，生成新 PAT | 新 PAT 在 WF-01 测试运行中验证通过 |
| 0.3 更新 Credential Store | 旧 n8n Credential Store 中更新 Asana PAT 为新值 | WF-01 使用新 PAT 运行正常 |

#### Step 1：新实例初始化

| 任务 | 说明 |
|------|------|
| 1.1 新实例环境配置 | 数据库、环境变量、域名解析（n8n.janusd.io）配置完成 |
| 1.2 重建 5 类凭证 | Slack Bot Token、Asana PAT（新）、Notion API、Fireflies API、Gemini API |
| 1.3 凭证连通性验证 | 每类凭证执行一次测试调用，确认可用 |

#### Step 2：工作流导入（按推荐顺序）

推荐迁移顺序：**WF-09 → WF-08 → WF-01 → WF-02 → WF-05 → WF-06 → WF-04 → WF-07**

迁移顺序理由：
- WF-09 先迁（硬编码旧域名，迁移时直接修复）
- WF-08 次之（与 pmo-api 强耦合，需同步更新 `N8N_WF08_URL`，早迁早稳定）
- WF-01 因安全修复已在 Step 0 完成，可直接导出

每个 WF 导入步骤：
1. 从旧实例导出 JSON（保持 inactive 状态导出）
2. 修改硬编码 URL：`n8n.lysander.bond` → `n8n.janusd.io`
3. 检查并修改 `pmo-api.lysander.bond` 引用（按总裁决策点 5 的决策结果处理）
4. 导入新实例，初始状态设为 inactive
5. 单独激活，执行端到端测试，确认后保持 active

#### Step 3：WF-09 特殊处理

WF-09 包含硬编码 `n8n.lysander.bond/webhook/notify`，迁移时必须：
1. 修改为 `n8n.janusd.io/webhook/notify`
2. 更新所有调用方（检查是否有外部系统直接调用旧 Webhook URL）
3. 在新实例激活后，验证 Webhook 可被正常触发

#### Step 4：WF-08 + pmo-api 联动切换

WF-08 通过 pmo-api 的 `N8N_WF08_URL` 环境变量接收触发，迁移步骤：
1. 新实例 WF-08 激活并记录新 Webhook URL
2. 更新 pmo-api 环境变量 `N8N_WF08_URL` 为新 URL
3. 重启 pmo-api 服务
4. 验证端到端触发链路正常

#### Step 5：WF-05 staticData 处理

WF-05 的 staticData 在新实例重新初始化，步骤：
1. 记录旧实例 WF-05 当前 staticData 内容（留存备查）
2. 新实例 WF-05 激活后状态归零，接受初始化
3. 在低流量时段（如凌晨）激活 WF-05
4. 人工观察 24 小时，确认去重逻辑无异常重复推送

#### Step 6：全量验收与切换

所有 8 个 active WF 在新实例验证通过后：
1. 执行完整端到端回归测试（见验收标准）
2. 通知相关用户切换时间窗口（建议选择低流量时段，如周末凌晨）
3. 切换动作：确认新实例所有 WF active 后，停止旧实例所有 WF（pause，不删除）
4. 观察 48 小时，无异常后关闭旧实例（保留备份）

### 关键风险控制点

| 风险 | 概率 | 影响 | 控制措施 |
|------|------|------|----------|
| WF 导出 JSON 包含加密凭证引用失效 | 中 | 高 | 每个 WF 导入后立即执行凭证重绑 |
| 硬编码 URL 漏改 | 中 | 中 | 导入前执行全文搜索（`lysander.bond`），确认零残留 |
| WF-08/pmo-api 切换后 Webhook 断联 | 低 | 高 | 切换前在 staging 环境验证，切换后立即测试 |
| WF-05 去重失效导致重复推送 | 中 | 低 | 低流量时段切换 + 24小时人工监控 |
| 回滚需求触发 | 低 | 高 | 旧实例保持 pause（非删除）状态 7 天，随时可激活 |

### 验收标准

| 编号 | 标准 | 验证方式 |
|------|------|----------|
| M1-A | 全部 8 个 active WF 在新实例状态为 active | n8n UI 截图确认 |
| M1-B | WF-01 使用 Credential Store（无明文 PAT） | 代码审查 + 测试运行 |
| M1-C | WF-09 Webhook URL 指向 janusd.io | Webhook 触发测试 |
| M1-D | WF-08 ↔ pmo-api 触发链路正常 | 端到端触发测试 + 日志确认 |
| M1-E | 新实例无任何 `lysander.bond` 硬编码残留（除 pmo-api 指向决策处理完毕外） | 全文搜索验证 |
| M1-F | 旧实例所有 WF 已 pause，备份完整 | 状态截图 + 备份文件校验 |

### 回滚方案

**回滚触发条件**：新实例任意 WF 出现无法在 30 分钟内修复的故障

**回滚步骤（目标：< 2 分钟完成）**：
1. 激活旧实例所有 WF（从 pause 状态恢复）
2. 修改 pmo-api `N8N_WF08_URL` 环境变量为旧值
3. 重启 pmo-api
4. 验证旧实例 WF-08 触发链路恢复

**回滚后处理**：记录故障原因，修复后重新执行对应 Step，不重复整个流程。

---

## 阶段 2：Asana → Monday 迁移方案（详细）

### 推荐方案及理由

**双轨并行 + 历史数据存档 + 72 小时切换观察**

理由：
- 完整历史迁移复杂度极高，ROI 不合理（Asana API 导出 + Monday API 导入需处理大量字段映射和错误）
- 双轨期控制在 72 小时，最小化数据一致性风险窗口
- 历史数据在 Asana 保留只读访问，业务查阅需求有保障

### 前置条件

| # | 条件 |
|---|------|
| 1 | Monday.com Pro 方案已激活（总裁授权后采购） |
| 2 | Monday.com Admin 权限可用 |
| 3 | 阶段 1 完成后稳定运行满 5 个工作日 |
| 4 | pmo-api Webhook Handler 重写完成并通过安全测试 |
| 5 | `wbs_to_asana.py` 重写为 `wbs_to_monday.py` 并通过单元测试 |

### 技术架构变化说明

#### 概念映射

| Asana 概念 | Monday 对应 | 备注 |
|-----------|-------------|------|
| Project | Board | 1:1 |
| Section | Group | 1:1 |
| Task | Item | 1:1 |
| Subtask（L1-L3） | Subitem | 经典 Board 支持 1 层 |
| Subtask L4（嵌套） | Multi-Level Board | 需验证功能可用性 |
| Custom Field | Column | 类型需逐一映射 |
| Webhook（任务变更通知） | Monday Webhook | 无 HMAC，需替代安全方案 |

#### L4 子任务层级问题

Monday 经典 Board 仅支持 1 层 Subitem，PMO Auto 的 WBS 结构存在 L4 嵌套子任务。解决方案：
- **方案 A**：启用 Multi-Level Board（较新功能，需验证账号是否可用）
- **方案 B**：L4 子任务改为独立 Board + 关联 Link Column

执行前需 ai_systems_dev 验证 Pro 账号下 Multi-Level Board 是否可用，再决定采用 A 或 B。

#### Webhook 替代安全方案（必须实现，不可跳过）

由于 Monday.com 标准 Webhook 不提供 HMAC 签名验证，pmo-api 须实现以下双重安全机制：

**机制 1：IP 白名单过滤**
- Monday.com Webhook 出口 IP 固定（官方文档公布），在 pmo-api 入口做 IP 白名单验证
- 非白名单 IP 的请求直接返回 403，不进入业务逻辑
- 注意：IP 白名单可能因 Monday 基础设施变更而失效，需订阅 Monday 官方变更通知

**机制 2：时间戳窗口验证**
- Monday Webhook Payload 包含事件时间戳
- pmo-api 服务端验证：拒绝时间戳超出当前时间 ±5 分钟的请求
- 防止重放攻击（即使 Webhook URL 泄露，5 分钟后 Payload 无效）

**实现位置**：`pmo-api/src/webhook_handler.py`（新增 `MondayWebhookValidator` 类）

此安全方案必须作为阶段 2 Step 3 的交付物，且为 M2-D 验收标准的必要条件。

#### 代码重写工作量

| 文件 | 重写比例 | 主要变化 |
|------|----------|----------|
| `wbs_to_asana.py` → `wbs_to_monday.py` | 90%+ | 整体 API 客户端替换，GraphQL 接口，字段映射重写 |
| `pmo-api/webhook_handler.py` | 70% | 从 Asana HMAC 验证改为 Monday 替代安全方案 |
| `pmo-api/task_sync.py` | 50% | 任务 CRUD 接口重写 |

### 分步执行清单

#### Step 0：环境准备

| 任务 | 说明 |
|------|------|
| 0.1 Monday Pro 账号激活 | 总裁授权后执行，确认 Automation Actions 配额（25,000次/月） |
| 0.2 Monday Board 结构设计 | 对照 Asana 项目结构，在 Monday 建立等效 Board + Group + Column 结构 |
| 0.3 L4 层级方案确认 | 验证 Multi-Level Board 可用性，确定采用方案 A 或 B |

#### Step 1：代码重写

| 任务 | 说明 |
|------|------|
| 1.1 `wbs_to_monday.py` 开发 | 完整重写 WBS 生成 → Monday 创建逻辑 |
| 1.2 Webhook Handler 重写 | 实现 MondayWebhookValidator（IP 白名单 + 时间戳窗口） |
| 1.3 单元测试 | 覆盖主要场景：WBS 生成、任务创建、Webhook 验证 |

#### Step 2：n8n 工作流适配

| 任务 | 说明 |
|------|------|
| 2.1 Monday API 凭证配置 | 在新 n8n（janusd.io）中添加 Monday API Token 凭证 |
| 2.2 调用 Asana 的 WF 节点替换 | 逐一替换各 WF 中的 Asana 节点为 Monday 节点 |
| 2.3 WF 单独测试 | 每个修改过的 WF 在 staging 环境用真实数据验证 |

#### Step 3：Webhook 安全验证

| 任务 | 说明 |
|------|------|
| 3.1 IP 白名单配置 | 获取 Monday 出口 IP 列表，配置 pmo-api 入口过滤 |
| 3.2 时间戳验证测试 | 测试正常请求通过 + 超时请求被拒绝 + 非白名单 IP 被拒绝 |
| 3.3 安全测试报告 | 输出安全验证报告（作为 M2-D 验收依据） |

#### Step 4：双轨期（72 小时）

| 任务 | 说明 |
|------|------|
| 4.1 进行中 Asana 任务手动迁移 | 切换前盘点所有进行中任务，手动在 Monday 重建 |
| 4.2 双轨启动 | 同时激活 Asana 和 Monday 的数据写入（监控双向一致性） |
| 4.3 72 小时观察 | 监控任务创建、状态更新、通知触发全链路，确认无异常 |

#### Step 5：切换

| 任务 | 说明 |
|------|------|
| 5.1 停止 Asana 写入 | 关闭所有 WF 中的 Asana 节点 |
| 5.2 Monday 全量激活 | 确认 Monday 为唯一写入源 |
| 5.3 Asana 权限降级 | 将 Asana 账号降为只读（保留 90 天，具体以总裁确认为准） |

#### Step 6：稳定运行验收

| 任务 | 说明 |
|------|------|
| 6.1 全量回归测试 | 验证所有 PMO 核心流程在 Monday 上运行正常 |
| 6.2 用户通知 | 通知相关用户 Asana 历史数据可查阅期限 |
| 6.3 文档更新 | 更新 OBS 知识库中涉及 Asana 的 SOP 文档 |

### 关键风险控制点

| 风险 | 概率 | 影响 | 控制措施 |
|------|------|------|----------|
| Monday Webhook 安全漏洞被利用 | 中 | 高 | IP 白名单 + 时间戳窗口双重机制，不可跳过 |
| L4 子任务层级结构在 Monday 不可用 | 中 | 高 | Step 0 提前验证，提前确定备选方案 B |
| GraphQL 并发请求被限速 | 中 | 中 | 实现指数退避重试，批量请求控制并发数 |
| Webhook Payload 不完整需二次 API 回查 | 高 | 中 | 在 webhook_handler 中实现补全查询逻辑，预留延迟处理 |
| 双轨期 Asana/Monday 数据不一致 | 中 | 中 | 双轨期最多 72 小时，专人监控，发现不一致立即修正 |
| Pro 方案 Automation Actions 配额耗尽 | 低 | 高 | 监控配额使用，设置 80% 告警阈值 |

### 验收标准

| 编号 | 标准 | 验证方式 |
|------|------|----------|
| M2-A | WBS 生成 → Monday Item 创建端到端成功 | 真实 WBS 测试运行 |
| M2-B | 任务状态变更 → n8n Webhook 触发 → 通知链路正常 | 端到端测试 |
| M2-C | L4 子任务层级结构正确呈现 | UI 截图 + 数据验证 |
| M2-D | IP 白名单 + 时间戳验证均通过安全测试 | 安全测试报告 |
| M2-E | Asana 账号已降级为只读，历史数据可查阅 | 访问验证 |
| M2-F | 所有相关 OBS 文档已更新（无 Asana 操作引用） | 文档审查 |

---

## 风险矩阵（Top 10）

| 排名 | 风险描述 | 概率 | 影响 | 综合评级 | 缓解措施 |
|------|----------|------|------|----------|----------|
| 1 | WF-01 明文 PAT 已在 git 历史中暴露，修复前凭证处于持续风险中 | 已发生 | 极高 | P0 | 立即轮换 PAT，Step 0 强制前置 |
| 2 | Monday Webhook 无 HMAC，伪造事件可触发高权限 PMO 操作 | 中 | 高 | P1 | IP 白名单 + 时间戳窗口双重机制 |
| 3 | L4 子任务层级在 Monday 不支持，WBS 结构需重设计 | 中 | 高 | P1 | Step 0 提前验证，备选方案 B 已备 |
| 4 | 回滚触发时 DNS 传播延迟导致中断时间超预期 | 中 | 高 | P1 | 改用 URL/环境变量切换，DNS 不变 |
| 5 | 阶段 2 未采购 Monday Pro 直接上线，Automation 配额耗尽 | 低 | 高 | P1 | 前置条件强制：Pro 激活后方可启动阶段 2 |
| 6 | WF-05 状态归零后去重逻辑短暂失效，出现重复推送 | 中 | 中 | P2 | 低流量时段切换 + 24 小时人工监控 |
| 7 | WF-08 / pmo-api URL 切换后触发链路断裂 | 低 | 高 | P2 | 切换前 staging 验证，切换后即时端到端测试 |
| 8 | Monday GraphQL API 并发限速触发批量创建失败 | 中 | 中 | P2 | 指数退避重试 + 并发控制 |
| 9 | 进行中 Asana 任务未在切换前手动迁移，任务丢失 | 低 | 高 | P2 | 切换前强制盘点并全部迁移完成才允许切换 |
| 10 | 阶段 1 和阶段 2 无稳定期间隔，双重变更叠加故障 | 低 | 高 | P2 | 强制 5 个工作日间隔，设为执行约束不可跳过 |

---

## 里程碑总览

| 里程碑 | 内容 | 前置条件 |
|--------|------|----------|
| M0 | 4 项阶段 1 前置条件全部满足 | 总裁审批方案 |
| M0.5 | WF-01 PAT 修复 + 轮换完成 | M0 |
| M1 | 新 n8n 实例所有 8 个 WF 验证通过 | M0.5 |
| M1.5 | 切换完成，旧实例 pause，48 小时稳定观察通过 | M1 |
| M2 | 阶段 1 稳定满 5 个工作日，阶段 2 前置条件满足（含 Pro 方案采购） | M1.5 |
| M3 | `wbs_to_monday.py` + 安全 Webhook Handler 开发完成，测试通过 | M2 |
| M4 | 双轨期 72 小时无异常 | M3 |
| M5 | Monday 全量切换，Asana 只读，全量回归测试通过 | M4 |
| M6 | OBS 文档更新完成，用户通知发出，迁移归档 | M5 |

---

## 执行前需总裁确认的事项

### 决策点 1：Monday.com Pro 方案采购授权

**背景**：Monday.com Free/Basic/Standard 方案的 Automation Actions 配额仅 250 次/月，PMO Auto 每日自动化执行量远超此上限。生产环境必须使用 Pro 方案（25,000 次/月）或 Enterprise 方案。

**影响**：若不采购 Pro，阶段 2 无法在生产环境运行，迁移被迫中止。Pro 方案价格约 $XX/用户/月（需总裁确认可接受的预算范围）。

**推荐决策**：授权采购 Monday.com Pro 方案，作为阶段 2 的硬性前置条件。

**需总裁回答**：是否授权采购 Monday.com Pro 方案？可接受的月预算上限是多少？

---

### 决策点 2：Asana 账号保留期限

**背景**：历史数据不迁移策略已通过评审，但 Asana 账号需保留只读访问一段时间，供团队查阅历史任务记录。

**影响**：
- 保留期越长：查阅灵活性越高，但持续有账号费用（如果是付费账号）
- 保留期越短：成本低，但团队可能在需要时无法访问历史记录

**推荐决策**：保留 90 天只读访问，到期后导出全量数据（JSON/CSV）存档至 OBS，关闭账号。

**需总裁回答**：Asana 账号保留多长时间？90 天是否可接受？

---

### 决策点 3：pmo-api 域名迁移策略

**背景**：`pmo-api.lysander.bond` 在 WF-03、WF-05、WF-08 中硬编码。迁移完成后，此域名需要决策：

- **选项 A：保持 lysander.bond 不变**：零额外工作，但长期维护需同时管理两个域名体系（n8n 在 janusd.io，pmo-api 在 lysander.bond）
- **选项 B：迁移至 pmo-api.janusd.io**：需同步修改 3 个 WF + pmo-api 配置 + DNS，工作量约半天，但长期统一

**总裁决策（2026-04-27）**：两步走方案 — Phase 1 保持 `pmo-api.lysander.bond` 不变（零额外工作，不阻塞 n8n 迁移执行）；Phase 2（Asana→Monday 迁移）完成后，申请 `pmo-api.janusd.io` 并同步迁移，统一 janusd.io 域名体系。

**已批准，无需进一步确认。**

---

### 决策点 4：WF-01 PAT 轮换立即执行授权

**背景**：WF-01 Code 节点中的明文 Asana PAT 已在 git 历史中存在（安全漏洞）。修复需要立即轮换此 PAT，轮换期间 WF-01 会有约 30 分钟中断（修改 + 验证时间）。

**影响**：WF-01 是情报收集相关工作流，30 分钟中断影响极低（不是实时处理）。但轮换 PAT 需要访问 Asana 开发者设置，且轮换后所有使用此 PAT 的地方（如果有其他调用方）需同步更新。

**推荐决策**：立即授权轮换，在下次低流量时段（如当天非工作时间）执行，不等待迁移开始。

**需总裁回答**：是否授权立即轮换 WF-01 使用的 Asana PAT？

---

### 决策点 5：迁移切换时间窗口偏好

**背景**：阶段 1 切换（旧→新 n8n）需约 1~2 小时工作流暂停窗口。阶段 2 切换（Asana→Monday）有 72 小时双轨期。

**影响**：选择切换时间直接影响业务中断风险。建议选择周末凌晨（Dubai 时间）或总裁指定的低风险时段。

**需总裁回答**：是否对迁移切换时间窗口有偏好（例如周末、深夜）？还是授权执行团队自行选择低流量时段？

---

## 附录

### A. n8n Workflow 清单

| WF ID | 名称/功能 | 状态 | 特殊风险 |
|-------|-----------|------|----------|
| WF-01 | 情报收集/Asana 任务处理 | Active | 含明文 PAT（P0，Step 0 修复） |
| WF-02 | 日常任务同步 | Active | 无特殊风险 |
| WF-03 | pmo-api 联动 | Active | 硬编码 `pmo-api.lysander.bond` |
| WF-04 | 报告生成 | Active | 无特殊风险 |
| WF-05 | 去重/状态管理 | Active | staticData 迁移不可携带，状态归零 |
| WF-06 | 通知推送 | Active | Slack Channel ID `C0AJN5PN1G8` 硬编码 |
| WF-07 | 辅助流程 | Active | 无特殊风险 |
| WF-08 | pmo-api Webhook 接收 | Active | 与 pmo-api `N8N_WF08_URL` 强耦合（P0） |
| WF-09 | Notify 通知网关 | Active | 硬编码 `n8n.lysander.bond/webhook/notify`（P0） |

*注：WF-06 中 Slack Channel ID `C0AJN5PN1G8` 为硬编码值，迁移时确认是否需要更新（如 Slack 工作区已切换至 janussandbox）。*

### B. Monday.com API 对比摘要

| 特性 | Asana | Monday.com | 影响 |
|------|-------|------------|------|
| API 协议 | REST | GraphQL | 代码需完整重写 |
| 认证方式 | PAT / OAuth | API Token | 凭证重建 |
| Webhook 安全 | HMAC-SHA256 | 无签名验证 | 需替代安全方案（IP+时间戳） |
| 子任务层级 | 多层 | 1层（标准）/ 多层（Multi-Level） | L4 场景需验证 |
| Automation 配额 | 充足 | 250次/月（Free），25,000次/月（Pro） | 必须 Pro |
| Webhook Payload | 完整 | 部分字段，可能需二次回查 | 需实现补全逻辑 |

### C. 凭证清单

| 凭证类型 | 用途 | 迁移方式 | 安全风险 |
|----------|------|----------|----------|
| Slack Bot Token | WF 通知推送 | 新 n8n 手动录入 | 无（Credential Store） |
| Asana PAT | WF-01 任务操作 | **轮换后** 新 n8n 手动录入 | P0：WF-01 含明文，须先轮换 |
| Notion API Key | 知识库操作 | 新 n8n 手动录入 | 无（Credential Store） |
| Fireflies API Key | 会议记录同步 | 新 n8n 手动录入 | 无（Credential Store） |
| Gemini API Key | AI 处理节点 | 新 n8n 手动录入 | 无（Credential Store） |
| Monday API Token | 阶段 2 新增 | 新 n8n 手动录入 | 新凭证，采购后配置 |

---

*文档版本 v1.0 — 由 synapse_product_owner 主持，execution_auditor + strategy_advisor 评审通过*
*生成时间：2026-04-26*
*下一步：提交总裁审批，确认 5 个决策点后，授权 harness_engineer 启动 Step 0*
