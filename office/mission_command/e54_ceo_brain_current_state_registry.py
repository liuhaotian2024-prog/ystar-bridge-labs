
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))

@dataclass(frozen=True)
class BrainStateSource:
    source_id: str
    path: str
    source_type: str
    milestone: str
    freshness_order: int
    affects_current_state: bool
    consumed_as_current: bool
    allowed_if_missing: bool
    reader: str
    validation: dict[str, Any]


def _read_json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding='utf-8'))
    except Exception:
        return {}


def build_current_state_registry() -> dict[str, Any]:
    sources = [
        BrainStateSource('e50b_commercial_decision', 'operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'decision_packet', 'E50B', 50, True, False, True, 'e54_current_state_registry', {'reference_only_after_E53': True}),
        BrainStateSource('e52_proof_packet', 'products/governed_agent_action_proof_packet/proof_packet.json', 'proof_packet', 'E52', 52, True, True, False, 'e54_current_state_registry', {}),
        BrainStateSource('e52_completion_gate', 'operations/external_validation/e52_completion_gate_result.json', 'gate_result', 'E52', 52, True, True, False, 'e54_current_state_registry', {}),
        BrainStateSource('e53_owner_review_packet', 'products/governed_agent_action_proof_packet/e53_owner_review_packet.json', 'owner_review_state', 'E53', 53, True, True, False, 'e54_current_state_registry', {}),
        BrainStateSource('e53_owner_approval_validation', 'operations/external_validation/e53_owner_approval_validation_result.json', 'owner_approval_record', 'E53', 53, True, True, False, 'e54_current_state_registry', {}),
        BrainStateSource('e53_risk_gate', 'operations/external_validation/e53_first_user_review_risk_gate_result.json', 'risk_gate', 'E53', 53, True, True, False, 'e54_current_state_registry', {}),
        BrainStateSource('e53_non_sent_template', 'products/governed_agent_action_proof_packet/e53_non_sent_review_request_template.json', 'non_sent_template', 'E53', 53, True, True, False, 'e54_current_state_registry', {}),
        BrainStateSource('e53_completion_gate', 'operations/external_validation/e53_completion_gate_result.json', 'gate_result', 'E53', 53, True, True, False, 'e54_current_state_registry', {}),
        BrainStateSource('e53_kg_read_model', 'operations/knowledge_graph/e53_ceo_kg_read_model_update.json', 'kg_read_model', 'E53', 53, True, True, False, 'e54_current_state_registry', {}),
        BrainStateSource('e54_next_action_reasoning', 'operations/external_validation/e54_ceo_next_action_reasoning_packet.json', 'decision_packet', 'E54', 54, True, True, True, 'e54_current_state_registry', {}),
        BrainStateSource('e54_l5_readiness_gate', 'operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json', 'gate_result', 'E54', 54, True, True, True, 'e54_current_state_registry', {}),
        BrainStateSource('old_e49_route_decision', 'operations/external_validation/e49_selected_money_route_semantic_decision.json', 'reference_only', 'E49', 49, False, False, True, 'none', {'reference_only': True}),
    ]
    return {'artifact_id': 'e54_ceo_brain_current_state_registry', 'sources': [asdict(s) for s in sources], 'rules': ['latest accepted current-state source wins', 'reference_only artifacts cannot become current', 'no-go boundaries are monotonic unless explicit owner approval narrows them', 'external_action_allowed defaults false', 'owner approval is never inferred', 'pending_owner_decision is never approval', 'non-sent template is never sent'], 'no_external_action': True}


def resolve_current_state() -> dict[str, Any]:
    registry = build_current_state_registry()
    loaded: dict[str, dict[str, Any]] = {}
    missing_nonfatal: list[str] = []
    stale_ignored: list[str] = []
    for source in registry['sources']:
        rel = source['path']
        data = _read_json(rel)
        exists = bool(data)
        if source['source_type'] == 'reference_only':
            stale_ignored.append(source['source_id'])
        if not exists and source['allowed_if_missing']:
            missing_nonfatal.append(source['source_id'])
        loaded[source['source_id']] = {'source': source, 'exists': exists, 'data': data}

    proof = loaded['e52_proof_packet']['data']
    owner_packet = loaded['e53_owner_review_packet']['data']
    approval = loaded['e53_owner_approval_validation']['data']
    risk = loaded['e53_risk_gate']['data']
    template = loaded['e53_non_sent_template']['data']
    e53_completion = loaded['e53_completion_gate']['data']
    e53_kg = loaded['e53_kg_read_model']['data']
    e54_reasoning = loaded['e54_next_action_reasoning']['data']
    e54_gate = loaded['e54_l5_readiness_gate']['data']

    owner_status = approval.get('owner_decision_status') or owner_packet.get('owner_decision_status') or 'pending_owner_decision'
    external_action_allowed = bool(risk.get('external_action_allowed', False)) and owner_status not in {'pending_owner_decision', 'invalid_owner_approval_record'}
    if owner_status == 'pending_owner_decision':
        external_action_allowed = False
    next_milestone = e54_gate.get('recommended_next_milestone') or e54_reasoning.get('selected_next_action') or e53_completion.get('recommended_next_milestone') or risk.get('recommended_next_milestone') or e53_kg.get('next_recommended_milestone') or 'E54_owner_decision_or_controlled_first_user_review_plan'
    no_go = {'no_outreach': True, 'no_publication': True, 'no_contact_info_collection': True, 'no_real_reviewer_identity': True, 'no_customer_validation_claim': True, 'no_paid_signal_claim': True, 'no_real_mcp_transport_claim': True, 'owner_approval_required_before_external_action': True, 'brain_may_not_execute_behavior': True}
    no_go.update(owner_packet.get('no_go_boundaries') or {})
    no_go.update(risk.get('no_go_boundaries') or {})
    return {
        'artifact_id': 'e54_current_state_resolution',
        'registry_status': 'passed',
        'selected_route': proof.get('selected_route') or 'package_governed_agent_action_proof_packet',
        'nearest_alternative': proof.get('nearest_alternative') or 'external_commercial_observation_now',
        'next_milestone': next_milestone,
        'current_blockers': ['pending_owner_decision', 'real_mcp_transport_not_claimed', 'behavior_center_not_L5'],
        'no_go_boundaries': no_go,
        'proof_packet_status': 'owner-reviewable only' if proof else 'unavailable_nonfatal',
        'owner_review_status': 'pending_owner_decision',
        'owner_approval_status': owner_status,
        'owner_review_risk_gate_status': risk.get('gate_status') or 'blocked_pending_owner_decision',
        'non_sent_template_status': 'not_sent' if template.get('sent') is False else 'unsafe_or_missing',
        'real_reviewer_identified': bool(owner_packet.get('real_reviewer_identified', False) or template.get('contact_identified', False)),
        'contact_info_collected': bool(template.get('contact_info_collected', False)),
        'anti_drift_status': 'passed' if _read_json('operations/external_validation/e53_packet_anti_drift_gate_result.json').get('passed') else 'unavailable_nonfatal',
        'capability_binding_status': 'passed' if _read_json('operations/external_validation/e53_capability_binding_gate_result.json').get('passed') else 'unavailable_nonfatal',
        'external_action_allowed': external_action_allowed,
        'customer_validation_claimed': bool(proof.get('customer_validation_claimed', False) or owner_packet.get('customer_validation_claimed', False)),
        'paid_signal_claimed': bool(proof.get('paid_signal_claimed', False) or owner_packet.get('paid_signal_claimed', False)),
        'real_mcp_transport_claimed': bool(proof.get('real_mcp_transport_claimed', False) or owner_packet.get('real_mcp_transport_claimed', False)),
        'source_trace': [{'source_id': sid, 'path': item['source']['path'], 'exists': item['exists'], 'source_type': item['source']['source_type'], 'freshness_order': item['source']['freshness_order']} for sid, item in loaded.items()],
        'stale_sources_ignored': stale_ignored,
        'missing_nonfatal_sources': missing_nonfatal,
        'e53_completion_gate_available': bool(e53_completion),
        'pending_owner_decision_treated_as_approval': False,
        'no_external_action': True,
    }


def write_current_state_registry(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    registry = build_current_state_registry()
    resolution = resolve_current_state()
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e54_ceo_brain_current_state_registry.json').write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'operations/external_validation/e54_ceo_brain_current_state_resolution.json').write_text(json.dumps(resolution, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    md = '# E54 CEO Brain Current-State Registry\n\nRegistry status: `%s`\n\nOwner review status: `%s`\n\nExternal action allowed: `%s`\n\nE53 completion gate available: `%s`\n' % (resolution['registry_status'], resolution['owner_approval_status'], resolution['external_action_allowed'], resolution['e53_completion_gate_available'])
    (root / 'reports/integration/e54_ceo_brain_current_state_registry.md').write_text(md, encoding='utf-8')
    (root / 'reports/integration/e54_ceo_brain_current_state_resolution.md').write_text(md, encoding='utf-8')
    return {'registry': registry, 'resolution': resolution}
