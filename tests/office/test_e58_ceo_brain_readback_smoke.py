from office.mission_command.e58_ceo_brain_readback_smoke import run_case_study_readback_smoke


def test_ceo_brain_reads_case_study_state_back():
    data = run_case_study_readback_smoke()
    assert data["passes"] is True
    assert data["state"]["case_study_id"] == "ai_agent_company_runtime_harness_case_study_e58"
    assert data["state"]["selected_route_from_E57"] == "AI_agent_company_runtime_harness_case_study"
    assert data["state"]["E59_required_before_market_contact"] is True
    assert data["state"]["external_action_allowed"] is False
    assert data["state"]["next_recommended_milestone"] == "E59_external_world_intelligence_L5_convergence"

