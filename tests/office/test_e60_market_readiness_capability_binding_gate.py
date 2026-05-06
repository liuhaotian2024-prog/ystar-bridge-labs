from office.mission_command.e60_market_readiness_capability_binding_gate import run_market_readiness_capability_binding_gate


def test_e60_capability_binding_gate_binds_decision_authorization_and_evidence():
    data = run_market_readiness_capability_binding_gate()
    assert data["passed"] is True
    assert data["checks"]["selected_authorization_bound_to_behavior_center"] is True
    assert data["checks"]["live_read_limitation_bound_to_boundary"] is True
    assert data["external_action_allowed"] is False
