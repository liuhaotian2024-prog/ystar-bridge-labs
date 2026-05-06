from office.mission_command.e58_case_study_completion_gate import run_case_study_completion_gate


def test_case_study_completion_gate_passes_only_with_readback_and_no_overclaim():
    data = run_case_study_completion_gate()
    assert data["gate_passed"] is True
    assert data["final_status"] == "AI_agent_company_runtime_harness_case_study_packaged"
    assert data["recommended_next_milestone"] == "E59_external_world_intelligence_L5_convergence"
    assert data["checks"]["CEO_brain_readback_passed"] is True
    assert data["checks"]["no_overclaim_validation_passed"] is True
    assert data["checks"]["external_intelligence_L5_not_claimed_complete"] is True
    assert data["external_action_allowed"] is False

