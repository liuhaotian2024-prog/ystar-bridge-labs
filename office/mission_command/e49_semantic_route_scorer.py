from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e49_minimal_mcp_client_path_maturity import inspect_minimal_mcp_client_path
from .e49_semantic_object_model import build_semantic_route_decision

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))

ROUTE_IDS = [
    'governed_agent_action_proof_packet', 'gov_mcp_ystar_local_proof', 'paid_setup_implementation_service', 'claude_desktop_mcpb_packaging', 'ystar_claude_code_plugin_marketplace', 'ai_agent_bug_bounty_service', 'workflow_resale_n8n_czl', 'enterprise_compliance_pilot', 'k9audit_causal_audit_proof', 'bridge_labs_agent_company_case_study', 'consulting_advisory_proof_packet', 'developer_led_proof_bundle'
]


def _num(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _route_base() -> dict[str, dict[str, Any]]:
    return {
        'governed_agent_action_proof_packet': {'buyer': 'AI engineer / agent team', 'value_object': 'Governed Agent Action Proof Packet', 'route_kind': 'service_wedge_anchored_by_proof_artifact', 'proof_readiness': .78, 'asset_support': .82, 'paid_signal_time': .58, 'execution_blocker_severity': .42, 'overclaim_risk': .20, 'owner_burden': .24, 'revenue_potential': .62, 'learning_value': .88, 'm_triangle_alignment': .92, 'blocker_class': 'major_manageable'},
        'gov_mcp_ystar_local_proof': {'buyer': 'local MCP user', 'value_object': 'local proof substrate', 'route_kind': 'technical_substrate', 'proof_readiness': .70, 'asset_support': .78, 'paid_signal_time': .25, 'execution_blocker_severity': .64, 'overclaim_risk': .10, 'owner_burden': .18, 'revenue_potential': .30, 'learning_value': .82, 'm_triangle_alignment': .82, 'blocker_class': 'major_manageable'},
        'paid_setup_implementation_service': {'buyer': 'AI ops team', 'value_object': 'paid setup / implementation service', 'route_kind': 'service_offer', 'proof_readiness': .52, 'asset_support': .66, 'paid_signal_time': .72, 'execution_blocker_severity': .48, 'overclaim_risk': .34, 'owner_burden': .50, 'revenue_potential': .72, 'learning_value': .78, 'm_triangle_alignment': .84, 'blocker_class': 'major_manageable'},
        'claude_desktop_mcpb_packaging': {'buyer': 'Claude Desktop / MCP power user', 'value_object': 'MCPB/plugin package', 'route_kind': 'packaged_install', 'proof_readiness': .43, 'asset_support': .60, 'paid_signal_time': .46, 'execution_blocker_severity': .55, 'overclaim_risk': .30, 'owner_burden': .44, 'revenue_potential': .70, 'learning_value': .72, 'm_triangle_alignment': .78, 'blocker_class': 'major_manageable'},
        'ystar_claude_code_plugin_marketplace': {'buyer': 'Claude Code user', 'value_object': 'plugin marketplace listing', 'route_kind': 'marketplace', 'proof_readiness': .28, 'asset_support': .55, 'paid_signal_time': .48, 'execution_blocker_severity': .70, 'overclaim_risk': .62, 'owner_burden': .72, 'revenue_potential': .76, 'learning_value': .58, 'm_triangle_alignment': .70, 'blocker_class': 'fatal_external_publish_dependency'},
        'ai_agent_bug_bounty_service': {'buyer': 'AI tooling teams', 'value_object': 'agent bug bounty/risk service', 'route_kind': 'service_concept', 'proof_readiness': .32, 'asset_support': .50, 'paid_signal_time': .54, 'execution_blocker_severity': .62, 'overclaim_risk': .52, 'owner_burden': .64, 'revenue_potential': .74, 'learning_value': .70, 'm_triangle_alignment': .72, 'blocker_class': 'needs_market_validation'},
        'workflow_resale_n8n_czl': {'buyer': 'SMB ops buyer', 'value_object': 'workflow resale with CZL', 'route_kind': 'workflow_offer', 'proof_readiness': .26, 'asset_support': .44, 'paid_signal_time': .52, 'execution_blocker_severity': .66, 'overclaim_risk': .46, 'owner_burden': .60, 'revenue_potential': .66, 'learning_value': .54, 'm_triangle_alignment': .60, 'blocker_class': 'weak_current_proof'},
        'enterprise_compliance_pilot': {'buyer': 'enterprise AI governance buyer', 'value_object': 'compliance pilot', 'route_kind': 'enterprise_pilot', 'proof_readiness': .34, 'asset_support': .58, 'paid_signal_time': .30, 'execution_blocker_severity': .78, 'overclaim_risk': .76, 'owner_burden': .82, 'revenue_potential': .86, 'learning_value': .72, 'm_triangle_alignment': .80, 'blocker_class': 'fatal_overclaim_risk_now'},
        'k9audit_causal_audit_proof': {'buyer': 'agent platform builder', 'value_object': 'causal audit proof', 'route_kind': 'audit_addon', 'proof_readiness': .38, 'asset_support': .56, 'paid_signal_time': .42, 'execution_blocker_severity': .58, 'overclaim_risk': .36, 'owner_burden': .50, 'revenue_potential': .62, 'learning_value': .68, 'm_triangle_alignment': .76, 'blocker_class': 'integration_not_active'},
        'bridge_labs_agent_company_case_study': {'buyer': 'agent-company builder', 'value_object': 'case study / runtime proof', 'route_kind': 'case_study', 'proof_readiness': .68, 'asset_support': .80, 'paid_signal_time': .38, 'execution_blocker_severity': .50, 'overclaim_risk': .44, 'owner_burden': .48, 'revenue_potential': .52, 'learning_value': .82, 'm_triangle_alignment': .84, 'blocker_class': 'publish_approval_required'},
        'consulting_advisory_proof_packet': {'buyer': 'founder / AI ops lead', 'value_object': 'advisory proof packet', 'route_kind': 'consulting_offer', 'proof_readiness': .54, 'asset_support': .68, 'paid_signal_time': .64, 'execution_blocker_severity': .46, 'overclaim_risk': .44, 'owner_burden': .54, 'revenue_potential': .68, 'learning_value': .70, 'm_triangle_alignment': .78, 'blocker_class': 'offer_language_needed'},
        'developer_led_proof_bundle': {'buyer': 'developer-led growth audience', 'value_object': 'developer-led proof bundle', 'route_kind': 'developer_package', 'proof_readiness': .50, 'asset_support': .62, 'paid_signal_time': .50, 'execution_blocker_severity': .52, 'overclaim_risk': .32, 'owner_burden': .42, 'revenue_potential': .62, 'learning_value': .74, 'm_triangle_alignment': .78, 'blocker_class': 'packaging_needed'},
    }


def _score(row: dict[str, Any]) -> float:
    positive = (
        row['semantic_goal_fit'] * .14 + row['buyer_pain_clarity'] * .10 + row['current_asset_support'] * .12 + row['proof_readiness'] * .13 + row['time_to_first_user'] * .08 + row['time_to_paid_signal'] * .08 + row['revenue_potential'] * .10 + row['learning_value'] * .10 + row['m_triangle_alignment'] * .15
    )
    penalty = row['execution_blocker_severity'] * .14 + row['evidence_burden'] * .08 + row['overclaim_risk'] * .12 + row['owner_burden'] * .06 + row['implementation_complexity'] * .07
    return round(_num(positive - penalty + .18), 4)


def score_semantic_routes(*, packaging_readiness_override: bool = False) -> dict[str, Any]:
    maturity = inspect_minimal_mcp_client_path()
    rows = []
    for route_id, base in _route_base().items():
        row = {
            'route_id': route_id,
            'buyer': base['buyer'],
            'value_object': base['value_object'],
            'route_kind': base['route_kind'],
            'semantic_goal_fit': .92 if route_id in {'governed_agent_action_proof_packet', 'paid_setup_implementation_service'} else .72,
            'buyer_pain_clarity': .86 if route_id in {'governed_agent_action_proof_packet', 'paid_setup_implementation_service', 'consulting_advisory_proof_packet'} else .62,
            'current_asset_support': base['asset_support'],
            'proof_readiness': base['proof_readiness'],
            'execution_blocker_severity': base['execution_blocker_severity'],
            'time_to_first_user': .85 if route_id in {'governed_agent_action_proof_packet', 'paid_setup_implementation_service', 'gov_mcp_ystar_local_proof'} else .48,
            'time_to_paid_signal': base['paid_signal_time'],
            'evidence_burden': .38 if route_id == 'governed_agent_action_proof_packet' else (.55 if route_id in {'paid_setup_implementation_service', 'consulting_advisory_proof_packet'} else .72),
            'overclaim_risk': base['overclaim_risk'],
            'owner_burden': base['owner_burden'],
            'implementation_complexity': base['execution_blocker_severity'],
            'revenue_potential': base['revenue_potential'],
            'learning_value': base['learning_value'],
            'M_triangle_alignment': base['m_triangle_alignment'],
            'm_triangle_alignment': base['m_triangle_alignment'],
            'blocker_class': base['blocker_class'],
            'unresolved_fatal_blocker': base['blocker_class'].startswith('fatal'),
        }
        if route_id == 'claude_desktop_mcpb_packaging' and packaging_readiness_override:
            row['proof_readiness'] = .84
            row['current_asset_support'] = .88
            row['execution_blocker_severity'] = .20
            row['time_to_first_user'] = .90
            row['blocker_class'] = 'packaging_ready'
            row['unresolved_fatal_blocker'] = False
        if route_id == 'governed_agent_action_proof_packet' and maturity['classification'].startswith('blocked_missing'):
            row['execution_blocker_severity'] = max(row['execution_blocker_severity'], .42)
            row['blocker_class'] = 'major_manageable_missing_mcp_client_path'
        row['semantic_score'] = _score(row)
        if row['unresolved_fatal_blocker']:
            row['recommended_action'] = 'parked'
        elif route_id == 'governed_agent_action_proof_packet':
            row['recommended_action'] = 'harden_first'
        elif route_id == 'claude_desktop_mcpb_packaging' and packaging_readiness_override:
            row['recommended_action'] = 'package_first'
        elif route_id in {'paid_setup_implementation_service', 'consulting_advisory_proof_packet', 'developer_led_proof_bundle'}:
            row['recommended_action'] = 'package_after_client_proof'
        else:
            row['recommended_action'] = 'parked'
        rows.append(row)
    eligible = [row for row in rows if not row['unresolved_fatal_blocker']]
    selected = sorted(eligible, key=lambda item: (-item['semantic_score'], item['execution_blocker_severity'], item['owner_burden']))[0]
    why_not = []
    for row in sorted(rows, key=lambda item: item['route_id']):
        if row['route_id'] == selected['route_id']:
            continue
        why_not.append({'route_id': row['route_id'], 'reason': 'fatal blocker' if row['unresolved_fatal_blocker'] else ('lower semantic score or higher burden/blocker severity'), 'score_delta': round(selected['semantic_score'] - row['semantic_score'], 4)})
    next_milestone = 'E50_build_minimal_gov_mcp_local_test_client' if selected['route_id'] == 'governed_agent_action_proof_packet' or maturity['classification'].startswith('blocked') else 'E50_owner_approved_single_external_user_attempt'
    decision = build_semantic_route_decision('e49_money_route_decision', selected_route=selected['route_id'], rejected_routes=[item for item in why_not if item['reason'] == 'fatal blocker'], parked_routes=[item for item in why_not if item['reason'] != 'fatal blocker'], evidence_burden=selected['evidence_burden'], execution_burden=selected['execution_blocker_severity'], owner_burden=selected['owner_burden'], next_milestone=next_milestone, stop_conditions=['missing MCP client path persists', 'route would require external action before approval', 'overclaim language appears'], evidence_semantics=['e48_allow_deny_kernel_proof', 'e38_e39_public_evidence_context'], blocker_semantics=[selected['blocker_class'], maturity['classification']])
    return {'artifact_id': 'e49_semantic_route_score_matrix', 'routes': sorted(rows, key=lambda item: item['route_id']), 'selected_route': selected, 'why_not_other_routes': why_not, 'semantic_route_decision': decision, 'mcp_client_path_maturity': maturity, 'packaging_readiness_override': packaging_readiness_override, 'no_external_action': True}
