from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e40_czl_closure_shape_and_flags():
    closure = get_artifact("e40_czl_closure")
    assert closure["expert_review_preflight_packet_created"] is True
    assert closure["evidence_briefs_created"] is True
    assert closure["question_bank_created"] is True
    assert closure["no_send_message_drafts_created"] is True
    assert closure["provider_API_or_tool_execution_occurred"] is False
    assert closure["external_integration_occurred"] is False
    assert closure["customer_contact_occurred"] is False
    assert closure["expert_contact_occurred"] is False
    assert closure["send_occurred"] is False
    assert closure["customer_validation_claimed"] is False
    assert closure["paid_signal_claimed"] is False
