#!/usr/bin/env python3
"""Commercial residual analysis from customer feedback."""

from __future__ import annotations

from typing import Any

from .commercial_action_queue import get_action
from .first_cash_path_loader import initialize_first_cash_path
from .first_cash_path_model import base_packet, get_packet, load_packets, now_id, now_iso, write_packet


RESIDUAL_MAP = {
    "no_response": ("weak_signal_or_channel_mismatch", "medium", "Revise target segment or message opening."),
    "interested": ("offer_specificity_gap", "low", "Clarify deliverables, timeline, sample output, and price."),
    "asks_for_more_info": ("offer_specificity_gap", "medium", "Provide clearer deliverable examples and credibility boundary."),
    "wants_call": ("positive_signal", "low", "Prepare owner-approved conversation packet and scope boundaries."),
    "paid_signal": ("positive_signal", "low", "Prepare paid pilot delivery runtime and payment/contract approval path."),
    "pilot_accepted": ("pilot_acceptance", "low", "Prepare paid delivery runtime and post-approval execution plan."),
    "not_interested": ("irrelevant_target", "medium", "Tighten target selection and pain trigger."),
    "rejected": ("pricing_friction", "medium", "Review price, trust gap, and offer clarity."),
}


def build_commercial_residual(feedback_id: str) -> dict[str, Any]:
    feedback = get_packet("customer_feedback", feedback_id)
    if not feedback:
        raise ValueError(f"Unknown customer feedback: {feedback_id}")
    cash_path = initialize_first_cash_path()
    action = get_action(feedback["action_id"])
    residual_type, severity, adjustment = RESIDUAL_MAP.get(feedback["response_status"], ("unknown", "medium", "Review feedback manually."))
    residual_id = f"residual_{feedback_id}_{now_id()}"
    residual = {
        **base_packet("commercial_residual"),
        "residual_id": residual_id,
        "cash_path_id": cash_path["cash_path_id"],
        "action_id": action["action_id"],
        "source_feedback_id": feedback_id,
        "expected_signal": "Founder/operator urgently wants an audit and may accept a paid diagnostic pilot.",
        "actual_signal": feedback["response_status"],
        "residual_type": residual_type,
        "severity": severity,
        "interpretation": _interpretation(feedback["response_status"], action["action_type"]),
        "recommended_adjustment": adjustment,
        "created_at": now_iso(),
    }
    return write_packet("commercial_residuals", residual_id, residual)


def _interpretation(response_status: str, action_type: str) -> str:
    if response_status in {"paid_signal", "pilot_accepted"}:
        return "The first cash path has a positive commercial signal; prepare paid delivery with approval gates."
    if response_status == "no_response":
        return f"The {action_type} channel/message did not produce a visible signal yet."
    if response_status in {"interested", "asks_for_more_info", "wants_call"}:
        return "The offer has some pull, but the value, trust proof, or next step needs clarification."
    return "The target/message/price may not fit; use the signal to refine the path."


def list_commercial_residuals() -> list[dict[str, Any]]:
    return load_packets("commercial_residuals")

