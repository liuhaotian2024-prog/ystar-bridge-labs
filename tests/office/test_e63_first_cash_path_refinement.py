from office.mission_command.e63_first_cash_path_refinement import run_first_cash_path_refinement


def test_e63_first_cash_path_refinement_keeps_runtime_harness_path_owner_gated():
    data = run_first_cash_path_refinement()
    assert data["starting_selected_path_from_E62"] == "AI_agent_company_runtime_harness_deployment_service"
    assert data["refined_selected_first_cash_path"] == "AI_agent_company_runtime_harness_deployment_service"
    assert "outreach" in data["what_remains_owner_gated"]
    assert data["external_action_allowed"] is False
