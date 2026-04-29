"""P1-A Step 1: Backup all 3 target workflows + inspect Slack nodes."""
import os, sys, json, requests

sys.stdout.reconfigure(encoding='utf-8')

key = open('.tmp/n8n_key.txt').read().strip()
BASE = 'https://n8n.lysander.bond/api/v1'
H = {'X-N8N-API-KEY': key}
BACKUP_DIR = 'harness/n8n-snapshots/_pre-p1a-backup'
os.makedirs(BACKUP_DIR, exist_ok=True)

TARGETS = [
    ('203fXfKkfqD1juuT', 'pre-rename'),     # WF-09 audit (to rename)
    ('knVJ8Uq2D1UZmpxr', 'pre-refactor'),   # WF-06
    ('ZCHNwHozL2Ib0urk', 'pre-refactor'),   # WF-08
]

for wf_id, tag in TARGETS:
    r = requests.get(f'{BASE}/workflows/{wf_id}', headers=H, timeout=15)
    if r.status_code != 200:
        print(f"FAIL {wf_id}: HTTP {r.status_code}: {r.text[:200]}")
        continue
    wf = r.json()
    path = f'{BACKUP_DIR}/{wf_id}_{tag}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
    print(f"\n=== {wf_id} | name='{wf.get('name')}' ===")
    print(f"  backup -> {path}")
    print(f"  nodes ({len(wf.get('nodes', []))}):")
    for n in wf.get('nodes', []):
        ntype = n.get('type', '')
        nname = n.get('name', '')
        marker = ''
        if ntype == 'n8n-nodes-base.slack':
            marker = ' <-- SLACK'
        elif ntype == 'n8n-nodes-base.httpRequest':
            url = n.get('parameters', {}).get('url', '')
            if isinstance(url, dict):
                url = url.get('value', '') or ''
            if 'slack.com' in str(url):
                marker = f' <-- HTTP-SLACK url={url}'
        print(f"    [{ntype}] {nname}{marker}")
