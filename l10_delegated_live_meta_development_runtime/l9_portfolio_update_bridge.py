#!/usr/bin/env python3
"""Create L9 portfolio update packets from L10 mission outputs."""

from __future__ import annotations

from typing import Any

from .mission_model import base_packet, now_iso, write_packet
from .opportunity_signal_extractor import list_opportunity_signals


def build_l9_portfolio_update_packet(mission_id: str) -> dict[str, Any]:
    signals = [item for item in list_opportunity_signals() if item["mission_id"] == mission_id]
    packet = {
        **base_packet("l9_portfolio_update_packet"),
        "packet_id": f"l9_portfolio_update_{mission_id}",
        "mission_id": mission_id,
        "recommended_new_opportunity": signals[0]["signal_title"] if signals else "needs_more_evidence",
        "recommended_money_path_update": [signal["recommended_money_path"] for signal in signals],
        "evidence_basis_update": [ref for signal in signals for ref in signal["evidence_refs"]],
        "ranking_adjustment_suggestion": "Increase weight on fastest feedback and owner leverage until real customer signal exists.",
        "writeback_allowed": False,
        "review_required": True,
        "created_at": now_iso(),
    }
    return write_packet("l9_portfolio_update_packets", packet["packet_id"], packet)


def list_l9_portfolio_update_packets() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("l9_portfolio_update_packets")

