#!/usr/bin/env python3
"""Residual analysis for L9 opportunity portfolio feedback."""

from __future__ import annotations

from typing import Any

from .opportunity_model import base_packet, get_packet, latest_packet, load_packets, now_iso, write_packet


def build_portfolio_residual(feedback_id: str | None = None) -> dict[str, Any]:
    feedback = get_packet("portfolio_feedback", feedback_id) if feedback_id else latest_packet("portfolio_feedback")
    if not feedback:
        raise ValueError("portfolio feedback is required before building residual")
    residual_type = _residual_type(str(feedback.get("actual_signal", "unknown")))
    residual_id = f"portfolio_residual_{feedback['feedback_id']}"
    packet = {
        **base_packet("portfolio_residual"),
        "residual_id": residual_id,
        "opportunity_id": feedback["opportunity_id"],
        "money_path_id": feedback["money_path_id"],
        "expected_signal": feedback["expected_signal"],
        "actual_signal": feedback["actual_signal"],
        "residual_type": residual_type,
        "severity": _severity(residual_type),
        "interpretation": _interpretation(residual_type),
        "recommended_portfolio_adjustment": _adjustment(residual_type),
        "created_at": now_iso(),
    }
    return write_packet("portfolio_residuals", residual_id, packet)


def list_portfolio_residuals() -> list[dict[str, Any]]:
    return load_packets("portfolio_residuals")


def _residual_type(signal: str) -> str:
    signal = signal.lower()
    if signal in {"positive_signal", "interested", "asks_for_more_info", "wants_call"}:
        return "positive_signal"
    if signal in {"paid_signal", "pilot_accepted"}:
        return "positive_signal"
    if signal in {"no_response", "no_signal"}:
        return "no_signal"
    if "price" in signal:
        return "pricing_friction"
    if "target" in signal:
        return "target_mismatch"
    if "offer" in signal:
        return "offer_mismatch"
    if "capability" in signal:
        return "capability_gap"
    if "channel" in signal:
        return "channel_mismatch"
    if "heavy" in signal:
        return "execution_too_heavy"
    if "evidence" in signal:
        return "promising_but_needs_evidence"
    return "unknown"


def _severity(residual_type: str) -> str:
    if residual_type in {"positive_signal"}:
        return "low"
    if residual_type in {"no_signal", "pricing_friction", "target_mismatch", "offer_mismatch"}:
        return "medium"
    if residual_type in {"capability_gap", "strategic_misalignment", "execution_too_heavy"}:
        return "high"
    return "medium"


def _interpretation(residual_type: str) -> str:
    return {
        "positive_signal": "The path appears worth advancing through approval-gated commercial action.",
        "no_signal": "The channel, target, or opening may be weak; revise before increasing effort.",
        "pricing_friction": "The value proof or price anchor may need tightening.",
        "target_mismatch": "The buyer profile may be wrong for this path.",
        "offer_mismatch": "The problem may be real but the proposed package is not sharp enough.",
        "capability_gap": "The path may need internal tooling before commercial push.",
        "channel_mismatch": "The path may need a different discovery or trust channel.",
        "execution_too_heavy": "The path may be strategically useful but too costly for first cash.",
        "promising_but_needs_evidence": "Gather controlled read-only evidence before owner action.",
    }.get(residual_type, "The signal is ambiguous and needs owner/team review.")


def _adjustment(residual_type: str) -> str:
    return {
        "positive_signal": "Create next approval packet and prepare delivery readiness.",
        "no_signal": "Revise target segment or opening; keep effort bounded.",
        "pricing_friction": "Add clearer deliverables, proof, and a lower-friction pilot option.",
        "target_mismatch": "Move the path to a better-fit buyer archetype.",
        "offer_mismatch": "Rework the offer promise and expected output.",
        "capability_gap": "Backpropagate the missing tool into the build queue.",
        "channel_mismatch": "Try a warmer/manual channel after owner approval.",
        "execution_too_heavy": "Hold or convert into a lower-scope diagnostic service.",
        "promising_but_needs_evidence": "Create an observation planning packet; do not run uncontrolled search.",
    }.get(residual_type, "Request more evidence or hold the path.")
