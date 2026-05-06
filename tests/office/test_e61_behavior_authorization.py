from office.mission_command.e61_behavior_authorization import run_behavior_authorization


def test_e61_behavior_authorization_allows_smoke_probe_and_denies_unsafe_actions():
    data = run_behavior_authorization()
    assert data["passed"] is True
    assert "controlled_public_read_smoke_probe" in data["allowed_actions"]
    for denied in ["outreach", "publication", "customer_validation_claim", "expert_feedback_claim", "paid_signal_claim", "contact_scraping", "login_form_send"]:
        assert denied in data["denied_actions"]
    assert data["external_action_allowed"] is False
