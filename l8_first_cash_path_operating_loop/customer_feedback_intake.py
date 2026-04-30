#!/usr/bin/env python3
"""Owner-entered customer feedback intake for L8."""

from __future__ import annotations

from typing import Any

from .first_cash_path_model import base_packet, load_packets, now_id, now_iso, write_packet
from .manual_send_packet import get_manual_send_packet


RESPONSE_STATUSES = {
    "no_response",
    "interested",
    "not_interested",
    "asks_for_more_info",
    "wants_call",
    "paid_signal",
    "pilot_accepted",
    "rejected",
}


def record_customer_feedback(
    manual_send_packet_id: str,
    response_status: str,
    feedback_text: str = "",
    paid_signal: bool | None = None,
    objection_type: str = "unknown",
    next_step_requested: str = "",
) -> dict[str, Any]:
    if response_status not in RESPONSE_STATUSES:
        raise ValueError(f"Unsupported response status: {response_status}")
    packet = get_manual_send_packet(manual_send_packet_id)
    feedback_id = f"feedback_{manual_send_packet_id}_{now_id()}"
    paid = paid_signal if paid_signal is not None else response_status in {"paid_signal", "pilot_accepted"}
    feedback = {
        **base_packet("customer_feedback_packet"),
        "feedback_id": feedback_id,
        "action_id": packet["action_id"],
        "manual_send_packet_id": manual_send_packet_id,
        "response_status": response_status,
        "feedback_text": feedback_text,
        "paid_signal": bool(paid),
        "objection_type": objection_type,
        "next_step_requested": next_step_requested,
        "created_at": now_iso(),
    }
    return write_packet("customer_feedback", feedback_id, feedback)


def list_customer_feedback() -> list[dict[str, Any]]:
    return load_packets("customer_feedback")

