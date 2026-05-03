from __future__ import annotations

from typing import Any, Dict, List, Mapping

from office.mission_command.c2_feedback_loop import FEEDBACK_TYPES


def build_e15a_feedback_capture_form(console: Mapping[str, Any]) -> Dict[str, Any]:
    valid_actions = [
        {
            "action_id": action["action_id"],
            "ledger_id": action["ledger_id"],
            "feedback_event_id": action["feedback_event_id"],
            "target_id": action["target_id"],
            "target_name": action["target_name"],
        }
        for action in console.get("primary_actions", [])
    ]
    return {
        "form_id": "e15a_feedback_capture_form",
        "source_console_id": console.get("console_id"),
        "valid_actions": valid_actions,
        "feedback_types": FEEDBACK_TYPES,
        "fields": {
            "action_id": "REQUIRED_FROM_VALID_ACTION",
            "ledger_id": "REQUIRED_FROM_VALID_ACTION",
            "feedback_event_id": "REQUIRED_FROM_VALID_ACTION",
            "target_id": "REQUIRED_FROM_VALID_ACTION",
            "raw_feedback_summary": "OWNER_TO_FILL_NO_INVENTED_FEEDBACK",
            "feedback_type": "|".join(FEEDBACK_TYPES),
            "received_at": "ISO8601_OR_NO_RESPONSE_TIMEOUT_DATE",
            "channel": "owner_selected_channel",
            "owner_notes": "",
            "do_not_contact_requested": False,
            "safety_or_trust_concern": False,
            "price_question_present": False,
            "request_for_details_present": False,
            "referral_present": False,
            "positive_interest_present": False,
        },
        "public_evidence_is_not_feedback": True,
        "no_response_requires_valid_sent_ledger": True,
        "external_action_executed_by_agent": False,
    }


def validate_e15a_feedback_capture_form(form: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    fields = dict(form.get("fields", {}))
    for key in [
        "action_id",
        "ledger_id",
        "feedback_event_id",
        "target_id",
        "raw_feedback_summary",
        "feedback_type",
        "received_at",
        "channel",
        "do_not_contact_requested",
        "safety_or_trust_concern",
        "price_question_present",
        "request_for_details_present",
        "referral_present",
        "positive_interest_present",
    ]:
        if key not in fields:
            errors.append(f"missing_field_{key}")
    if form.get("public_evidence_is_not_feedback") is not True:
        errors.append("public_evidence_must_not_be_feedback")
    if form.get("no_response_requires_valid_sent_ledger") is not True:
        errors.append("no_response_requires_valid_sent_ledger")
    if form.get("external_action_executed_by_agent") is not False:
        errors.append("feedback_form_must_not_execute_agent_action")
    if len(form.get("valid_actions", [])) != 3:
        errors.append("feedback_form_must_cover_three_primary_actions")
    return list(dict.fromkeys(errors))


def render_e15a_feedback_capture_form(form: Mapping[str, Any]) -> str:
    lines = [
        "# E15A Feedback Capture Form",
        "",
        "## 人话摘要",
        "",
        "Owner 收到回复后，只需要选 action_id，写一句 raw_feedback_summary，再勾选反馈类型。没有真实发送 ledger 时，不要记录 no_response。",
        "",
        "## Valid Actions",
    ]
    for action in form.get("valid_actions", []):
        lines.append(f"- {action['target_name']}: action_id `{action['action_id']}`, ledger_id `{action['ledger_id']}`, feedback_event_id `{action['feedback_event_id']}`")
    lines.extend(
        [
            "",
            "## Feedback Types",
            "",
            ", ".join(form.get("feedback_types", [])),
            "",
            "## Boundary",
            "",
            "- Public evidence is not validation feedback.",
            "- no_response requires a valid sent ledger and wait window.",
            "- Do not invent customer response.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
