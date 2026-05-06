from office.mission_command.e52_first_user_review_packet_builder import build_first_user_review_packet


def test_e52_first_user_review_packet_has_no_contacts_or_outreach():
    data = build_first_user_review_packet()
    assert data['contains_real_names'] is False
    assert data['contains_emails'] is False
    assert data['outreach_sent'] is False
    assert data['owner_approval_required'] is True
