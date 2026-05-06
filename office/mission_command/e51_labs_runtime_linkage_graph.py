from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))

CURRENT = {
    'selected_route': 'package_governed_agent_action_proof_packet',
    'nearest_alternative': 'external_commercial_observation_now',
    'next_milestone': 'E51_package_governed_agent_action_proof_packet_for_first_user_review',
    'post_e51_next_milestone': 'E52_package_governed_agent_action_proof_packet_for_first_user_review',
    'blocker': 'real_mcp_transport_not_closed_but_E50A_tool_layer_allow_deny_closed',
    'e50a_status': 'tool_layer_allow_deny_closed',
}

NODE_TYPES = [
    'owner_task', 'board_directive', 'semantic_interpreter', 'CEO_brain', 'wisdom_memory', 'working_memory',
    'field_projection', 'capability_router', 'cognition_cascade', 'counterfactual_runtime', 'semantic_route_scorer',
    'commercial_decision_packet', 'selected_route', 'nearest_alternative', 'external_observation', 'evidence_receipt',
    'gov_mcp_boundary', 'Y_star_gov_boundary', 'K9Audit_context', 'execution_or_packaging_path', 'KG_update',
    'CZL_closure', 'CIEU_residual', 'next_milestone_state', 'test_gate', 'future_closure_policy',
]


def _node(node_type: str, **extra: Any) -> dict[str, Any]:
    out = {'node_id': node_type, 'node_type': node_type}
    out.update(extra)
    return out


def _edge(src: str, dst: str, edge_type: str, **extra: Any) -> dict[str, Any]:
    out = {'from': src, 'to': dst, 'edge_type': edge_type}
    out.update(extra)
    return out


def build_labs_runtime_linkage_graph() -> dict[str, Any]:
    nodes = [_node(kind) for kind in NODE_TYPES]
    for node in nodes:
        if node['node_id'] == 'selected_route':
            node['value'] = CURRENT['selected_route']
            node['written_at'] = 'operations/external_validation/e50b_ceo_commercial_decision_packet.json'
            node['read_by_next'] = 'office/mission_command/e46b_ceo_brain_adapter.py'
        if node['node_id'] == 'nearest_alternative':
            node['value'] = CURRENT['nearest_alternative']
        if node['node_id'] == 'next_milestone_state':
            node['value'] = CURRENT['next_milestone']
        if node['node_id'] == 'test_gate':
            node['value'] = 'E51 anti-drift validates valid manifest and denies broken P0 manifest'
    edges = [
        _edge('owner_task', 'semantic_interpreter', 'calls'),
        _edge('board_directive', 'CEO_brain', 'reads'),
        _edge('wisdom_memory', 'CEO_brain', 'reads'),
        _edge('working_memory', 'CEO_brain', 'reads'),
        _edge('CEO_brain', 'field_projection', 'calls'),
        _edge('field_projection', 'capability_router', 'calls'),
        _edge('capability_router', 'cognition_cascade', 'calls'),
        _edge('cognition_cascade', 'counterfactual_runtime', 'calls'),
        _edge('counterfactual_runtime', 'semantic_route_scorer', 'calls'),
        _edge('semantic_route_scorer', 'commercial_decision_packet', 'writes'),
        _edge('commercial_decision_packet', 'selected_route', 'selects'),
        _edge('commercial_decision_packet', 'nearest_alternative', 'rejects'),
        _edge('selected_route', 'CEO_brain', 'reads'),
        _edge('nearest_alternative', 'CEO_brain', 'reads'),
        _edge('CEO_brain', 'selected_route', 'consumes_next'),
        _edge('CEO_brain', 'next_milestone_state', 'consumes_next'),
        _edge('selected_route', 'execution_or_packaging_path', 'gates'),
        _edge('gov_mcp_boundary', 'execution_or_packaging_path', 'gates'),
        _edge('Y_star_gov_boundary', 'execution_or_packaging_path', 'gates'),
        _edge('K9Audit_context', 'CIEU_residual', 'audits'),
        _edge('commercial_decision_packet', 'KG_update', 'writes'),
        _edge('commercial_decision_packet', 'CZL_closure', 'writes'),
        _edge('commercial_decision_packet', 'CIEU_residual', 'writes'),
        _edge('KG_update', 'CEO_brain', 'updates'),
        _edge('CZL_closure', 'CEO_brain', 'updates'),
        _edge('CIEU_residual', 'CEO_brain', 'updates'),
        _edge('test_gate', 'selected_route', 'tests'),
        _edge('test_gate', 'next_milestone_state', 'tests'),
        _edge('test_gate', 'CEO_brain', 'tests'),
        _edge('future_closure_policy', 'test_gate', 'gates'),
        _edge('Y_star_gov_boundary', 'test_gate', 'validated_by_y_star_gov'),
        _edge('gov_mcp_boundary', 'test_gate', 'exposed_by_gov_mcp'),
        _edge('K9Audit_context', 'test_gate', 'evidenced_by_K9_CIEU'),
    ]
    answers = {
        'current_selected_route': {'value': CURRENT['selected_route'], 'written_in': ['operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'operations/external_validation/e50b_counterfactual_money_route_retest.json'], 'read_next_by': ['office/mission_command/e46b_ceo_brain_adapter.py', 'office/mission_command/e50c_ceo_brain_centerline_smoke.py', 'office/mission_command/e51_labs_runtime_linkage_manifest.py']},
        'current_nearest_alternative': {'value': CURRENT['nearest_alternative'], 'written_in': ['operations/external_validation/e50b_ceo_commercial_decision_packet.json'], 'read_next_by': ['office/mission_command/e46b_ceo_brain_adapter.py', 'office/mission_command/e51_labs_runtime_linkage_manifest.py']},
        'current_next_milestone': {'value': CURRENT['next_milestone'], 'written_in': ['operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'operations/external_validation/e50c_e51_readiness_gate.json'], 'read_next_by': ['office/mission_command/e46b_ceo_brain_adapter.py', 'office/mission_command/e51_current_readiness_anti_drift_gate.py']},
        'current_blockers': {'value': [CURRENT['blocker']], 'written_in': ['operations/external_validation/e50a_mcp_client_blocker_update.json', 'operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'operations/external_validation/e50c_cieu_residual_summary.json'], 'read_next_by': ['office/mission_command/e46b_ceo_brain_adapter.py', 'office/mission_command/e51_current_readiness_anti_drift_gate.py']},
        'current_no_go_boundaries': {'value': ['no outreach', 'no publication', 'no customer validation claim', 'no paid signal claim', 'owner approval required before external action', 'brain may not bypass governance'], 'written_in': ['operations/external_validation/e50c_ceo_brain_centerline_policy.json'], 'read_next_by': ['office/mission_command/e46b_ceo_brain_adapter.py', 'office/mission_command/e51_labs_runtime_linkage_manifest.py']},
        'written_but_not_read': [],
        'stale_runtime_modules': [{'module': 'e46b_canonical_ceo_operating_runtime', 'stale_reference': 'route decision still names E47 in legacy field', 'severity': 'P1', 'current_state_reader': 'CEO brain context overrides package route for E51'}],
        'readback_tests': ['tests/office/test_e50c_ceo_brain_loader_update.py', 'tests/office/test_e50c_ceo_brain_centerline_smoke.py', 'tests/office/test_e51_labs_runtime_linkage_manifest.py', 'tests/office/test_e51_current_readiness_anti_drift_gate.py'],
        'promote_to_y_star_gov': ['RuntimeArtifact schema', 'RuntimeLinkageGraph validation', 'CenterlineContract validation', 'ReadbackProof validation', 'AntiDriftGate invariants'],
        'expose_through_gov_mcp': ['gov_validate_runtime_linkage', 'gov_validate_centerline_contract', 'gov_validate_readback_proof', 'gov_enforce_anti_drift_gate'],
    }
    return {'graph_id': 'e51_labs_runtime_linkage_graph', 'nodes': nodes, 'edges': edges, 'generated_at': '2026-05-06T00:00:00Z', 'subject_system': 'Y*Bridge Labs runtime centerline', 'validation_context': answers, 'answers': answers, 'no_external_action': True}


def render_labs_runtime_linkage_graph_markdown(data: dict[str, Any]) -> str:
    answers = data['answers']
    return '\n'.join([
        '# E51 Labs Runtime Linkage Graph', '',
        f"Nodes: {len(data['nodes'])}", f"Edges: {len(data['edges'])}", '',
        f"Current selected route: `{answers['current_selected_route']['value']}`",
        f"Nearest alternative: `{answers['current_nearest_alternative']['value']}`",
        f"Current next milestone: `{answers['current_next_milestone']['value']}`",
        f"Current blocker: `{answers['current_blockers']['value'][0]}`", '',
        'Y-star-gov validates the generic contract. gov-mcp exposes the validator tools. K9Audit remains read-only audit context.', '',
        'No external action occurred.', ''
    ])


def write_labs_runtime_linkage_graph(output_root: Path | None = None) -> dict[str, Any]:
    data = build_labs_runtime_linkage_graph()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e51_labs_runtime_linkage_graph.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e51_labs_runtime_linkage_graph.md').write_text(render_labs_runtime_linkage_graph_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_labs_runtime_linkage_graph(), indent=2, ensure_ascii=False))
