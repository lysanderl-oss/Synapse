#!/usr/bin/env python3
"""check_claude_md_edit.py — Enforce CLAUDE.md edit checklist (5 dimensions).

Per .claude/harness/claude-md-edit-checklist.md, runs A-E checks.
Exits 1 if any P0 check fails (blocks commit when run as pre-commit hook).

Dimensions:
  A: Numbers vs organization.yaml SSOT (forbidden: 44/46/50 Agent residue)
  B: Path references must exist (agent-butler/* deprecated)
  C: Function/skill references must be implemented
  D: Line budget <= 350
  E: QA threshold = 85/100 (not 3.5)
"""

import os
import re
import sys
import subprocess
from pathlib import Path

# Ensure UTF-8 output even on Windows cp1252 consoles so we can print
# Chinese characters in failure messages without UnicodeEncodeError.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = ROOT / 'CLAUDE.md'
ORG_YAML = ROOT / 'agent-CEO' / 'config' / 'organization.yaml'
LINE_BUDGET = 350

failures = []
warnings = []


def check_a_numbers():
    """A: Numbers must align with organization.yaml SSOT."""
    if not CLAUDE_MD.exists():
        failures.append('A: CLAUDE.md missing')
        return
    text = CLAUDE_MD.read_text(encoding='utf-8', errors='replace')

    # Forbidden old numbers (from 4-27 fact-fix lessons)
    forbidden_phrases = [
        '44人',
        '44 人 Agent',
        '46 人',
        '50 个 Agent',
        '44 人',
    ]
    for phrase in forbidden_phrases:
        if phrase in text:
            failures.append(f'A: forbidden number residue "{phrase}" found')

    # Detect any "X 人/位/个 Agent" outside accepted set
    accepted = {58, 69, 13}
    for m in re.finditer(r'(\d+)\s*(?:人|位|个)\s*Agent', text):
        num = int(m.group(1))
        if num not in accepted:
            failures.append(
                f'A: unusual Agent count {num} in "{m.group(0)}" — '
                f'accepted: {sorted(accepted)} (verify against organization.yaml)'
            )


def check_b_paths():
    """B: All path references must exist; deprecated paths forbidden."""
    if not CLAUDE_MD.exists():
        return
    text = CLAUDE_MD.read_text(encoding='utf-8', errors='replace')

    # Deprecated paths (renamed 4-19: agent-butler -> agent-CEO)
    deprecated = ['agent-butler/', 'agent-butler\\']
    for d in deprecated:
        if d in text:
            failures.append(
                f'B: deprecated path "{d}" found '
                f'(renamed to agent-CEO on 4-19)'
            )

    # Verify .claude/harness/ fragment references exist
    for m in re.finditer(r'`(\.claude/harness/[\w\-]+\.md)`', text):
        rel = m.group(1)
        if not (ROOT / rel).exists():
            failures.append(f'B: missing harness fragment: {rel}')

    # Verify agent-CEO/ file references
    for m in re.finditer(r'`(agent-CEO/[\w/\-\.]+\.(?:py|yaml|yml|md))`', text):
        rel = m.group(1)
        if not (ROOT / rel).exists():
            failures.append(f'B: missing agent-CEO file: {rel}')


def check_c_functions():
    """C: Function and skill references must exist."""
    if not CLAUDE_MD.exists():
        return
    text = CLAUDE_MD.read_text(encoding='utf-8', errors='replace')

    # Forbidden non-existent skill (deprecated 4-27)
    if '/dispatch Skill' in text or '/dispatch skill' in text:
        failures.append('C: "/dispatch Skill" referenced but not implemented')

    # If audit_harness() referenced, must be implemented
    if 'audit_harness()' in text:
        found = False
        for search_dir in [ROOT / 'agent-CEO', ROOT / 'scripts']:
            if not search_dir.exists():
                continue
            for py in search_dir.rglob('*.py'):
                try:
                    body = py.read_text(encoding='utf-8', errors='replace')
                    if 'def audit_harness' in body:
                        found = True
                        break
                except Exception:
                    pass
            if found:
                break
        if not found:
            failures.append(
                'C: audit_harness() referenced but no '
                'implementation found in agent-CEO/ or scripts/'
            )


def check_d_consistency():
    """D: Line budget <= 350."""
    if not CLAUDE_MD.exists():
        return
    content = CLAUDE_MD.read_text(encoding='utf-8', errors='replace')
    # Count lines (newline-terminated + any trailing partial)
    lines = content.count('\n')
    if not content.endswith('\n') and content:
        lines += 1
    if lines > LINE_BUDGET:
        failures.append(f'D: CLAUDE.md {lines} lines > {LINE_BUDGET} budget')
    elif lines > LINE_BUDGET - 10:
        warnings.append(
            f'D: CLAUDE.md {lines} lines (within 10 of {LINE_BUDGET} budget)'
        )


def check_e_qa_threshold():
    """E: QA threshold must be 85/100, not 3.5."""
    if not CLAUDE_MD.exists():
        return
    text = CLAUDE_MD.read_text(encoding='utf-8', errors='replace')

    # Pattern: qa_auto_review ... >=3.5 (with various unicode >= chars)
    if re.search(r'qa_auto_review[^\n]*(?:≥|>=)\s*3\.5', text):
        failures.append(
            'E: qa_auto_review >=3.5 found — should be >=85/100 per hr_base.py'
        )


def main():
    if not CLAUDE_MD.exists():
        print('SKIP: CLAUDE.md not found')
        return 0

    print('=== CLAUDE.md Edit Checklist Enforcement ===')

    check_a_numbers()
    check_b_paths()
    check_c_functions()
    check_d_consistency()
    check_e_qa_threshold()

    print(f'\n-> {len(failures)} P0 failures, {len(warnings)} warnings')

    if warnings:
        print('\nWarnings:')
        for w in warnings:
            print(f'  [WARN] {w}')

    if failures:
        print('\nFailures (BLOCK):')
        for f in failures:
            print(f'  [FAIL] {f}')
        print('\nFix before commit. See .claude/harness/claude-md-edit-checklist.md')
        return 1

    print('\n[OK] CLAUDE.md fact-check passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
