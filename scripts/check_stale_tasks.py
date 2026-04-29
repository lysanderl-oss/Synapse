#!/usr/bin/env python3
"""check_stale_tasks.py - Detect inbox-status tasks older than 14 days.

Scans agent-CEO/config/active_tasks.yaml for tasks that have been sitting
in inbox/pending/queued state for over STALE_DAYS days.

Exit code:
  0 = no stale tasks
  1 = stale tasks found
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# Resolve relative to script location to allow running from anywhere
ROOT = Path(__file__).resolve().parent.parent
ACTIVE_TASKS = ROOT / 'agent-CEO' / 'config' / 'active_tasks.yaml'
STALE_DAYS = 14


def normalize_tasks(data):
    """Adapt to actual schema (might be list, dict, or nested)."""
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    # Try common keys
    for key in ('tasks', 'active_tasks', 'items'):
        if key in data and isinstance(data[key], (list, dict)):
            inner = data[key]
            if isinstance(inner, dict):
                return [{**v, 'id': k} for k, v in inner.items() if isinstance(v, dict)]
            return inner
    # Fall back: treat all dict values that look like tasks as tasks
    candidate_tasks = []
    for k, v in data.items():
        if isinstance(v, dict) and ('status' in v or 'title' in v):
            candidate_tasks.append({**v, 'id': v.get('id', k)})
        elif isinstance(v, list):
            for t in v:
                if isinstance(t, dict):
                    candidate_tasks.append(t)
    return candidate_tasks


def main():
    if not ACTIVE_TASKS.exists():
        print(f"WARNING: active_tasks.yaml not found at {ACTIVE_TASKS}", file=sys.stderr)
        return 0

    with open(ACTIVE_TASKS, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    cutoff = datetime.now(timezone.utc) - timedelta(days=STALE_DAYS)
    stale = []

    tasks = normalize_tasks(data)

    for t in tasks:
        if not isinstance(t, dict):
            continue
        status = str(t.get('status', '')).lower()
        if status not in {'inbox', 'pending', 'queued', 'todo', 'new'}:
            continue
        created = (t.get('created_at') or t.get('approved_at')
                   or t.get('reported_at') or t.get('created'))
        if not created:
            continue
        try:
            ts = datetime.fromisoformat(str(created).replace('Z', '+00:00'))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts < cutoff:
                stale.append({
                    'id': t.get('id', '?'),
                    'title': t.get('title', t.get('name', '?')),
                    'status': status,
                    'created': str(created),
                    'age_days': (datetime.now(timezone.utc) - ts).days,
                })
        except Exception:
            pass

    print(f"=== Stale Tasks Audit ===")
    print(f"Source: {ACTIVE_TASKS}")
    print(f"Cutoff: {STALE_DAYS} days ago ({cutoff.date()})")
    print(f"Tasks scanned: {len(tasks)}")
    print(f"Stale count: {len(stale)}")
    if stale:
        print("\nDetails:")
        for s in stale:
            print(f"  [{s['id']}] {s['title']} | {s['status']} | "
                  f"{s['age_days']} days old (created {s['created']})")
    return 1 if stale else 0


if __name__ == '__main__':
    sys.exit(main())
