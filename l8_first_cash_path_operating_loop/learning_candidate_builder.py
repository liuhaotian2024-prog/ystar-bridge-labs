#!/usr/bin/env python3
"""Review-gated learning candidates from commercial residuals."""

from __future__ import annotations

from typing import Any

from .first_cash_path_model import base_packet, get_packet, load_packets, now_id, now_iso, write_packet


TARGET_BY_RESIDUAL = {
    "weak_signal_or_channel_mismatch": "customer segment and outreach opening",
    "offer_specificity_gap": "offer positioning and deliverable clarity",
    "pricing_friction": "pricing hypothesis",
    "credibility_gap": "risk boundary and proof package",
    "positive_signal": "delivery workflow",
    "pilot_acceptance": "paid pilot delivery playbook",
    "irrelevant_target": "target customer profile",
    "unknown": "team playbook",
}


def build_learning_candidate(residual_id: str) -> dict[str, Any]:
    residual = get_packet("commercial_residuals", residual_id)
    if not residual:
        raise ValueError(f"Unknown commercial residual: {residual_id}")
    feedback = get_packet("customer_feedback", residual["source_feedback_id"]) or {}
    target_area = TARGET_BY_RESIDUAL.get(residual["residual_type"], "team playbook")
    candidate_id = f"learning_candidate_{residual_id}_{now_id()}"
    candidate = {
        **base_packet("learning_candidate"),
        "candidate_id": candidate_id,
        "source_feedback_id": residual["source_feedback_id"],
        "source_residual_id": residual_id,
        "proposed_update_type": residual["residual_type"],
        "proposed_update_summary": residual["recommended_adjustment"],
        "target_area": target_area,
        "writeback_allowed": False,
        "review_required": True,
        "owner_review_status": "pending_review",
        "feedback_status": feedback.get("response_status", "unknown"),
        "created_at": now_iso(),
        "forbidden_writeback_targets": ["brain", "memory", "canonical strategy", "CIEU DB", "Y-star-gov", "gov-mcp"],
    }
    return write_packet("learning_candidates", candidate_id, candidate)


def list_learning_candidates() -> list[dict[str, Any]]:
    return load_packets("learning_candidates")

