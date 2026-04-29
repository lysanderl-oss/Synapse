---
title: PMO Auto 产品迭代治理规范
version: v1.0
status: active
created: 2026-04-24
approved_by: 总裁刘子杨
approved_date: 2026-04-24
---

# PMO Auto 产品迭代治理规范 v1.0

## 一、工作模式声明

**生效日期**：2026-04-24（总裁口头批准）

PMO Auto 产品迭代采用**全程自主模式**：Lysander CEO 统筹团队完成产品设计→开发→测试全链路，专家委员会验收通过后通知总裁。总裁不参与过程工作。

> 变更背景：原"边测试边反馈"模式要求总裁参与中间过程，2026-04-24 总裁明确要求改为基于产品和需求角度沟通，过程工作全部由 Lysander 组织团队完成。

---

## 二、总裁参与边界

| 场景 | 总裁参与方式 | 
|------|------------|
| 大版本 GA 验收（如 V2.1, V3.0） | L4 决策：查看验收报告，批准发布 |
| 新产品线立项 / 方向性变更 | L4 决策：策略对齐 |
| P0 缺陷影响生产且团队无法自主修复 | L4 上报：提供阻塞原因 + 方案建议 |
| 需要总裁操作外部系统 | 具体操作请求（DNS/凭证/服务器），一次性 |
| 小版本发布（patch/minor） | **无需参与**：Slack 通知摘要（无需回复） |
| 需求评审、Sprint 规划 | **无需参与**：产品委员会内部完成 |
| 开发过程、代码审查 | **无需参与** |
| 测试执行与修复 | **无需参与** |

---

## 三、标准迭代流程

```
需求入池（requirements_pool.yaml）
    ↓
requirements_analyst RICE 评分 + 优先级排序
    ↓
synapse_product_owner PRD 更新（功能规格 + AC 定义）
    ↓
产品委员会 PRD 评审（Lysander 批准）         ← 无需总裁
    ↓
harness_engineer / ai_systems_dev 开发
    ↓
integration_qa 代码审查 + 单元测试
    ↓
pmo_test_engineer 验收测试套件（Suite A/B/C）
    ↓
synapse_product_owner 出具验收报告
    ↓
Lysander 签发 + git tag 打版本号
    ↓
Slack 通知总裁（小版本：摘要通知；大版本：附验收报告请求确认）
```

---

## 四、通知标准

### 小版本（patch x.x.y）
- 通知方式：Slack 消息摘要
- 包含内容：版本号、修复/功能摘要（3句话内）、git tag
- 无需总裁回复

### 大版本 GA（x.y.0）
- 通知方式：Slack 消息 + 验收报告链接
- 包含内容：北极星指标实测值、测试通过率、已知遗留项、git tag
- 需要总裁确认批准（L4 节点）

---

## 五、当前在途任务（2026-04-24 快照）

| 版本目标 | 需求 | 优先级 | 状态 |
|---------|------|--------|------|
| pmo-auto-2.0.3 | REQ-012-D-01：WF-05 OOM 崩溃修复 | P0 | in_progress |
| next-available | REQ-INFRA-001：credentials.mdenc 损坏修复 | P1 | approved |
| v2.1 | REQ-012：WBS WF-02~05 专项验证 | P1 | approved |
| v2.1 | REQ-002：WBS L3/L4 前置依赖字段 | P2 | candidate |
| v2.1 | REQ-003：时区配置统一 | P2 | candidate |
| v2.1 | REQ-004：WF-06/WF-08 幂等去重 | P2 | candidate |
| v2.1 | Webhook 监控面板 + 未注册告警 | P3 | planned |

---

*编制：knowledge_engineer | 批准：Lysander CEO | 总裁授权日期：2026-04-24*
