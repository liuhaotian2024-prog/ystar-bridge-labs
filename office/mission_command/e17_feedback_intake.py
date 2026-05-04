from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


E17_FEEDBACK_TYPES = [
    "no_response_yet",
    "no_response_after_wait_window",
    "positive_interest",
    "clarification_request",
    "pricing_question",
    "meeting_request",
    "referral",
    "objection",
    "unsubscribe_or_do_not_contact",
    "negative_response",
    "bounced_or_invalid_target",
    "manual_notes_only",
]


@dataclass(frozen=True)
class E17FeedbackIntakeSchema:
    artifact_id: str
    action_id: str
    ledger_id: str
    feedback_event_id: str
    required_fields: List[str]
    feedback_type_enum: List[str]
    boolean_signal_fields: List[str]
    provenance_rules: List[str]
    external_action_executed_by_agent: bool = False
    real_customer_response_claimed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E17FeedbackIntakeEvent:
    artifact_id: str
    action_id: str
    ledger_id: str
    feedback_event_id: str
    target_id: str
    target_name: str
    owner_sent_status: str
    feedback_type: str
    raw_feedback_summary: str
    received_at: str
    channel: str
    owner_notes: str
    response_evidence_present: bool
    do_not_contact_requested: bool = False
    safety_or_trust_concern: bool = False
    price_question_present: bool = False
    meeting_request_present: bool = False
    request_for_details_present: bool = False
    referral_present: bool = False
    positive_interest_present: bool = False
    objection_present: bool = False
    bounced_or_invalid: bool = False
    external_action_executed_by_agent: bool = False
    real_customer_response_claimed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_feedback_intake_schema(selected_action: Dict[str, Any]) -> E17FeedbackIntakeSchema:
    return E17FeedbackIntakeSchema(
        artifact_id="e17_feedback_intake_schema",
        action_id=str(selected_action.get("action_id", "unknown_action")),
        ledger_id=str(selected_action.get("ledger_id", "unknown_ledger")),
        feedback_event_id=str(selected_action.get("feedback_event_id", "unknown_feedback_event")),
        required_fields=[
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
            "response_evidence_present",
        ],
        feedback_type_enum=E17_FEEDBACK_TYPES,
        boolean_signal_fields=[
            "do_not_contact_requested",
            "safety_or_trust_concern",
            "price_question_present",
            "meeting_request_present",
            "request_for_details_present",
            "referral_present",
            "positive_interest_present",
            "objection_present",
            "bounced_or_invalid",
        ],
        provenance_rules=[
            "Owner-reported feedback is provisional until source/provenance is recorded.",
            "No customer response is claimed by the empty intake file.",
            "CIEU/core writeback remains hard-gated and is not performed by E17.",
            "Do-not-contact requests suppress the target immediately.",
        ],
    )


def build_empty_feedback_intake(selected_action: Dict[str, Any]) -> E17FeedbackIntakeEvent:
    return E17FeedbackIntakeEvent(
        artifact_id="e17_feedback_intake_empty",
        action_id=str(selected_action.get("action_id", "unknown_action")),
        ledger_id=str(selected_action.get("ledger_id", "unknown_ledger")),
        feedback_event_id=str(selected_action.get("feedback_event_id", "unknown_feedback_event")),
        target_id=str(selected_action.get("target_id", "unknown_target")),
        target_name=str(selected_action.get("target_name", "selected target")),
        owner_sent_status="not_sent_in_repo",
        feedback_type="no_response_yet",
        raw_feedback_summary="",
        received_at="",
        channel="",
        owner_notes="",
        response_evidence_present=False,
    )


def validate_feedback_intake_event(event: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field_name in ["action_id", "ledger_id", "feedback_event_id", "target_id", "owner_sent_status", "feedback_type"]:
        if not event.get(field_name):
            errors.append(f"missing_{field_name}")
    if event.get("feedback_type") not in E17_FEEDBACK_TYPES:
        errors.append("invalid_feedback_type")
    if event.get("external_action_executed_by_agent") is True:
        errors.append("agent_external_action_not_allowed")
    if event.get("real_customer_response_claimed") is True and not event.get("response_evidence_present"):
        errors.append("real_response_claim_requires_evidence")
    return errors


def render_feedback_runtime(schema: E17FeedbackIntakeSchema, empty_event: E17FeedbackIntakeEvent, rules: Dict[str, Any]) -> str:
    lines = [
        "# E17 Feedback Runtime",
        "",
        "Owner can import a response later with a small structured intake. The empty file claims no send and no customer response.",
        "",
        f"- action_id: {schema.action_id}",
        f"- ledger_id: {schema.ledger_id}",
        f"- feedback_event_id: {schema.feedback_event_id}",
        f"- empty_feedback_type: {empty_event.feedback_type}",
        f"- real_customer_response_claimed: {str(empty_event.real_customer_response_claimed).lower()}",
        "",
        "## Supported Feedback Types",
    ]
    lines.extend(f"- {item}" for item in schema.feedback_type_enum)
    lines.extend(["", "## Classification Rule Families"])
    lines.extend(f"- {item['rule_id']}: {item['route_recommendation']}" for item in rules.get("rules", []))
    return "\n".join(lines).rstrip() + "\n"
