from office.mission_command.e53_owner_review_packet_builder import build_owner_review_packet

def test_owner_review_packet_plain_chinese_pending():
    packet = build_owner_review_packet()
    assert packet["owner_decision_status"] == "pending_owner_decision"
    assert packet["external_action_allowed"] is False
    assert packet["real_reviewer_identified"] is False
    assert "发送" in packet["recommended_decision"]
