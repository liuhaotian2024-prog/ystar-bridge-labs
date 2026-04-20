#!/usr/bin/env python3
"""
Audience: Board (executes from shell). CEO authors; Board invokes because governance/ write is secretary-scope.
Research basis: 2026-04-19 evening incident — 9h+ session + 4 concurrent long sub-agents → 4-of-4 stream-idle-timeout. Consultant: parent context accumulation is root cause, concurrency × duration ≈ failure probability. Board directive: codify age-aware concurrency cap as ForgetGuard rule, CEO self-observed, Samantha-monitored.
Synthesis: add `session_age_concurrency_cap` rule to governance/forget_guard_rules.yaml. Detector fires on Agent tool spawn when cap is exceeded; action=warn (non-blocking but visible) with escalate action when violation recurs.
Purpose: prevent future repetition of today's 4-of-4 failure class by hard-observing session-age-based concurrency caps.

Board Authorization: 2026-04-19 evening explicit message "把'session超过6小时后降低并发'变成治理规则".
"""

import pathlib
import yaml

yaml_path = pathlib.Path('/Users/haotianliu/.openclaw/workspace/ystar-company/governance/forget_guard_rules.yaml')

with yaml_path.open() as f:
    data = yaml.safe_load(f)

rules = data.get('rules', data)

new_rule = {
    'id': 'session_age_concurrency_cap',
    'enabled': True,
    'description': (
        'Session-age-aware concurrency cap for CEO sub-agent spawns. '
        'Rationale: parent-session context accumulation over long sessions degrades stream I/O scheduling; '
        'concurrent long sub-agents exceed watchdog idle timeout when parent is busy consuming their streams. '
        'Empirical evidence: 2026-04-19 9h+ session, 4 concurrent spawns all hit stream-idle-timeout.'
    ),
    'last_reviewed': '2026-04-19',
    'reviewer': 'Board',
    'trigger': {
        'tool': ['Agent'],
        'logic': 'AND',
        'conditions': [
            {'type': 'active_agent_equals', 'value': 'ceo'},
            {'type': 'session_age_concurrency_exceeded', 'caps': [
                {'session_age_hours_gt': 6, 'max_concurrent': 2},
                {'session_age_hours_gt': 8, 'max_concurrent': 1}
            ]}
        ]
    },
    'action': 'warn',
    'recipe': (
        'Session age exceeds threshold. Current concurrent sub-agents: {current_count}. '
        'Cap at your session_age: {cap}. Either (a) wait for in-flight to complete before spawning, '
        '(b) reduce scope of pending spawn to single-file + ≤8 tool_uses, '
        '(c) use Board-shell ops script path (no sub-agent spawn needed).'
    ),
    'cieu_event': 'SESSION_AGE_CONCURRENCY_CAP_WARN',
    'severity': 'medium',
    'monitored_by': 'secretary',
    'authority': 'Board 2026-04-19 directive via consultant diagnosis'
}

# Check if rule already present (idempotent)
existing_ids = {r.get('id') for r in rules}
if 'session_age_concurrency_cap' in existing_ids:
    print('[SKIP] session_age_concurrency_cap rule already present.')
else:
    rules.append(new_rule)
    data['rules'] = rules if isinstance(data, dict) and 'rules' in data else rules
    yaml_path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True))
    print(f'[ADDED] session_age_concurrency_cap rule. Total rules now: {len(rules)}')

# Verify
with yaml_path.open() as f:
    reloaded = yaml.safe_load(f)
    final_count = len(reloaded.get('rules', reloaded))
    has_rule = any(r.get('id') == 'session_age_concurrency_cap' for r in reloaded.get('rules', reloaded))
    print(f'[VERIFY] Final rule count: {final_count}. Rule present: {has_rule}')
