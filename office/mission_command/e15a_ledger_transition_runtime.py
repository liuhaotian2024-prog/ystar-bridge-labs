from __future__ import annotations

from typing import Any, Dict, List, Mapping


E15A_LEDGER_TRANSITIONS = [
    "owner_handoff_ready -> waiting_owner_send",
    "waiting_owner_send -> sent_confirmed_by_owner",
    "waiting_owner_send -> skipped_by_owner",
    "waiting_owner_send -> replaced_by_fallback",
    "sent_confirmed_by_owner -> waiting_feedback",
    "waiting_feedback -> feedback_received",
    "waiting_feedback -> no_response_timeout",
    "feedback_received -> closed_positive",
    "feedback_received -> closed_negative",
    "feedback_received -> requires_offer_revision",
    "feedback_received -> requires_governance_review",
]

E15A_AUTO_STATES = ["waiting_owner_send", "awaiting_owner_confirmation"]


def build_e15a_ledger_transition_template() -> Dict[str, Any]:
    return {
        "template_id": "e15a_ledger_transition_template",
        "transitions": E15A_LEDGER_TRANSITIONS,
        "auto_states_allowed_in_e15a": E15A_AUTO_STATES,
        "owner_confirmation_required_for": ["sent_confirmed_by_owner", "waiting_feedback", "feedback_received", "no_response_timeout"],
        "no_fake_sent": True,
        "fields": {
            "ledger_id": "REQUIRED",
            "action_id": "REQUIRED",
            "from_state": "owner_handoff_ready",
            "to_state": "|".join(E15A_AUTO_STATES + ["sent_confirmed_by_owner", "skipped_by_owner", "replaced_by_fallback"]),
            "owner_confirmation_ref": "REQUIRED_IF_SENT",
            "feedback_event_ref": "REQUIRED_AFTER_FEEDBACK",
            "transition_reason": "REQUIRED",
        },
    }


def build_e15a_ledger_state_after_owner_handoff(
    console: Mapping[str, Any],
    confirmation_fixture: Mapping[str, Any],
) -> Dict[str, Any]:
    confirmation_by_action = {row["action_id"]: row for row in confirmation_fixture.get("rows", [])}
    rows: List[Dict[str, Any]] = []
    for action in console.get("primary_actions", []):
        confirmation = confirmation_by_action.get(action["action_id"], {})
        rows.append(
            {
                "ledger_id": action["ledger_id"],
                "action_id": action["action_id"],
                "feedback_event_id": action["feedback_event_id"],
                "previous_state": "owner_handoff_ready",
                "state": "waiting_owner_send",
                "secondary_state": "awaiting_owner_confirmation",
                "send_status": confirmation.get("send_status", "not_sent"),
                "sent_confirmed_by_owner": False,
                "external_action_executed_by_agent": False,
                "transition_reason": "E15A moved C3 owner-handoff-ready row into owner send waiting state only.",
            }
        )
    return {
        "state_id": "e15a_ledger_state_after_owner_handoff",
        "rows": rows,
        "external_action_executed_by_agent": False,
        "sent_confirmed_by_owner": False,
    }


def validate_e15a_ledger_state_after_owner_handoff(state: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if state.get("external_action_executed_by_agent") is not False:
        errors.append("ledger_state_must_not_execute_agent_action")
    if state.get("sent_confirmed_by_owner") is not False:
        errors.append("ledger_state_must_not_fake_sent")
    for row in state.get("rows", []):
        if row.get("state") not in E15A_AUTO_STATES:
            errors.append(f"{row.get('action_id')}:invalid_auto_state")
        if row.get("sent_confirmed_by_owner") is not False:
            errors.append(f"{row.get('action_id')}:must_wait_for_owner_confirmation")
    if len(state.get("rows", [])) != 3:
        errors.append("ledger_state_must_cover_three_primary_actions")
    return list(dict.fromkeys(errors))
