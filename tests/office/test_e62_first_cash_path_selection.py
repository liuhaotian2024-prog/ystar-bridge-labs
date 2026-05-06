from office.mission_command.e62_first_cash_path_selection import run_first_cash_path_selection


def test_e62_first_cash_path_is_internal_draft_only_until_owner_approval():
    data = run_first_cash_path_selection()
    assert data["selected_first_cash_path"] == "AI_agent_company_runtime_harness_deployment_service"
    assert data["selected_action_risk_tier"] == "T2_draft_only_external_material"
    assert data["owner_approval_required_before_external_action"] is True
    assert data["external_action_allowed"] is False
    assert data["revenue_not_achieved"] is True
