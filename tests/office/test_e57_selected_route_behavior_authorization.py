from office.mission_command.e57_selected_route_behavior_authorization import run_selected_route_behavior_authorization


def test_selected_route_has_behavior_authorization_and_denies_external():
    data = run_selected_route_behavior_authorization()
    assert data["passed"] is True
    assert data["authorization_outcome"] == "internal_analysis_allowed"
    assert data["checks"]["direct_outreach_denied"] is True
    assert data["checks"]["ceo_brain_not_executor"] is True

