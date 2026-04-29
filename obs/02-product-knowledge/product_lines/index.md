# Synapse-PJ 产品线总章

**目录建立日期**：2026-04-24
**当前产品线数**：5 条（V2 章程生效后确认）
**总章编制**：synapse_product_owner（执行秘书）
**关联章程**：`obs/02-product-knowledge/product_committee_charter.md`（v2.0）

---

## 一、产品组合总览

Synapse-PJ 的产品组合采用"内核 + 垂直业务 + 对外交付 + 品牌叙事"四层架构：**Synapse Core** 作为内核能力底座支撑全部业务；**PMO Auto** 是已 GA 的垂直业务自动化实例；**Content Marketing** 承担对外品牌叙事与变现漏斗；**Janus Digital** 把内核 Agent 能力产品化对外销售；**Enterprise Governance** 把内核治理能力咨询化对外交付。五条产品线互为支撑，共享 Synapse Core 的底层能力，互不重复造轮子。

| 产品线 | ID | 成熟度 | 产品线常委 | 首要价值 |
|--------|-----|:---:|-----------|----------|
| Synapse Core | synapse_core | 生产运行 | 总裁 + Lysander 直管 | 内核能力底座 |
| PMO Auto | pmo_auto | V2.0.3 GA 生产运行 | synapse_product_owner | 项目管理自动化 |
| Content Marketing | content_marketing | 生产运行 | content_strategist | 品牌叙事与变现漏斗 |
| Janus Digital | janus_digital | Q2 路线图制定中 | graphify_strategist | 企业 Agent 产品销售 |
| Enterprise Governance | enterprise_governance | Q2 交付物制定中 | graphify_strategist（联合 harness_engineer）| Agent 治理方案交付 |

## 二、产品线关系图

```
                    ┌─────────────────────────────────────┐
                    │  Synapse Core（内核能力底座）         │
                    │  Harness + OBS + Multi-Agent + 决策   │
                    └─────┬────────┬─────────┬─────────────┘
                          │        │         │
                ┌─────────┘        │         └──────────┐
                │                  │                    │
                ▼                  ▼                    ▼
         ┌───────────┐      ┌───────────┐        ┌───────────┐
         │ PMO Auto  │      │  Content  │        │   Janus   │
         │（垂直业务）│      │ Marketing │        │  Digital  │
         │ 生产运行   │      │（品牌叙事）│        │（产品外化）│
         └─────┬─────┘      └─────┬─────┘        └─────┬─────┘
               │                  │                    │
               │   【反哺 Core：方法论升级 / 素材沉淀】 │
               │                  │                    │
               │                  ▼                    │
               │        ┌───────────────────┐         │
               └───────▶│    Enterprise     │◀────────┘
                        │   Governance      │
                        │（治理方案外化）    │
                        └───────────────────┘
```

**关系本质**：Core 为底座，业务线（PMO Auto）反哺方法论，外化产品线（Janus / Enterprise Governance）把 Core 能力对外产品化/咨询化，Content Marketing 横跨所有产品线作为品牌叙事层。

## 三、治理矩阵

| 决策事项 | synapse_core | pmo_auto | content_marketing | janus_digital | enterprise_governance |
|---------|:---:|:---:|:---:|:---:|:---:|
| 日常功能评审 | Lysander | L3: po+Lysander | L3: cs+po | L3: gs+po | L3: gs+po |
| 大版本发布 | L4: 总裁 | L4: 总裁 | L4: 总裁 | L4: 总裁 | L4: 总裁 |
| 技术方案 | L2 harness_ops | L2 harness_ops | L2 harness_ops | L2 harness_ops + ai_ml | L2 harness_ops + ai_ml |
| Bug 修复 | L1 auto | L1 auto | L1 auto | L1 auto | L1 auto |

*（po = synapse_product_owner, cs = content_strategist, gs = graphify_strategist）*

## 四、共享基础设施

所有 5 条产品线共享以下 Synapse Core 提供的底层能力：

- **CEO Guard**：PreToolUse hook 执行链硬约束（主对话工具白/黑名单）
- **Multi-Agent 44 人虚拟组织**：按产品线路由，智囊团 + 8 个执行团队
- **跨会话状态管理**：`agent-butler/config/active_tasks.yaml`
- **凭证管理**：`credentials.mdenc`（由 `creds.py` 加密，主密码由总裁掌握）
- **价值对齐 memory 系统**：feedback / project / user / reference 四类 auto memory
- **自动化编排层**：3 个定时远程 Agent（任务恢复 6:00 / 情报日报 8:00 / 情报行动 10:00 Dubai）

## 五、需求池分区规则

`obs/02-product-knowledge/requirements_pool.yaml` 采用 `product:` 字段分区：

| 字段值 | 对应产品线 |
|--------|-----------|
| `product: synapse_core` | Synapse Core |
| `product: pmo_auto` | PMO Auto |
| `product: content_marketing` | Content Marketing |
| `product: janus_digital` | Janus Digital |
| `product: enterprise_governance` | Enterprise Governance |

新建需求必须声明 `product:` 字段，缺失即视为未归档，QA 门禁拦截。

## 六、版本策略

各产品线独立版本号（子系统版本），根 `VERSION` 保留所有子系统清单：

| 产品线 | 当前版本（tag）| 下一里程碑 |
|--------|--------------|----------|
| Synapse Core | 1.0.0（根 VERSION）| Phase 2 熵增治理收紧（350 → 300 行）|
| PMO Auto | `pmo-auto-2.0.3` | V2.1 backlog 规划（REQ-002 / 003 / 004 重评估）|
| Infra（交叉）| `infra-1.0.1` | 按需 |
| Content Marketing | 未独立打 tag | SEO 策略 + 咨询漏斗落地 |
| Janus Digital | 未独立打 tag | Q2 路线图草案 → 首版 SKU 定义 |
| Enterprise Governance | 未独立打 tag | 《企业 Agent 治理方案白皮书 v1.0》（Q2 末）|

## 七、跨产品线协同原则

1. **Synapse Core 优先**：任何产品线需要新能力时，优先评估是否为 Core 的通用缺失（若是 → 沉淀至 Core 而非业务线重复实现）
2. **方法论反哺 Core**：业务线（如 PMO Auto）发现的经验教训（如 REQ-012-TC-01）必须提炼升级至 Core 的 QA/流程规则
3. **产品线不应重复发明轮子**：已有 Agent 岗位、路由、凭证、工作流都应复用
4. **联合销售优先**：Janus Digital × Enterprise Governance 天然互补（做 Agent vs 管 Agent），大客户场景联合出单
5. **内容矩阵横跨全线**：PMO Auto 的 B 类问题日志、Core 的 A 类系统拆解、治理经验的 C 类方法论，均为 Content Marketing 素材源
6. **跨产品线资源冲突**：由 Lysander 统筹（L3）；涉及 > 100 万资源或战略调整由总裁决策（L4）

## 八、新产品线引入流程

若未来需引入第 6 条产品线（例如：Stock / Growth / 其他）：

1. 产品线提案 → synapse_product_owner 评估市场依据与战略对齐
2. 战略对齐评审 → strategy_advisor（L2 专家评审）
3. 产品委员会正式立项 → Lysander + 产品线常委提名（L3）
4. 建立产品线档案 → `product_lines/{new_product}.md`
5. 需求池分区开启 → `product: {new_id}`
6. 更新本 index.md（增加第 6 条至总览表、治理矩阵、版本表格）

## 九、产品线详情入口

- [Synapse Core](synapse_core.md) — 内核协作运营体系（Harness + OBS + Multi-Agent + 决策）
- [PMO Auto](pmo_auto.md) — 项目管理自动化产品（V2.0.3 GA，WF-01~WF-08 工作流）
- [Content Marketing](content_marketing.md) — 对外品牌与内容营销（lysander.bond，全自动博客流水线）
- [Janus Digital](janus_digital.md) — 企业 Agent 产品销售（Q2 路线图制定中）
- [Enterprise Governance](enterprise_governance.md) — Agent 治理方案交付（白皮书 v1.0 Q2 末）

## 十、关联章程与决议

- 产品委员会章程 v2.0：`../product_committee_charter.md`
- V2 章程批准纪要：`../committee_sessions/2026-04-24-v2-charter-approval.md`
- 综合执行报告：`../../06-daily-reports/2026-04-24-product-committee-execution-report.md`
- 需求池分区规则：`../requirements_pool.yaml`（meta 区）

---

**编制**：synapse_product_owner · **生效**：2026-04-24 · **下次审查**：当新产品线引入或现有产品线重大变化时
