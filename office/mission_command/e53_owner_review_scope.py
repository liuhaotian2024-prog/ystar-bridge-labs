
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))

DECISION_OPTIONS = [
    'approve_prepare_single_controlled_first_user_review',
    'request_packet_revision',
    'require_real_mcp_transport_first',
    'require_more_local_demo_evidence',
    'reject_external_review_for_now',
]

FORBIDDEN_APPROVAL_SCOPE = [
    'outreach', 'publication', 'customer validation claim', 'paid signal claim',
    'production readiness claim', 'real MCP transport claim', 'naming a specific real reviewer', 'sending a message',
]


def build_owner_review_scope() -> dict[str, Any]:
    return {
        'artifact_id': 'e53_owner_review_scope',
        'packet_id': 'governed_agent_action_proof_packet_e52',
        'owner_review_focus': [
            'whether the E52 proof packet is clear enough',
            'whether limitations are honest enough',
            'whether no-overclaim boundaries are strong enough',
            'whether first-user-review category is appropriate',
            'whether a future single controlled first-user review should be prepared',
            'whether real MCP transport must be closed before external review',
            'whether proof language must be revised before any external review',
        ],
        'decision_options': DECISION_OPTIONS,
        'recommended_owner_decision': 'approve_prepare_single_controlled_first_user_review',
        'recommendation_scope': 'prepare plan and non-sent materials only',
        'not_approval_for': FORBIDDEN_APPROVAL_SCOPE,
        'owner_decision_status': 'pending_owner_decision',
        'external_action_allowed': False,
        'no_external_action': True,
    }


def render_scope_markdown(data: dict[str, Any]) -> str:
    lines = ['# E53 Owner Review Scope', '', f"Owner decision status: `{data['owner_decision_status']}`", '', '## Review Focus']
    lines += [f"- {item}" for item in data['owner_review_focus']]
    lines += ['', '## Decision Model']
    lines += [f"- {item}" for item in data['decision_options']]
    lines += ['', f"Recommendation: `{data['recommended_owner_decision']}` but only for `{data['recommendation_scope']}`.", '', 'This is not approval for outreach, publication, naming a real reviewer, customer validation claims, paid signal claims, or real MCP transport claims.', '']
    return '\n'.join(lines)


def write_owner_review_scope(output_root: Path | None = None) -> dict[str, Any]:
    data = build_owner_review_scope()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e53_owner_review_scope.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e53_owner_review_scope.md').write_text(render_scope_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_owner_review_scope(), indent=2, ensure_ascii=False))
