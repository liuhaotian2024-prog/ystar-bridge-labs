from office.mission_command.e9_feedback_capture import E9FeedbackEvent
from office.mission_command.e9_signal_evaluator import classify_e9_validation_signal


def test_e9_signal_strong_positive_on_asks_price_or_offers_workflow():
    events = [
        E9FeedbackEvent("f1", "t1", "", "email", "asks_price", ""),
        E9FeedbackEvent("f2", "t2", "", "email", "offers_workflow", ""),
    ]
    assert classify_e9_validation_signal(events) == "strong_positive"


def test_e9_signal_negative_on_tools_solve_it_or_rejects_no_urgency():
    events = [E9FeedbackEvent("f1", "t1", "", "email", "says_tools_solve_it", "")]
    assert classify_e9_validation_signal(events) == "negative"
