from office.mission_command.e60_market_entry_decision import run_market_entry_decision_packet


def test_e60_decision_does_not_allow_external_action_or_live_freshness_overclaim():
    data = run_market_entry_decision_packet()
    assert data["selected_next_milestone"] == "E61_live_public_read_adapter_repair_or_host_network_refresh"
    assert data["current_readiness_level"] == "L3_external_intelligence_structurally_ready"
    assert data["external_contact_allowed_now"] is False
    assert data["publication_allowed_now"] is False
    assert data["controlled_review_execution_allowed_now"] is False
    assert data["fixture_only_evidence_treated_as_live_market_freshness"] is False
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    assert data["expert_feedback_claimed"] is False
    assert data["real_mcp_transport_claimed"] is False
