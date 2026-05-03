from __future__ import annotations

from typing import Any, Mapping


def evaluate_c1_signal(
    *,
    envelope_present: bool,
    y_gov_decision: str = "",
    gov_mcp_decision: str = "",
    action_executed: bool = False,
    feedback_event: Mapping[str, Any] | None = None,
) -> str:
    if not envelope_present:
        return "blocked_no_envelope"
    if y_gov_decision in {"deny", "denied"}:
        return "denied_by_Y_gov"
    if gov_mcp_decision in {"deny", "denied"}:
        return "denied_by_gov_mcp"
    if not action_executed:
        return "approved_not_executed"
    if not feedback_event:
        return "executed_no_feedback_yet"
    feedback_type = str(feedback_event.get("feedback_type", ""))
    if feedback_event.get("feedback_source") == "public_evidence":
        return "invalid_feedback"
    if feedback_type == "no_response_after_valid_action":
        return "no_response_after_valid_action"
    if feedback_type in {"asks_price"} or feedback_event.get("paid_signal_candidate") is True:
        return "paid_signal_candidate"
    if feedback_type in {"asks_followup", "describes_buyer_pain"} and feedback_event.get("budget"):
        return "strong_positive"
    if feedback_type in {"interested", "asks_followup", "describes_buyer_pain"}:
        return "weak_positive"
    if feedback_type in {"rejects_no_urgency", "rejects_price", "opt_out", "complaint"}:
        return "negative"
    return "invalid_feedback"
