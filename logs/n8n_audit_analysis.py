"""
n8n Workflow Full Audit Analysis Script (READ-ONLY)
Phase 1 of OBJ-N8N-WORKFLOW-AUDIT
"""
import os, json, sys, io
from pathlib import Path
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests

# Read API key
key = open('/tmp/n8n_key.txt').read().strip()
print(f"KEY_LEN={len(key)}", file=sys.stderr)

REPO = Path('C:/Users/lysanderl_janusd/Synapse-Mini')
SNAP = REPO / 'harness' / 'n8n-snapshots'
OUT  = REPO / 'logs' / 'n8n_audit_data.json'

# Step 1: Load all snapshots
all_wfs = []
for f in sorted(SNAP.glob('*.json')):
    try:
        wf = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        print(f"BAD JSON: {f}: {e}", file=sys.stderr)
        continue
    all_wfs.append({
        'id': wf.get('id'),
        'name': wf.get('name'),
        'active': wf.get('active'),
        'updatedAt': wf.get('updatedAt'),
        'createdAt': wf.get('createdAt'),
        'nodes_count': len(wf.get('nodes', [])),
        '_full': wf,
    })

print(f"Loaded snapshots: {len(all_wfs)}", file=sys.stderr)

# Step 2: Pull executions per workflow
now = datetime.now(timezone.utc)
session = requests.Session()
session.headers.update({'X-N8N-API-KEY': key, 'Accept': 'application/json'})

for i, wf in enumerate(all_wfs, 1):
    try:
        r = session.get(
            'https://n8n.lysander.bond/api/v1/executions',
            params={'workflowId': wf['id'], 'limit': 5},
            timeout=20,
        )
        if r.status_code != 200:
            wf['exec_error'] = f'HTTP {r.status_code}'
            print(f"  [{i}] {wf['id']} HTTP {r.status_code}", file=sys.stderr)
            continue
        execs = r.json().get('data', [])
        wf['exec_count_recent'] = len(execs)
        if execs:
            last = execs[0]
            started = last.get('startedAt') or last.get('stoppedAt') or ''
            wf['last_exec'] = started
            wf['last_exec_status'] = ('success' if last.get('finished') and not last.get('stoppedAt', '').endswith('error')
                                       else last.get('status') or
                                       ('success' if last.get('finished') else 'failed'))
            try:
                t = datetime.fromisoformat(started.replace('Z', '+00:00'))
                wf['last_exec_age_days'] = round((now - t).total_seconds() / 86400, 2)
            except Exception:
                wf['last_exec_age_days'] = None
        else:
            wf['last_exec'] = None
            wf['last_exec_age_days'] = None
            wf['last_exec_status'] = 'no_runs'
    except Exception as e:
        wf['exec_error'] = str(e)
        print(f"  [{i}] {wf['id']} EXCEPT {e}", file=sys.stderr)

print(f"Executions fetched.", file=sys.stderr)

# Step 3: Slack pattern detection
def slack_call_pattern(wf_full):
    pat = {
        'has_slack_node': False,
        'has_http_to_slack': False,
        'calls_wf09': False,
        'http_request_count': 0,
        'http_targets': [],
    }
    for n in wf_full.get('nodes', []):
        ntype = n.get('type', '')
        params = n.get('parameters', {}) or {}
        if ntype == 'n8n-nodes-base.slack':
            pat['has_slack_node'] = True
        if ntype == 'n8n-nodes-base.httpRequest':
            pat['http_request_count'] += 1
            url = params.get('url', '') or ''
            if isinstance(url, dict):
                url = url.get('value', '') or ''
            url_s = str(url)
            pat['http_targets'].append(url_s[:120])
            if 'hooks.slack.com' in url_s or 'slack.com' in url_s:
                pat['has_http_to_slack'] = True
            if '/webhook/notify' in url_s or 'atit1zW3VYUL54CJ' in url_s or 'webhook/synapse-notify' in url_s:
                pat['calls_wf09'] = True
    return pat

for wf in all_wfs:
    wf['slack_pattern'] = slack_call_pattern(wf['_full'])

# Step 4: Categorize health
def health_bucket(wf):
    if not wf.get('active'):
        return 'INACTIVE'
    age = wf.get('last_exec_age_days')
    if age is None:
        return 'NEVER_RUN'
    if age <= 7:
        return 'ACTIVE_7D'
    if age <= 30:
        return 'LOW_FREQ_7_30D'
    return 'STALE_OVER_30D'

for wf in all_wfs:
    wf['health_bucket'] = health_bucket(wf)

# Step 5: Slack category
def slack_bucket(wf):
    p = wf['slack_pattern']
    if p['calls_wf09']:
        return 'C_USES_WF09'
    if p['has_slack_node']:
        return 'A_DIRECT_SLACK_NODE'
    if p['has_http_to_slack']:
        return 'B_HTTP_TO_SLACK'
    return 'D_NO_SLACK'

for wf in all_wfs:
    wf['slack_bucket'] = slack_bucket(wf)

# Step 6: Naming detection
import re
def naming_issues(name):
    issues = []
    if not name:
        return ['EMPTY_NAME']
    if re.search(r'[一-鿿]', name) and re.search(r'[A-Za-z]', name):
        issues.append('MIXED_LANG')
    if re.match(r'^My workflow', name):
        issues.append('DEFAULT_NAME')
    if 'WF-' not in name and 'Synapse-' not in name and 'Harness' not in name:
        # candidate non-numbered
        pass
    return issues

for wf in all_wfs:
    wf['naming_issues'] = naming_issues(wf['name'])

# Step 7: Same prefix collision
from collections import Counter, defaultdict
prefix_buckets = defaultdict(list)
for wf in all_wfs:
    name = wf['name'] or ''
    m = re.match(r'^(WF-\d+|Synapse-WF\d+|Harness[\w\s]+?)', name)
    if m:
        prefix_buckets[m.group(1).strip()].append(wf['id'])

# Step 8: Summary stats
buckets = Counter(wf['health_bucket'] for wf in all_wfs)
sbuckets = Counter(wf['slack_bucket'] for wf in all_wfs)
active_n = sum(1 for w in all_wfs if w.get('active'))
inactive_n = sum(1 for w in all_wfs if not w.get('active'))

print("\n=== HEALTH BUCKETS ===")
for k, v in buckets.most_common():
    print(f"  {k}: {v}")
print(f"\nActive: {active_n}, Inactive: {inactive_n}, Total: {len(all_wfs)}")

print("\n=== SLACK BUCKETS ===")
for k, v in sbuckets.most_common():
    print(f"  {k}: {v}")

print("\n=== PREFIX COLLISIONS (same prefix > 1) ===")
for k, ids in prefix_buckets.items():
    if len(ids) > 1:
        print(f"  '{k}': {len(ids)} workflows -> {ids}")

# Save data (without _full to keep it small)
slim = []
for wf in all_wfs:
    sl = {k: v for k, v in wf.items() if k != '_full'}
    slim.append(sl)

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(slim, f, ensure_ascii=False, indent=2)

print(f"\nSaved: {OUT}")
print(f"Total entries: {len(slim)}")
