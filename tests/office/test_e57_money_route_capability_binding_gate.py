from office.mission_command.e57_money_route_capability_binding_gate import run_money_route_capability_binding_gate


def test_money_route_capability_binding_gate_passes():
    data = run_money_route_capability_binding_gate()
    assert data["passed"] is True
    assert data["checks"]["decision_is_cognitive_not_executor"] is True
    assert data["checks"]["behavior_authorization_bound_to_action_runtime"] is True

