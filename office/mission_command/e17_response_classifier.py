from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class E17ResponseClassification:
    artifact_id: str
    action_id: str
    feedback_type: str
    paid_signal_strength: int
    paid_signal_label: str
    buyer_pain_confirmed: bool
    offer_clarity_score: int
    urgency_signal: int
    budget_signal: int
    authority_signal: int
    next_action_allowed: str
    suppression_required: bool
    offer_revision_required: bool
    target_revision_required: bool
    route_recommendation: str
    reason_codes: List[str]
    external_action_executed_by_agent: bool = False
    real_customer_response_claimed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _bool(event: Dict[str, Any], key: str) -> bool:
    return bool(event.get(key) is True)


def classify_e17_response(event: Dict[str, Any]) -> E17ResponseClassification:
    feedback_type = str(event.get("feedback_type", "no_response_yet"))
    action_id = str(event.get("action_id", "unknown_action"))
    reason_codes: List[str] = []
    paid_signal_strength = 0
    label = "none"
    buyer_pain_confirmed = False
    offer_clarity_score = 2
    urgency_signal = 0
    budget_signal = 0
    authority_signal = 0
    next_action_allowed = "none"
    suppression_required = False
    offer_revision_required = False
    target_revision_required = False
    route = "E17_wait_for_owner_feedback_import"

    if _bool(event, "do_not_contact_requested") or feedback_type == "unsubscribe_or_do_not_contact":
        reason_codes.append("do_not_contact_suppresses_target")
        suppression_required = True
        next_action_allowed = "suppress_only"
        route = "E17_suppress_target"
    elif _bool(event, "safety_or_trust_concern"):
        reason_codes.append("safety_or_trust_concern_requires_review")
        suppression_required = True
        next_action_allowed = "governance_review_only"
        route = "E17_requires_governance_review"
    elif _bool(event, "bounced_or_invalid") or feedback_type == "bounced_or_invalid_target":
        reason_codes.append("target_identity_or_channel_invalid")
        target_revision_required = True
        next_action_allowed = "replace_target"
        route = "E17_target_evidence_expansion_required"
    elif feedback_type in {"meeting_request", "positive_interest"} or _bool(event, "meeting_request_present") or _bool(event, "positive_interest_present"):
        reason_codes.append("positive_interest_or_meeting_signal")
        paid_signal_strength = 5 if _bool(event, "meeting_request_present") or feedback_type == "meeting_request" else 4
        label = "strong" if paid_signal_strength == 5 else "promising"
        buyer_pain_confirmed = True
        offer_clarity_score = 4
        urgency_signal = 4 if feedback_type == "meeting_request" else 3
        authority_signal = 3
        next_action_allowed = "owner_manual_follow_up_or_meeting_scheduling"
        route = "E18_commercial_acceleration_candidate"
    elif feedback_type == "pricing_question" or _bool(event, "price_question_present"):
        reason_codes.append("pricing_question_indicates_budget_interest")
        paid_signal_strength = 4
        label = "budget_signal"
        buyer_pain_confirmed = True
        offer_clarity_score = 3
        urgency_signal = 2
        budget_signal = 4
        authority_signal = 2
        next_action_allowed = "owner_answer_pricing_or_offer_detail"
        route = "E17_manual_follow_up_allowed_after_owner_review"
    elif feedback_type in {"clarification_request", "referral"} or _bool(event, "request_for_details_present") or _bool(event, "referral_present"):
        reason_codes.append("clarification_or_referral_is_qualified_interest")
        paid_signal_strength = 3
        label = "qualified_interest"
        buyer_pain_confirmed = True
        offer_clarity_score = 2 if _bool(event, "request_for_details_present") else 3
        urgency_signal = 2
        authority_signal = 2 if _bool(event, "referral_present") else 1
        next_action_allowed = "owner_clarify_or_route_to_referred_contact"
        route = "E17_wait_for_owner_feedback_import"
        offer_revision_required = _bool(event, "request_for_details_present")
    elif feedback_type in {"objection", "negative_response"} or _bool(event, "objection_present"):
        reason_codes.append("objection_or_negative_response_requires_revision")
        paid_signal_strength = 1
        label = "weak_or_negative"
        offer_clarity_score = 1
        offer_revision_required = True
        next_action_allowed = "revise_offer_or_target"
        route = "E17_offer_revision_required"
    elif feedback_type == "no_response_after_wait_window":
        reason_codes.append("no_response_after_wait_window")
        paid_signal_strength = 1
        label = "no_response"
        offer_clarity_score = 2
        offer_revision_required = True
        next_action_allowed = "revise_message_or_expand_targets"
        route = "E17_offer_revision_required"
    else:
        reason_codes.append("no_response_yet_no_customer_signal_claimed")
        next_action_allowed = "owner_manual_send_or_wait_for_feedback_import"
        route = "E17_manual_send_ready"

    return E17ResponseClassification(
        artifact_id="e17_response_classification",
        action_id=action_id,
        feedback_type=feedback_type,
        paid_signal_strength=paid_signal_strength,
        paid_signal_label=label,
        buyer_pain_confirmed=buyer_pain_confirmed,
        offer_clarity_score=offer_clarity_score,
        urgency_signal=urgency_signal,
        budget_signal=budget_signal,
        authority_signal=authority_signal,
        next_action_allowed=next_action_allowed,
        suppression_required=suppression_required,
        offer_revision_required=offer_revision_required,
        target_revision_required=target_revision_required,
        route_recommendation=route,
        reason_codes=reason_codes,
        external_action_executed_by_agent=bool(event.get("external_action_executed_by_agent") is True),
        real_customer_response_claimed=bool(event.get("real_customer_response_claimed") is True),
    )


def build_response_classification_rules(selected_action: Dict[str, Any]) -> Dict[str, Any]:
    action_id = str(selected_action.get("action_id", "unknown_action"))
    sample_types = [
        "no_response_yet",
        "positive_interest",
        "pricing_question",
        "meeting_request",
        "clarification_request",
        "unsubscribe_or_do_not_contact",
        "bounced_or_invalid_target",
        "negative_response",
    ]
    rules = []
    for feedback_type in sample_types:
        event = {"action_id": action_id, "feedback_type": feedback_type}
        if feedback_type == "positive_interest":
            event["positive_interest_present"] = True
        if feedback_type == "pricing_question":
            event["price_question_present"] = True
        if feedback_type == "meeting_request":
            event["meeting_request_present"] = True
        if feedback_type == "clarification_request":
            event["request_for_details_present"] = True
        if feedback_type == "unsubscribe_or_do_not_contact":
            event["do_not_contact_requested"] = True
        if feedback_type == "bounced_or_invalid_target":
            event["bounced_or_invalid"] = True
        if feedback_type == "negative_response":
            event["objection_present"] = True
        classification = classify_e17_response(event).to_dict()
        rules.append(
            {
                "rule_id": f"classify_{feedback_type}",
                "trigger_feedback_type": feedback_type,
                "paid_signal_strength": classification["paid_signal_strength"],
                "route_recommendation": classification["route_recommendation"],
                "reason_codes": classification["reason_codes"],
            }
        )
    return {
        "artifact_id": "e17_response_classification_rules",
        "action_id": action_id,
        "scoring_method": "deterministic_explicit_field_rules_no_llm_judge",
        "rules": rules,
        "external_action_executed": False,
    }
