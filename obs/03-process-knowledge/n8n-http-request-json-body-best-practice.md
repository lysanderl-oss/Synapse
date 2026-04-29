# n8n HTTP Request 节点 JSON Body 最佳实践

**来源**：2026-04-25 WF-09 Unified Notification (`atit1zW3VYUL54CJ`) 生产事故诊断
**适用**：n8n 中所有 HTTP Request 节点（含 Slack / Notion / Asana 等 API 调用）

## 背景

2026-04-25 04:47 UTC，WF-09 Unified Notification 处理含换行符的 body 时抛 `Bad control character in string literal in JSON at position 126`，导致情报管线 Slack 通知 HTTP 500。

总裁本人于 04:55 UTC 把 Send Slack 节点从 **raw JSON 模板模式** 改为 **keypair 模式**，治本。

## 根因

n8n HTTP Request 节点支持两种 JSON Body 配置：

### 模式 A：raw JSON 模板（高风险）

```
specifyBody: json
contentType: json
jsonBody: ={"channel":"{{ $json.channelId }}","text":"{{ $json.body }}"}
```

n8n 把 `{{ $json.body }}` 渲染为**真实字符串值**直接拼接进 JSON 模板，再 `JSON.parse()`。

**风险**：如果 body 含 `\n`（0x0A）、tab（0x09）等控制字符或未转义引号 `"` ，渲染后的字符串是**非法 JSON**，触发 `Bad control character` 错误。

### 模式 B：keypair（推荐）

```
specifyBody: keypair
contentType: json
bodyParameters:
  - name: channel
    value: ={{ $json.channelId }}
  - name: text
    value: ={{ $json.body }}
```

n8n 对每个 value 调用 `JSON.stringify(value)` **安全转义**：
- `\n` → `\\n`（合法 JSON 字符串）
- `"` → `\"`
- 等等

**优势**：
- 字段值可以含任意字符（换行 / 引号 / emoji）
- 不需要调用方提前转义
- 节点配置可读性更好

## 强制原则

**Lysander 治理规则**：n8n 任何 HTTP Request 节点的 `contentType=json` 时：

- ✅ **必须使用 keypair 模式**
- ❌ **禁止 raw JSON 模板模式**（除非有特殊原因，且必须在 prompt 中提前 JSON.stringify）

## 验证方法

定期 review n8n workflow 时，对每个 HTTP Request 节点检查：

```python
# 来自 scripts/n8n/export_workflows.py 的 snapshot
import json
wf = json.load(open('harness/n8n-snapshots/{wf_id}.json'))
for n in wf.get('nodes', []):
    if n.get('type') == 'n8n-nodes-base.httpRequest':
        params = n.get('parameters', {})
        if params.get('contentType') == 'json' and params.get('specifyBody') == 'json':
            print(f"WARN {n.get('name')} uses raw JSON template - audit required")
```

可以扩展到 GH Actions cron 中作为日常审计。

## 教训

- 2026-04-25 WF-09 事故是 raw JSON 模板的典型失败案例
- Lysander 之前未深入 n8n 内部就猜测根因为"multiline bug"，是错误方法论
- 总裁亲自定位到具体节点 + 修复模式
- 新治理：n8n workflow JSON 入 git（`harness/n8n-snapshots/`）+ raw JSON 模板审计

## 关联文档

- 事故诊断报告：`obs/06-daily-reports/2026-04-25-*-diagnosis.md`（如有）
- WF JSON 治理：`harness/n8n-snapshots/`
- feedback memory：`feedback_root_cause_first.md`
- feedback memory：`feedback_canonical_naming.md`
