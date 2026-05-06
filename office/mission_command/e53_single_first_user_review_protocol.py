
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_DIR = BRIDGE_ROOT / 'products/governed_agent_action_proof_packet'


def build_single_first_user_review_protocol() -> dict[str, Any]:
    return {
        'protocol_id': 'e53_single_controlled_first_user_review_protocol',
        'status': 'future_only_blocked_without_owner_approval',
        'reviewer_persona_categories': ['AI agent builder', 'MCP power user', 'AI ops lead', 'governance-minded developer'],
        'review_goal': 'assess clarity, credibility, proof gaps, and language risk of the owner-review proof packet',
        'review_material_package': ['README.md', 'proof_packet.json', 'executive_brief.md', 'technical_proof.md', 'limitations_and_no_overclaim.md', 'first_user_review_packet.md'],
        'review_questions': ['What is clear?', 'What feels overstated?', 'What proof gap blocks trust?', 'Would this help you reason about governed agent actions?', 'What local demo would you want next?'],
        'acceptable_feedback_types': ['clarity_feedback', 'credibility_feedback', 'proof_gap_feedback', 'language_risk_feedback', 'technical_interest_signal', 'not_customer_validation', 'not_paid_signal'],
        'prohibited_claims': ['customer validation', 'no paid signal claim', 'real MCP transport remains unclaimed', 'production readiness', 'enterprise compliance readiness', 'expert feedback claim'],
        'stop_conditions': ['owner approval missing', 'request to identify a real reviewer', 'request to collect contact info', 'request to send or publish', 'unsupported claim appears'],
        'owner_approval_required': True,
        'evidence_capture_requirements': ['review must be logged only after owner approval', 'feedback must be categorized without overclaim', 'CIEU/KG/CZL closure required after any future review'],
        'no_go_boundaries': {'no_send': True, 'no_publication': True, 'no_real_reviewer_identity': True, 'no_contact_info_collection': True},
        'after_review_classification_rules': ['feedback is not customer validation', 'feedback is not paid signal', 'technical interest is not demand claim'],
        'contains_real_contacts': False,
        'sent': False,
        'no_external_action': True,
    }


def render_protocol_md(protocol: dict[str, Any]) -> str:
    lines = ['# E53 Single Controlled First-User Review Protocol', '', f"Status: `{protocol['status']}`", '', '## Reviewer Persona Categories']
    lines += [f"- {x}" for x in protocol['reviewer_persona_categories']]
    lines += ['', '## Review Questions'] + [f"- {x}" for x in protocol['review_questions']]
    lines += ['', '## Stop Conditions'] + [f"- {x}" for x in protocol['stop_conditions']]
    lines += ['', 'This protocol contains no real names, emails, social profiles, outreach targets, sent message, external publication, or actual review execution.', '']
    return '\n'.join(lines)


def write_single_first_user_review_protocol(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    protocol = build_single_first_user_review_protocol()
    product = root / 'products/governed_agent_action_proof_packet'
    product.mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    product.joinpath('e53_single_first_user_review_protocol.json').write_text(json.dumps(protocol, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    product.joinpath('e53_single_first_user_review_protocol.md').write_text(render_protocol_md(protocol), encoding='utf-8')
    result = {'artifact_id': 'e53_single_first_user_review_protocol_result', 'protocol_path': 'products/governed_agent_action_proof_packet/e53_single_first_user_review_protocol.md', 'status': protocol['status'], 'contains_real_contacts': False, 'sent': False, 'owner_approval_required': True, 'no_external_action': True}
    (root / 'operations/external_validation/e53_single_first_user_review_protocol_result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e53_single_first_user_review_protocol.md').write_text(render_protocol_md(protocol), encoding='utf-8')
    return result


if __name__ == '__main__':
    print(json.dumps(build_single_first_user_review_protocol(), indent=2, ensure_ascii=False))
