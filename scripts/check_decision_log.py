#!/usr/bin/env python3
"""Block commits that smell like 'decision' but lack D-numbered archive.

Per president decision D-2026-0427-001 (④A): all L3+ decisions must be archived
as D-numbered documents in obs/04-decision-knowledge/decision-log/.

This script is intended to run as either:
  - A pre-commit hook (checking the staged diff + draft commit message)
  - A CI gate (checking the latest commit on a PR branch)

Exit codes:
  0  pass (no decision smell, OR D-reference present, OR decision-log file modified,
          OR commit message contains 'no-decision' opt-out)
  1  block (decision smell detected and no archive evidence)
"""

import os
import re
import subprocess
import sys

DECISION_KEYWORDS = [
    'decision', 'decided', 'approved', 'authorize', 'authorized',
    'L3', 'L4',
    '决策', '裁决', '批准', '授权', 'decision-log', 'D-',
]

# Words that strongly suggest the commit is NOT a decision archival itself
# (e.g., infra commits about the decision-log feature)
NO_DECISION_OPT_OUT = 'no-decision'

D_NUMBER_PATTERN = re.compile(r'D-\d{4}-\d{4}-\d{3}')


def _git(args, default=''):
    """Run a git command and return stdout, or `default` on failure."""
    try:
        out = subprocess.check_output(
            ['git'] + args,
            stderr=subprocess.DEVNULL,
        )
        return out.decode('utf-8', errors='replace').strip()
    except Exception:
        return default


def get_commit_message():
    """Get the message under inspection.

    commit-msg hook mode (preferred): argv[1] = path to COMMIT_EDITMSG (git
        passes this natively when invoking the commit-msg hook). This is the
        ONLY phase where the about-to-commit message is reliably readable.
    Pre-commit hook mode (legacy fallback): read .git/COMMIT_EDITMSG.
        Note: this file may be stale or empty during pre-commit phase.
    CI mode (final fallback): use the latest HEAD commit message.
    """
    # commit-msg hook: argv[1] passed by git
    if len(sys.argv) > 1:
        msg_path = sys.argv[1]
        if os.path.exists(msg_path):
            try:
                with open(msg_path, 'r', encoding='utf-8') as f:
                    msg = f.read().strip()
                    if msg:
                        return msg
            except Exception:
                pass

    # Legacy pre-commit fallback (often stale, but keep for compat)
    git_dir = _git(['rev-parse', '--git-dir'])
    if git_dir:
        candidate = os.path.join(git_dir, 'COMMIT_EDITMSG')
        if os.path.exists(candidate):
            try:
                with open(candidate, 'r', encoding='utf-8') as f:
                    msg = f.read().strip()
                    if msg:
                        return msg
            except Exception:
                pass

    # CI path
    return _git(['log', '-1', '--pretty=%B', 'HEAD'])


def get_changed_files():
    """Get the list of files changed in this commit (or staged)."""
    # Try staged first (pre-commit hook context)
    staged = _git(['diff', '--cached', '--name-only'])
    if staged:
        return staged.split('\n')

    # Fall back to last commit (CI context)
    last = _git(['diff', '--name-only', 'HEAD~1', 'HEAD'])
    if last:
        return last.split('\n')

    return []


def main():
    msg = get_commit_message()
    if not msg:
        # No commit context available, allow
        return 0

    msg_lower = msg.lower()

    # Explicit opt-out
    if NO_DECISION_OPT_OUT in msg_lower:
        return 0

    has_decision_keyword = any(k.lower() in msg_lower for k in DECISION_KEYWORDS)
    if not has_decision_keyword:
        return 0

    # Decision smell detected — verify archive evidence
    has_d_number = bool(D_NUMBER_PATTERN.search(msg))

    changed = get_changed_files()
    has_decision_log_file = any('decision-log/' in f for f in changed)

    if has_d_number or has_decision_log_file:
        return 0

    # Block
    print('=' * 70)
    print('DECISION_LOG_GUARD: blocked commit')
    print('=' * 70)
    print('This commit looks like a decision but lacks both:')
    print('  - A D-YYYY-MMDD-NNN reference in the commit message, AND')
    print('  - A modified file under obs/04-decision-knowledge/decision-log/')
    print('')
    print('Per president decision D-2026-0427-001 (decision (4)A, 2026-04-27):')
    print('  All L3+ decisions must be archived as D-numbered documents in')
    print('  obs/04-decision-knowledge/decision-log/.')
    print('')
    print('How to fix:')
    print('  1. Create or update the D-numbered file under decision-log/, OR')
    print('  2. Reference the existing D-number in your commit message, OR')
    print('  3. If this commit is genuinely not a decision, add the literal')
    print('     token "no-decision" to your commit message.')
    print('')
    print('Detected decision keywords in message:')
    matched = [k for k in DECISION_KEYWORDS if k.lower() in msg_lower]
    for k in matched:
        print(f'  - {k}')
    print('=' * 70)
    return 1


if __name__ == '__main__':
    sys.exit(main())
