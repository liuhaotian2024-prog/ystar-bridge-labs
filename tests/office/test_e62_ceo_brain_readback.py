from office.mission_command.e62_ceo_brain_readback_smoke import run_ceo_brain_readback_smoke


def test_e62_ceo_brain_reads_revenue_runtime_state_back():
    data = run_ceo_brain_readback_smoke()
    assert data["passes"] is True
    state = data["observed_state"]
    assert state["selected_first_cash_path"] == "AI_agent_company_runtime_harness_deployment_service"
    assert state["external_action_allowed"] is False
    assert state["autonomous_revenue_achieved"] is False
