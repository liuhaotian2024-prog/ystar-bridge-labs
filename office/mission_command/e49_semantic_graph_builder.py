from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e46b_ceo_brain_adapter import load_ceo_brain_context
from .e46b_field_projection_adapter import project_task_from_m_triangle
from .e49_minimal_mcp_client_path_maturity import inspect_minimal_mcp_client_path
from .e49_semantic_object_model import (
    build_semantic_capability,
    build_semantic_evidence,
    build_semantic_execution_path,
    build_semantic_projection,
    build_semantic_task,
    build_semantic_value_object,
)

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))


def _read(path: Path, limit: int = 2_000_000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > limit:
            return ''
        return path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


def _json(rel: str, default: Any = None) -> Any:
    try:
        return json.loads(_read(BRIDGE_ROOT / rel))
    except Exception:
        return default


def _node(node_id: str, node_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {'id': node_id, 'type': node_type, 'payload': payload}


def _edge(source: str, target: str, edge_type: str, reason: str = '') -> dict[str, str]:
    return {'source': source, 'target': target, 'type': edge_type, 'reason': reason}


def build_semantic_graph(task_text: str | None = None) -> dict[str, Any]:
    task_text = task_text or 'What is the fastest credible route for Y*Bridge Labs to make real money or obtain the strongest near-term real user / usage / paid signal, using existing assets and without overclaiming?'
    task_obj = build_semantic_task('e49_money_route_task', task_text)
    projection_raw = project_task_from_m_triangle({'task_title': 'E49 semantic route retest', 'task_description': task_text})
    projection = build_semantic_projection('e49_projection', action_candidates=projection_raw.get('action_candidates', []), behavior_constraints=projection_raw.get('behavior_constraints', []), task_objective=task_text, y_star_candidate=projection_raw.get('y_star_candidate', 'Governed Agent Action Proof Packet'))
    brain = load_ceo_brain_context({'task_title': 'E49 semantic route retest', 'task_description': task_text})
    e47_matrix = _json('operations/external_validation/e47_money_route_retest_matrix.json', {}) or {}
    e48_proof = _json('operations/external_validation/e48_server_client_proof_result.json', {}) or {}
    e48_doctor = _json('operations/external_validation/e48_ystar_doctor_codegrounded_result.json', {}) or {}
    coverage = _json('operations/external_validation/e47_capability_final_status_matrix.json', {}) or {}
    mcp = inspect_minimal_mcp_client_path()

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    nodes.append(_node('task:e49_money_route', 'task', task_obj))
    nodes.append(_node('projection:e49', 'projection', projection))
    nodes.append(_node('ceo_brain:e46b_context', 'boundary', {'object_type': 'CEOBrainContext', 'source': 'e46b_ceo_brain_adapter', 'wisdom_invoked': brain.get('wisdom_search', {}).get('invoked'), 'commercial_asset_count': len(brain.get('commercial_assets', [])), 'no_external_action': True}))
    nodes.append(_node('capability:e47_coverage_gate', 'capability', build_semantic_capability('e47_full_capability_coverage_gate', source_path='operations/external_validation/e47_capability_final_status_matrix.json', runtime_status='active_runtime_adapter', semantic_role='coverage_gate', evidence_support=f"{coverage.get('resource_count', 'unknown')} resources classified")))
    nodes.append(_node('value_object:governed_agent_action_proof_packet', 'value_object', build_semantic_value_object('Governed Agent Action Proof Packet', route_dependency=['minimal local MCP client proof', 'owner approval before outreach'], monetization_mode='service wedge anchored by proof artifact')))
    nodes.append(_node('execution:gov_mcp_ystar', 'execution_path', build_semantic_execution_path('gov_mcp_ystar_execution_path', command_tool_server_client_path='gov-mcp gov_demo/gov_check over local MCP client + Y-star-gov kernel', local_proof_status='partial_allow_deny_kernel_passed', blocker=e48_proof.get('server_client_transport_blocker', 'missing_mcp_client_path'), cleanup='no process started; no port opened', side_effect_risk='install can mutate real client config, blocked unless sandboxed')))
    nodes.append(_node('blocker:missing_mcp_client_path', 'blocker', {'blocker_id': 'missing_mcp_client_path', 'severity': 'major_manageable', 'source': 'operations/external_validation/e48_server_client_proof_result.json', 'classification': e48_proof.get('server_client_transport_blocker', ''), 'fatal_to_route': False, 'blocks_external_attempt': True}))
    nodes.append(_node('blocker:ystar_doctor', 'blocker', {'blocker_id': 'ystar_doctor_status', 'severity': 'nonblocking_classified', 'source': 'operations/external_validation/e48_ystar_doctor_codegrounded_result.json', 'classification': e48_doctor.get('repo_doctor_classification', []), 'fatal_to_route': False, 'blocks_external_attempt': False}))
    nodes.append(_node('evidence:e48_allow_deny', 'evidence', build_semantic_evidence('e48_allow_deny_kernel_proof', source_artifact='operations/external_validation/e48_server_client_proof_result.json', claim='Y-star-gov kernel allowed echo e48_safe and denied rm -rf /tmp/e48_nonexistent', support_level='local_codegrounded_proof', limitation=['full gov-mcp server/client transport not closed'])) )
    nodes.append(_node('evidence:e38_e39_claim_graph', 'evidence', build_semantic_evidence('e38_e39_public_evidence_context', source_artifact='operations/external_validation/e39_deep_research_claim_graph.json', claim='public evidence and claim graph inform route but do not validate demand', support_level='public_observation')))
    nodes.append(_node('boundary:governance_execution_audit', 'boundary', {'boundary_id': 'governance_execution_audit', 'Y_star_gov': 'governance kernel', 'gov_mcp': 'execution boundary', 'K9Audit': 'audit layer', 'Bridge Labs': 'CEO semantic route runtime', 'no_external_action': True}))
    nodes.append(_node('closure:e49', 'closure', {'closure_expectation': 'semantic route decision + blocker + next milestone + no external action', 'CIEU_CZL': 'artifact closure only'}))
    nodes.append(_node('capability:minimal_mcp_client_maturity', 'capability', build_semantic_capability('minimal_mcp_client_path_maturity', source_path='office/mission_command/e49_minimal_mcp_client_path_maturity.py', runtime_status='active_runtime_adapter', semantic_role='execution_blocker_classifier', evidence_support=mcp['classification'])))

    routes = e47_matrix.get('routes') or []
    for route in routes:
        route_id = route.get('route_id', 'unknown_route')
        nodes.append(_node(f'route:{route_id}', 'route', route))
        edges.append(_edge(f'route:{route_id}', 'task:e49_money_route', 'derives_from', 'route is evaluated for money task'))
        if route_id == 'governed_agent_action_proof_packet':
            edges.extend([
                _edge(f'route:{route_id}', 'value_object:governed_agent_action_proof_packet', 'produces', 'route packages proof object'),
                _edge('evidence:e48_allow_deny', f'route:{route_id}', 'supports', 'local allow/deny proof supports the wedge'),
                _edge('blocker:missing_mcp_client_path', f'route:{route_id}', 'blocks', 'blocks external attempt until local client proof exists'),
                _edge('blocker:ystar_doctor', f'route:{route_id}', 'blocks', 'doctor is classified nonfatal'),
            ])
        if any(term in route_id for term in ['plugin', 'mcpb', 'setup', 'consulting', 'bug_bounty', 'workflow', 'enterprise']):
            edges.append(_edge(f'route:{route_id}', 'ceo_brain:e46b_context', 'requires', 'commercial assets and wisdom context required'))
    edges.extend([
        _edge('task:e49_money_route', 'projection:e49', 'requires', 'field projection is required'),
        _edge('projection:e49', 'ceo_brain:e46b_context', 'requires', 'brain context grounds route semantics'),
        _edge('ceo_brain:e46b_context', 'capability:e47_coverage_gate', 'read_by', 'runtime uses full capability mainline status'),
        _edge('execution:gov_mcp_ystar', 'boundary:governance_execution_audit', 'owned_by', 'execution path is owned by gov-mcp/Y-star-gov boundaries'),
        _edge('value_object:governed_agent_action_proof_packet', 'evidence:e48_allow_deny', 'requires', 'value object requires proof evidence'),
        _edge('evidence:e48_allow_deny', 'boundary:governance_execution_audit', 'must_not_claim', 'not customer validation or paid signal'),
        _edge('route:governed_agent_action_proof_packet', 'closure:e49', 'next_action', 'semantic decision writes closure'),
        _edge('capability:minimal_mcp_client_maturity', 'blocker:missing_mcp_client_path', 'produces', 'maturity check explains blocker'),
    ])
    selected_has_support = any(e['source'].startswith('evidence:') and e['target'] == 'route:governed_agent_action_proof_packet' and e['type'] == 'supports' for e in edges)
    selected_has_blocker = any(e['source'].startswith('blocker:') and e['target'] == 'route:governed_agent_action_proof_packet' and e['type'] == 'blocks' for e in edges)
    return {'artifact_id': 'e49_semantic_graph', 'node_count': len(nodes), 'edge_count': len(edges), 'nodes': nodes, 'edges': edges, 'selected_route_id': 'governed_agent_action_proof_packet', 'selected_route_has_evidence_semantics': selected_has_support, 'selected_route_has_blocker_semantics': selected_has_blocker, 'no_orphan_selected_route': selected_has_support and selected_has_blocker, 'no_external_action': True}
