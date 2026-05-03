from __future__ import annotations

from typing import Any, Dict, List, Mapping

from office.mission_command.e15d_outbound_safety_guards import evaluate_e15d_guard_results


def build_e15d_outbound_audit_receipts(
    queue: Mapping[str, Any],
    envelope: Mapping[str, Any],
    guard_matrix: Mapping[str, Any],
) -> Dict[str, Any]:
    receipts: List[Dict[str, Any]] = []
    for row in queue.get("rows", []):
        guard = evaluate_e15d_guard_results(row, envelope, guard_matrix)
        receipts.append(
            {
                "receipt_id": f"e15d_audit_receipt_{row['action_id']}",
                "action_id": row["action_id"],
                "execution_mode": row["mcp_execution_mode"],
                "preflight_result": guard["preflight_result"],
                "guard_results": guard["guard_results"],
                "execution_status": "blocked_pending_authorization" if row.get("blocked_until_authorized") else "ready",
                "external_action_executed": False,
                "ledger_transition": "waiting_owner_send -> send_gated_pending_authorization",
                "feedback_wait_state": row.get("feedback_wait_state"),
                "czl_fields": {
                    "Y*": "No outbound execution until envelope is active and all guards pass.",
                    "Xt": f"action={row['action_id']}, envelope_status={envelope.get('status')}",
                    "U": "draft-only receipt plus send-gated audit receipt",
                    "Yt+1": "blocked_pending_authorization",
                    "Rt+1": 1,
                },
                "deterministic_reason_codes": ["authorization_required", "envelope_not_active", "no_external_action_executed"],
            }
        )
    return {
        "receipt_set_id": "e15d_outbound_audit_receipts",
        "receipts": receipts,
        "external_action_executed": False,
    }


def validate_e15d_outbound_audit_receipts(receipt_set: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if receipt_set.get("external_action_executed") is not False:
        errors.append("audit_receipts_must_not_execute_external_action")
    if len(receipt_set.get("receipts", [])) != 3:
        errors.append("audit_receipts_must_cover_three_primary_actions")
    for receipt in receipt_set.get("receipts", []):
        if receipt.get("external_action_executed") is not False:
            errors.append(f"{receipt.get('action_id')}:external_action_executed")
        if receipt.get("execution_status") != "blocked_pending_authorization":
            errors.append(f"{receipt.get('action_id')}:must_be_blocked_pending_authorization")
        if "envelope_not_active" not in receipt.get("deterministic_reason_codes", []):
            errors.append(f"{receipt.get('action_id')}:missing_envelope_reason")
        if "czl_fields" not in receipt:
            errors.append(f"{receipt.get('action_id')}:missing_czl_fields")
    return list(dict.fromkeys(errors))
