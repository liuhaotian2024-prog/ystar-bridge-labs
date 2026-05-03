from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping


def message_hash(message: str) -> str:
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


def build_e15d_draft_only_execution_receipts(
    console: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> Dict[str, Any]:
    decision_by_action = {decision["action_id"]: decision for decision in policy.get("decisions", [])}
    receipts: List[Dict[str, Any]] = []
    for action in console.get("primary_actions", []):
        digest = message_hash(action["message_to_send"])
        decision = decision_by_action.get(action["action_id"], {})
        receipts.append(
            {
                "receipt_id": f"e15d_draft_receipt_{digest[:10]}",
                "action_id": action["action_id"],
                "decision_id": decision.get("decision_id", action.get("decision_id")),
                "ledger_id": action["ledger_id"],
                "feedback_event_id": action["feedback_event_id"],
                "target_id": action["target_id"],
                "message_hash": digest,
                "draft_status": "draft_only_simulated",
                "external_action_executed": False,
                "send_allowed_now": False,
                "owner_authorization_required": True,
                "allowed_local_outputs": ["message_hash", "draft_receipt", "ledger_preview", "feedback_wait_preview"],
                "prohibited_external_outputs": ["real_email_send", "real_message_send", "publication", "form_submission", "login"],
                "reason_codes": ["draft_only_mode", "owner_authorization_required_before_send", "no_external_side_effect"],
            }
        )
    return {
        "receipt_set_id": "e15d_draft_only_execution_receipts",
        "receipts": receipts,
        "external_action_executed": False,
    }


def validate_e15d_draft_only_execution_receipts(receipt_set: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if receipt_set.get("external_action_executed") is not False:
        errors.append("draft_receipts_must_not_execute_external_action")
    if len(receipt_set.get("receipts", [])) != 3:
        errors.append("draft_receipts_must_cover_three_primary_actions")
    for receipt in receipt_set.get("receipts", []):
        if receipt.get("draft_status") != "draft_only_simulated":
            errors.append(f"{receipt.get('action_id')}:invalid_draft_status")
        if receipt.get("external_action_executed") is not False:
            errors.append(f"{receipt.get('action_id')}:external_action_executed")
        if receipt.get("send_allowed_now") is not False:
            errors.append(f"{receipt.get('action_id')}:send_allowed_now")
        if len(str(receipt.get("message_hash", ""))) != 64:
            errors.append(f"{receipt.get('action_id')}:missing_message_hash")
    return list(dict.fromkeys(errors))
