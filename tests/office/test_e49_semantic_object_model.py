from office.mission_command.e49_semantic_object_model import (
    build_semantic_evidence,
    build_semantic_execution_path,
    build_semantic_route_decision,
    build_semantic_task,
    semantic_object_model_contract,
    validate_semantic_object,
)


def test_e49_semantic_objects_validate_and_fail_missing_fields():
    task = build_semantic_task('t1', 'Make the deep semantic layer fully mature.')
    assert validate_semantic_object(task)['valid'] is True
    broken = dict(task)
    broken.pop('explicit_goal')
    assert validate_semantic_object(broken)['valid'] is False


def test_e49_evidence_has_no_validation_or_paid_signal_flags():
    evidence = build_semantic_evidence('e1', source_artifact='x', claim='public artifact supports claim')
    assert evidence['not_customer_validation'] is True
    assert evidence['not_paid_signal'] is True
    assert validate_semantic_object(evidence)['valid'] is True


def test_e49_execution_and_route_require_blocker_semantics():
    path = build_semantic_execution_path('p1', command_tool_server_client_path='local mcp client', side_effect_risk='scratch only')
    assert path['side_effect_risk'] == 'scratch only'
    decision = build_semantic_route_decision('d1', selected_route='governed_agent_action_proof_packet', evidence_semantics=['e1'], blocker_semantics=['missing_mcp_client_path'])
    assert validate_semantic_object(decision)['valid'] is True
    bad = dict(decision)
    bad['evidence_semantics'] = []
    assert validate_semantic_object(bad)['valid'] is False


def test_e49_semantic_model_contract_samples_validate():
    contract = semantic_object_model_contract()
    assert contract['sample_validation']['valid'] is True
    assert 'SemanticValueObject' in contract['kinds']
