from office.mission_command.e63_ceo_brain_readback_smoke import run_ceo_brain_readback_smoke


def test_e63_ceo_brain_reads_opportunity_discovery_state():
    data = run_ceo_brain_readback_smoke()
    assert data["passes"] is True
    state = data["observed_state"]
    assert state["selected_first_cash_path_consumed"] == "AI_agent_company_runtime_harness_deployment_service"
    assert state["external_action_allowed"] is False
    assert state["customer_validation_claimed"] is False
