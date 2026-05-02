from office.mission_command.e8_feedback_capture import E8FeedbackEvent
from office.mission_command.e8_validation_signal_evaluator import classify_validation_signal


def _event(response_type):
    return E8FeedbackEvent("f1", "t1", "2026-05-01T00:00:00Z", "email", response_type, "summary", "", "", "", "", "", True, "a1")


def test_validation_signal_detects_asks_price_positive():
    assert classify_validation_signal([_event("asks_price")]) == "weak_positive"


def test_validation_signal_detects_tools_solve_it_negative():
    assert classify_validation_signal([_event("says_tools_solve_it")]) == "negative"


def test_validation_signal_reports_no_feedback_as_blocked():
    assert classify_validation_signal([]) == "blocked_no_feedback"
