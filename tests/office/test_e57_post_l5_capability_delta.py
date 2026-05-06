from office.mission_command.e57_post_l5_capability_delta import run_post_l5_capability_delta


def test_l5_capability_delta_is_consumed_and_preserves_blockers():
    data = run_post_l5_capability_delta()
    assert data["big_improvement_internal_runtime_trust"] is True
    assert len(data["dimensions"]) == 14
    assert data["real_mcp_transport_claimed"] is False
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False

