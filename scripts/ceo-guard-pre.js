#!/usr/bin/env node
// CEO Guard - PreToolUse Hook v2.1
// 确认型门禁：要求 Lysander 在调用 Bash/Edit/Write 前输出标准化确认文本
// 从 stdin 读取 hook input JSON
//
// v2.1 变更（2026-04-23）：Worker Agent 豁免
// ────────────────────────────────────────────────────
// 依据：CLAUDE.md 2026-04-23 "Worker Agent 豁免"条款。
// 通过 Agent 工具派生的子 Agent 不是 Lysander，不受 CEO Guard 约束。
//
// 识别方法（按优先级，命中任一即判定为 Worker Agent）：
//   1) hook input JSON 的 transcript_path 含 "subagents/"（Claude Code 结构特征）
//   2) hook input JSON 直接含 agent_id / subagent_type / parent_session_id
//   3) 环境变量 CLAUDE_CODE_IS_SUBAGENT / CLAUDE_AGENT_ID / CLAUDE_AGENT_TYPE
//      （若未来 Claude Code 添加这些 env；名称为 best-effort，以实际为准）
//
// Worker Agent 行为：
//   - 仍然写入审计日志（保留追溯能力）
//   - 不注入确认型门禁文本（消除"【派单确认】"噪声）
//   - 返回空 additionalContext（静默放行）

const fs = require('fs');
const path = require('path');

const PROJECT_DIR = path.resolve(__dirname, '..');
const LOG_DIR = path.join(PROJECT_DIR, 'logs');
const LOG_FILE = path.join(LOG_DIR, 'ceo-guard-audit.log');
const VIOLATION_FILE = path.join(LOG_DIR, 'ceo-guard-violation-count.tmp');
// 一次性调试转储：第一次命中时写入 hook input 原始 JSON，便于确认字段名
const DEBUG_DUMP_FILE = path.join(LOG_DIR, 'ceo-guard-hook-input-sample.json');

// 确保日志目录存在
try { fs.mkdirSync(LOG_DIR, { recursive: true }); } catch(e) {}

// 读取当前违规计数（同一会话内跨 hook 调用累积）
function getViolationCount(sessionId) {
  try {
    const data = JSON.parse(fs.readFileSync(VIOLATION_FILE, 'utf8'));
    return (data[sessionId] || 0);
  } catch(e) {
    return 0;
  }
}

// 增加并保存违规计数
function incrementViolationCount(sessionId) {
  let counts = {};
  try {
    counts = JSON.parse(fs.readFileSync(VIOLATION_FILE, 'utf8'));
  } catch(e) {}
  counts[sessionId] = (counts[sessionId] || 0) + 1;
  try {
    fs.writeFileSync(VIOLATION_FILE, JSON.stringify(counts));
  } catch(e) {}
}

// 工具名称是否属于执行类（主对话禁止 Lysander 直接调用）
function isForbiddenTool(toolName) {
  return ['Bash', 'Edit', 'Write', 'WebSearch', 'WebFetch'].includes(toolName);
}

// 判定是否为 Worker Agent（子 Agent）调用
// 命中任一条件即视为 Worker Agent
function detectWorkerAgent(hookInput) {
  // 条件 1：transcript_path 含 subagents 目录（Claude Code 目录结构）
  const transcriptPath = (hookInput && hookInput.transcript_path) || '';
  if (typeof transcriptPath === 'string' && /[\\/]subagents[\\/]/.test(transcriptPath)) {
    return { isWorker: true, reason: 'transcript_path-in-subagents' };
  }

  // 条件 2：hook input 直接含 subagent 标识字段（若 Claude Code 未来添加）
  if (hookInput) {
    if (hookInput.agent_id || hookInput.subagent_type || hookInput.parent_session_id || hookInput.is_subagent) {
      return { isWorker: true, reason: 'hook-field-agent-marker' };
    }
  }

  // 条件 3：环境变量（best-effort，具体名称未经官方文档确认）
  if (process.env.CLAUDE_CODE_IS_SUBAGENT || process.env.CLAUDE_AGENT_ID || process.env.CLAUDE_AGENT_TYPE) {
    return { isWorker: true, reason: 'env-subagent-marker' };
  }

  return { isWorker: false, reason: 'no-marker' };
}

// 生成确认型门禁文本
function buildConfirmGateContext(toolName, sessionId, violationCount) {
  const toolLabel = {
    Bash: 'Bash（Shell 命令执行）',
    Edit: 'Edit（文件修改）',
    Write: 'Write（文件写入）',
    WebSearch: 'WebSearch（网络搜索）',
    WebFetch: 'WebFetch（网页抓取）',
  }[toolName] || toolName;

  let gateText = `
[CEO-GUARD v2.1 确认型门禁]
━━━━━━━━━━━━━━━━━━━━━━━━━━
你正在调用 ${toolLabel}，这是 CEO 执行禁区工具。

根据 CLAUDE.md 执行链规定，Lysander 主对话调用此类工具前必须：
  ① 已输出团队派单表（含执行者/交付物）
  ② 在继续执行前输出以下确认文本

━━━━━━━━━━━━━━━━━━━━━━━━━━
【派单确认】
已派单给 [执行者名称]，执行者标注：[XXX 执行]
[A] 确认（已输出派单表，继续执行）
[B] 取消（当前工具调用不应由 Lysander 主对话执行）
━━━━━━━━━━━━━━━━━━━━━━━━━━
`;

  if (violationCount >= 3) {
    gateText += `
⚠️ 警告：你已在同一会话中连续 ${violationCount} 次调用执行工具而未输出有效派单确认。
请立即停止违规模式，上报执行链断裂情况。`;
  } else if (violationCount >= 1) {
    gateText += `
⚠️ 注意：你已连续 ${violationCount} 次调用，请确认已输出派单表。
连续违规将触发强制阻断警告。`;
  }

  return gateText;
}

// 从 stdin 读取输入
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  let toolName = 'unknown';
  let sessionId = 'unknown';
  let summary = '';
  let hookInput = null;

  try {
    hookInput = JSON.parse(input);
    toolName = hookInput.tool_name || 'unknown';
    sessionId = hookInput.session_id || 'unknown';

    if (toolName === 'Bash') {
      summary = (hookInput.tool_input?.command || '').substring(0, 200);
    } else if (toolName === 'Edit') {
      summary = 'Edit: ' + (hookInput.tool_input?.file_path || 'unknown');
    } else if (toolName === 'Write') {
      summary = 'Write: ' + (hookInput.tool_input?.file_path || 'unknown');
    } else {
      summary = toolName;
    }
  } catch(e) {
    summary = 'parse-error';
  }

  // 一次性调试转储：如样本文件不存在，写入当前 hook input，便于查看 Claude Code 实际传递字段
  try {
    if (!fs.existsSync(DEBUG_DUMP_FILE) && input) {
      fs.writeFileSync(DEBUG_DUMP_FILE, input);
    }
  } catch(e) {}

  // 识别 Worker Agent
  const detection = detectWorkerAgent(hookInput);

  // 写入审计日志（无论主对话还是 Worker Agent 都记录，保留追溯能力）
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const actorTag = detection.isWorker ? `WORKER(${detection.reason})` : 'MAIN';
  const logLine = `[${timestamp}] PRE session=${sessionId} actor=${actorTag} tool=${toolName} summary="${summary}"\n`;
  try { fs.appendFileSync(LOG_FILE, logLine); } catch(e) {}

  // 构建 additionalContext
  let additionalContext = '';

  if (detection.isWorker) {
    // Worker Agent 豁免：不注入任何门禁文本，静默放行
    // （审计日志仍已写入，保留追溯能力）
    additionalContext = '';
  } else if (isForbiddenTool(toolName)) {
    // Lysander 主对话调用执行禁区工具：确认型门禁
    const violationCount = getViolationCount(sessionId);
    additionalContext = buildConfirmGateContext(toolName, sessionId, violationCount);
    incrementViolationCount(sessionId);
  } else {
    // 主对话调用白名单工具：轻量提示
    additionalContext = '[CEO-GUARD] 白名单工具调用，无额外限制。';
  }

  // 输出 hook response
  const response = {
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      additionalContext: additionalContext
    }
  };

  process.stdout.write(JSON.stringify(response));
});
