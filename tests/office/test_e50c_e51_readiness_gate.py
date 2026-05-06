from office.mission_command.e50c_e51_readiness_gate import build_e51_readiness_gate


def test_e51_readiness_gate_passes_only_with_e50b_current_state_loaded():
    gate = build_e51_readiness_gate()
    assert gate['gate_passed'] is True
    assert all(gate['checks'].values())
    assert gate['recommended_next_milestone'] == 'E51_package_governed_agent_action_proof_packet_for_first_user_review'
    assert gate['no_external_action'] is True
