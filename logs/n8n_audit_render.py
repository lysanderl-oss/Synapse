"""Render the n8n audit data into report tables (Markdown)."""
import json, sys, io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = Path('C:/Users/lysanderl_janusd/Synapse-Mini')
DATA = REPO / 'logs' / 'n8n_audit_data.json'

wfs = json.load(open(DATA, encoding='utf-8'))

def fmt_age(d):
    if d is None: return 'N/A'
    if d < 1: return f'{d*24:.1f}h'
    return f'{d:.1f}d'

# Group by health bucket
groups = defaultdict(list)
for w in wfs:
    groups[w['health_bucket']].append(w)

print("=" * 80)
print("HEALTH BUCKETS DETAIL")
print("=" * 80)
for bucket in ['ACTIVE_7D', 'LOW_FREQ_7_30D', 'STALE_OVER_30D', 'NEVER_RUN', 'INACTIVE']:
    items = groups.get(bucket, [])
    print(f"\n--- {bucket} ({len(items)}) ---")
    for w in sorted(items, key=lambda x: x.get('last_exec_age_days') or 999):
        age = fmt_age(w.get('last_exec_age_days'))
        st = w.get('last_exec_status', 'n/a')
        active = '✅' if w.get('active') else '❌'
        print(f"  {active} {w['id']:22s} | {(w['name'] or '')[:50]:50s} | last={age:8s} status={st}")

# Slack bucket detail
print("\n" + "=" * 80)
print("SLACK BUCKETS DETAIL")
print("=" * 80)
sgroups = defaultdict(list)
for w in wfs:
    sgroups[w['slack_bucket']].append(w)

for bucket in ['A_DIRECT_SLACK_NODE', 'B_HTTP_TO_SLACK', 'C_USES_WF09', 'D_NO_SLACK']:
    items = sgroups.get(bucket, [])
    print(f"\n--- {bucket} ({len(items)}) ---")
    for w in items:
        active = '✅' if w.get('active') else '❌'
        print(f"  {active} {w['id']:22s} | {(w['name'] or '')[:50]:50s}")
        for t in w['slack_pattern']['http_targets'][:3]:
            print(f"      http -> {t}")

# Naming issues
print("\n" + "=" * 80)
print("NAMING ISSUES")
print("=" * 80)
for w in wfs:
    if w['naming_issues']:
        print(f"  {w['id']}: '{w['name']}' -> {w['naming_issues']}")

# Default-named (My workflow / Test)
print("\n--- Suspicious default/test names ---")
for w in wfs:
    n = w['name'] or ''
    if 'My workflow' in n or n.endswith(' Test') or 'test' in n.lower() and 'Harness' in n:
        active = '✅' if w.get('active') else '❌'
        print(f"  {active} {w['id']}: '{n}'")
