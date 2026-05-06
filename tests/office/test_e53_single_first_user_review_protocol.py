from office.mission_command.e53_single_first_user_review_protocol import build_single_first_user_review_protocol

def test_protocol_contains_no_real_contacts_and_is_future_only():
    data = build_single_first_user_review_protocol()
    assert data["status"] == "future_only_blocked_without_owner_approval"
    assert data["contains_real_contacts"] is False
    assert data["sent"] is False
    assert data["owner_approval_required"] is True
