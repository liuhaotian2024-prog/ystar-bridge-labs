from office.mission_command.e55_behavior_center_l5_readiness_gate import run_behavior_center_l5_readiness_gate

def test_l5_readiness_gate_passes_only_with_all_gates():
    data = run_behavior_center_l5_readiness_gate()
    assert data["gate_passed"] is True
    assert data["final_status"] == "behavior_control_center_l5_ready"
    assert data["recommended_next_milestone"] == "E56_internal_company_operating_loop_L5"
    assert data["checks"]["no_ceo_brain_direct_execution"] is True
    assert data["checks"]["no_action_lacks_evidence_path"] is True
