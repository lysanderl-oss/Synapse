# 2026-04-24 Slack 通知修复报告 — REQ-INFRA-004

## TL;DR

情报管线心跳告警 3 天静默不达总裁 Slack。根因不是 n8n/Slack 配置，而是 **调用方 payload 契约不匹配**。修复 heartbeat_check.py 一处，Slack DM 已实际送达 `D0AUZENMGMS`（总裁 DM），`"ok":true` 确认。REQ-INFRA-004 shipped。

## 一、根因

WF-09 (`atit1zW3VYUL54CJ`) unified notify workflow 的 Parse Recipient 节点期望 payload：

```json
{
  "recipient": "president",    // → 翻译为 U0ASLJZMVDE
  "title": "...",
  "body": "...",
  "source": "...",
  "priority": "P0|P1|P2|P3"
}
```

但 `scripts/intelligence/heartbeat_check.py` 直接发：

```json
{"text": "..."}
```

WF-09 Parse Recipient 代码：

```js
const r = b.recipient || '';    // 无 recipient → r = ''
let ch = r;                      // ch = ''
if (r === 'president') ch = 'U0ASLJZMVDE';   // 不触发
```

→ 下游 Send Slack 节点调 `chat.postMessage` with `channel=""` → Slack API 返回 `channel_not_found`。

HTTP 层一切正常（webhook 200 OK），但 Slack 业务层失败，调用方原代码只检查 HTTP 状态码 → 返回"OK" → 告警永远送不出，且 GH Actions 无法察觉。

## 二、修复路径（Path A：修调用方，非改 n8n）

原因：n8n WF-09 本身实现是正确的 unified notify 契约，问题只是调用方没遵守契约。修调用方一处比改 n8n 的契约更安全。

### 变更 1 — heartbeat_check.py payload 契约对齐

- Repo: `lysanderl-glitch/synapse-ops`
- Commit: `644730f`
- 文件：`scripts/intelligence/heartbeat_check.py`
- 关键变更：
  1. 发送 `{recipient: 'president', title, body, source, priority}` 标准 payload
  2. 判成功同时校验 `"ok":true`（不再只看 HTTP 200）— 避免未来类似假阳性

### 变更 2 — REQ-INFRA-004 shipped

- `obs/02-product-knowledge/requirements_pool.yaml`：status `approved` → `shipped`，补 evidence 与根因说明

## 三、验证证据

- GH Actions RUN: `24903092408`（触发 heartbeat-check.yml）
- 日志关键行：
  ```
  [Slack] status=200 http_ok=True slack_ok=True body_preview='{"ok":true,"channel":"D0AUZENMGMS","ts":"1777052001.234579","message":{...,"text":"*情报管线心跳告警*\n..."'
  [Notify] Slack OK
  ```
- `D0AUZENMGMS` 是 Slack DM 的 channel 前缀（`D` = Direct Message），即已送到总裁私聊窗口
- 本次 run 的 failure exit code 是正确行为：2026-04-23 日报确实缺失（情报管线真停摆了），心跳脚本如实报告 → 这次告警是真的"被送达的真告警"

## 四、影响面 / 需关注

- 其他调用 `SLACK_WEBHOOK_N8N` 的脚本（若有）同样需要用 WF-09 契约 payload。建议审计：
  - `intel-daily.yml` / `intel-action.yml` / `task-resume.yml` 是否发送 Slack（目前 heartbeat 是主要使用方，其他 workflow 未确认）
- WF-09 HMAC signature 为可选，未提供时跳过验证；本次未使用签名，工作正常

## 五、经验沉淀

- **HTTP 200 ≠ 业务成功**：对 Slack / Asana / 任何 API proxy 类集成，必须检查上游响应体里的 `ok/success` 字段
- **契约文档缺失**：WF-09 的 payload 契约只藏在节点 JS 代码里，未沉淀到 `obs/03-process-knowledge/`。建议后续补 `wf-09-unified-notify-contract.md`（非本次工单范围）
- **静默告警的元问题**：心跳告警本身不可达 → 监控的监控也要有。下次可考虑给 SLACK_WEBHOOK_N8N 加独立的 Slack-API ok 断言测试（作为 weekly smoke test）
