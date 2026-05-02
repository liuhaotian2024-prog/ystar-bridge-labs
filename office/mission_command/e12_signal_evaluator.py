from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from .e12_feedback_capture import E12FeedbackCapture, NEGATIVE_TYPES, POSITIVE_TYPES


@dataclass(frozen=True)
class E12SignalEvaluation:
    classification: str
    positive_event_count: int
    negative_event_count: int
    neutral_event_count: int
    paid_pilot_prep_allowed: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_e12_validation_signal(capture: E12FeedbackCapture, *, execution_attempted: bool = False) -> E12SignalEvaluation:
    if capture.errors and capture.feedback_file_present:
        return E12SignalEvaluation("invalid_feedback", 0, 0, 0, False, "feedback_events_invalid")
    if not capture.feedback_captured:
        return E12SignalEvaluation("blocked_no_execution" if not execution_attempted else "no_feedback_yet", 0, 0, 0, False, "no_valid_feedback_events")
    response_types = [event.response_type for event in capture.events]
    positive = sum(1 for item in response_types if item in POSITIVE_TYPES)
    negative = sum(1 for item in response_types if item in NEGATIVE_TYPES)
    neutral = sum(1 for item in response_types if item in {"neutral", "no_response"})
    if any(item in {"asks_price", "says_would_pay"} for item in response_types) or ("asks_example" in response_types and "offers_workflow" in response_types):
        return E12SignalEvaluation("strong_positive", positive, negative, neutral, True, "price_or_workflow_signal_present")
    if positive and negative:
        return E12SignalEvaluation("mixed", positive, negative, neutral, False, "positive_and_negative_signals_present")
    if positive:
        return E12SignalEvaluation("weak_positive", positive, negative, neutral, False, "interest_without_paid_signal")
    if negative:
        return E12SignalEvaluation("negative", positive, negative, neutral, False, "negative_or_opt_out_signals_present")
    return E12SignalEvaluation("neutral", positive, negative, neutral, False, "neutral_or_no_response_only")


def render_e12_signal_evaluation(evaluation: E12SignalEvaluation) -> str:
    return "\n".join(
        [
            "# E12 Validation Signal Evaluation",
            "",
            f"- classification: {evaluation.classification}",
            f"- positive_event_count: {evaluation.positive_event_count}",
            f"- negative_event_count: {evaluation.negative_event_count}",
            f"- neutral_event_count: {evaluation.neutral_event_count}",
            f"- paid_pilot_prep_allowed: {str(evaluation.paid_pilot_prep_allowed).lower()}",
            f"- reason: {evaluation.reason}",
        ]
    )

