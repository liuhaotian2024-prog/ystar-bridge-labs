#!/usr/bin/env python3
"""Local portfolio feedback packets for L9 opportunity learning."""

from __future__ import annotations

from typing import Any

from .money_path_model import get_money_path
from .opportunity_model import base_packet, load_packets, now_id, now_iso, write_packet


def record_portfolio_feedback(
    money_path_id: str,
    actual_signal: str = "no_signal",
    feedback_summary: str = "Simulated or owner-entered portfolio feedback.",
) -> dict[str, Any]:
    path = get_money_path(money_path_id)
    if not path:
        raise ValueError(f"unknown money path: {money_path_id}")
    feedback_id = f"portfolio_feedback_{now_id()}"
    packet = {
        **base_packet("portfolio_feedback"),
        "feedback_id": feedback_id,
        "opportunity_id": path["opportunity_id"],
        "money_path_id": money_path_id,
        "expected_signal": path["expected_signal"],
        "actual_signal": actual_signal,
        "feedback_summary": feedback_summary,
        "source": "owner_entered_or_local_demo",
        "created_at": now_iso(),
        "external_side_effects": False,
    }
    return write_packet("portfolio_feedback", feedback_id, packet)


def list_portfolio_feedback() -> list[dict[str, Any]]:
    return load_packets("portfolio_feedback")
