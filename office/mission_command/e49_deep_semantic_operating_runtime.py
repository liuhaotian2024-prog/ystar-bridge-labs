from __future__ import annotations

from typing import Any

from .e46b_ceo_brain_adapter import load_ceo_brain_context
from .e46b_field_projection_adapter import project_task_from_m_triangle
from .e47_canonical_ceo_runtime_v2 import run_canonical_ceo_runtime_v2
from .e47_full_capability_coverage_gate import build_full_capability_coverage_gate
from .e49_deep_semantic_task_interpreter import interpret_owner_task_semantically
from .e49_minimal_mcp_client_path_maturity import inspect_minimal_mcp_client_path
from .e49_semantic_graph_builder import build_semantic_graph
from .e49_semantic_route_scorer import score_semantic_routes


def _side_effect_report() -> dict[str, bool]:
    return {key: False for key in ['customer_contact', 'expert_contact', 'human_identification', 'scraping', 'send', 'publish', 'form_submission', 'login', 'provider_api_execution', 'internet_install', 'payment', 'secret_use', 'real_client_config_mutation']}


def run_deep_semantic_operating_runtime(task_text: str, mode: str = 'local_dry_run') -> dict[str, Any]:
    interpretation = interpret_owner_task_semantically(task_text)
    if not interpretation.get('semantic_task_validation', {}).get('valid'):
        return {'artifact_id': 'e49_deep_semantic_runtime_smoke_result', 'status': 'blocked', 'reason': 'invalid_semantic_task', 'interpretation': interpretation, 'no_external_action': True}
    if 'report-only output with no runtime object validation' not in interpretation.get('what_would_count_as_shallow_answer', []):
        return {'artifact_id': 'e49_deep_semantic_runtime_smoke_result', 'status': 'blocked', 'reason': 'shallow_interpretation_rejected', 'interpretation': interpretation, 'no_external_action': True}
    task = {'task_title': 'E49 deep semantic runtime', 'task_description': task_text}
    projection = project_task_from_m_triangle(task, {})
    brain = load_ceo_brain_context(task)
    graph = build_semantic_graph(task_text)
    coverage = build_full_capability_coverage_gate()
    canonical = run_canonical_ceo_runtime_v2(task, mode=mode)
    mcp = inspect_minimal_mcp_client_path()
    scores = score_semantic_routes()
    selected = scores['selected_route']
    next_milestone = scores['semantic_route_decision']['next_milestone']
    closure = {
        'route_decision_produced': True,
        'selected_route': selected['route_id'],
        'selected_value_object': selected['value_object'],
        'selected_route_kind': selected['route_kind'],
        'missing_client_path_blocks_external_attempt': mcp['classification'].startswith('blocked'),
        'owner_approval_required_before_external_action': True,
        'no_external_action': True,
    }
    return {
        'artifact_id': 'e49_deep_semantic_runtime_smoke_result',
        'status': 'completed',
        'mode': mode,
        'interpretation': interpretation,
        'field_projection': projection,
        'ceo_brain_context': {'active_task_time_source': brain.get('active_task_time_source'), 'wisdom_invoked': brain.get('wisdom_search', {}).get('invoked'), 'commercial_asset_count': len(brain.get('commercial_assets', []))},
        'semantic_graph_summary': {'node_count': graph['node_count'], 'edge_count': graph['edge_count'], 'no_orphan_selected_route': graph['no_orphan_selected_route']},
        'coverage_gate': {'passed': coverage.get('coverage_gate_passed'), 'unknown_status_count': coverage.get('unknown_status_count')},
        'canonical_runtime_v2': {'route': canonical.get('route_decision', {}), 'adapter_count': canonical.get('mandatory_adapter_count'), 'no_external_action': canonical.get('no_external_action')},
        'evidence_audit_closure_context': {'evidence_nodes': len([n for n in graph['nodes'] if n['type'] == 'evidence']), 'audit_boundary_present': any(n['type'] == 'boundary' for n in graph['nodes']), 'closure_nodes': len([n for n in graph['nodes'] if n['type'] == 'closure'])},
        'semantic_route_scores': scores,
        'execution_blockers': {'minimal_mcp_client_path': mcp['classification'], 'server_import_returncode': mcp['server_import_check']['returncode']},
        'route_decision': scores['semantic_route_decision'],
        'next_milestone': next_milestone,
        'closure_packet': closure,
        'side_effect_report': _side_effect_report(),
        'no_external_action': True,
    }
