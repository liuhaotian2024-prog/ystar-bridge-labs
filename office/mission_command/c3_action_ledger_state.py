from __future__ import annotations

from typing import Any, Dict, List, Mapping


C3_LEDGER_STATES = [
    "prepared",
    "owner_handoff_ready",
    "owner_sent_unconfirmed",
    "sent_confirmed_by_owner",
    "waiting_feedback",
    "feedback_received",
    "no_response_timeout",
    "suppressed",
    "closed_positive",
    "closed_negative",
    "closed_no_response",
    "requires_offer_revision",
    "requires_governance_review",
]

C3_AUTO_STATES = ["prepared", "owner_handoff_ready", "dry_run_completed", "waiting_owner_action"]


def build_c3_action_ledger_state_template() -> Dict[str, Any]:
    return {
        "states": C3_LEDGER_STATES,
        "auto_states_allowed_in_c3": C3_AUTO_STATES,
        "owner_confirmation_required_for": ["sent_confirmed_by_owner", "waiting_feedback", "feedback_received", "no_response_timeout"],
        "no_fake_sent": True,
        "template": {
            "ledger_id": "REQUIRED",
            "action_id": "REQUIRED",
            "state": "|".join(C3_LEDGER_STATES),
            "owner_confirmation_ref": "",
            "gov_mcp_receipt_ref": "",
            "dry_run_receipt_ref": "",
            "feedback_event_ref": "",
            "transition_reason": "",
        },
    }


def build_c3_action_ledger_state_fixture(batch: Mapping[str, Any], receipts: Mapping[str, Any]) -> Dict[str, Any]:
    receipt_by_action = {receipt["action_id"]: receipt for receipt in receipts.get("receipts", [])}
    rows: List[Dict[str, Any]] = []
    for action in batch.get("actions", []):
        if action.get("role") == "excluded":
            continue
        rows.append(
            {
                "ledger_id": action["ledger_id"],
                "action_id": action["action_id"],
                "state": "owner_handoff_ready",
                "previous_state": "prepared",
                "dry_run_receipt_ref": receipt_by_action.get(action["action_id"], {}).get("receipt_id", ""),
                "owner_confirmation_ref": "",
                "sent_confirmed_by_owner": False,
                "external_action_executed": False,
                "transition_reason": "C3 generated owner-handoff package and dry-run receipt only.",
            }
        )
    return {"fixture_id": "c3_action_ledger_state_fixture", "rows": rows, "external_action_executed": False}


def validate_c3_action_ledger_state_fixture(fixture: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if fixture.get("external_action_executed") is not False:
        errors.append("ledger_fixture_must_not_execute_external_action")
    for row in fixture.get("rows", []):
        if row.get("state") not in C3_AUTO_STATES:
            errors.append(f"{row.get('action_id')}:state_not_allowed_for_c3_auto_transition")
        if row.get("sent_confirmed_by_owner") is not False:
            errors.append(f"{row.get('action_id')}:must_not_fake_owner_sent")
        if row.get("external_action_executed") is not False:
            errors.append(f"{row.get('action_id')}:external_action_executed")
    if len(fixture.get("rows", [])) < 6:
        errors.append("ledger_fixture_must_cover_non_excluded_batch_actions")
    return list(dict.fromkeys(errors))
