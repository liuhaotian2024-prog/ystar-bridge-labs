
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e53_owner_approval_record import validate_owner_approval_record

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding='utf-8'))
    except Exception:
        return {}


def evaluate_first_user_review_risk_gate(approval_record: dict[str, Any] | None = None) -> dict[str, Any]:
    record = approval_record if approval_record is not None else _json('operations/external_validation/e53_owner_approval_record_placeholder.json')
    approval = validate_owner_approval_record(record)
    proof = _json('products/governed_agent_action_proof_packet/proof_packet.json')
    e52_completion = _json('operations/external_validation/e52_completion_gate_result.json')
    e52_anti = _json('operations/external_validation/e52_packet_anti_drift_gate_result.json')
    e52_binding = _json('operations/external_validation/e52_capability_binding_gate_result.json')
    e52_brain = _json('operations/external_validation/e52_ceo_brain_readback_smoke_result.json')
    template = _json('products/governed_agent_action_proof_packet/e53_non_sent_review_request_template.json')
    packet = _json('products/governed_agent_action_proof_packet/e53_owner_review_packet.json')
    checks = {
        'owner_approval_exists': approval.get('valid') is True,
        'packet_no_overclaim_validation_passed': _json('operations/external_validation/e52_no_overclaim_validation_result.json').get('passed') is True,
        'e52_completion_gate_passed': e52_completion.get('gate_passed') is True,
        'e51_anti_drift_gate_passed': e52_anti.get('passed') is True,
        'e51_capability_binding_gate_passed': e52_binding.get('passed') is True,
        'proof_packet_readback_passed': e52_brain.get('passes') is True,
        'no_real_reviewer_identified': packet.get('real_reviewer_identified') is False and template.get('contact_identified') is False,
        'no_contact_info_collected': template.get('contact_info_collected') is False,
        'no_outreach_sent': template.get('sent') is False,
        'no_publication_done': proof.get('publication_status') == 'not_published',
        'no_customer_validation_claimed': proof.get('customer_validation_claimed') is False and packet.get('customer_validation_claimed') is False,
        'no_paid_signal_claimed': proof.get('paid_signal_claimed') is False and packet.get('paid_signal_claimed') is False,
        'real_mcp_transport_not_claimed': proof.get('real_mcp_transport_claimed') is False and packet.get('real_mcp_transport_claimed') is False,
        'owner_approval_required_before_any_external_action': True,
    }
    if approval.get('valid') is True:
        gate_status = 'approved_to_prepare_review_plan_only'
        next_allowed = 'prepare E54 controlled first-user review plan'
    else:
        gate_status = 'blocked_pending_owner_decision'
        next_allowed = 'owner_reviews_packet_and_decides'
    return {
        'artifact_id': 'e53_first_user_review_risk_gate_result',
        'approval_validation': approval,
        'checks': checks,
        'gate_status': gate_status,
        'external_action_allowed': False,
        'next_allowed_action': next_allowed,
        'recommended_next_milestone': 'E54_owner_decision_or_controlled_first_user_review_plan',
        'no_go_boundaries': {'no_outreach': True, 'no_publication': True, 'no_real_reviewer_identity': True, 'no_contact_info_collection': True, 'no_customer_validation_claim': True, 'no_paid_signal_claim': True},
        'no_external_action': True,
    }


def render_risk_gate_markdown(data: dict[str, Any]) -> str:
    lines = ['# E53 First-User Review Risk Gate', '', f"Gate status: `{data['gate_status']}`", f"External action allowed: `{data['external_action_allowed']}`", f"Next allowed action: `{data['next_allowed_action']}`", '', '## Checks']
    lines += [f"- {k}: {v}" for k, v in data['checks'].items()]
    lines += ['', 'No external action occurred.', '']
    return '\n'.join(lines)


def write_first_user_review_risk_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = evaluate_first_user_review_risk_gate()
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e53_first_user_review_risk_gate_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e53_first_user_review_risk_gate_result.md').write_text(render_risk_gate_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(evaluate_first_user_review_risk_gate(), indent=2, ensure_ascii=False))
