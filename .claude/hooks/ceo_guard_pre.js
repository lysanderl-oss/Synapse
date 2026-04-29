#!/usr/bin/env node
/**
 * CEO Guard Pre-Tool Hook — Synapse v3.0
 * Blocks Lysander CEO from directly using execution tools in the main session.
 * Sub-agents (CLAUDE_SUBAGENT=true) are always exempt.
 * Automation window (Dubai 22:00–08:00, UTC+4) is always exempt.
 *
 * Mode: BLOCKING (ceo_guard_override: false by default)
 * Audit log: audit/ceo_guard.jsonl (JSONL format, one event per line)
 */

const fs = require('fs');
const path = require('path');

// Path-agnostic: works regardless of where Claude Code opens the workspace
const ROOT = path.resolve(__dirname, '..', '..');
const AUDIT_LOG = path.join(ROOT, 'audit', 'ceo_guard.jsonl');
const SETTINGS_PATH = path.join(ROOT, '.claude', 'settings.json');

// Ensure audit directory exists
const auditDir = path.dirname(AUDIT_LOG);
if (!fs.existsSync(auditDir)) {
  fs.mkdirSync(auditDir, { recursive: true });
}

function logEvent(event) {
  const line = JSON.stringify({ ...event, timestamp: new Date().toISOString() });
  fs.appendFileSync(AUDIT_LOG, line + '\n', 'utf8');
}

function loadSettings() {
  try {
    return JSON.parse(fs.readFileSync(SETTINGS_PATH, 'utf8'));
  } catch {
    return { ceo_guard_override: false };
  }
}

// Read hook input from stdin
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const hookData = input.trim() ? JSON.parse(input) : {};
    const args = process.argv.slice(2);
    const isSessionStart = args.includes('--session-start');

    // Sub-agents are ALWAYS exempt from CEO Guard
    if (process.env.CLAUDE_SUBAGENT === 'true') {
      logEvent({ type: 'pre_tool', action: 'allowed', reason: 'sub_agent_exempt', tool: hookData.tool_name || 'unknown' });
      process.exit(0);
    }

    // Automation window: Dubai 22:00–08:00 (UTC+4). All scheduled tasks are confined to this window.
    const dubaiHour = (new Date().getUTCHours() + 4) % 24;
    if (dubaiHour >= 22 || dubaiHour < 8) {
      logEvent({ type: 'pre_tool', action: 'allowed', reason: 'automation_window_22_08_Dubai', tool: hookData.tool_name || 'unknown' });
      process.exit(0);
    }

    if (isSessionStart) {
      logEvent({ type: 'session_start', action: 'logged', identity: 'Lysander_CEO' });
      process.exit(0);
    }

    const toolName = hookData.tool_name || '';
    const blockedTools = ['Edit', 'Write', 'Bash', 'WebSearch', 'WebFetch', 'MultiEdit'];
    const isBlocked = blockedTools.some(t => toolName === t || toolName.startsWith(t));

    if (!isBlocked) {
      process.exit(0);
    }

    const settings = loadSettings();
    const override = settings.ceo_guard_override === true;

    if (override) {
      logEvent({ type: 'pre_tool', action: 'allowed_override', tool: toolName, warning: 'CEO_GUARD_OVERRIDE_ACTIVE' });
      process.stderr.write(`[CEO Guard] ⚠️  OVERRIDE ACTIVE — ${toolName} allowed. This will be audited.\n`);
      process.exit(0);
    }

    // BLOCKING MODE
    logEvent({ type: 'pre_tool', action: 'blocked', tool: toolName, reason: 'ceo_guard_blocking_mode' });

    const blockResponse = {
      decision: 'block',
      reason: `[CEO Guard] Lysander CEO cannot directly use ${toolName}. ` +
               `Use /dispatch to delegate this task to the appropriate team member. ` +
               `This enforces the CEO执行禁区 constraint from the Harness Configuration.`
    };

    process.stdout.write(JSON.stringify(blockResponse));
    process.exit(0);

  } catch (err) {
    // Fail-open on hook error to avoid blocking normal operation
    logEvent({ type: 'pre_tool', action: 'error', error: err.message });
    process.exit(0);
  }
});
