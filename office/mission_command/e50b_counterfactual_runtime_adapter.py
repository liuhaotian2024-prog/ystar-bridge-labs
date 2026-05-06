from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))


def _read_text(path: Path, limit: int = 800000) -> str:
    try:
        data = path.read_text(encoding='utf-8', errors='ignore')
        return data[:limit]
    except Exception:
        return ''


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _contains(text: str, needles: list[str]) -> bool:
    low = text.lower()
    return any(needle.lower() in low for needle in needles)

from .e50b_counterfactual_asset_inventory import build_counterfactual_asset_inventory

SOURCE_MINIMUM_HINTS = [
    'governance/WORKING_STYLE.md',
    '.claude/agents/ceo.md',
    'knowledge/ceo/wisdom/meta/autonomous_loop_algorithm.md',
    'knowledge/ceo/wisdom/meta/retrospective_sandbox_workflow.md',
]


def load_counterfactual_assets() -> dict[str, Any]:
    inventory = build_counterfactual_asset_inventory()
    selected = []
    for asset in inventory['assets']:
        if asset['path'] in SOURCE_MINIMUM_HINTS or asset['path'] == 'office/mission_command/counterfactual_router.py':
            selected.append(asset)
    return {
        'asset_count': inventory['asset_count'],
        'source_assets': selected,
        'source_asset_ids': [asset['asset_id'] for asset in selected],
        'minimum_source_paths_consumed': [asset['path'] for asset in selected],
    }


def _route_candidates() -> list[dict[str, Any]]:
    return [
        {'route_id': 'external_commercial_observation_now', 'route_name': 'External commercial observation now, using E50A tool-layer proof as wedge', 'technical_readiness': .70, 'revenue_immediacy': .54, 'evidence_available': .46, 'evidence_needed': .35, 'governance_risk': .18, 'commercial_risk': .30, 'reversibility': .92, 'opportunity_cost': .20},
        {'route_id': 'build_real_mcp_transport_before_market', 'route_name': 'Build real MCP package/client transport before market observation', 'technical_readiness': .42, 'revenue_immediacy': .35, 'evidence_available': .34, 'evidence_needed': .45, 'governance_risk': .10, 'commercial_risk': .24, 'reversibility': .74, 'opportunity_cost': .54},
        {'route_id': 'patch_gov_mcp_testability_surface', 'route_name': 'Patch gov-mcp testability surface before commercial route work', 'technical_readiness': .48, 'revenue_immediacy': .30, 'evidence_available': .32, 'evidence_needed': .50, 'governance_risk': .12, 'commercial_risk': .20, 'reversibility': .78, 'opportunity_cost': .50},
        {'route_id': 'package_governed_agent_action_proof_packet', 'route_name': 'Package Governed Agent Action Proof Packet as first commercial artifact', 'technical_readiness': .78, 'revenue_immediacy': .68, 'evidence_available': .58, 'evidence_needed': .30, 'governance_risk': .16, 'commercial_risk': .22, 'reversibility': .88, 'opportunity_cost': .18},
        {'route_id': 'continue_internal_dogfood_only', 'route_name': 'Continue internal dogfood only', 'technical_readiness': .86, 'revenue_immediacy': .18, 'evidence_available': .40, 'evidence_needed': .55, 'governance_risk': .08, 'commercial_risk': .40, 'reversibility': .92, 'opportunity_cost': .70},
        {'route_id': 'immediate_customer_expert_outreach', 'route_name': 'Immediate customer or expert outreach', 'technical_readiness': .30, 'revenue_immediacy': .70, 'evidence_available': .20, 'evidence_needed': .70, 'governance_risk': .95, 'commercial_risk': .78, 'reversibility': .20, 'opportunity_cost': .45},
        {'route_id': 'k9audit_only_causal_audit_wedge', 'route_name': 'K9Audit-only causal audit wedge', 'technical_readiness': .44, 'revenue_immediacy': .38, 'evidence_available': .36, 'evidence_needed': .56, 'governance_risk': .14, 'commercial_risk': .42, 'reversibility': .72, 'opportunity_cost': .46},
        {'route_id': 'ystar_gov_standalone_kernel_wedge', 'route_name': 'Y-star-gov standalone governance kernel wedge', 'technical_readiness': .62, 'revenue_immediacy': .34, 'evidence_available': .42, 'evidence_needed': .48, 'governance_risk': .12, 'commercial_risk': .38, 'reversibility': .84, 'opportunity_cost': .42},
        {'route_id': 'gov_mcp_integration_service_wedge', 'route_name': 'gov-mcp integration service wedge', 'technical_readiness': .66, 'revenue_immediacy': .64, 'evidence_available': .50, 'evidence_needed': .36, 'governance_risk': .18, 'commercial_risk': .30, 'reversibility': .82, 'opportunity_cost': .26},
        {'route_id': 'full_governed_execution_causal_audit_proof_packet_wedge', 'route_name': 'Full governed execution plus causal audit plus proof packet wedge', 'technical_readiness': .60, 'revenue_immediacy': .66, 'evidence_available': .56, 'evidence_needed': .34, 'governance_risk': .20, 'commercial_risk': .26, 'reversibility': .76, 'opportunity_cost': .30},
    ]


def score_counterfactual_route(route: dict[str, Any]) -> dict[str, Any]:
    if route['route_id'] == 'immediate_customer_expert_outreach':
        decision = 'deny'
    else:
        decision = 'select'
    score = round(
        route['technical_readiness'] * .22
        + route['revenue_immediacy'] * .18
        + route['evidence_available'] * .16
        + route['reversibility'] * .12
        - route['evidence_needed'] * .10
        - route['governance_risk'] * .18
        - route['commercial_risk'] * .12
        - route['opportunity_cost'] * .12
        + .25,
        4,
    )
    if route['route_id'] == 'immediate_customer_expert_outreach':
        score = min(score, .05)
    elif score >= .50:
        decision = 'select'
    elif score >= .36:
        decision = 'defer'
    else:
        decision = 'quarantine'
    if route['route_id'] == 'immediate_customer_expert_outreach':
        decision = 'deny'
    components = {
        'technical_readiness': route['technical_readiness'],
        'revenue_immediacy': route['revenue_immediacy'],
        'evidence_available': route['evidence_available'],
        'evidence_needed': route['evidence_needed'],
        'governance_risk': route['governance_risk'],
        'commercial_risk': route['commercial_risk'],
        'reversibility': route['reversibility'],
        'opportunity_cost': route['opportunity_cost'],
        'counterfactual_score': score,
    }
    return {**route, 'deterministic_score_components': components, 'decision': decision}


def _to_counterfactual_route(route: dict[str, Any], task_text: str, source_ids: list[str]) -> dict[str, Any]:
    scored = score_counterfactual_route(route)
    rid = route['route_id']
    if rid == 'package_governed_agent_action_proof_packet':
        blocker = 'real_mcp_transport_not_closed_but_E50A_tool_layer_allow_deny_closed'
        predicted_y = 'A first-user-reviewable proof packet exists without claiming real transport/customer validation.'
        predicted_r = 'Higher learning/revenue adjacency with reversible owner-approved next step.'
    elif rid == 'full_governed_execution_causal_audit_proof_packet_wedge':
        blocker = 'requires packaging K9/CIEU add-on and clear proof language before use.'
        predicted_y = 'Stronger differentiated wedge but slower to explain and package.'
        predicted_r = 'Potentially higher value, with more integration burden.'
    elif rid == 'immediate_customer_expert_outreach':
        blocker = 'owner_approval_missing_and_no_outreach_allowed'
        predicted_y = 'Boundary violation risk before proof packet is owner-reviewed.'
        predicted_r = 'Invalid route for this milestone.'
    else:
        blocker = 'manageable_or_deferred_blocker'
        predicted_y = 'Could improve readiness but either delays market learning or weakens commercial focus.'
        predicted_r = 'Lower near-term value than selected proof-packet packaging route.'
    return {
        'route_id': rid,
        'route_name': route['route_name'],
        'Xt_current_state': 'E50A closed gov-mcp tool-layer ALLOW/DENY via fake FastMCP harness; real MCP transport remains unclaimed; no customer validation or paid signal exists.',
        'Y_star_target': 'Fastest credible owner-reviewable path to real user/value/revenue learning without overclaiming or external side effects.',
        'U_intervention': route['route_name'],
        'predicted_Yt_plus_1': predicted_y,
        'predicted_Rt_plus_1': predicted_r,
        'evidence_available': route['evidence_available'],
        'evidence_needed': route['evidence_needed'],
        'blocker_state': blocker,
        'governance_risk': route['governance_risk'],
        'commercial_risk': route['commercial_risk'],
        'technical_readiness': route['technical_readiness'],
        'revenue_immediacy': route['revenue_immediacy'],
        'reversibility': route['reversibility'],
        'opportunity_cost': route['opportunity_cost'],
        'nearest_alternative': '',
        'why_better_than_nearest_alternative': '',
        'decision': scored['decision'],
        'source_assets_used': source_ids,
        'deterministic_score_components': scored['deterministic_score_components'],
    }


def build_counterfactual_decision_context(task_text: str, route_candidates: list[dict[str, Any]] | None = None, evidence_atoms: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    assets = load_counterfactual_assets()
    return {
        'task_text': task_text,
        'source_asset_ids': assets['source_asset_ids'],
        'minimum_source_paths_consumed': assets['minimum_source_paths_consumed'],
        'route_candidate_count': len(route_candidates or _route_candidates()),
        'evidence_atom_count': len(evidence_atoms or []),
        'interpretation': 'Apply GOV-005 counterfactual proposal discipline to commercial route choice: compare current state Xt, target Y*, intervention U, predicted outcome Yt+1 and result Rt+1.',
        'no_external_action': True,
    }


def build_counterfactual_route_matrix(task_text: str, route_candidates: list[dict[str, Any]] | None = None, evidence_atoms: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    candidates = route_candidates or _route_candidates()
    assets = load_counterfactual_assets()
    routes = [_to_counterfactual_route(route, task_text, assets['source_asset_ids']) for route in candidates]
    selectable = [route for route in routes if route['decision'] == 'select']
    selected = sorted(selectable, key=lambda row: (-row['deterministic_score_components']['counterfactual_score'], -row['reversibility'], row['governance_risk']))[0]
    alternatives = [route for route in routes if route['route_id'] != selected['route_id'] and route['decision'] in {'select', 'defer'}]
    nearest = sorted(alternatives, key=lambda row: abs(selected['deterministic_score_components']['counterfactual_score'] - row['deterministic_score_components']['counterfactual_score']))[0]
    for route in routes:
        route['nearest_alternative'] = nearest['route_id'] if route['route_id'] == selected['route_id'] else selected['route_id']
        if route['route_id'] == selected['route_id']:
            route['why_better_than_nearest_alternative'] = 'More reversible, owner-reviewable, and commercially legible than the nearest full-stack proof wedge while preserving no-outreach/no-overclaim boundaries.'
        else:
            route['why_better_than_nearest_alternative'] = 'Not selected because it has weaker readiness, higher opportunity cost, higher boundary risk, or slower commercial learning than the proof packet packaging route.'
    matrix = {
        'matrix_id': 'e50b_counterfactual_money_route_matrix',
        'task_text': task_text,
        'source_asset_ids': assets['source_asset_ids'],
        'selected_route': selected['route_id'],
        'nearest_rejected_or_deferred_route': nearest['route_id'],
        'routes': routes,
        'validation': {},
        'no_external_action': True,
    }
    matrix['validation'] = validate_counterfactual_matrix(matrix)
    return matrix


def validate_counterfactual_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    required = ['Xt_current_state', 'Y_star_target', 'U_intervention', 'predicted_Yt_plus_1', 'predicted_Rt_plus_1']
    route_errors = []
    for route in matrix.get('routes', []):
        missing = [field for field in required if not route.get(field)]
        if missing:
            route_errors.append({'route_id': route.get('route_id'), 'missing': missing})
        if route.get('decision') not in {'select', 'defer', 'quarantine', 'deny'}:
            route_errors.append({'route_id': route.get('route_id'), 'invalid_decision': route.get('decision')})
    return {
        'valid': not route_errors and bool(matrix.get('selected_route')) and bool(matrix.get('nearest_rejected_or_deferred_route')),
        'route_errors': route_errors,
        'selected_has_nearest_alternative': bool(matrix.get('nearest_rejected_or_deferred_route')),
        'immediate_outreach_denied': any(route['route_id'] == 'immediate_customer_expert_outreach' and route['decision'] in {'deny', 'quarantine'} for route in matrix.get('routes', [])),
        'no_external_action': matrix.get('no_external_action') is True,
    }


def summarize_counterfactual_connection_status() -> dict[str, Any]:
    assets = load_counterfactual_assets()
    smoke = build_counterfactual_route_matrix('E50B smoke: reconnect counterfactual route selection')
    return {
        'status': 'counterfactual_runtime_reconnected',
        'source_asset_count': len(assets['source_assets']),
        'selected_route': smoke['selected_route'],
        'nearest_alternative': smoke['nearest_rejected_or_deferred_route'],
        'matrix_valid': smoke['validation']['valid'],
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(summarize_counterfactual_connection_status(), indent=2, ensure_ascii=False))
