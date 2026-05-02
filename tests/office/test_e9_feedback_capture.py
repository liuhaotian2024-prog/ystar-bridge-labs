from office.mission_command.e9_feedback_capture import E9FeedbackEvent, validate_e9_feedback_event


def test_e9_feedback_capture_does_not_invent_feedback():
    assert validate_e9_feedback_event(E9FeedbackEvent("", "", "", "", "", "")) == ["missing_feedback_id", "missing_target_id", "missing_response_type"]


def test_e9_feedback_capture_allows_owner_entered_feedback():
    event = E9FeedbackEvent("f1", "t1", "2026-05-01T00:00:00Z", "email", "asks_price", "Asked price", owner_entered=True)
    assert validate_e9_feedback_event(event) == []
