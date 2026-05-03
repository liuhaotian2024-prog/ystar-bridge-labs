from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List


E14_FEEDBACK_TYPES = [
    "strong_positive",
    "weak_positive",
    "neutral",
    "negative",
    "objection_only",
    "no_response_after_valid_action",
    "invalid_feedback",
    "blocked_no_action",
]


@dataclass(frozen=True)
class E14FeedbackEventTemplate:
    feedback_event_id: str
    action_id: str
    target_id: str
    source: str
    feedback_type: str
    response_text_or_summary: str
    buyer_pain_signal: str
    budget_signal: str
    urgency_signal: str
    trust_signal: str
    objection_signal: str
    next_step_signal: str
    paid_signal_candidate: bool
    limitations: str
    recorded_by: str
    recorded_at: str
    evidence_or_message_ref: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_e14_feedback_events_template() -> Dict[str, Any]:
    template = E14FeedbackEventTemplate(
        feedback_event_id="OWNER_TO_FILL",
        action_id="VALID_E14_ACTION_ID_REQUIRED",
        target_id="OWNER_APPROVED_TARGET_ID_REQUIRED",
        source="owner_entered_after_manual_validation",
        feedback_type="strong_positive|weak_positive|neutral|negative|objection_only|no_response_after_valid_action|invalid_feedback|blocked_no_action",
        response_text_or_summary="OWNER_TO_FILL_NO_INVENTED_FEEDBACK",
        buyer_pain_signal="OWNER_TO_FILL",
        budget_signal="OWNER_TO_FILL",
        urgency_signal="OWNER_TO_FILL",
        trust_signal="OWNER_TO_FILL",
        objection_signal="OWNER_TO_FILL",
        next_step_signal="OWNER_TO_FILL",
        paid_signal_candidate=False,
        limitations="Feedback must be owner-entered from a real manual validation action; public evidence is not validation feedback.",
        recorded_by="OWNER_TO_FILL",
        recorded_at="OWNER_TO_FILL_ISO8601",
        evidence_or_message_ref="ACTION_LEDGER_OR_MESSAGE_REFERENCE_REQUIRED",
    )
    return {"feedback_events": [], "template": template.to_dict(), "feedback_captured": False}


def validate_e14_feedback_event(event: Dict[str, Any], valid_action_ids: List[str] | None = None, owner_entered: bool = False) -> List[str]:
    valid_action_ids = valid_action_ids or []
    errors: List[str] = []
    action_id = str(event.get("action_id", ""))
    if not action_id or action_id.startswith("OWNER") or action_id not in valid_action_ids:
        errors.append("feedback_requires_valid_action_id")
    if event.get("source") != "owner_entered_after_manual_validation" and not owner_entered:
        errors.append("feedback_must_be_owner_entered")
    if event.get("feedback_type") == "no_response_after_valid_action" and action_id not in valid_action_ids:
        errors.append("no_response_requires_valid_action_ledger")
    if str(event.get("response_text_or_summary", "")).strip().lower() in {"", "fake", "owner_to_fill", "tbd"}:
        errors.append("feedback_must_not_be_invented_or_placeholder")
    if event.get("feedback_type") not in E14_FEEDBACK_TYPES:
        errors.append("invalid_feedback_type")
    return list(dict.fromkeys(errors))


def write_e14_feedback_events_template(repo_root: Path) -> Path:
    path = repo_root / "operations" / "external_validation" / "e14_feedback_events.template.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_e14_feedback_events_template(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
