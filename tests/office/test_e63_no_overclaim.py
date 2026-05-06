from office.mission_command.e63_completion_gate import run_e63_completion_gate


def test_e63_completion_gate_has_no_overclaim_fields_true():
    data = run_e63_completion_gate()
    assert data["gate_passed"] is True
    for key in [
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "production_readiness_claimed",
        "autonomous_revenue_achieved",
        "real_client_delivery_claimed",
        "real_mcp_transport_claimed",
    ]:
        assert data[key] is False
    assert data["external_action_allowed"] is False
