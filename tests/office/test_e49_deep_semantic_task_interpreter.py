from office.mission_command.e49_deep_semantic_task_interpreter import interpret_owner_task_semantically


def test_e49_task_semantic_layer_not_report_only():
    data = interpret_owner_task_semantically('Make the deep semantic layer fully mature.')
    assert 'semantic_object_model' in data['capability_families_required']
    assert 'runtime integration' in data['commercial_evidence_execution_audit_requirements']
    assert 'report-only output with no runtime object validation' in data['what_would_count_as_shallow_answer']


def test_e49_money_task_requires_commercial_evidence_execution_blockers():
    data = interpret_owner_task_semantically('How do we make money fastest?')
    assert 'commercial_route' in data['capability_families_required']
    assert 'execution_blocker' in data['capability_families_required']
    assert data['required_output_type'] == 'money_route_decision'


def test_e49_external_user_task_keeps_approval_boundary():
    data = interpret_owner_task_semantically('Prepare a first external user attempt.')
    assert 'owner_approval_gate' in data['capability_families_required']
    assert 'owner approval required' in data['commercial_evidence_execution_audit_requirements']
    assert 'no real human identification' in data['commercial_evidence_execution_audit_requirements']


def test_e49_cognition_and_projection_tasks_route_correctly():
    cognition = interpret_owner_task_semantically('Use our previous imagination and innovation modules.')
    projection = interpret_owner_task_semantically('Reconnect CEO brain and field projection.')
    assert 'E34_strategic_imagination' in cognition['capability_families_required']
    assert 'E35_six_dimensional_cognition' in cognition['capability_families_required']
    assert 'field_functional_projection' in projection['capability_families_required']
    assert 'ceo_brain_context' in projection['capability_families_required']
