from office.mission_command.e51_current_readiness_anti_drift_gate import evaluate_current_readiness_anti_drift_gate


def test_e51_current_gate_includes_capability_centerline_binding_checks():
    result = evaluate_current_readiness_anti_drift_gate()
    assert result['gate_passed'] is True
    for key in [
        'capability_centerline_binding_gate_passed',
        'no_active_cognitive_capability_outside_brain',
        'no_behavior_capability_bypassing_action_runtime',
        'no_current_state_evidence_without_readback',
        'no_reference_only_artifact_consumed_as_current',
    ]:
        assert result['checks'][key] is True
    assert result['capability_centerline_binding_summary']['passed'] is True
