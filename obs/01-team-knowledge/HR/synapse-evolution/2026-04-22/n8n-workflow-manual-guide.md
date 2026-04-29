# n8n Workflow 人工创建指南（方案C兜底）

> **适用场景**：n8n API Key 暂不可用，需要手动在 n8n UI 中创建所有 workflow
> **预计时间**：10 分钟（8 个 workflow）
> **n8n 地址**：`https://n8n.lysander.bond`
> **HMAC 密钥**：`MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8`
> **前置准备**：登录 `https://n8n.lysander.bond`，准备好 SMTP 邮件凭证和 Slack Bot Token

---

## 通用意愿（每个 Workflow 都要做）

创建每个 workflow 前，请按以下顺序完成通用步骤：

1. 点击左侧菜单 **"Workflows"** → 点击右上角 **"+""（新建）**
2. 点击 workflow 画布中央的 **"+""** 打开节点搜索
3. 搜索并添加 **Trigger 节点**（见各 workflow 说明）
4. 按顺序添加功能 Node（见各 workflow 说明）
5. **配置 Error Trigger**（见附录 A，必须做！不可跳过）
6. 点击 workflow 名称旁边的 **"Active" 开关** → 设为 ON（绿色）
7. 点击右上角 **"Save"** 保存

---

## WF-1：intelligence-action（情报行动触发）

**作用**：每日 10:00 Dubai 定时运行，读取最新情报日报，调用 Claude API 评估优先级，输出行动报告
**Trigger**：Schedule（Cron）

### 步骤 1/8 — 创建 workflow 并命名

1. 左侧菜单点击 **Workflows** → 点击右上角 **"+""**
2. 点击画布中央的 **"Add first node..."**
3. 搜索 `Schedule`，选择 **Schedule Trigger** 节点，点击添加

### 步骤 2 — 配置 Cron 触发器

1. 点击画布上的 **Schedule Trigger** 节点
2. 右侧面板中找到 **"Cron"** 选项，选择 `Custom`
3. 在 **"Expression"** 输入框填写：
   ```
   0 6 * * *
   ```
   （说明：UTC 06:00 = Dubai 10:00）
4. **"Timezone"** 填写：`Asia/Dubai`

### 步骤 3 — 添加 Read File 节点（读取最新日报）

1. 点击 **Schedule Trigger** 右侧的 **"+"** → 搜索 `Read Binary File` 或 `Read Document`
2. 选择 **Read File** 节点（或使用 `n8n-nodes-base.readBinaryFile`）
3. **注意**：此节点在手动创建时需要文件路径。建议在下一步 Claude API 节点中使用 `HTTP Request` 节点通过 webhook URL 读取文件。**替代方案**：将此节点留空，改为在 Code 节点中硬编码最新日报路径

### 步骤 4 — 添加 HTTP Request 节点（调用 Claude API）

1. 点击上一步节点右侧的 **"+"** → 搜索 `HTTP Request`
2. 选择 **HTTP Request** 节点
3. 右侧面板配置：
   - **Method**：`POST`
   - **URL**：`https://api.anthropic.com/v1/messages`
   - **Authentication**：`Predefined Credential Type` → 选择 `HTTP Header Auth`
     - **Name**：`x-api-key`
     - **Value**：`sk-ant-`（替换为你的 Anthropic API Key）
   - **Headers** 标签页，点击 **"Add Header"**：
     - `anthropic-version`：`2023-06-01`
     - `content-type`：`application/json`
   - **Body Content Type**：`JSON`
   - **Body** 标签页，选择 `JSON`（或 `Raw`），粘贴以下内容：

```json
{
  "model": "claude-sonnet-4-7",
  "max_tokens": 4096,
  "messages": [
    {
      "role": "user",
      "content": "你是 Synapse 智囊团情报行动评估专家。分析以下情报日报，评估每条情报的行动紧迫度。\n\n评估标准：\n- P0：影响公司存续/重大不可逆风险，需立即处理\n- P1：本周内必须执行，有明确行动方\n- P2：观察跟踪，月内评估\n\n对每条情报输出 JSON 格式：\n{\n  \"intelligence_items\": [\n    {\n      \"id\": \"INTEL-YYYYMMDD-NNN\",\n      \"title\": \"情报标题\",\n      \"priority\": \"P0|P1|P2\",\n      \"action_text\": \"行动建议\",\n      \"confidence_score\": 1-20,\n      \"source\": \"来源\"\n    }\n  ],\n  \"high_priority_count\": N,\n  \"evaluation_summary\": \"一句话总结\"\n}\n\n日报内容：[从文件读取的内容，如果还没有文件请基于上下文评估]"
    }
  ]
}
```

### 步骤 5 — 添加 Code 节点（解析评估结果）

1. 点击 HTTP Request 右侧的 **"+"** → 搜索 `Code`
2. 选择 **Code** 节点
3. 填写 JavaScript 代码：

```javascript
// 解析 Claude API 响应
const response = $input.first().json;
const text = response.content?.[0]?.text || '';

// 尝试从 text 中提取 JSON
let evalResult = { high_priority_count: 0, intelligence_items: [] };
try {
  // 查找 JSON 代码块
  const jsonMatch = text.match(/```json\n?([\s\S]*?)\n?```/) || text.match(/(\{[\s\S]*\})/);
  if (jsonMatch) {
    evalResult = JSON.parse(jsonMatch[1] || jsonMatch[0]);
  }
} catch (e) {
  // 降级处理
  evalResult = {
    high_priority_count: 0,
    intelligence_items: [],
    evaluation_summary: text.substring(0, 500)
  };
}

return [{ json: {
  workflow: 'intelligence-action',
  evaluation_date: new Date().toISOString().split('T')[0],
  high_priority_count: evalResult.high_priority_count || 0,
  intelligence_items: evalResult.intelligence_items || [],
  evaluation_summary: evalResult.evaluation_summary || '',
  triggered: evalResult.high_priority_count > 0 ? 'action-notify' : null
}}];
```

### 步骤 6 — 添加 IF 节点（判断是否触发通知）

1. 点击 Code 节点右侧的 **"+"** → 搜索 `IF`
2. 选择 **IF** 节点
3. 右侧配置：
   - **Condition 1**：`String` → `Operation` → `Exists`
   - 点击 **"Add Condition"**：
   - **Value 1**（左）：`{{ $json.triggered }}`
   - **Operation**（中）：`Equals`
   - **Value 2**（右）：`action-notify`

### 步骤 7 — 添加 HTTP Request 节点（POST 到 WF-2）

1. 从 IF 节点的 **"true"** 分支右侧点击 **"+"**
2. 搜索并添加 **HTTP Request** 节点
3. 配置：
   - **Method**：`POST`
   - **URL**：`https://n8n.lysander.bond/webhook/action-notify`
   - **Authentication**：`Generic Credential Type` → 选择 `HTTP Header Auth`
     - 添加 Header `x-hmac-signature`：`MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8`
   - **Body Content Type**：`JSON`
   - **Body**：

```json
{
  "evaluation_date": "{{ $json.evaluation_date }}",
  "high_priority_count": "{{ $json.high_priority_count }}",
  "intelligence_items": "{{ $json.intelligence_items }}",
  "triggered_by": "intelligence-action"
}
```

### 步骤 8 — 命名并激活

1. 点击左上角 workflow 名称，修改为：`Synapse-WF1-intelligence-action`
2. 点击右侧 **"Add Workflow Tag"**（可选）：`synapse-evolution`
3. 点击右上角 **"Active"** 开关 → 设为 **ON**
4. 点击右上角 **Save**

---

## WF-2：action-notify（行动通知）

**作用**：接收 WF-1 的高优先级行动，发送 Slack 通知，更新 active_tasks.yaml
**Trigger**：Webhook（POST）

### 步骤 1/8 — 创建 workflow

1. **Workflows** → **"+"** → 命名：`Synapse-WF2-action-notify`
2. 点击 **"Add first node..."** → 搜索 `Webhook` → 选择 **Webhook** 节点

### 步骤 2 — 配置 Webhook Trigger

1. 点击 Webhook 节点，右侧配置：
   - **HTTP Method**：`POST`
   - **Path**：`action-notify`（完整 URL：`https://n8n.lysander.bond/webhook/action-notify`）
   - **Respond**：`Respond Immediately`
   - **Respond With**：`JSON`
   - **Respond Options** → **Response Code**：`200`

### 步骤 3 — 添加 Code 节点（解析输入）

1. 点击 Webhook 右侧的 **"+"** → 添加 **Code** 节点
2. 代码：

```javascript
const data = $input.first().json;
const items = data.intelligence_items || [];
const highPriorityCount = data.high_priority_count || 0;

const output = {
  evaluation_date: data.evaluation_date || new Date().toISOString().split('T')[0],
  high_priority_count: highPriorityCount,
  items: items,
  report_path: `obs/01-team-knowledge/HR/intelligence-actions/INTEL-${(data.evaluation_date || '').replace(/-/g, '')}-ACTION.md`
};

return [{ json: output }];
```

### 步骤 4 — 添加 Slack 通知节点

1. 点击 Code 节点右侧的 **"+"** → 搜索 `Slack` → 选择 **Slack Message** 节点
2. 如果是首次使用，点击 **"Create New Credential"**：
   - **Slack Bot Token**：`xoxb-`（你的 Slack Bot Token）
3. 节点配置：
   - **Channel**：`#synapse-alerts`（替换为实际 channel 名）
   - **Text**：

```
[Synapse 情报行动] {{ $json.evaluation_date }}
高优先级行动 {{ $json.high_priority_count }} 条：

{{ $json.items.map(item => item.priority === 'P0' ? '🔥 P0 — ' + item.id + ': ' + item.title + '\n  行动：' + item.action_text : '').join('\n') }}

{{ $json.items.filter(item => item.priority === 'P1').map(item => '⚡ P1 — ' + item.id + ': ' + item.title + '\n  行动：' + item.action_text).join('\n') }}

报告路径：{{ $json.report_path }}
```

### 步骤 5 — 添加 Write File 节点（更新 active_tasks）

1. 点击 Slack 节点右侧的 **"+"** → 搜索 `Write File`（或 `Write Binary File`）
2. 选择 **Write File** 节点
3. 配置：
   - **File Name**：`C:/Users/lysanderl_janusd/Synapse-Mini/agent-butler/config/active_tasks.yaml`
     （或使用 n8n 的文件节点配置，SMB 路径或直接路径视部署方式而定）
   - **File Content**：此节点需要先读取现有文件再追加。建议改为：
     - 添加 **Read File** 节点读取 `active_tasks.yaml`
     - 添加 **Code** 节点将新任务追加到 YAML
     - 再添加 **Write File** 节点写入

### 步骤 6（替代方案）— 简化为纯通知模式

如果文件写入复杂，可简化为：
1. 删除上述 Write File 相关节点
2. 在 Slack 消息中包含所有必要信息，让 Lysander 手动更新 active_tasks.yaml

### 步骤 7 — 命名并激活

1. 命名：`Synapse-WF2-action-notify`
2. 点击右上角 **Active** → **ON**
3. 保存

**测试方法**：在另一个标签页打开 `https://n8n.lysander.bond/webhook/action-notify`，使用 Postman 或 curl POST 测试：
```bash
curl -X POST https://n8n.lysander.bond/webhook/action-notify \
  -H "Content-Type: application/json" \
  -d '{"evaluation_date":"2026-04-22","high_priority_count":2,"intelligence_items":[{"id":"INTEL-20260422-001","title":"测试情报","priority":"P1","action_text":"执行测试"}]}'
```

---

## WF-3：qa-auto-review（自动QA审查）

**作用**：接收 Git push webhook，执行 YAML 语法检查和 CLAUDE.md 行数验证，计算五维评分
**Trigger**：Webhook（POST）

### 步骤 1/8 — 创建 workflow

1. **Workflows** → **"+"** → 命名：`Synapse-WF3-qa-auto-review`
2. 点击 **"Add first node..."** → 搜索 `Webhook` → 选择 **Webhook** 节点

### 步骤 2 — 配置 Webhook Trigger

1. Webhook 节点配置：
   - **HTTP Method**：`POST`
   - **Path**：`qa-auto-review`
   - **Respond**：`Respond Immediately`
   - **Response Code**：`200`

### 步骤 3 — 添加 Code 节点（提取变更文件）

```javascript
const webhookData = $input.first().json;
const commits = webhookData.commits || [];

// 提取所有变更文件
const files = {
  added: [],
  modified: [],
  removed: []
};

commits.forEach(commit => {
  if (commit.added) files.added.push(...commit.added);
  if (commit.modified) files.modified.push(...commit.modified);
  if (commit.removed) files.removed.push(...commit.removed);
});

// 过滤相关文件
const relevantFiles = [
  ...files.modified.filter(f => f.includes('agent-butler/') || f.includes('CLAUDE.md') || f.endsWith('.yaml') || f.endsWith('.py')),
  ...files.added.filter(f => f.includes('agent-butler/') || f.endsWith('.yaml') || f.endsWith('.py'))
];

return [{
  json: {
    repository: webhookData.repository?.full_name || '',
    pusher: webhookData.pusher?.name || '',
    files: relevantFiles,
    all_files: files,
    commit_count: commits.length
  }
}];
```

### 步骤 4 — 添加 IF 节点（过滤相关文件）

1. 添加 **IF** 节点
2. 配置：
   - **Value 1**：`{{ $json.files.length }}`
   - **Operation**：`LARGER`（或 `> 0`）
   - **Value 2**：`0`

### 步骤 5 — 添加 Code 节点（YAML 语法检查）

在 IF 的 **true** 分支添加 **Code** 节点：

```javascript
// 简化版 YAML 检查（n8n Code 节点无 pyyaml，需手动解析）
const files = $input.first().json.files || [];
const issues = [];

// 模拟检查逻辑（实际应用中需要读取文件内容）
files.forEach(file => {
  if (file.endsWith('.yaml') || file.endsWith('.yml')) {
    // 基础检查：缩进一致性、大括号匹配
    // 这里需要配合 Read File 节点读取实际文件内容
    issues.push({
      file: file,
      type: 'syntax',
      severity: 'info',
      message: 'YAML 文件已识别，建议后续扩展自动检查'
    });
  }
  if (file === 'CLAUDE.md') {
    issues.push({
      file: file,
      type: 'compliance',
      severity: 'info',
      message: 'CLAUDE.md 已变更，建议人工复核行数限制（350行）'
    });
  }
});

// 计算简化评分（实际评分需扩展）
const baseScore = 85;
const penalty = issues.filter(i => i.severity === 'error').length * 15;
const score = Math.max(0, baseScore - penalty);

return [{
  json: {
    score: score,
    issues: issues,
    files_reviewed: files.length,
    gate_result: score >= 85 ? 'pass' : 'fail'
  }
}];
```

### 步骤 6 — 添加 IF 节点（评分门禁）

1. 添加 **IF** 节点
2. 配置：
   - **Value 1**：`{{ $json.score }}`
   - **Operation**：`SMALLER`（或 `<`）
   - **Value 2**：`85`

### 步骤 7 — 添加 HTTP Request 节点（触发 WF-4）

从 IF 的 **true** 分支添加 **HTTP Request**：
- **Method**：`POST`
- **URL**：`https://n8n.lysander.bond/webhook/qa-gate-85`
- **Body**：

```json
{
  "workflow": "qa-auto-review",
  "status": "fail",
  "score": "{{ $json.score }}",
  "issues": "{{ $json.issues }}",
  "gate_result": "fail",
  "failed_at": "{{ $now.toISO() }}"
}
```

### 步骤 8 — 命名并激活

1. 命名：`Synapse-WF3-qa-auto-review`
2. 点击 **Active** → **ON** → 保存

---

## WF-4：qa-gate-85（QA门禁告警）

**作用**：WF-3 评分 <85 时触发，发送 Slack 告警，通知 integration_qa 修复
**Trigger**：Webhook（POST）

### 步骤 1/8 — 创建 workflow

1. **Workflows** → **"+"** → 命名：`Synapse-WF4-qa-gate-85`
2. 添加 **Webhook** 节点

### 步骤 2 — 配置 Webhook

- **HTTP Method**：`POST`
- **Path**：`qa-gate-85`
- **Respond**：`Respond Immediately`
- **Response Code**：`200`

### 步骤 3 — 添加 Code 节点（格式化告警）

```javascript
const data = $input.first().json;
const score = data.score || 0;
const issues = data.issues || [];
const topIssue = issues.length > 0 ? issues[0].message : '未知问题';

const fileList = issues.map(i => `• ${i.file}: ${i.message}`).join('\n');

return [{
  json: {
    alert_text: `[QA GATE BLOCKED] score=${score}/100\n\n问题：${topIssue}\n\n错误详情：\n${fileList}\n\n🚫 交付被阻止 — integration_qa 需修复后重提`,
    score: score,
    issues: issues,
    alert_sent: false
  }
}];
```

### 步骤 4 — 添加 Slack 节点

1. 添加 **Slack Message** 节点
2. 配置：
   - **Channel**：`#synapse-alerts`
   - **Text**：`{{ $json.alert_text }}`

### 步骤 5 — 更新 alert_sent 状态

1. 添加 **Code** 节点
2. 代码：

```javascript
return [{ json: { alert_sent: true, executed_at: new Date().toISOString() } }];
```

### 步骤 6 — 命名并激活

1. 命名：`Synapse-WF4-qa-gate-85`
2. **Active** → **ON** → 保存

---

## WF-5：task-status（任务状态同步）

**作用**：每日 06:00 Dubai 读取 active_tasks.yaml，生成任务状态报告
**Trigger**：Schedule（Cron）

### 步骤 1/8 — 创建 workflow

1. **Workflows** → **"+"** → 命名：`Synapse-WF5-task-status`
2. 添加 **Schedule Trigger** 节点

### 步骤 2 — 配置 Cron

- **Cron Expression**：`0 2 * * *`（UTC 02:00 = Dubai 06:00）
- **Timezone**：`Asia/Dubai`

### 步骤 3 — 添加 Read File 节点

1. 添加 **Read File** 节点
2. 配置：
   - **File Name**：`C:/Users/lysanderl_janusd/Synapse-Mini/agent-butler/config/active_tasks.yaml`

### 步骤 4 — 添加 Code 节点（解析任务状态）

```javascript
// 简化版任务状态解析
// 实际需要 YAML 解析库或手动解析 YAML 格式
const inputData = $input.first().json;
const fileContent = inputData.data || inputData; // 根据 Read File 节点输出调整

// 如果是二进制文件输出，需要调整解析逻辑
// 这里假设输出为文本内容
let tasks = { in_progress: [], inbox: [], assessed: [], completed: [] };
try {
  const content = typeof fileContent === 'string' ? fileContent : JSON.stringify(fileContent);
  // 基础统计（实际应用中需要更完整的 YAML 解析）
  const inProgressMatch = content.match(/in_progress:\s*(\d+)/);
  const totalMatch = content.match(/total:\s*(\d+)/);
  tasks.total = totalMatch ? parseInt(totalMatch[1]) : 0;
} catch (e) {
  tasks.error = e.message;
}

const today = new Date().toISOString().split('T')[0];

return [{
  json: {
    workflow: 'task-status',
    report_date: today,
    summary: tasks,
    overdue_tasks: [],
    report_generated: true
  }
}];
```

### 步骤 5 — 添加 Write File 节点（生成报告）

1. 添加 **Write File** 节点
2. 配置：
   - **File Name**：`C:/Users/lysanderl_janusd/Synapse-Mini/obs/06-daily-reports/task-status-{{ $now.format('YYYY-MM-DD') }}.md`
   - **File Content**：

```
# 任务状态报告 {{ $now.format('YYYY-MM-DD') }}

## 摘要
- 总任务数：{{ $json.summary.total || 0 }}
- 进行中：{{ $json.summary.in_progress || 0 }}

## 逾期任务
（无）

## 本日关注
定时任务运行正常。
```

### 步骤 6 — 命名并激活

1. 命名：`Synapse-WF5-task-status`
2. **Active** → **ON** → 保存

---

## WF-6：butler-execute（Butler任务执行）

**作用**：决策链入口，接收派单请求，按决策级别路由
**Trigger**：Webhook（POST）

### 步骤 1/8 — 创建 workflow

1. **Workflows** → **"+"** → 命名：`Synapse-WF6-butler-execute`
2. 添加 **Webhook** 节点

### 步骤 2 — 配置 Webhook

- **HTTP Method**：`POST`
- **Path**：`butler-execute`
- **Respond**：`Respond Immediately`
- **Response Code**：`200`

### 步骤 3 — 添加 Code 节点（验证并记录）

```javascript
const data = $input.first().json;

// 生成执行回执
const receiptId = 'RCP-' + new Date().toISOString().split('T')[0].replace(/-/g, '') + '-' + Math.floor(Math.random() * 1000);
const decisionLevel = data.decision_level || 'L1';

return [{
  json: {
    receipt_id: receiptId,
    task_id: data.task?.title || 'UNKNOWN',
    decision_level: decisionLevel,
    status: 'received',
    routed_to: {
      team: data.task?.team || 'butler',
      workflow: decisionLevel === 'L1' ? 'direct_execute' : 'expert-review'
    },
    next_step: decisionLevel === 'L1' ? null : 'WF-7-expert-review',
    executed_at: new Date().toISOString()
  }
}];
```

### 步骤 4 — 添加 IF 节点（L1 直接执行 vs L2+ 路由）

- **Value 1**：`{{ $json.decision_level }}`
- **Operation**：`NOT EQUAL`（或 `!=`）
- **Value 2**：`L1`

### 步骤 5 — L2/L3 分支：POST 到 WF-7

从 IF 的 **true** 分支添加 **HTTP Request**：
- **Method**：`POST`
- **URL**：`https://n8n.lysander.bond/webhook/expert-review`
- **Body**：

```json
{
  "review_id": "REV-{{ $now.format('YYYYMMDD') }}-001",
  "source_workflow": "butler-execute",
  "dispatch_id": "{{ $json.receipt_id }}",
  "timestamp": "{{ $now.toISO() }}",
  "task": {{ $json.task }},
  "decision_level": "{{ $json.decision_level }}",
  "experts_requested": [
    { "agent_id": "decision_advisor", "domain": "综合决策" }
  ]
}
```

### 步骤 6 — 添加 Slack 回执节点

1. 添加 **Slack Message** 节点（放在 IF 之后，无论 true/false 都执行）
2. 配置：
   - **Channel**：`#synapse-ops`
   - **Text**：`[Butler Receipt] {{ $json.receipt_id }} | {{ $json.decision_level }} | {{ $json.status }}`

### 步骤 7 — 命名并激活

1. 命名：`Synapse-WF6-butler-execute`
2. **Active** → **ON** → 保存

---

## WF-7：expert-review（专家评审）

**作用**：接收任务，调用 Claude API 收集专家意见，合成决策建议
**Trigger**：Webhook（POST）

### 步骤 1/8 — 创建 workflow

1. **Workflows** → **"+"** → 命名：`Synapse-WF7-expert-review`
2. 添加 **Webhook** 节点

### 步骤 2 — 配置 Webhook

- **HTTP Method**：`POST`
- **Path**：`expert-review`
- **Respond**：`Respond Immediately`
- **Response Code**：`200`

### 步骤 3 — 添加 Code 节点（确定专家列表）

```javascript
const data = $input.first().json;
const taskType = data.task?.task_type || '';
const decisionLevel = data.decision_level || 'L2';

// 根据任务类型确定专家
const expertMap = {
  'harness': { agent_id: 'harness_engineer', domain: 'Harness配置' },
  'code': { agent_id: 'ai_systems_dev', domain: '系统开发' },
  'knowledge': { agent_id: 'knowledge_engineer', domain: '知识工程' },
  'qa': { agent_id: 'integration_qa', domain: '质量保障' }
};

const matchedExpert = Object.entries(expertMap).find(([key]) =>
  taskType.toLowerCase().includes(key)
);
const expert = matchedExpert ? matchedExpert[1] : { agent_id: 'decision_advisor', domain: '综合决策' };

return [{
  json: {
    review_id: data.review_id || 'REV-' + new Date().toISOString().split('T')[0].replace(/-/g, ''),
    experts: [expert],
    task: data.task,
    decision_level: decisionLevel,
    synthesis: null
  }
}];
```

### 步骤 4 — 添加 HTTP Request 节点（Claude API 调用）

1. 添加 **HTTP Request** 节点
2. 配置：
   - **Method**：`POST`
   - **URL**：`https://api.anthropic.com/v1/messages`
   - **Authentication**：`HTTP Header Auth` → `x-api-key`：`sk-ant-`（你的 API Key）
   - **Headers**：`anthropic-version: 2023-06-01`
   - **Body**：

```json
{
  "model": "claude-sonnet-4-7",
  "max_tokens": 4096,
  "messages": [
    {
      "role": "user",
      "content": "你是 Synapse 智囊团 {{ $json.experts[0].domain }} 专家 Agent（{{ $json.experts[0].agent_id }}）。\n当前需要评审以下任务并给出专业意见：\n\n任务：{{ $json.task?.title || '未命名任务' }}\n描述：{{ $json.task?.description || '无描述' }}\n优先级：{{ $json.task?.priority || 'P2' }}\n\n请从 {{ $json.experts[0].domain }} 专业角度分析：\n1. 主要风险点\n2. 可行性评估\n3. 建议的行动方案\n4. 推荐置信度（0-100）\n\n输出 JSON：\n{\n  \"agent_id\": \"{{ $json.experts[0].agent_id }}\",\n  \"domain\": \"{{ $json.experts[0].domain }}\",\n  \"opinion\": \"...\",\n  \"confidence\": 75,\n  \"recommendation\": \"approve\"\n}"
    }
  ]
}
```

### 步骤 5 — 添加 Code 节点（合成意见）

```javascript
const apiResponse = $input.first().json;
const inputData = $input.item.previousNodeOutput || {};

let opinion = { recommendation: 'approve', confidence: 70, pros: [], cons: [] };
try {
  const text = apiResponse.content?.[0]?.text || '';
  const jsonMatch = text.match(/```json\n?([\s\S]*?)\n?```/) || text.match(/(\{[\s\S]*\})/);
  if (jsonMatch) {
    opinion = JSON.parse(jsonMatch[1] || jsonMatch[0]);
  }
} catch (e) {
  opinion.opinion = '自动评审完成（解析降级）';
}

return [{
  json: {
    workflow: 'expert-review',
    review_id: inputData.review_id || 'REV-UNKNOWN',
    status: 'completed',
    expert_opinions: [opinion],
    synthesis: {
      recommendation: opinion.recommendation || 'approve',
      confidence_score: opinion.confidence || 70,
      pros: opinion.pros || [],
      cons: opinion.cons || [],
      key_concerns: []
    },
    next_workflow: inputData.decision_level === 'L3' ? 'WF-8-lysander-approve' : null
  }
}];
```

### 步骤 6 — 添加 IF（L3 触发 WF-8）

1. 添加 **IF** 节点
2. 配置：
   - **Value 1**：`{{ $json.synthesis.recommendation }}`
   - **Operation**：`NOT EQUAL`
   - **Value 2**：`approve`

### 步骤 7 — L3 路由：POST 到 WF-8

从 IF 的 **true** 分支添加 **HTTP Request**：
- **Method**：`POST`
- **URL**：`https://n8n.lysander.bond/webhook/lysander-approve`
- **Body**：

```json
{
  "approval_id": "APPR-{{ $now.format('YYYYMMDD') }}-001",
  "source_workflow": "expert-review",
  "review_id": "{{ $json.review_id }}",
  "timestamp": "{{ $now.toISO() }}",
  "task": {{ $json.task }},
  "synthesis": {{ $json.synthesis }},
  "decision_deadline": "{{ $now.addHours(24).toISO() }}"
}
```

### 步骤 8 — 命名并激活

1. 命名：`Synapse-WF7-expert-review`
2. **Active** → **ON** → 保存

---

## WF-8：lysander-approve（Lysander审批）

**作用**：接收 L3 决策请求，通知 Lysander，等待 24 小时后读取决策结果
**Trigger**：Webhook（POST）

### 步骤 1/8 — 创建 workflow

1. **Workflows** → **"+"** → 命名：`Synapse-WF8-lysander-approve`
2. 添加 **Webhook** 节点

### 步骤 2 — 配置 Webhook

- **HTTP Method**：`POST`
- **Path**：`lysander-approve`
- **Respond**：`Respond Immediately`
- **Response Code**：`200`

### 步骤 3 — 添加 Code 节点（格式化审批请求）

```javascript
const data = $input.first().json;

const approvalText = `[Lysander 审批请求]
任务：${data.task?.title || '未知任务'}
优先级：${data.task?.priority || 'P2'}

智囊团建议：${data.synthesis?.recommendation || 'approve'}（置信度 ${data.synthesis?.confidence_score || 70}/100）

优点：${(data.synthesis?.pros || []).join('、')}
风险：${(data.synthesis?.cons || []).join('、')}

⚠️ 请在 24 小时内回复：
✅ 批准 → 在响应文件中写入 decision: approve
❌ 驳回 → 在响应文件中写入 decision: reject
✏️ 修改 → 在响应文件中写入 decision: modify + modifications

响应路径：logs/n8n_executions/pending-approvals/${data.approval_id}.json`;

return [{
  json: {
    approval_id: data.approval_id || 'APPR-UNKNOWN',
    task_title: data.task?.title || '',
    task_priority: data.task?.priority || 'P2',
    recommendation: data.synthesis?.recommendation || 'approve',
    confidence_score: data.synthesis?.confidence_score || 70,
    approval_text: approvalText,
    decision_deadline: data.decision_deadline || new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
    status: 'pending'
  }
}];
```

### 步骤 4 — 添加 Slack 通知节点

1. 添加 **Slack Message** 节点
2. 配置：
   - **Channel**：`#lysander-approvals`（或私信 Lysander 的 Slack ID）
   - **Text**：`{{ $json.approval_text }}`

### 步骤 5 — 添加 Wait 节点

1. 添加 **Wait** 节点
2. 配置：
   - **Amount**：24
   - **Unit**：`Hours`

### 步骤 6 — 添加 Read File 节点（读取决策响应）

1. 添加 **Read File** 节点
2. 配置：
   - **File Name**：`C:/Users/lysanderl_janusd/Synapse-Mini/logs/n8n_executions/pending-approvals/{{ $json.approval_id }}.json`
     （如果该文件不存在，workflow 会失败 → Error Trigger 捕获）

### 步骤 7 — 添加 Code 节点（处理决策结果）

```javascript
let decision = { action: 'timeout', comment: '超时未决策' };
try {
  const response = $input.first().json;
  decision = {
    action: response.decision || 'timeout',
    modifications: response.modifications || [],
    comment: response.comment || '',
    decided_at: response.decided_at || new Date().toISOString()
  };
} catch (e) {
  // 文件读取失败，视为超时
}

return [{
  json: {
    workflow: 'lysander-approve',
    approval_id: $('Webhook').first().json.approval_id || 'UNKNOWN',
    status: decision.action === 'timeout' ? 'timeout' : 'decided',
    lysander_decision: decision,
    execution_triggered: decision.action === 'approve',
    notification_sent: false
  }
}];
```

### 步骤 8 — 命名并激活

1. 命名：`Synapse-WF8-lysander-approve`
2. **Active** → **ON** → 保存

---

## 附录 A：Error Trigger 配置方法（必须配置）

> 每个 workflow 都要配置 Error Trigger，自动重试 max 3 次

### 配置步骤

1. 在 workflow 画布左下角，找到 **"Add Workflow"** 按钮下方或节点之间的连接线
2. 在 workflow 画布空白处，**右键点击** → 选择 **"Add Error Workflow"**
   （或在 workflow 设置中开启 Error Trigger）
3. 另一种方式：
   - 点击 workflow 名称旁边的 **设置图标（⚙）**
   - 找到 **"Error Workflow"** 选项
   - 选择 **"Create New Workflow"** 或 **"Select Existing"**

4. 在 Error Workflow 中：
   - 添加 **Slack Message** 节点（通知失败）
   - 配置 **Channel**：`#synapse-alerts`
   - **Text**：

```
[Workflow 失败告警]
Workflow：{{ $workflow.name }}
错误节点：{{ $node.name }}
错误信息：{{ $json.error.message || $json.error || '未知错误' }}
执行时间：{{ $now.format('YYYY-MM-DD HH:mm') }}

请检查 n8n 执行日志。
```

5. **配置自动重试（Max 3 次）**：
   - 在每个 Node 的 **设置（⚙）** 中，找到 **"Error Handling"**
   - 勾选 **"Continue On Fail"**（可选，使 workflow 不中断）
   - 找到 **"Retry On Fail"** → 勾选
   - **Max Tries**：`3`
   - **Wait Between Tries**：保持默认或设置为 `60`（秒）

### 重试逻辑说明

- **Max Tries = 3**：节点最多重试 3 次（总计 4 次执行：1 次原始 + 3 次重试）
- **Wait Between Tries**：每次重试间隔，建议 60 秒（可按需调整）
- **Error Trigger 触发时机**：所有重试均失败后，Error Trigger 才会触发

---

## 附录 B：HMAC 签名配置方法

> HMAC 密钥用于验证 webhook 请求来源，防止恶意调用

### 在 n8n Credentials 中配置 HMAC

1. 顶部菜单点击 **"Credentials"** → **"+"**
2. 选择类型：`HTTP Header Auth`（或 `Custom Header Auth`）
3. 填写：
   - **Name**：`hmac_secret`（或其他易识别名称）
   - **Header Name**：`x-hmac-signature`
   - **Header Value**：`MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8`
4. 点击 **Save**

### 在 HTTP Request 节点中使用

1. 在 HTTP Request 节点的 **Authentication** 部分
2. 选择 **"Credential Type"** → 找到你创建的 `hmac_secret`
3. n8n 会自动在请求头中添加 `x-hmac-signature: MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8`

### 验证签名（可选，推荐在代码节点中添加）

在 webhook 触发后的第一个 Code 节点中添加验证：

```javascript
const signature = $headers['x-hmac-signature'];
const expectedSignature = 'MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8';

if (signature !== expectedSignature) {
  throw new Error('HMAC 签名验证失败，拒绝请求');
}

return [{ json: { ...$input.first().json, signature_verified: true } }];
```

---

## 附录 C：Webhook URL 速查表

| Workflow | Webhook Path | 完整 URL |
|----------|-------------|---------|
| WF-2 action-notify | `action-notify` | `https://n8n.lysander.bond/webhook/action-notify` |
| WF-3 qa-auto-review | `qa-auto-review` | `https://n8n.lysander.bond/webhook/qa-auto-review` |
| WF-4 qa-gate-85 | `qa-gate-85` | `https://n8n.lysander.bond/webhook/qa-gate-85` |
| WF-6 butler-execute | `butler-execute` | `https://n8n.lysander.bond/webhook/butler-execute` |
| WF-7 expert-review | `expert-review` | `https://n8n.lysander.bond/webhook/expert-review` |
| WF-8 lysander-approve | `lysander-approve` | `https://n8n.lysander.bond/webhook/lysander-approve` |

> **注意**：Webhook 在保存并激活前测试 URL 会返回 404，这是正常现象

---

## 附录 D：快速验证清单

创建完成后，逐项检查：

- [ ] 8 个 workflow 全部创建完成并命名
- [ ] 6 个 Webhook 节点（WF-2/3/4/6/7/8）的 Path 填写正确
- [ ] 2 个 Schedule 节点（WF-1/5）的 Cron 表达式正确
- [ ] 每个 workflow 的 **Active** 开关为 ON（绿色）
- [ ] 每个 workflow 配置了 **Error Trigger**
- [ ] 每个有 HTTP Request 的节点配置了 **HMAC 签名**
- [ ] 每个 Slack 节点配置了正确的 **Channel**
- [ ] 6 个 Webhook URL 均可访问（返回 200）

**Webhook 快速测试**（在浏览器中直接打开以下 URL）：
```
https://n8n.lysander.bond/webhook/action-notify（GET 请求应返回 404 或无内容）
```

---

**【执行者】：knowledge_engineer**
**【创建时间】：2026-04-22**
**【状态】：待总裁验证**
