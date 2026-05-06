from office.mission_command.e60_selected_action_behavior_authorization import run_selected_action_behavior_authorization


def test_e60_behavior_authorization_denies_external_execution_without_owner_approval():
    data = run_selected_action_behavior_authorization()
    assert data["passed"] is True
    assert data["authorization_class"] == "internal_allowed"
    assert data["fixture_results"]["direct_outreach_denied"]["status"] == "deny"
    assert data["fixture_results"]["publication_denied"]["status"] == "deny"
    assert data["fixture_results"]["controlled_review_execution_denied_without_owner_approval"]["status"] == "deny"
    assert data["external_action_allowed"] is False
