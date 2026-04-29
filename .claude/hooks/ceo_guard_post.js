#!/usr/bin/env node
/**
 * CEO Guard Post-Tool Hook — Synapse v3.0
 * Audits tool usage after execution for compliance reporting.
 * Sub-agents (CLAUDE_SUBAGENT=true) are always exempt.
 *
 * Audit log: audit/ceo_guard.jsonl (JSONL format)
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const AUDIT_LOG = path.join(ROOT, 'audit', 'ceo_guard.jsonl');

const auditDir = path.dirname(AUDIT_LOG);
if (!fs.existsSync(auditDir)) {
  fs.mkdirSync(auditDir, { recursive: true });
}

function logEvent(event) {
  const line = JSON.stringify({ ...event, timestamp: new Date().toISOString() });
  fs.appendFileSync(AUDIT_LOG, line + '\n', 'utf8');
}

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const hookData = input.trim() ? JSON.parse(input) : {};

    // Sub-agents exempt
    if (process.env.CLAUDE_SUBAGENT === 'true') { process.exit(0); }

    const toolName = hookData.tool_name || '';
    const blockedTools = ['Edit', 'Write', 'Bash', 'WebSearch', 'WebFetch', 'MultiEdit'];
    const wasMonitored = blockedTools.some(t => toolName === t || toolName.startsWith(t));

    if (wasMonitored) {
      logEvent({
        type: 'post_tool',
        action: 'audit',
        tool: toolName,
        status: hookData.status || 'unknown',
        note: 'Monitored tool completed — override was active or pre-hook bypass occurred'
      });
    }

    process.exit(0);
  } catch (err) {
    process.exit(0);
  }
});
