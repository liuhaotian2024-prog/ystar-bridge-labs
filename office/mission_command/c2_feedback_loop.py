from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping


FEEDBACK_TYPES = [
    "no_response",
    "positive_interest",
    "request_for_details",
    "price_question",
    "referral",
    "negative_not_relevant",
    "negative_timing",
    "unsubscribe_or_do_not_contact",
    "safety_or_trust_concern",
    "unclear_response",
]


@dataclass(frozen=True)
class C2FeedbackSignal:
    feedback_type: str
    signal_strength: str
    sales_implication: str
    governance_implication: str
    next_action_recommendation: str
    allowed_next_step: str
    blocked_next_step: str
    owner_escalation_required: bool
    offer_revision_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_c2_feedback_ingestion_template() -> Dict[str, Any]:
    return {
        "template_only": True,
        "feedback_event": {
            "feedback_event_id": "TO_FILL_AFTER_VALID_ACTION",
            "action_id": "REQUIRED_VALID_ACTION_LEDGER_ID",
            "feedback_source": "reply|form_response|publication_response|owner_recorded|gov_mcp_captured",
            "feedback_type": "|".join(FEEDBACK_TYPES),
            "buyer_pain": "",
            "urgency": "",
            "budget": "",
            "trust": "",
            "objection": "",
            "next_step": "",
            "paid_signal_candidate": False,
            "limitations": "",
            "recorded_by": "owner|gov-mcp",
            "recorded_at": "ISO8601",
        },
        "public_evidence_is_not_validation_feedback": True,
        "no_response_requires_valid_action_ledger": True,
    }


def evaluate_c2_feedback(feedback_event: Mapping[str, Any], *, valid_action_ledger_exists: bool) -> C2FeedbackSignal:
    feedback_type = str(feedback_event.get("feedback_type", ""))
    if feedback_event.get("feedback_source") == "public_evidence":
        feedback_type = "invalid_public_evidence"
    if feedback_type == "no_response" and not valid_action_ledger_exists:
        feedback_type = "invalid_no_response_without_action"
    if feedback_type == "price_question" or feedback_event.get("paid_signal_candidate") is True:
        return C2FeedbackSignal("price_question", "strong", "paid-signal candidate may exist", "requires ledger-backed feedback and CIEU residual candidate", "prepare_E15_paid_signal_review_gate", "record_paid_signal_candidate_feedback", "claim_revenue_or_collect_payment", False, False)
    if feedback_type in {"positive_interest", "request_for_details", "referral"}:
        return C2FeedbackSignal(feedback_type, "medium", "buyer interest exists but may not be paid signal", "requires next-step envelope before follow-up", "prepare_governed_followup_decision", "draft_followup_for_Y_gov_preflight", "automatic_followup_without_envelope", False, False)
    if feedback_type == "no_response":
        return C2FeedbackSignal("no_response", "weak", "no buyer signal yet", "valid only after real action ledger and wait window", "wait_or_rotate_to_fallback_target", "record_no_response_after_valid_action", "count_as_negative_without_wait_window", False, False)
    if feedback_type in {"negative_not_relevant", "negative_timing"}:
        return C2FeedbackSignal(feedback_type, "negative", "segment or timing may be wrong", "stop or suppress target depending on wording", "suppress_or_revise_target_segment", "revise_offer_or_target_filter", "continue_same_target", False, True)
    if feedback_type == "unsubscribe_or_do_not_contact":
        return C2FeedbackSignal(feedback_type, "hard_stop", "target must be suppressed", "suppression and stop condition triggered", "suppress_target_and_stop", "write_suppression_receipt", "follow_up", True, False)
    if feedback_type == "safety_or_trust_concern":
        return C2FeedbackSignal(feedback_type, "risk", "trust gap blocks conversion until addressed", "owner/Y*gov escalation required for trust-risk handling", "escalate_and_revise_trust_boundary", "prepare_trust_gap_revision", "continue_outreach", True, True)
    return C2FeedbackSignal(feedback_type or "unclear_response", "invalid", "no usable commercial signal", "invalid or unsupported feedback cannot drive learning", "request_clarification_or_mark_invalid", "record_limitation", "enter_E15", False, False)


def build_c2_signal_loop_fixture() -> Dict[str, Any]:
    return {
        "classifications": [evaluate_c2_feedback({"feedback_type": item, "feedback_source": "reply"}, valid_action_ledger_exists=True).to_dict() for item in FEEDBACK_TYPES],
        "invalid_examples": [
            evaluate_c2_feedback({"feedback_type": "no_response", "feedback_source": "owner_recorded"}, valid_action_ledger_exists=False).to_dict(),
            evaluate_c2_feedback({"feedback_type": "positive_interest", "feedback_source": "public_evidence"}, valid_action_ledger_exists=True).to_dict(),
        ],
    }


def validate_c2_feedback_template(template: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    event = dict(template.get("feedback_event", {}))
    for key in ["feedback_event_id", "action_id", "feedback_source", "feedback_type", "recorded_by", "recorded_at"]:
        if key not in event:
            errors.append(f"missing_{key}")
    if template.get("public_evidence_is_not_validation_feedback") is not True:
        errors.append("must_reject_public_evidence_as_feedback")
    if template.get("no_response_requires_valid_action_ledger") is not True:
        errors.append("no_response_must_require_valid_action_ledger")
    return errors
