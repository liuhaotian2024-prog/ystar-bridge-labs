from office.mission_command.e9_offer_learning import build_e9_offer_learning_update


def test_e9_offer_learning_does_not_recommend_paid_pilot_without_positive_signal():
    update = build_e9_offer_learning_update(pattern_count=14, validation_signal="blocked_no_feedback", execution_status="handoff")
    assert update["recommend_paid_pilot"] is False
