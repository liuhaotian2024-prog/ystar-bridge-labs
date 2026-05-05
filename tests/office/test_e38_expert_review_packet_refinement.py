from office.mission_command.e38_expert_review_packet_refinement import build_expert_review_packet_refinement


def test_expert_packet_remains_unsent():
    data = build_expert_review_packet_refinement()
    assert data["message_draft_status"] == "unsent"
    assert data["owner_approval_required_before_any_contact"] is True
    assert data["customer_or_expert_contact_occurred"] is False
    assert "customer validation" in data["do_not_claim_list"]
