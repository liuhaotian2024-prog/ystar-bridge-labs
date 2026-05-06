from office.mission_command.e62_revenue_runtime_behavior_authorization import run_revenue_runtime_behavior_authorization


def test_e62_behavior_authorization_allows_internal_recenter_and_denies_external_execution():
    data = run_revenue_runtime_behavior_authorization()
    assert data["authorization_status"] == "ALLOW_INTERNAL_ONLY"
    assert "internal_revenue_route_analysis" in data["allowed_actions"]
    assert "customer_outreach" in data["denied_actions"]
    assert "payment_action" in data["denied_actions"]
    assert data["pending_owner_decision_is_not_approval"] is True
    assert data["external_action_allowed"] is False
