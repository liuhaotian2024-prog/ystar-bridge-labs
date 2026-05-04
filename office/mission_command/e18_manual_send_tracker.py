from __future__ import annotations

from typing import Any, Dict, List


E18_TRACKER_STATES = [
    "not_approved",
    "approved_not_sent",
    "manually_sent_by_owner",
    "response_imported",
    "no_response_yet",
    "followup_blocked",
    "followup_allowed",
    "meeting_requested",
    "paid_signal_detected",
    "suppress",
    "closed_no_signal",
]


def build_manual_send_tracker(batch: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for candidate in batch.get("candidates", []):
        rows.append(
            {
                "action_id": candidate["action_id"],
                "target_id": candidate["target_id"],
                "target_name": candidate["target_name"],
                "ledger_id": candidate["ledger_id"],
                "feedback_event_id": candidate["feedback_event_id"],
                "current_state": "not_approved",
                "allowed_states": E18_TRACKER_STATES,
                "manual_send_claimed": False,
                "owner_approval_present": False,
                "followup_state": "followup_blocked",
                "real_send_receipt_present": False,
                "external_action_executed": False,
            }
        )
    return {
        "artifact_id": "e18_manual_send_tracker",
        "batch_id": batch["batch_id"],
        "tracker_policy": "no_send_tracking_board_does_not_claim_owner_sent",
        "states": E18_TRACKER_STATES,
        "rows": rows,
        "sent_count_placeholder": 0,
        "external_action_executed": False,
    }


def render_manual_send_tracker(tracker: Dict[str, Any]) -> str:
    lines = [
        "# E18 Manual Send Tracker",
        "",
        f"- batch_id: {tracker['batch_id']}",
        f"- tracker_policy: {tracker['tracker_policy']}",
        f"- sent_count_placeholder: {tracker['sent_count_placeholder']}",
        "- external_action_executed: false",
        "",
        "| target | state | manual_send_claimed | followup_state |",
        "| --- | --- | --- | --- |",
    ]
    for row in tracker["rows"]:
        lines.append(f"| {row['target_name']} | {row['current_state']} | {str(row['manual_send_claimed']).lower()} | {row['followup_state']} |")
    return "\n".join(lines).rstrip() + "\n"
