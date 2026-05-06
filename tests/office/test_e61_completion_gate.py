from office.mission_command.e61_completion_gate import run_e61_completion_gate


def test_e61_completion_gate_passes_with_truthful_status():
    data = run_e61_completion_gate()
    assert data["gate_passed"] is True
    assert data["final_status"] in {
        "live_public_read_adapter_repaired_and_smoke_passed",
        "live_public_read_code_repaired_but_host_network_unavailable",
        "live_public_read_blocker_diagnosed_no_code_repair_needed",
        "live_public_read_adapter_still_blocked",
    }
    assert data["fixture_only_evidence_treated_as_live_market_freshness"] is False
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    assert data["expert_feedback_claimed"] is False
