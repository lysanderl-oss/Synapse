## Lysander 目标承接确认

**诉求ID**: {request_id}
**接收时间**: {timestamp}

### 原始诉求
```
{original_input}
```

### Lysander 理解与复述
```
{lysander_restatement}
```

### 目标对齐确认
- [ ] Lysander 理解与总裁目标一致
- [ ] 无偏差，可以执行
- [ ] 有偏差（请总裁确认）: {clarification_needed}

### 决策级别
| 级别 | 判断依据 | 结果 |
|------|---------|------|
| L1 | 例行操作/查询 | {L1_result} |
| L2 | 专家评审需求 | {L2_result} |
| L3 | 跨团队/战略/P0-P1 | {L3_result} ← 默认 |
| L4 | 法律/100万+/公司存亡 | {L4_result} |

**判定结果**: **{decision_level}**

### 派单决策
- [x] 需要派单执行
- [ ] Lysander 直接处理（无需派单）

### 团队派单表
| 工作项 | 执行者 | 交付物 |
|--------|--------|--------|
| {task} | {agent} | {deliverable} |

### Lysander 备注
{note}

---
*此节点为强制机制，不可跳过。*
