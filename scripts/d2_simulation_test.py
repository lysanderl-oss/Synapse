"""
D2 dispatch_rules 模拟匹配（端到端验证脚本，仅模拟不修改 yaml）

用 active_tasks.yaml 中所有 status=approved-pending-dispatch 的 INTEL，
按 active_objectives.yaml 的 dispatch_rules 模拟匹配，输出每条会被怎么处理。

两种匹配模式：
  1. literal: 严格按 rules 字段（task.rice.score），任务无 rice 字段时 score=0
  2. realistic: 从 notes 中正则提取「综合评分 N/20」作为 rice_score

跑法：
  python scripts/d2_simulation_test.py
"""
import yaml
import re
import sys

# Windows utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def extract_embedded_score(task):
    """从 notes 中提取「综合评分 N/20」"""
    notes = task.get('notes', '') or ''
    m = re.search(r'综合评分\s*(\d+)\s*/\s*20', notes)
    return int(m.group(1)) if m else None


def get_rice_score(task, mode='realistic'):
    """根据 mode 返回 rice_score；literal=只看 task.rice.score；realistic=fallback 到 notes 提取"""
    rice = task.get('rice')
    if isinstance(rice, dict) and 'score' in rice:
        return rice['score']
    if mode == 'realistic':
        return extract_embedded_score(task)
    return None  # literal 模式下没有 rice 字段就是 None


def match_rule(task, rule, mode='realistic'):
    """检查 task 是否命中 rule。返回 (matched_bool, reason_str)"""
    cond = rule.get('conditions', {}) or {}

    # default_fallback 总命中
    if cond.get('default_fallback'):
        return True, 'default_fallback'

    # priority 必须一致
    if 'priority' in cond and task.get('priority') != cond['priority']:
        return False, f"priority mismatch ({task.get('priority')} vs {cond['priority']})"

    # rice_score_min / max
    score = get_rice_score(task, mode)
    if 'rice_score_min' in cond:
        if score is None:
            return False, 'rice_score_min set but task has no score'
        if score < cond['rice_score_min']:
            return False, f"score {score} < min {cond['rice_score_min']}"
    if 'rice_score_max' in cond:
        if score is None:
            return False, 'rice_score_max set but task has no score'
        if score > cond['rice_score_max']:
            return False, f"score {score} > max {cond['rice_score_max']}"

    return True, 'all conditions met'


def simulate(mode='realistic'):
    print(f"\n{'='*60}")
    print(f"  Simulation mode: {mode}")
    print(f"{'='*60}")

    # 1. 读规则
    with open('agent-CEO/config/active_objectives.yaml', encoding='utf-8') as f:
        objs = yaml.safe_load(f)

    rules_config = objs.get('dispatch_rules', {}) or {}
    if not rules_config.get('enabled'):
        print("dispatch_rules.enabled = false, 模拟终止")
        return None

    rules = rules_config.get('rules', [])
    safeguards = rules_config.get('safeguards', {}) or {}
    print(f"Loaded {len(rules)} rules, {len(safeguards)} safeguards")

    # 2. 读 pending-dispatch INTEL
    with open('agent-CEO/config/active_tasks.yaml', encoding='utf-8') as f:
        tasks_data = yaml.safe_load(f)
    pending = [t for t in tasks_data.get('tasks', [])
               if t.get('status') == 'approved-pending-dispatch']
    print(f"Pending-dispatch INTEL: {len(pending)}")

    # 3. 模拟匹配
    results = []
    action_counts = {}
    for task in pending:
        matched_rule = None
        for rule in rules:
            ok, _ = match_rule(task, rule, mode)
            if ok:
                matched_rule = rule
                break

        action = matched_rule.get('action') if matched_rule else 'NO_MATCH'
        action_counts[action] = action_counts.get(action, 0) + 1
        score = get_rice_score(task, mode)

        results.append({
            'id': task.get('id'),
            'priority': task.get('priority'),
            'score': score,
            'matched_rule': matched_rule.get('name') if matched_rule else 'NONE',
            'action': action,
        })

    # 4. safeguards
    max_dispatch = safeguards.get('max_auto_dispatch_per_session', 3)
    max_upgrade = safeguards.get('max_auto_upgrade_per_session', 10)
    triggered = []
    if action_counts.get('dispatch_immediately', 0) > max_dispatch:
        triggered.append(
            f"dispatch_immediately {action_counts['dispatch_immediately']} > {max_dispatch}")
    if action_counts.get('upgrade_to_req', 0) > max_upgrade:
        triggered.append(
            f"upgrade_to_req {action_counts['upgrade_to_req']} > {max_upgrade}")

    # 5. 输出
    print("\n--- 匹配明细 ---")
    for r in results:
        print(f"  {r['id']} (P={r['priority']}, score={r['score']}) "
              f"-> {r['matched_rule']} -> {r['action']}")

    print("\n--- Action 分布 ---")
    for action, count in sorted(action_counts.items()):
        print(f"  {action}: {count}")

    print("\n--- Safeguards ---")
    if triggered:
        for t in triggered:
            print(f"  TRIGGERED: {t}")
    else:
        print("  none triggered")

    no_match = action_counts.get('NO_MATCH', 0)
    print(f"\n--- NO_MATCH: {no_match} ---")

    return {
        'mode': mode,
        'results': results,
        'action_counts': action_counts,
        'safeguards_triggered': triggered,
        'no_match': no_match,
    }


if __name__ == '__main__':
    literal = simulate('literal')
    realistic = simulate('realistic')
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    print(f"literal mode action_counts: {literal['action_counts']}")
    print(f"realistic mode action_counts: {realistic['action_counts']}")
