from office.mission_command.e38_public_readonly_permission_envelope import build_public_readonly_permission_envelope


def test_permission_envelope_allows_public_reading_and_forbids_effects():
    data = build_public_readonly_permission_envelope()
    assert data["permission_status"] == "approved_for_public_read_only_execution"
    assert "access public web pages" in data["allowed_actions"]
    for forbidden in ["customer contact", "email/message/send", "publication", "form submission", "login", "provider send API", "payment"]:
        assert forbidden in data["forbidden_actions"]
