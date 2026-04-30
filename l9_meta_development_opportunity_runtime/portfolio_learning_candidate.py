#!/usr/bin/env python3
"""Review-gated portfolio learning candidates for L9."""

from __future__ import annotations

from typing import Any

from .opportunity_model import base_packet, get_packet, latest_packet, load_packets, now_iso, write_packet


def build_portfolio_learning_candidate(residual_id: str | None = None) -> dict[str, Any]:
    residual = get_packet("portfolio_residuals", residual_id) if residual_id else latest_packet("portfolio_residuals")
    if not residual:
        raise ValueError("portfolio residual is required before building learning candidate")
    candidate_id = f"portfolio_learning_{residual['residual_id']}"
    packet = {
        **base_packet("portfolio_learning_candidate"),
        "candidate_id": candidate_id,
        "source_opportunity_id": residual["opportunity_id"],
        "source_money_path_id": residual["money_path_id"],
        "source_residual_id": residual["residual_id"],
        "proposed_update_type": _update_type(residual["residual_type"]),
        "proposed_update_summary": residual["recommended_portfolio_adjustment"],
        "target_area": _target_area(residual["residual_type"]),
        "writeback_allowed": False,
        "review_required": True,
        "owner_review_status": "pending_review",
        "created_at": now_iso(),
        "core_writeback": False,
    }
    return write_packet("portfolio_learning_candidates", candidate_id, packet)


def list_portfolio_learning_candidates() -> list[dict[str, Any]]:
    return load_packets("portfolio_learning_candidates")


def _update_type(residual_type: str) -> str:
    if residual_type in {"target_mismatch", "channel_mismatch"}:
        return "customer_segment_or_channel_update"
    if residual_type in {"pricing_friction"}:
        return "pricing_hypothesis_update"
    if residual_type in {"offer_mismatch", "no_signal"}:
        return "offer_positioning_update"
    if residual_type == "capability_gap":
        return "tool_gap_update"
    if residual_type == "positive_signal":
        return "portfolio_priority_increase"
    return "portfolio_review_note"


def _target_area(residual_type: str) -> str:
    if residual_type == "capability_gap":
        return "toolmaking_backlog"
    if residual_type == "positive_signal":
        return "opportunity_portfolio_priority"
    return "commercial_portfolio_playbook"
