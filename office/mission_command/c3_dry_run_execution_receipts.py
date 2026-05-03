from __future__ import annotations

from typing import Any, Dict, List, Mapping


def build_c3_dry_run_receipts(batch: Mapping[str, Any], replay_report: Mapping[str, Any]) -> Dict[str, Any]:
    replay_by_action = {record["action_id"]: record for record in replay_report.get("records", [])}
    receipts: List[Dict[str, Any]] = []
    for action in batch.get("actions", []):
        if action.get("role") == "excluded":
            continue
        replay = replay_by_action.get(action["action_id"], {})
        receipts.append(
            {
                "receipt_id": f"dry_run_receipt_{action['action_id']}",
                "action_id": action["action_id"],
                "decision_id": replay.get("replay_decision_id", action.get("ygov_decision_id")),
                "mcp_execution_mode": replay.get("gov_mcp_execution_mode", action.get("gov_mcp_execution_mode")),
                "dry_run_status": "completed_control_plane_only",
                "external_action_executed": False,
                "allowed_local_outputs": [
                    "message_capsule_prepared",
                    "owner_handoff_packet_prepared",
                    "ledger_transition_preview_prepared",
                    "feedback_wait_state_prepared",
                ],
                "prohibited_external_outputs": [
                    "email_message_sent",
                    "publication",
                    "form_submission",
                    "login",
                    "payment",
                    "account_creation",
                ],
                "ledger_transition_preview": "prepared -> owner_handoff_ready -> waiting_owner_action",
                "feedback_wait_state": "feedback_waiting_only_after_valid_owner_confirmed_send",
                "generated_at": "deterministic_c3_generation",
                "reason_codes": replay.get("deterministic_reason_codes", ["dry_run_local"]),
            }
        )
    return {"receipt_set_id": "c3_dry_run_execution_receipts", "external_action_executed": False, "receipts": receipts}


def validate_c3_dry_run_receipts(receipt_set: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if receipt_set.get("external_action_executed") is not False:
        errors.append("receipt_set_must_not_execute_external_action")
    if len(receipt_set.get("receipts", [])) < 6:
        errors.append("dry_run_receipts_must_cover_non_excluded_batch_actions")
    for receipt in receipt_set.get("receipts", []):
        if receipt.get("external_action_executed") is not False:
            errors.append(f"{receipt.get('action_id')}:external_action_executed")
        for key in ["action_id", "decision_id", "mcp_execution_mode", "dry_run_status", "ledger_transition_preview", "feedback_wait_state", "reason_codes"]:
            if not receipt.get(key):
                errors.append(f"{receipt.get('action_id', 'unknown')}:missing_{key}")
        if "email_message_sent" not in receipt.get("prohibited_external_outputs", []):
            errors.append(f"{receipt.get('action_id')}:missing_email_prohibition")
    return list(dict.fromkeys(errors))
