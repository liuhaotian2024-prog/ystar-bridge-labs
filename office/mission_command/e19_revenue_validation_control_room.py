from __future__ import annotations

from typing import Any, Dict, List


def build_revenue_validation_control_room(
    e18_batch: Dict[str, Any],
    e18_scores: Dict[str, Any],
    e18_console: Dict[str, Any],
    e18_tracker: Dict[str, Any],
    e18_kpi: Dict[str, Any],
    e18_route: Dict[str, Any],
    alignment_scan: Dict[str, Any],
    drift_register: Dict[str, Any],
) -> Dict[str, Any]:
    score_by_action = {item["action_id"]: item for item in e18_scores.get("scores", [])}
    tracker_by_action = {item["action_id"]: item for item in e18_tracker.get("rows", [])}
    console_by_action = {item["action_id"]: item for item in e18_console.get("candidates", [])}
    candidates: List[Dict[str, Any]] = []
    for candidate in e18_batch.get("candidates", []):
        action_id = candidate["action_id"]
        score = score_by_action.get(action_id, {})
        tracker = tracker_by_action.get(action_id, {})
        console = console_by_action.get(action_id, {})
        candidates.append(
            {
                "action_id": action_id,
                "target_name": candidate["target_name"],
                "target_readiness": candidate["status"],
                "offer_variant": score.get("recommended_message_variant_id", console.get("recommended_message_variant_id")),
                "manual_send_state": tracker.get("current_state", "not_approved"),
                "feedback_import_state": "not_imported",
                "kpi_state": "placeholder_no_fake_data",
                "per_target_next_action": "owner_review_candidate" if candidate["status"] == "ready_for_owner_review" else "evidence_or_suppression_review",
                "risk_tier": candidate["risk_tier"],
            }
        )
    return {
        "artifact_id": "e19_revenue_validation_control_room",
        "control_room_type": "single_owner_revenue_validation_surface",
        "batch_id": e18_batch["batch_id"],
        "batch_level_route_recommendation": e18_route["recommended_route"],
        "ecosystem_alignment_state": alignment_scan["alignment_status"],
        "kpi_state": {
            "target_count": e18_kpi["target_count"],
            "ready_target_count": e18_kpi["ready_target_count"],
            "sent_count_placeholder": e18_kpi["sent_count_placeholder"],
            "response_count_placeholder": e18_kpi["response_count_placeholder"],
            "paid_signal_count_placeholder": e18_kpi["paid_signal_count_placeholder"],
        },
        "blockers": drift_register["blockers"],
        "owner_decision_options": [
            "approve_manual_send_for_candidate",
            "revise_message",
            "reject_candidate",
            "request_more_evidence",
            "import_feedback",
            "suppress_candidate",
            "defer_batch",
            "prepare_provider_adapter_plan",
            "keep_real_provider_send_blocked",
        ],
        "candidates": candidates,
        "external_action_executed": False,
    }


def render_revenue_validation_control_room(control_room: Dict[str, Any]) -> str:
    lines = [
        "# E19 Revenue Validation Control Room",
        "",
        "This is the single owner-facing control room for the revenue validation batch. It does not send anything.",
        "",
        f"- batch_id: {control_room['batch_id']}",
        f"- batch_level_route_recommendation: {control_room['batch_level_route_recommendation']}",
        f"- ecosystem_alignment_state: {control_room['ecosystem_alignment_state']}",
        "- external_action_executed: false",
        "",
        "## KPI State",
    ]
    for key, value in control_room["kpi_state"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Owner Decisions"])
    lines.extend(f"- {item}" for item in control_room["owner_decision_options"])
    lines.extend(["", "## Candidates"])
    for item in control_room["candidates"]:
        lines.extend(
            [
                f"### {item['target_name']}",
                f"- action_id: {item['action_id']}",
                f"- target_readiness: {item['target_readiness']}",
                f"- offer_variant: {item['offer_variant']}",
                f"- manual_send_state: {item['manual_send_state']}",
                f"- feedback_import_state: {item['feedback_import_state']}",
                f"- per_target_next_action: {item['per_target_next_action']}",
                "",
            ]
        )
    lines.append("## Blockers")
    lines.extend(f"- {item['blocker_id']}: {item['summary']}" for item in control_room["blockers"])
    return "\n".join(lines).rstrip() + "\n"
