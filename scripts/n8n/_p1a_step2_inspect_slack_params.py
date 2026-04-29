"""Inspect the Slack-calling node parameters in each WF to understand body/text expressions."""
import json

TARGETS = [
    ('203fXfKkfqD1juuT', 'pre-rename', '发送 Slack 告警'),
    ('knVJ8Uq2D1UZmpxr', 'pre-refactor', '发送监控汇总'),
    ('ZCHNwHozL2Ib0urk', 'pre-refactor', '汇总发送监控频道'),
]
# Also need to look at upstream Code nodes that build the payload

for wf_id, tag, slack_node_name in TARGETS:
    path = f'harness/n8n-snapshots/_pre-p1a-backup/{wf_id}_{tag}.json'
    with open(path, 'r', encoding='utf-8') as f:
        wf = json.load(f)
    print(f"\n{'='*70}")
    print(f"WF: {wf_id} ({wf.get('name')})")
    print(f"{'='*70}")
    for n in wf.get('nodes', []):
        if n.get('name') == slack_node_name:
            print(f"\n--- TARGET SLACK NODE: {n.get('name')} ---")
            print(json.dumps(n.get('parameters', {}), ensure_ascii=False, indent=2))
        # Also print upstream code nodes that likely build the payload
        if n.get('type') == 'n8n-nodes-base.code' and ('slack' in n.get('name', '').lower() or '通知' in n.get('name', '') or '汇报' in n.get('name', '') or '告警' in n.get('name', '')):
            print(f"\n--- CODE NODE: {n.get('name')} ---")
            params = n.get('parameters', {})
            code = params.get('jsCode', '') or params.get('functionCode', '')
            # Print full code (we need to see what fields it sets)
            print(code[:3000])
            if len(code) > 3000:
                print(f"... ({len(code)-3000} more chars)")
