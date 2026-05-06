from office.mission_command.e58_owner_review_package import build_owner_review_packet


def test_owner_review_package_does_not_fabricate_approval():
    data = build_owner_review_packet()
    assert data["packet_status"] == "owner_reviewable_only"
    assert data["owner_decision_status"] == "pending_owner_decision"
    assert data["approval_fabricated"] is False
    assert data["external_action_allowed"] is False
    assert data["what_owner_can_approve_now"] == ["continue_internal_E59_external_world_intelligence_L5_convergence"]

