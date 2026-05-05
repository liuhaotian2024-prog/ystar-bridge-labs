from office.mission_command.e40_no_send_message_and_walkthrough import build_no_send_message_drafts, build_five_minute_walkthroughs


def test_no_send_messages_and_walkthroughs_are_prepared_only():
    messages = build_no_send_message_drafts()
    walks = build_five_minute_walkthroughs()
    assert messages["message_draft_status"] == "unsent"
    assert messages["customer_or_expert_contact_occurred"] is False
    assert messages["send_occurred"] is False
    assert walks["status"] == "prepared_only"
    for msg in messages["message_drafts"]:
        assert msg["status"] == "unsent"
        assert msg["no_attachment_no_link_assumption"] is True
