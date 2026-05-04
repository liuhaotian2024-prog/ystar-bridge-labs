from __future__ import annotations

from typing import Any, Dict


def build_commercial_kpi_packet(batch: Dict[str, Any], tracker: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
    rows = tracker.get("rows", [])
    blocked = int(batch.get("blocked_or_not_ready_count", 0))
    ready = int(batch.get("ready_for_owner_review_count", 0))
    return {
        "artifact_id": "e18_commercial_kpi_packet",
        "batch_id": batch["batch_id"],
        "target_count": int(batch.get("candidate_count", 0)),
        "ready_target_count": ready,
        "blocked_target_count": blocked,
        "approved_count_placeholder": 0,
        "sent_count_placeholder": 0,
        "response_count_placeholder": 0,
        "positive_signal_count_placeholder": 0,
        "meeting_request_count_placeholder": 0,
        "paid_signal_count_placeholder": 0,
        "suppression_count_placeholder": 0,
        "next_decision_threshold": {
            "commercial_acceleration_candidate": "at least one meeting request, pricing question, or positive interest imported with provenance",
            "offer_revision": "no response after wait window or objection/clarification pattern",
            "target_expansion": "less than two ready targets or invalid/bounce feedback",
            "suppression": "any do-not-contact or safety/trust concern",
        },
        "manual_send_rows": len(rows),
        "no_fake_data_policy": "All sent/response/paid-signal counts remain placeholders until owner imports evidence.",
        "external_action_executed": False,
    }


def render_commercial_kpi_packet(packet: Dict[str, Any]) -> str:
    lines = [
        "# E18 Commercial KPI Packet",
        "",
        f"- target_count: {packet['target_count']}",
        f"- ready_target_count: {packet['ready_target_count']}",
        f"- blocked_target_count: {packet['blocked_target_count']}",
        f"- approved_count_placeholder: {packet['approved_count_placeholder']}",
        f"- sent_count_placeholder: {packet['sent_count_placeholder']}",
        f"- response_count_placeholder: {packet['response_count_placeholder']}",
        f"- paid_signal_count_placeholder: {packet['paid_signal_count_placeholder']}",
        f"- no_fake_data_policy: {packet['no_fake_data_policy']}",
        "- external_action_executed: false",
        "",
        "## Next Decision Thresholds",
    ]
    for key, value in packet["next_decision_threshold"].items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines).rstrip() + "\n"
