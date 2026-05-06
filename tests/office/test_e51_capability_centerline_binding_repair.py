from office.mission_command.e51_capability_centerline_binding_repair import build_capability_centerline_binding_repair_result


def test_capability_binding_repair_passes_and_gov_mcp_denies_bad_bindings():
    result = build_capability_centerline_binding_repair_result()
    assert result['passed'] is True
    assert result['checks']['capability_centerline_binding_gate_passed'] is True
    assert result['checks']['no_active_cognitive_capability_outside_brain'] is True
    assert result['checks']['no_behavior_capability_bypassing_action_runtime'] is True
    assert result['checks']['no_current_state_evidence_without_readback'] is True
    assert result['checks']['no_reference_only_artifact_consumed_as_current'] is True
    assert result['gov_mcp_deny_proofs']['cognitive_missing_brain_binding']['status'] == 'DENY'
    assert result['gov_mcp_deny_proofs']['behavior_bypassing_action_runtime']['status'] == 'DENY'
    assert result['gov_mcp_deny_proofs']['reference_only_consumed_as_current']['status'] == 'DENY'
