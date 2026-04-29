"""P1-A Step 3: Rename 203fXfKkfqD1juuT + refactor httpRequest→Slack nodes in 3 WFs to call WF-09."""
import os, sys, json, requests, copy

sys.stdout.reconfigure(encoding='utf-8')

key = open('.tmp/n8n_key.txt').read().strip()
BASE = 'https://n8n.lysander.bond/api/v1'
H = {'X-N8N-API-KEY': key, 'Content-Type': 'application/json'}
WF09_URL = 'https://n8n.lysander.bond/webhook/notify'


def get_wf(wf_id):
    r = requests.get(f'{BASE}/workflows/{wf_id}', headers=H, timeout=15)
    r.raise_for_status()
    return r.json()


def put_wf(wf_id, wf):
    body = {
        'name': wf['name'],
        'nodes': wf['nodes'],
        'connections': wf['connections'],
        'settings': wf.get('settings', {}),
    }
    r = requests.put(f'{BASE}/workflows/{wf_id}', headers=H, json=body, timeout=20)
    return r


def make_wf09_node(orig_node, source, title_expr, body_expr, priority='info'):
    """Replace an existing httpRequest→slack node in-place (preserving id/position/connections)."""
    new_params = {
        'method': 'POST',
        'url': WF09_URL,
        'sendBody': True,
        'specifyBody': 'keypair',
        'contentType': 'json',
        'bodyParameters': {
            'parameters': [
                {'name': 'recipient', 'value': 'president'},
                {'name': 'title', 'value': title_expr},
                {'name': 'body', 'value': body_expr},
                {'name': 'source', 'value': source},
                {'name': 'priority', 'value': priority},
            ]
        },
        'options': {},
    }
    # Preserve everything else (id, position, typeVersion, credentials cleared)
    new_node = copy.deepcopy(orig_node)
    new_node['parameters'] = new_params
    # Strip Slack credential since WF-09 webhook is unauthenticated
    if 'credentials' in new_node:
        del new_node['credentials']
    new_node['name'] = f"Notify via WF-09 (was {orig_node['name']})"
    return new_node


# === Step 1: Rename 203fXfKkfqD1juuT ===
print("="*70)
print("Step 1: Rename 203fXfKkfqD1juuT")
print("="*70)
wf_audit = get_wf('203fXfKkfqD1juuT')
old_name = wf_audit.get('name')
print(f"Old name: {old_name}")

# Replace its Slack node too while we're at it
for i, n in enumerate(wf_audit['nodes']):
    if n.get('name') == '发送 Slack 告警':
        title_expr = "=Webhook 覆盖告警：发现 {{ $json.unregisteredCount }} 个项目未注册"
        body_expr = (
            "=发现 {{ $json.unregisteredCount }} 个项目未注册 Webhook，PM 将无法收到实时通知。\n\n"
            "未覆盖项目：\n"
            "{{ $json.unregisteredProjects.map(p => '• ' + p.name + ' (https://app.asana.com/0/' + p.gid + '/list)').join('\\n') }}\n\n"
            "请登录 https://pmo-api.lysander.bond/dashboard 查看详情并执行批量注册。\n\n"
            "检测时间：{{ $json.checkedAt.replace('T',' ').slice(0,19) }} UTC | "
            "活跃项目总数：{{ $json.totalActive }} | 已注册：{{ $json.totalRegistered }}"
        )
        wf_audit['nodes'][i] = make_wf09_node(
            n, source='Synapse-Audit-Webhook-Coverage',
            title_expr=title_expr, body_expr=body_expr, priority='warning',
        )
        print(f"  Replaced node: {n['name']} -> {wf_audit['nodes'][i]['name']}")

wf_audit['name'] = 'Synapse-Audit-Webhook-Coverage'
r = put_wf('203fXfKkfqD1juuT', wf_audit)
print(f"PUT status: {r.status_code}")
if r.status_code not in (200, 201):
    print(f"Body: {r.text[:500]}")
    sys.exit(1)

# Verify
v = get_wf('203fXfKkfqD1juuT')
assert v.get('name') == 'Synapse-Audit-Webhook-Coverage', f"Rename verify failed: {v.get('name')}"
print(f"Verified new name: {v.get('name')}")


# === Step 2: WF-06 refactor ===
print()
print("="*70)
print("Step 2: WF-06 (knVJ8Uq2D1UZmpxr) refactor 发送监控汇总")
print("="*70)
wf06 = get_wf('knVJ8Uq2D1UZmpxr')
replaced_06 = 0
for i, n in enumerate(wf06['nodes']):
    if n.get('name') == '发送监控汇总':
        title_expr = "=WF-06 依赖链通知汇总（已发 {{ $json.totalNotified }} 条）"
        body_expr = (
            "=WF-06 任务依赖通知执行结果：\n\n"
            "发出通知：{{ $json.totalNotified }} 条\n"
            "跳过（已通知）：{{ $json.totalSkipped }} 条\n"
            "执行时间：{{ $json.executedAt.replace('T',' ').slice(0,19) }} UTC\n\n"
            "明细：\n"
            "{{ $json.notifications.map(n => (n.type === 'dm' ? '[OK]' : '[WARN]') + ' ' + n.assignee + ' -> ' + n.task + ' [' + n.status + ']').join('\\n') || '无' }}"
        )
        wf06['nodes'][i] = make_wf09_node(
            n, source='WF-06', title_expr=title_expr, body_expr=body_expr, priority='info',
        )
        replaced_06 += 1
        print(f"  Replaced node: {n['name']} -> {wf06['nodes'][i]['name']}")

print(f"Replaced {replaced_06} nodes")
r = put_wf('knVJ8Uq2D1UZmpxr', wf06)
print(f"PUT status: {r.status_code}")
if r.status_code not in (200, 201):
    print(f"Body: {r.text[:500]}")
    sys.exit(1)


# === Step 3: WF-08 refactor ===
print()
print("="*70)
print("Step 3: WF-08 (ZCHNwHozL2Ib0urk) refactor 汇总发送监控频道")
print("="*70)
wf08 = get_wf('ZCHNwHozL2Ib0urk')
replaced_08 = 0
for i, n in enumerate(wf08['nodes']):
    if n.get('name') == '汇总发送监控频道':
        title_expr = "=WF-08 Webhook 依赖通知（{{ $json.notifiedCount }} 条 DM）"
        body_expr = (
            "=WF-08 Webhook 任务完成 → 依赖通知：\n\n"
            "前置任务：{{ $json.taskName }}\n"
            "已发出 DM：{{ $json.notifiedCount }} 条\n"
            "事件：{{ $json.eventKey ? $json.eventKey.slice(0,12) : '-' }}\n"
            "时间：{{ $json.executedAt.replace('T',' ').slice(0,19) }} UTC\n\n"
            "明细：\n"
            "{{ ($json.notifications || []).map(function(n){ return (n.type==='dm' ? '[OK]' : '[WARN]') + ' ' + n.assignee + ' -> ' + n.task + ' [' + n.status + ']'; }).join('\\n') || '无' }}"
        )
        wf08['nodes'][i] = make_wf09_node(
            n, source='WF-08', title_expr=title_expr, body_expr=body_expr, priority='info',
        )
        replaced_08 += 1
        print(f"  Replaced node: {n['name']} -> {wf08['nodes'][i]['name']}")

print(f"Replaced {replaced_08} nodes")
r = put_wf('ZCHNwHozL2Ib0urk', wf08)
print(f"PUT status: {r.status_code}")
if r.status_code not in (200, 201):
    print(f"Body: {r.text[:500]}")
    sys.exit(1)


# === Verify all 3 ===
print()
print("="*70)
print("Verification")
print("="*70)
for wf_id in ('203fXfKkfqD1juuT', 'knVJ8Uq2D1UZmpxr', 'ZCHNwHozL2Ib0urk'):
    wf = get_wf(wf_id)
    print(f"\n{wf_id}: name='{wf.get('name')}'")
    for n in wf.get('nodes', []):
        nname = n.get('name', '')
        ntype = n.get('type', '')
        if 'Notify via WF-09' in nname or 'slack' in nname.lower() or '通知' in nname or '汇总' in nname or '告警' in nname:
            params = n.get('parameters', {})
            url = params.get('url', '')
            print(f"  [{ntype}] {nname} | url={url}")
print("\nDone.")
