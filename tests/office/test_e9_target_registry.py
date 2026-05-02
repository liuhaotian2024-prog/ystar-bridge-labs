from office.mission_command.e9_target_registry import E9ValidationTarget, e9_target_allows_action, validate_e9_target


def test_e9_target_rejects_invented_or_not_owner_provided_contact():
    target = E9ValidationTarget("t1", "known_contact", "Invented", "email", "x@example.com", "invented", "relevant", False, True, 1, False)
    errors = validate_e9_target(target)
    assert "target_not_owner_provided" in errors
    assert "invented_contact_not_allowed" in errors


def test_e9_target_rejects_unapproved_contact():
    target = E9ValidationTarget("t1", "known_contact", "Peer", "email", "x@example.com", "owner", "relevant", True, False, 1, False)
    assert "target_not_approved_for_contact" in validate_e9_target(target)


def test_e9_target_allows_valid_action():
    target = E9ValidationTarget("t1", "known_contact", "Peer", "email", "x@example.com", "owner", "relevant", True, True, 1, False)
    assert e9_target_allows_action(target, {"target_id": "t1", "channel": "email"})
