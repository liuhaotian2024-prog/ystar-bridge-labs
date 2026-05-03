from __future__ import annotations

from typing import Any, Dict, List, Mapping

from office.mission_command.c2_feedback_loop import FEEDBACK_TYPES, evaluate_c2_feedback


def build_c3_feedback_intake_template() -> Dict[str, Any]:
    return {
        "template_id": "c3_feedback_intake_template",
        "owner_later_fillable": True,
        "fields": {
            "action_id": "REQUIRED",
            "ledger_id": "REQUIRED",
            "feedback_event_id": "REQUIRED",
            "raw_feedback_summary": "REQUIRED",
            "feedback_type": "|".join(FEEDBACK_TYPES),
            "reply_channel": "email|message|form|owner_note|other",
            "received_at": "ISO8601",
            "owner_notes": "",
            "attachments_present": False,
            "privacy_safety_flags": [],
        },
        "public_evidence_is_not_feedback": True,
        "no_response_requires_valid_action_ledger": True,
    }


def normalize_c3_feedback_event(event: Mapping[str, Any], *, valid_action_ledger_exists: bool) -> Dict[str, Any]:
    signal = evaluate_c2_feedback(
        {
            "feedback_type": event.get("feedback_type"),
            "feedback_source": event.get("reply_channel", "owner_recorded"),
            "paid_signal_candidate": event.get("paid_signal_candidate", False),
        },
        valid_action_ledger_exists=valid_action_ledger_exists,
    )
    return {
        "feedback_event_id": event.get("feedback_event_id", ""),
        "action_id": event.get("action_id", ""),
        "ledger_id": event.get("ledger_id", ""),
        "feedback_type": signal.feedback_type,
        "raw_feedback_summary": event.get("raw_feedback_summary", ""),
        "reply_channel": event.get("reply_channel", ""),
        "received_at": event.get("received_at", ""),
        "owner_notes": event.get("owner_notes", ""),
        "attachments_present": bool(event.get("attachments_present", False)),
        "privacy_safety_flags": list(event.get("privacy_safety_flags", [])),
        "signal_strength": signal.signal_strength,
        "sales_implication": signal.sales_implication,
        "governance_implication": signal.governance_implication,
        "next_action_recommendation": signal.next_action_recommendation,
        "offer_revision_required": signal.offer_revision_required,
        "target_suppression_required": signal.feedback_type == "unsubscribe_or_do_not_contact",
        "owner_escalation_required": signal.owner_escalation_required,
        "allowed_next_step": signal.allowed_next_step,
        "blocked_next_step": signal.blocked_next_step,
    }


def build_c3_feedback_signal_fixture() -> Dict[str, Any]:
    examples = []
    for feedback_type in FEEDBACK_TYPES:
        examples.append(
            normalize_c3_feedback_event(
                {
                    "feedback_event_id": f"fixture_{feedback_type}",
                    "action_id": "c3_action_primary_001_cand_alicelabs_alicelabs",
                    "ledger_id": "ledger_c3_action_primary_001_cand_alicelabs_alicelabs",
                    "raw_feedback_summary": f"Fixture for {feedback_type}",
                    "feedback_type": feedback_type,
                    "reply_channel": "owner_recorded",
                    "received_at": "deterministic_fixture_time",
                },
                valid_action_ledger_exists=True,
            )
        )
    return {"fixture_id": "c3_feedback_signal_fixture", "examples": examples}


def validate_c3_feedback_intake_template(template: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    fields = dict(template.get("fields", {}))
    for key in ["action_id", "ledger_id", "feedback_event_id", "raw_feedback_summary", "feedback_type", "reply_channel", "received_at", "attachments_present", "privacy_safety_flags"]:
        if key not in fields:
            errors.append(f"missing_field_{key}")
    if template.get("public_evidence_is_not_feedback") is not True:
        errors.append("must_reject_public_evidence_as_feedback")
    if template.get("no_response_requires_valid_action_ledger") is not True:
        errors.append("no_response_requires_ledger")
    return errors
