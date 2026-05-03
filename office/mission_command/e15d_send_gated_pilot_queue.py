from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping

from office.mission_command.e15d_gov_mcp_outbound_adapter import mode_for_e15d_policy_decision


def _idempotency_key(action_id: str, message_hash: str, envelope_id: str) -> str:
    return hashlib.sha256(f"{action_id}:{message_hash}:{envelope_id}".encode("utf-8")).hexdigest()


def build_e15d_send_gated_pilot_queue(
    console: Mapping[str, Any],
    envelope: Mapping[str, Any],
    policy: Mapping[str, Any],
    draft_receipts: Mapping[str, Any],
    guard_matrix: Mapping[str, Any],
) -> Dict[str, Any]:
    decision_by_action = {decision["action_id"]: decision for decision in policy.get("decisions", [])}
    receipt_by_action = {receipt["action_id"]: receipt for receipt in draft_receipts.get("receipts", [])}
    rows: List[Dict[str, Any]] = []
    for action in console.get("primary_actions", []):
        decision = decision_by_action.get(action["action_id"], {})
        receipt = receipt_by_action.get(action["action_id"], {})
        message_hash = receipt.get("message_hash", "")
        rows.append(
            {
                "queue_id": "e15d_send_gated_pilot_queue",
                "batch_id": console.get("source_c3_batch_id"),
                "action_id": action["action_id"],
                "target_id": action["target_id"],
                "policy_decision": decision.get("decision"),
                "mcp_execution_mode": mode_for_e15d_policy_decision(decision),
                "authorization_required": True,
                "idempotency_key": _idempotency_key(action["action_id"], message_hash, str(envelope.get("envelope_id"))),
                "rate_limit_group": "e15d_day_1_max_1_action",
                "suppression_check": "required_before_send",
                "kill_switch_check": "required_before_send",
                "ledger_state_before_send": "waiting_owner_send",
                "feedback_wait_state": "pending_valid_send_receipt",
                "message_hash": message_hash,
                "blocked_until_authorized": True,
                "external_action_executed": False,
            }
        )
    return {
        "queue_id": "e15d_send_gated_pilot_queue",
        "source_console_id": console.get("console_id"),
        "rows": rows,
        "guard_matrix_id": guard_matrix.get("guard_matrix_id"),
        "blocked_until_authorized": True,
        "external_action_executed": False,
    }


def validate_e15d_send_gated_pilot_queue(queue: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if queue.get("blocked_until_authorized") is not True:
        errors.append("queue_must_be_blocked_until_authorized")
    if queue.get("external_action_executed") is not False:
        errors.append("queue_must_not_execute_external_action")
    if len(queue.get("rows", [])) != 3:
        errors.append("queue_must_cover_three_primary_actions")
    for row in queue.get("rows", []):
        if row.get("authorization_required") is not True:
            errors.append(f"{row.get('action_id')}:authorization_required_missing")
        if row.get("blocked_until_authorized") is not True:
            errors.append(f"{row.get('action_id')}:must_be_blocked_until_authorized")
        if not row.get("idempotency_key") or len(str(row.get("idempotency_key"))) != 64:
            errors.append(f"{row.get('action_id')}:invalid_idempotency_key")
        if row.get("external_action_executed") is not False:
            errors.append(f"{row.get('action_id')}:external_action_executed")
    return list(dict.fromkeys(errors))
