from __future__ import annotations

from typing import Dict, List

from .e8_feedback_capture import E8FeedbackEvent


POSITIVE = {"interested", "asks_price", "asks_example", "offers_workflow", "asks_followup", "referral"}
NEGATIVE = {"rejects_no_urgency", "rejects_price", "says_tools_solve_it", "wants_implementation_not_blueprint", "opt_out"}


def classify_validation_signal(events: List[E8FeedbackEvent]) -> str:
    if not events:
        return "blocked_no_feedback"
    positives = sum(1 for event in events if event.response_type in POSITIVE)
    negatives = sum(1 for event in events if event.response_type in NEGATIVE)
    if positives and not negatives:
        return "strong_positive" if positives >= 2 else "weak_positive"
    if negatives and not positives:
        return "negative"
    if positives and negatives:
        return "mixed"
    return "neutral"


def render_e8_validation_signal_evaluation(events: List[E8FeedbackEvent]) -> str:
    signal = classify_validation_signal(events)
    lines = ["# E8 Validation Signal Evaluation", "", f"- validation_signal_classification: {signal}", f"- feedback_event_count: {len(events)}"]
    if signal == "blocked_no_feedback":
        lines.append("- interpretation: no feedback exists; do not claim market validation.")
    elif signal in {"strong_positive", "weak_positive"}:
        lines.append("- interpretation: positive signal exists; consider E9 paid pilot prep, not payment collection.")
    elif signal == "negative":
        lines.append("- interpretation: revise offer, segment, or channel.")
    else:
        lines.append("- interpretation: collect more feedback or revise scope.")
    return "\n".join(lines)
