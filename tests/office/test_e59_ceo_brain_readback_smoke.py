from office.mission_command.e59_ceo_brain_readback_smoke import run_ceo_brain_readback_smoke


def test_ceo_brain_reads_e59_external_intelligence_state_back():
    data = run_ceo_brain_readback_smoke()
    assert data["passes"] is True
    assert data["state"]["external_action_allowed"] is False
    assert data["state"]["customer_validation_claimed"] is False
    assert data["state"]["paid_signal_claimed"] is False
    assert data["state"]["expert_feedback_claimed"] is False
    assert data["state"]["next_recommended_milestone"] == "E60_post_external_intelligence_money_route_and_market_entry_readiness_retest"

