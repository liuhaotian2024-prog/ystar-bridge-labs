from office.mission_command.e51_current_readiness_anti_drift_gate import evaluate_current_readiness_anti_drift_gate


def test_e51_current_readiness_anti_drift_gate_passes_and_recommends_e52():
    result = evaluate_current_readiness_anti_drift_gate()
    assert result['gate_passed'] is True
    assert result['checks']['e50b_selected_route_read_back'] is True
    assert result['checks']['gov_mcp_broken_p0_denied'] is True
    assert result['recommended_next_milestone'] == 'E52_package_governed_agent_action_proof_packet_for_first_user_review'
    assert result['no_external_action'] is True
