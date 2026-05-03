from __future__ import annotations

from typing import Any, Dict, List, Mapping


VALID_FEEDBACK_TYPES = {
    "interested",
    "asks_price",
    "asks_followup",
    "describes_buyer_pain",
    "rejects_no_urgency",
    "rejects_price",
    "opt_out",
    "complaint",
    "no_response_after_valid_action",
}


def build_c1_feedback_event_template() -> Dict[str, Any]:
    return {
        "template": {
            "feedback_event_id": "OWNER_OR_GOV_MCP_TO_FILL_AFTER_FEEDBACK",
            "action_id": "REQUIRED",
            "feedback_source": "reply|form_response|publication_response|owner_recorded",
            "feedback_type": "interested|asks_price|asks_followup|describes_buyer_pain|rejects_no_urgency|rejects_price|opt_out|complaint|no_response_after_valid_action",
            "buyer_pain": "",
            "urgency": "",
            "budget": "",
            "trust": "",
            "objection": "",
            "next_step": "",
            "paid_signal_candidate": False,
            "limitations": "",
            "recorded_by": "REQUIRED",
            "recorded_at": "REQUIRED",
        },
        "public_evidence_is_not_feedback": True,
    }


def validate_c1_feedback_event(event: Mapping[str, Any]) -> List[str]:
    required = ["feedback_event_id", "action_id", "feedback_source", "feedback_type", "recorded_by", "recorded_at"]
    errors = [f"missing_{key}" for key in required if not event.get(key) or str(event.get(key)).startswith("REQUIRED")]
    if str(event.get("feedback_event_id", "")).startswith("OWNER_OR_GOV_MCP_TO_FILL"):
        errors.append("placeholder_feedback_event_is_not_feedback")
    if event.get("feedback_source") == "public_evidence":
        errors.append("public_evidence_is_not_validation_feedback")
    if event.get("feedback_type") not in VALID_FEEDBACK_TYPES:
        errors.append("invalid_feedback_type")
    if event.get("feedback_type") == "no_response_after_valid_action" and not event.get("action_id"):
        errors.append("no_response_requires_valid_action")
    return list(dict.fromkeys(errors))
