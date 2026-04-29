# PMO Auto V2.1 Sprint 计划

**版本目标**：pmo-auto-2.1.0
**启动日期**：2026-04-24（总裁授权）
**核心目标**：WBS 链路置信度提升 + 幂等去重完善

## 范围确认

| REQ | 标题 | 优先级 | 分配 | 依赖 |
|-----|------|--------|------|------|
| REQ-012 | WBS WF-02~05 专项验证 | P1 | integration_qa + pmo_test_engineer | 无（Suite D 已就绪） |
| REQ-002 | WBS L3/L4 前置依赖字段 | P2 | harness_engineer | REQ-012 WF-04 验证完成后 |
| REQ-004 | WF-06/WF-08 幂等去重 | P2 | harness_engineer + n8n_ops | 无 |
| REQ-INFRA-001 | credentials.mdenc 修复 | P1 | harness_engineer | 总裁提供主密码（一次性） |

## 执行时序

（按阶段排列，不标注时间）

### 阶段一：测试执行 + 并行开发
- integration_qa 执行 Suite D（TC-D01~D05），生成测试报告
- harness_engineer 并行开发 REQ-004 幂等去重改造
- REQ-INFRA-001：harness_engineer 准备修复脚本 → Lysander 向总裁请求主密码 → 执行修复

### 阶段二：依赖项推进
- REQ-002：WF-04 验证通过后启动，harness_engineer 补齐 L3/L4 前置依赖字段

### 阶段三：集成验证
- integration_qa 执行全量回归（Suite A/B/C/D）
- pmo_test_engineer 出具 V2.1 验收报告

### 门禁条件（发布前必须通过）
- Suite A~D 全部 PASS
- REQ-004 AC1~AC3 验证通过
- REQ-002 AC1~AC3 验证通过
- REQ-INFRA-001 round-trip 验证通过
- 无 P0/P1 未关闭缺陷

## 总裁参与节点（仅以下情况通知）
1. REQ-INFRA-001 修复需主密码：一次性请求，Lysander 单独发起
2. V2.1 GA 验收：专家委员会验收通过后，Slack 通知附验收报告

## 排除范围
- REQ-003（已 shipped @ v2.0-ga）
- REQ-006 / Webhook 监控面板 / 自动告警（P3，deferred）
