from __future__ import annotations

from copy import deepcopy
from typing import Any

KIND_REQUIRED_FIELDS: dict[str, list[str]] = {
    'SemanticTask': ['object_type', 'task_id', 'owner_request', 'explicit_goal', 'implicit_goal', 'm_triangle_alignment', 'permitted_action_boundary', 'forbidden_action_boundary'],
    'SemanticProjection': ['object_type', 'projection_id', 'mission', 'company_objective', 'milestone_objective', 'task_objective', 'action_candidates', 'behavior_constraints', 'y_star_candidate', 'governance_gate', 'cieu_czl_closure_expectation', 'residual_learning_expectation'],
    'SemanticCapability': ['object_type', 'capability_id', 'source_path', 'canonical_spine_layer', 'runtime_status', 'semantic_role', 'inputs', 'outputs', 'side_effects', 'maturity', 'test_coverage', 'evidence_support'],
    'SemanticValueObject': ['object_type', 'value_object_name', 'buyer_persona', 'pain_solved', 'proof_needed', 'demo_artifact', 'overclaim_boundary', 'monetization_mode', 'route_dependency'],
    'SemanticEvidence': ['object_type', 'evidence_id', 'source_artifact', 'claim', 'support_level', 'contradiction', 'limitation', 'not_customer_validation', 'not_paid_signal', 'allowed_language', 'forbidden_language'],
    'SemanticExecutionPath': ['object_type', 'execution_path_id', 'command_tool_server_client_path', 'local_proof_status', 'blocker', 'cleanup', 'owner_approval_boundary', 'side_effect_risk'],
    'SemanticRouteDecision': ['object_type', 'decision_id', 'selected_route', 'rejected_routes', 'parked_routes', 'evidence_burden', 'execution_burden', 'owner_burden', 'next_milestone', 'stop_conditions', 'evidence_semantics', 'blocker_semantics'],
}

VALID_OBJECT_TYPES = set(KIND_REQUIRED_FIELDS)


def _base(kind: str) -> dict[str, Any]:
    if kind not in VALID_OBJECT_TYPES:
        raise ValueError(f'unknown semantic kind: {kind}')
    return {'object_type': kind, 'schema_version': 'e49.semantic.v1', 'confidence': 'artifact_supported', 'maturity': 'partial_runtime', 'no_external_action': True}


def build_semantic_task(task_id: str, owner_request: str, **overrides: Any) -> dict[str, Any]:
    text = owner_request.lower()
    data = _base('SemanticTask')
    data.update({
        'task_id': task_id,
        'owner_request': owner_request,
        'explicit_goal': overrides.get('explicit_goal') or owner_request.strip(),
        'implicit_goal': overrides.get('implicit_goal') or ('convert runtime capability into value production without overclaiming' if any(t in text for t in ['money', 'user', 'value', 'revenue']) else 'improve CEO runtime decision quality'),
        'm_triangle_alignment': overrides.get('m_triangle_alignment') or 'value production + governance discipline + learning closure',
        'urgency': overrides.get('urgency', 'near_term'),
        'permitted_action_boundary': overrides.get('permitted_action_boundary', ['local deterministic code', 'read-only repo inspection', 'artifact generation', 'tests']),
        'forbidden_action_boundary': overrides.get('forbidden_action_boundary', ['customer contact', 'expert contact', 'human identification', 'scraping', 'send', 'publish', 'login', 'provider/API execution', 'internet install', 'payment', 'secret use']),
    })
    return data


def build_semantic_projection(projection_id: str, **values: Any) -> dict[str, Any]:
    data = _base('SemanticProjection')
    data.update({
        'projection_id': projection_id,
        'mission': values.get('mission', 'Y*Bridge Labs produces real governed-agent value without fake validation'),
        'company_objective': values.get('company_objective', 'make governed agent action proof understandable and locally verifiable'),
        'milestone_objective': values.get('milestone_objective', 'mature semantic layer and retest route'),
        'session_objective': values.get('session_objective', 'local dry-run semantic route decision'),
        'task_objective': values.get('task_objective', 'semantic route retest'),
        'action_candidates': values.get('action_candidates', []),
        'behavior_constraints': values.get('behavior_constraints', []),
        'y_star_candidate': values.get('y_star_candidate', 'Governed Agent Action Proof Packet'),
        'governance_gate': values.get('governance_gate', 'owner approval before external action'),
        'cieu_czl_closure_expectation': values.get('cieu_czl_closure_expectation', 'record proof, blockers, route decision, next milestone'),
        'residual_learning_expectation': values.get('residual_learning_expectation', 'blockers become learning candidates, not validation claims'),
    })
    return data


def build_semantic_capability(capability_id: str, **values: Any) -> dict[str, Any]:
    data = _base('SemanticCapability')
    data.update({
        'capability_id': capability_id,
        'source_path': values.get('source_path', ''),
        'canonical_spine_layer': values.get('canonical_spine_layer', 'capability_activation_layer'),
        'runtime_status': values.get('runtime_status', 'active_read_model_input'),
        'semantic_role': values.get('semantic_role', 'decision_context'),
        'inputs': values.get('inputs', []),
        'outputs': values.get('outputs', []),
        'side_effects': values.get('side_effects', 'none'),
        'maturity': values.get('maturity', 'partial'),
        'test_coverage': values.get('test_coverage', 'artifact_or_targeted_test'),
        'evidence_support': values.get('evidence_support', 'source_artifact'),
    })
    return data


def build_semantic_value_object(name: str, **values: Any) -> dict[str, Any]:
    data = _base('SemanticValueObject')
    data.update({
        'value_object_name': name,
        'buyer_persona': values.get('buyer_persona', 'AI engineer / agent team'),
        'pain_solved': values.get('pain_solved', 'trust and explain agent actions'),
        'proof_needed': values.get('proof_needed', ['local allow/deny proof', 'governance envelope', 'no-overclaim boundary']),
        'demo_artifact': values.get('demo_artifact', 'First Value Demo Bundle'),
        'overclaim_boundary': values.get('overclaim_boundary', ['not customer validation', 'not paid signal', 'not compliance certification']),
        'monetization_mode': values.get('monetization_mode', 'service wedge / paid setup candidate'),
        'route_dependency': values.get('route_dependency', ['minimal local MCP client proof', 'owner approval before outreach']),
    })
    return data


def build_semantic_evidence(evidence_id: str, **values: Any) -> dict[str, Any]:
    data = _base('SemanticEvidence')
    data.update({
        'evidence_id': evidence_id,
        'source_artifact': values.get('source_artifact', ''),
        'claim': values.get('claim', ''),
        'support_level': values.get('support_level', 'artifact_supported'),
        'contradiction': values.get('contradiction', []),
        'limitation': values.get('limitation', []),
        'not_customer_validation': values.get('not_customer_validation', True),
        'not_paid_signal': values.get('not_paid_signal', True),
        'allowed_language': values.get('allowed_language', ['local proof', 'hypothesis', 'owner-ready packet']),
        'forbidden_language': values.get('forbidden_language', ['validated by customers', 'paid signal', 'guaranteed ROI', 'compliance certified']),
    })
    return data


def build_semantic_execution_path(execution_path_id: str, **values: Any) -> dict[str, Any]:
    data = _base('SemanticExecutionPath')
    data.update({
        'execution_path_id': execution_path_id,
        'command_tool_server_client_path': values.get('command_tool_server_client_path', ''),
        'local_proof_status': values.get('local_proof_status', 'partial'),
        'blocker': values.get('blocker', 'none'),
        'cleanup': values.get('cleanup', 'not_applicable_or_cleaned'),
        'owner_approval_boundary': values.get('owner_approval_boundary', 'owner approval required before external action'),
        'side_effect_risk': values.get('side_effect_risk', 'none'),
    })
    return data


def build_semantic_route_decision(decision_id: str, **values: Any) -> dict[str, Any]:
    data = _base('SemanticRouteDecision')
    data.update({
        'decision_id': decision_id,
        'selected_route': values.get('selected_route', ''),
        'rejected_routes': values.get('rejected_routes', []),
        'parked_routes': values.get('parked_routes', []),
        'evidence_burden': values.get('evidence_burden', 'medium'),
        'execution_burden': values.get('execution_burden', 'medium'),
        'owner_burden': values.get('owner_burden', 'low'),
        'next_milestone': values.get('next_milestone', 'E50_build_minimal_gov_mcp_local_test_client'),
        'stop_conditions': values.get('stop_conditions', []),
        'evidence_semantics': values.get('evidence_semantics', []),
        'blocker_semantics': values.get('blocker_semantics', []),
    })
    return data


def validate_semantic_object(obj: dict[str, Any]) -> dict[str, Any]:
    kind = obj.get('object_type')
    errors: list[str] = []
    if kind not in KIND_REQUIRED_FIELDS:
        return {'valid': False, 'errors': ['unknown_object_type']}
    for field in KIND_REQUIRED_FIELDS[kind]:
        if field not in obj or obj.get(field) in (None, ''):
            errors.append(f'missing_{field}')
    if kind == 'SemanticEvidence':
        if obj.get('not_customer_validation') is not True:
            errors.append('evidence_must_not_claim_customer_validation')
        if obj.get('not_paid_signal') is not True:
            errors.append('evidence_must_not_claim_paid_signal')
    if kind == 'SemanticExecutionPath' and 'side_effect_risk' not in obj:
        errors.append('execution_path_requires_side_effect_risk')
    if kind == 'SemanticRouteDecision':
        if not obj.get('evidence_semantics'):
            errors.append('route_decision_requires_evidence_semantics')
        if 'blocker_semantics' not in obj:
            errors.append('route_decision_requires_blocker_semantics')
    return {'valid': not errors, 'errors': errors}


def validate_semantic_contract(objects: list[dict[str, Any]]) -> dict[str, Any]:
    results = [validate_semantic_object(deepcopy(obj)) for obj in objects]
    return {'valid': all(item['valid'] for item in results), 'results': results, 'object_count': len(objects)}


def semantic_object_model_contract() -> dict[str, Any]:
    samples = [
        build_semantic_task('sample_task', 'Make the semantic layer mature'),
        build_semantic_projection('sample_projection', action_candidates=['build semantic graph'], behavior_constraints=['no external action']),
        build_semantic_capability('sample_capability', source_path='office/mission_command/e47_canonical_ceo_runtime_v2.py'),
        build_semantic_value_object('Governed Agent Action Proof Packet'),
        build_semantic_evidence('sample_evidence', source_artifact='operations/external_validation/e48_server_client_proof_result.json', claim='ALLOW/DENY kernel proof exists'),
        build_semantic_execution_path('sample_execution', command_tool_server_client_path='Y-star-gov check(...)', side_effect_risk='none'),
        build_semantic_route_decision('sample_decision', selected_route='governed_agent_action_proof_packet', evidence_semantics=['sample_evidence'], blocker_semantics=['missing_mcp_client_path']),
    ]
    return {'artifact_id': 'e49_semantic_object_model_contract', 'kinds': sorted(KIND_REQUIRED_FIELDS), 'required_fields': KIND_REQUIRED_FIELDS, 'sample_validation': validate_semantic_contract(samples), 'no_external_action': True}
