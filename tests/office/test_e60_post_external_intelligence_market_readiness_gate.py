from office.mission_command.e60_post_external_intelligence_market_readiness_gate import run_post_external_intelligence_market_readiness_gate


def test_e60_completion_gate_passes_with_readback_and_no_overclaim():
    data = run_post_external_intelligence_market_readiness_gate()
    assert data["gate_passed"] is True
    assert data["final_status"] == "post_external_intelligence_market_readiness_retest_closed"
    assert data["recommended_next_milestone"] == "E61_live_public_read_adapter_repair_or_host_network_refresh"
    assert data["checks"]["live_read_limitation_handled_honestly"] is True
    assert data["fixture_only_evidence_treated_as_live_market_freshness"] is False
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    assert data["expert_feedback_claimed"] is False
