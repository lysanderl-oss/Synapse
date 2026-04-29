# Webhook 激活执行报告
时间：2026-04-22

## 执行摘要

执行者：ai_systems_dev
任务：一次性激活所有 Synapse n8n webhook（8个）
执行方式：curl POST + GET 逐个验证

---

## 激活结果

| # | Webhook | 激活响应码 | 验证响应码 | 状态 |
|---|---------|:---------:|:---------:|:---:|
| 1 | intelligence-action | 404 | 404 | ❌ |
| 2 | action-notify | 404 | 404 | ❌ |
| 3 | qa-auto-review | 404 | 404 | ❌ |
| 4 | qa-gate-85 | 404 | 404 | ❌ |
| 5 | task-status | 404 | 404 | ❌ |
| 6 | butler-execute | 404 | 404 | ❌ |
| 7 | expert-review | 404 | 404 | ❌ |
| 8 | lysander-approve | 404 | 404 | ❌ |

---

## 诊断结论

- **成功：0/8**
- **失败：8/8**
- **需人工处理：8（全部）**

### 根本原因分析

所有 8 个 webhook 统一返回 HTTP 404（Not Found），POST 和 GET 行为一致。

**可能的根因（按概率排序）：**

1. **Webhook workflow 未在 n8n 中创建**
   - n8n 服务器本身在响应（而非网络不可达），但 webhook path 未注册
   - 404 是 n8n 对未注册 webhook path 的标准返回码

2. **Workflow 存在但处于 Inactive/Draft 状态**
   - n8n 的 webhook 需要 workflow 处于 Active 状态才能响应
   - 非活跃 workflow 同样返回 404

3. **URL path 与 n8n 内部定义不匹配**
   - n8n webhook path 可能包含额外前缀/后缀（如带测试环境的 `/webhook-test/` 而非 `/webhook/`）
   - workflow 名称与 webhook URL path 不一致

4. **n8n 部署/重启问题**
   - 新部署的 workflow 可能需要重启 n8n 实例才能生效

---

## 人工处理清单

> 需登录 n8n Web UI：https://n8n.lysander.bond

### Step 1：确认 n8n 服务状态
- [ ] 访问 n8n Web UI，确认可登录
- [ ] 检查 n8n 版本，确认 webhook 功能可用

### Step 2：逐个检查 8 个 workflow

| # | Workflow 预期名称 | 检查项 |
|---|-------------------|--------|
| 1 | Intelligence Action | 是否存在？是否 Active？ |
| 2 | Action Notify | 是否存在？是否 Active？ |
| 3 | QA Auto Review | 是否存在？是否 Active？ |
| 4 | QA Gate 85 | 是否存在？是否 Active？ |
| 5 | Task Status | 是否存在？是否 Active？ |
| 6 | Butler Execute | 是否存在？是否 Active？ |
| 7 | Expert Review | 是否存在？是否 Active？ |
| 8 | Lysander Approve | 是否存在？是否 Active？ |

### Step 3：如果 workflow 不存在
- [ ] 从备份/文档中恢复 workflow JSON 配置
- [ ] 或重新创建 workflow
- [ ] 确认 webhook path 与预期 URL 完全一致
- [ ] 保存并激活 workflow

### Step 4：如果 workflow 存在但不响应
- [ ] 确认 workflow 状态为 "Active"（绿色）
- [ ] 查看 workflow 执行日志，确认无触发错误
- [ ] 尝试手动触发一次，查看返回内容

---

## 后续验证建议

自动化验证脚本（修复后可运行）：
```bash
for url in \
  "https://n8n.lysander.bond/webhook/intelligence-action" \
  "https://n8n.lysander.bond/webhook/action-notify" \
  "https://n8n.lysander.bond/webhook/qa-auto-review" \
  "https://n8n.lysander.bond/webhook/qa-gate-85" \
  "https://n8n.lysander.bond/webhook/task-status" \
  "https://n8n.lysander.bond/webhook/butler-execute" \
  "https://n8n.lysander.bond/webhook/expert-review" \
  "https://n8n.lysander.bond/webhook/lysander-approve"; do
  echo "Testing: $url"
  curl -s -o /dev/null -w "POST:%{http_code} " -X POST "$url" -H "Content-Type: application/json" -d "{}" --max-time 15
  curl -s -o /dev/null -w "GET:%{http_code}\n" -X GET "$url" --max-time 15
done
```

**验收标准：** 修复后，8/8 webhook 应返回 200（POST）且 GET 响应一致。

---

## 附件：原始 curl 输出

### POST 激活测试
```
ACT: https://n8n.lysander.bond/webhook/intelligence-action → 404
ACT: https://n8n.lysander.bond/webhook/action-notify → 404
ACT: https://n8n.lysander.bond/webhook/qa-auto-review → 404
ACT: https://n8n.lysander.bond/webhook/qa-gate-85 → 404
ACT: https://n8n.lysander.bond/webhook/task-status → 404
ACT: https://n8n.lysander.bond/webhook/butler-execute → 404
ACT: https://n8n.lysander.bond/webhook/expert-review → 404
ACT: https://n8n.lysander.bond/webhook/lysander-approve → 404
```

### GET 验证测试
```
GET: https://n8n.lysander.bond/webhook/intelligence-action → 404
GET: https://n8n.lysander.bond/webhook/action-notify → 404
GET: https://n8n.lysander.bond/webhook/qa-auto-review → 404
GET: https://n8n.lysander.bond/webhook/qa-gate-85 → 404
GET: https://n8n.lysander.bond/webhook/task-status → 404
GET: https://n8n.lysander.bond/webhook/butler-execute → 404
GET: https://n8n.lysander.bond/webhook/expert-review → 404
GET: https://n8n.lysander.bond/webhook/lysander-approve → 404
```

---

*报告生成时间：2026-04-22*
*执行者：ai_systems_dev*
