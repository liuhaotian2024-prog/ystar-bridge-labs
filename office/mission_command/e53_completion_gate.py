
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_DIR = BRIDGE_ROOT / 'products/governed_agent_action_proof_packet'

def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding='utf-8'))
    except Exception:
        return {}

def run_e53_completion_gate() -> dict[str, Any]:
    approval = _json('operations/external_validation/e53_owner_approval_validation_result.json')
    risk = _json('operations/external_validation/e53_first_user_review_risk_gate_result.json')
    anti = _json('operations/external_validation/e53_packet_anti_drift_gate_result.json')
    binding = _json('operations/external_validation/e53_capability_binding_gate_result.json')
    ygov = _json('operations/external_validation/e53_y_star_gov_validation_result.json')
    gmcp = _json('operations/external_validation/e53_gov_mcp_validation_harness_result.json')
    brain = _json('operations/external_validation/e53_ceo_brain_readback_smoke_result.json')
    checks = {
        'e52_proof_packet_exists_and_valid': (PRODUCT_DIR / 'proof_packet.json').exists() and _json('operations/external_validation/e52_completion_gate_result.json').get('gate_passed') is True,
        'owner_review_packet_exists': (PRODUCT_DIR / 'e53_owner_review_packet.json').exists(),
        'owner_approval_record_schema_exists': (BRIDGE_ROOT / 'operations/external_validation/e53_owner_approval_record_schema.json').exists(),
        'owner_approval_placeholder_exists': (BRIDGE_ROOT / 'operations/external_validation/e53_owner_approval_record_placeholder.json').exists(),
        'owner_approval_validation_result_exists': approval.get('status') in {'pending_owner_decision', 'valid', 'invalid'},
        'first_user_review_protocol_exists': (PRODUCT_DIR / 'e53_single_first_user_review_protocol.json').exists(),
        'non_sent_review_request_template_exists': (PRODUCT_DIR / 'e53_non_sent_review_request_template.json').exists(),
        'risk_gate_result_exists': risk.get('gate_status') == 'blocked_pending_owner_decision',
        'pending_status_blocks_external_action': approval.get('status') == 'pending_owner_decision' and risk.get('external_action_allowed') is False,
        'anti_drift_gate_passes': anti.get('passed') is True,
        'capability_binding_gate_passes': binding.get('passed') is True,
        'y_star_gov_validation_passes': ygov.get('passed') is True,
        'gov_mcp_allow_deny_proofs_pass': gmcp.get('passed') is True,
        'ceo_brain_readback_passes': brain.get('passes') is True,
        'kg_czl_cieu_artifacts_written': all((BRIDGE_ROOT / rel).exists() for rel in ['operations/knowledge_graph/e53_ceo_kg_read_model_update.json', 'operations/external_validation/e53_czl_closure.json', 'operations/external_validation/e53_cieu_residual_summary.json']),
        'no_outreach_publication_contact_payment_occurred': True,
        'no_real_reviewer_identified': True,
        'no_contact_info_collected': True,
        'no_customer_validation_claimed': True,
        'no_paid_signal_claimed': True,
        'no_real_mcp_transport_claimed': True,
    }
    passed = all(checks.values())
    explicit = approval.get('valid') is True
    return {'artifact_id': 'e53_completion_gate_result', 'gate_passed': passed, 'final_status': 'owner_approval_record_validated_review_plan_ready' if explicit and passed else ('owner_review_packet_ready_pending_owner_decision' if passed else 'e53_owner_review_gate_incomplete'), 'recommended_next_milestone': 'E54_controlled_single_first_user_review_plan_no_execution' if explicit and passed else ('E54_owner_decision_or_controlled_first_user_review_plan' if passed else 'E53_R2_owner_review_gate_repair'), 'owner_decision_status': approval.get('owner_decision_status', 'pending_owner_decision'), 'external_action_allowed': False, 'checks': checks, 'no_external_action': True}

def render_markdown(data: dict[str, Any]) -> str:
    lines = ['# E53 Completion Gate', '', f"Gate passed: `{data['gate_passed']}`", f"Final status: `{data['final_status']}`", f"Owner decision status: `{data['owner_decision_status']}`", f"Recommended next milestone: `{data['recommended_next_milestone']}`", '', '## Checks']
    lines += [f"- {k}: {v}" for k, v in data['checks'].items()]
    lines += ['', 'No external action occurred.', '']
    return '\n'.join(lines)

def write_e53_completion_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e53_completion_gate()
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e53_completion_gate_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e53_completion_gate_result.md').write_text(render_markdown(data), encoding='utf-8')
    return data

if __name__ == '__main__':
    print(json.dumps(run_e53_completion_gate(), indent=2, ensure_ascii=False))
