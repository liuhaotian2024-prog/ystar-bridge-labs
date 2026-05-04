from __future__ import annotations

from typing import Any, Dict, List


E18_BATCH_FEEDBACK_TYPES = [
    "no_response",
    "positive_interest",
    "meeting_request",
    "pricing_question",
    "technical_clarification",
    "objection",
    "referral",
    "bounce",
    "unsubscribe_or_do_not_contact",
    "negative_response",
    "owner_notes_only",
]


def build_batch_feedback_intake_schema(batch: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e18_batch_feedback_intake_schema",
        "batch_id": batch["batch_id"],
        "required_per_target_fields": [
            "action_id",
            "ledger_id",
            "feedback_event_id",
            "target_id",
            "owner_sent_status",
            "feedback_type",
            "raw_feedback_summary",
            "received_at",
            "channel",
            "owner_notes",
        ],
        "feedback_type_enum": E18_BATCH_FEEDBACK_TYPES,
        "boolean_signal_fields": [
            "positive_interest_present",
            "meeting_request_present",
            "pricing_question_present",
            "technical_clarification_present",
            "objection_present",
            "referral_present",
            "do_not_contact_requested",
            "bounce_or_invalid",
        ],
        "provenance_rules": [
            "No feedback is claimed until owner imports it.",
            "Owner-reported feedback is provisional until provenance is recorded.",
            "Do-not-contact suppresses target immediately.",
            "CIEU/core writeback remains hard-gated.",
        ],
        "external_action_executed": False,
    }


def build_empty_batch_feedback_intake(batch: Dict[str, Any]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for candidate in batch.get("candidates", []):
        entries.append(
            {
                "action_id": candidate["action_id"],
                "ledger_id": candidate["ledger_id"],
                "feedback_event_id": candidate["feedback_event_id"],
                "target_id": candidate["target_id"],
                "target_name": candidate["target_name"],
                "owner_sent_status": "not_sent_or_not_imported",
                "feedback_type": "no_response",
                "raw_feedback_summary": "",
                "received_at": "",
                "channel": "",
                "owner_notes": "",
                "positive_interest_present": False,
                "meeting_request_present": False,
                "pricing_question_present": False,
                "technical_clarification_present": False,
                "objection_present": False,
                "referral_present": False,
                "do_not_contact_requested": False,
                "bounce_or_invalid": False,
                "real_customer_response_claimed": False,
                "external_action_executed_by_agent": False,
            }
        )
    return {
        "artifact_id": "e18_batch_feedback_intake_empty",
        "batch_id": batch["batch_id"],
        "entries": entries,
        "response_count_placeholder": 0,
        "external_action_executed": False,
    }


def render_batch_feedback_runtime(schema: Dict[str, Any], empty: Dict[str, Any]) -> str:
    lines = [
        "# E18 Batch Feedback Runtime",
        "",
        "The empty intake file claims no real customer feedback and no send.",
        "",
        f"- batch_id: {schema['batch_id']}",
        f"- feedback_type_count: {len(schema['feedback_type_enum'])}",
        f"- empty_entries: {len(empty['entries'])}",
        "- external_action_executed: false",
        "",
        "## Feedback Types",
    ]
    lines.extend(f"- {item}" for item in schema["feedback_type_enum"])
    return "\n".join(lines).rstrip() + "\n"
