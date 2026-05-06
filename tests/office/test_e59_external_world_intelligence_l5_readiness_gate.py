from office.mission_command.e59_external_world_intelligence_l5_readiness_gate import run_external_world_intelligence_l5_readiness_gate


def test_e59_l5_readiness_gate_passes_with_live_read_unavailable_nonfatal():
    data = run_external_world_intelligence_l5_readiness_gate()
    assert data["gate_passed"] is True
    assert data["final_status"] == "external_world_intelligence_L5_ready_with_live_read_unavailable_nonfatal"
    assert data["recommended_next_milestone"] == "E60_post_external_intelligence_money_route_and_market_entry_readiness_retest"
    assert data["live_public_read_status"] == "live_public_read_unavailable_nonfatal"
    assert data["external_action_allowed"] is False
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    assert data["expert_feedback_claimed"] is False

