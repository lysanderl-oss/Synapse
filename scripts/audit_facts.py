#!/usr/bin/env python3
"""audit_facts.py - Detect fact-type number drift across Synapse repos.

Per fact-SSOT meta-rule, key numbers (Agent count, module count, version)
must match across:
- synapse-core/docs/public/synapse-stats.yaml (SSOT)
- lysander-bond pages (network-deployed)
- Synapse-Mini obs/ documents

Reports drift count and specific mismatches.
"""

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# Cross-platform repo paths
HOME = Path.home()
REPOS = {
    'synapse-core': HOME / 'synapse-core',
    'lysander-bond': HOME / 'lysander-bond',
    'Synapse-Mini': HOME / 'Synapse-Mini',
}

# SSOT source
SSOT_PATH = REPOS['synapse-core'] / 'docs' / 'public' / 'synapse-stats.yaml'


def load_ssot():
    if not SSOT_PATH.exists():
        print(f"WARNING: SSOT not found at {SSOT_PATH}", file=sys.stderr)
        return {}
    with open(SSOT_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def scan_repo_for_numbers(repo_path: Path, patterns: dict):
    """Scan repo for hardcoded number+keyword patterns."""
    findings = []
    if not repo_path.is_dir():
        return findings
    skip_dirs = {'.git', 'node_modules', '.cache', 'dist', '__pycache__',
                 '.venv', 'venv', '.next', 'build', '.astro'}
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if not f.endswith(('.md', '.astro', '.yaml', '.yml', '.html', '.json', '.mdx')):
                continue
            fpath = Path(root) / f
            try:
                content = fpath.read_text(encoding='utf-8', errors='replace')
            except Exception:
                continue
            for label, pattern in patterns.items():
                for m in re.finditer(pattern, content):
                    findings.append({
                        'repo': repo_path.name,
                        'file': str(fpath.relative_to(repo_path)),
                        'label': label,
                        'value': m.group(0),
                    })
    return findings


def main():
    ssot = load_ssot()
    expected_agent = ssot.get('agents', {}).get('total_unique', 53)
    expected_modules = ssot.get('modules', {}).get('total', 13)

    patterns = {
        'agent_count': r'\b(\d+)\s*(?:个|位|名|人)?\s*(?:AI\s+)?[Aa]gents?\b',
        'module_count': r'\b(\d+)\s*(?:支|个)?\s*(?:专业|功能)?\s*(?:团队|module)\b',
    }

    drift = []
    for repo_name, repo_path in REPOS.items():
        if not repo_path.is_dir():
            continue
        for finding in scan_repo_for_numbers(repo_path, patterns):
            num_match = re.search(r'\d+', finding['value'])
            if not num_match:
                continue
            num = int(num_match.group(0))
            label = finding['label']
            expected = expected_agent if label == 'agent_count' else expected_modules

            # Filter out common false positives (e.g. "5 minutes", "100 modules"-type misreads)
            if num < 5 or num > 100:
                continue

            if num != expected:
                drift.append({
                    **finding,
                    'expected': expected,
                    'actual': num,
                })

    print(f"=== Fact SSOT Audit ===")
    print(f"SSOT: {SSOT_PATH}")
    print(f"Expected: {expected_agent} agents / {expected_modules} modules")
    print(f"Drift count: {len(drift)}")
    if drift:
        print("\nDetails (first 20):")
        for d in drift[:20]:
            print(f"  [{d['repo']}] {d['file']}: '{d['value']}' "
                  f"(label={d['label']}, expected ~{d['expected']})")
    return 1 if drift else 0


if __name__ == '__main__':
    sys.exit(main())
