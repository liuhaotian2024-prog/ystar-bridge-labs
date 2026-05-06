from office.mission_command.e61_external_intelligence_readiness_delta import run_external_intelligence_readiness_delta


def test_e61_readiness_delta_is_honest_about_live_freshness():
    data = run_external_intelligence_readiness_delta()
    assert data["previous_status"] == "external_world_intelligence_L5_ready_with_live_read_unavailable_nonfatal"
    assert data["fixture_only_evidence_treated_as_live_market_freshness"] is False
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    assert data["expert_feedback_claimed"] is False
    assert data["recommended_next_milestone"].startswith("E62_")
