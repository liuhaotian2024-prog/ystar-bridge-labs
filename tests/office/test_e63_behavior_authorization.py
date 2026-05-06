from office.mission_command.e63_behavior_authorization import run_behavior_authorization


def test_e63_behavior_authorization_allows_public_read_only_and_denies_external_actions():
    data = run_behavior_authorization()
    assert data["authorization_status"] == "ALLOW_PUBLIC_READ_ONLY_INTERNAL_DISCOVERY"
    assert "bounded_public_read_only_discovery" in data["allowed_actions"]
    assert "outreach" in data["denied_actions"]
    assert "payment_action" in data["denied_actions"]
    assert data["external_action_allowed"] is False
