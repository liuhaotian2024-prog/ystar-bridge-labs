from __future__ import annotations

from typing import Any, Dict, List, Mapping


E15A_SEND_STATUSES = [
    "not_sent",
    "sent_by_owner_unconfirmed",
    "sent_confirmed_by_owner",
    "skipped_by_owner",
    "blocked_by_missing_target_info",
    "replaced_by_fallback",
    "suppressed_by_owner",
]


def build_e15a_owner_send_confirmation_template(console: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "template_id": "e15a_owner_send_confirmation_template",
        "source_console_id": console.get("console_id"),
        "status_values": E15A_SEND_STATUSES,
        "instructions": "Owner fills one row only after manually sending, skipping, replacing, or suppressing a target. Aiden/Codex must not create sent confirmations.",
        "fields": {
            "action_id": "REQUIRED_FROM_CONSOLE",
            "ledger_id": "REQUIRED_FROM_CONSOLE",
            "feedback_event_id": "REQUIRED_FROM_CONSOLE",
            "target_id": "REQUIRED_FROM_CONSOLE",
            "send_status": "|".join(E15A_SEND_STATUSES),
            "sent_confirmed_by_owner": False,
            "sent_at": "OWNER_TO_FILL_IF_SENT",
            "channel_used": "OWNER_TO_FILL_IF_SENT",
            "not_sent_reason": "OWNER_TO_FILL_IF_NOT_SENT",
            "owner_notes": "",
        },
        "external_action_executed_by_agent": False,
        "no_fake_sent_confirmation": True,
    }


def build_e15a_owner_send_confirmation_fixture(console: Mapping[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for action in console.get("primary_actions", []):
        rows.append(
            {
                "action_id": action["action_id"],
                "ledger_id": action["ledger_id"],
                "feedback_event_id": action["feedback_event_id"],
                "target_id": action["target_id"],
                "send_status": "not_sent",
                "sent_confirmed_by_owner": False,
                "sent_at": "",
                "channel_used": "",
                "not_sent_reason": "awaiting_owner_execution",
                "awaiting_owner_confirmation": True,
                "external_action_executed_by_agent": False,
            }
        )
    return {
        "fixture_id": "e15a_owner_send_confirmation_fixture",
        "source_console_id": console.get("console_id"),
        "rows": rows,
        "sent_confirmed_by_owner": False,
        "external_action_executed_by_agent": False,
        "awaiting_owner_confirmation": True,
    }


def validate_e15a_owner_send_confirmation_fixture(fixture: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if fixture.get("sent_confirmed_by_owner") is not False:
        errors.append("fixture_must_not_fake_owner_sent")
    if fixture.get("external_action_executed_by_agent") is not False:
        errors.append("fixture_must_not_execute_agent_action")
    if fixture.get("awaiting_owner_confirmation") is not True:
        errors.append("fixture_must_wait_for_owner_confirmation")
    for row in fixture.get("rows", []):
        if row.get("send_status") not in E15A_SEND_STATUSES:
            errors.append(f"{row.get('action_id')}:invalid_send_status")
        if row.get("sent_confirmed_by_owner") is not False:
            errors.append(f"{row.get('action_id')}:must_not_confirm_sent")
    if len(fixture.get("rows", [])) != 3:
        errors.append("fixture_must_cover_three_primary_actions")
    return list(dict.fromkeys(errors))
