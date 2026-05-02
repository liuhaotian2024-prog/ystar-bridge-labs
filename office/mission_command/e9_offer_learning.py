from __future__ import annotations

from typing import Any, Dict, List


def build_e9_offer_learning_update(
    *,
    pattern_count: int,
    validation_signal: str,
    execution_status: str,
    top_offer: str = "48h AI Ops Operating Room Blueprint",
) -> Dict[str, Any]:
    positive = validation_signal in {"strong_positive", "weak_positive"}
    return {
        "top_offer": top_offer,
        "pattern_count": pattern_count,
        "external_patterns_changed_design": [
            "NIST/ISO patterns made risk controls lifecycle-based rather than one-off gates.",
            "MCP patterns strengthened consent, scope minimization, and anti-confused-deputy boundaries.",
            "HITL patterns added approve/edit/reject/hold/escalate as first-class decisions.",
            "FTC/CRM patterns added opt-out suppression and truthful identity requirements.",
            "YC discovery patterns kept validation small-batch and feedback-centered.",
        ],
        "validation_execution_status": execution_status,
        "validation_signal": validation_signal,
        "top_offer_remains_valid": True,
        "recommend_paid_pilot": positive,
        "recommended_e10": "prepare_paid_pilot_only_after_positive_signal" if positive else "provide_E9_manifest_targets_and_provider_or_owner_feedback",
    }


def render_e9_offer_learning_update(update: Dict[str, Any]) -> str:
    lines = [
        "# E9 Offer Learning Update",
        "",
        f"- top_offer: {update['top_offer']}",
        f"- pattern_count: {update['pattern_count']}",
        f"- validation_execution_status: {update['validation_execution_status']}",
        f"- validation_signal: {update['validation_signal']}",
        f"- top_offer_remains_valid: {update['top_offer_remains_valid']}",
        f"- recommend_paid_pilot: {update['recommend_paid_pilot']}",
        f"- recommended_E10: {update['recommended_e10']}",
        "",
        "## What External Patterns Changed",
    ]
    lines.extend(f"- {item}" for item in update["external_patterns_changed_design"])
    return "\n".join(lines)
