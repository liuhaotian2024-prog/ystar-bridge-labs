from office.mission_command.e37_expert_review_route_packet import build_expert_review_route_packet


def test_expert_review_packet_is_unsent_and_bounded():
    data = build_expert_review_route_packet()
    assert data["route_status"] == "prepared_unsent"
    assert data["message_draft_status"] == "unsent"
    assert data["customer_contact_occurred"] is False
    assert data["message_sent"] is False
    assert "customer validation" in data["do_not_claim_list"]
    assert data["reviewer_feedback_would_not_prove"]
