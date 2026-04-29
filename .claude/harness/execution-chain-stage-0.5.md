---
id: execution-chain-stage-0.5
type: harness-fragment
parent: CLAUDE.md
extracted_at: 2026-04-27
moved_per: president decision ①A
---

# 执行链【0.5】Lysander 承接节点（详细）

> 触发场景：每次新诉求处理前
> CLAUDE.md 仅保留概要：①复述 ②对齐 ③分级 ④判断派单 ⑤派单表 ⑥intercept 记录

## 强制 6 步骤（不可跳过）

1. **复述总裁的目标/需求**（用自己的语言）
2. **Pending-Dispatch INTEL 自动 review（D2 升级 2026-04-26）**
   - Read `agent-CEO/config/active_objectives.yaml` 的 `dispatch_rules` 段
   - 若 `dispatch_rules.enabled: true`：
     - Read `agent-CEO/config/active_tasks.yaml` 筛选 status=approved-pending-dispatch 的 INTEL-*
     - 按 dispatch_rules 5 条规则匹配每条 INTEL → 决定 action
     - 执行 action（dispatch_immediately / upgrade_to_req / mark_deferred / keep_pending）
     - 受 safeguards 上限保护（每会话 max_auto_dispatch=3, max_auto_upgrade=10）
     - 输出汇报 snapshot 给总裁
   - 若 `dispatch_rules.enabled: false` 或总裁说 override 关键字：跳过此步
   - 此步不阻塞总裁新诉求处理（先做新诉求，会话末尾汇报）
3. **对齐理解**（确认没有偏差）
4. **判断决策级别**（L1-L4）
5. **判断是否需要派单**（还是 Lysander 直接处理）
6. **如需派单 → 输出派单表 → 进入步骤【②】**
7. **调用 LysanderInterceptor.intercept() 记录本次诉求**（第一动作，紧接问候语后执行）
   - 触发时机：每次用户新诉求，不是续接上一个任务时
   - 调用方式：在主对话中直接调用 Python 函数
   - 代码位置：`agent-CEO/lysander_interceptor.py` → `LysanderInterceptor().intercept(original_user_input)`
   - 结果写入：`agent-CEO/data/intercept_log.yaml`
   - 违规检测：intercept_log.yaml 中无对应时间戳内的记录 → 执行链断裂

⚠️ 此节点不可跳过，无论 Auto Mode 还是手动模式
