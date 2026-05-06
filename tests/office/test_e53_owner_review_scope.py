from office.mission_command.e53_owner_review_scope import build_owner_review_scope

def test_owner_review_scope_pending_and_no_external_action():
    data = build_owner_review_scope()
    assert data["owner_decision_status"] == "pending_owner_decision"
    assert data["external_action_allowed"] is False
    assert "send_outreach" not in data["decision_options"]
