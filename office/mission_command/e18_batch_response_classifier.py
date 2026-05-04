from __future__ import annotations

from typing import Any, Dict, List


def classify_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    feedback_type = str(entry.get("feedback_type", "no_response"))
    strength = 0
    next_action = "wait_or_manual_send_if_not_sent"
    suppression = False
    followup = False
    offer_learning = "none_yet"
    target_learning = "none_yet"
    if entry.get("do_not_contact_requested") or feedback_type == "unsubscribe_or_do_not_contact":
        suppression = True
        next_action = "suppress_target"
        target_learning = "do_not_contact"
    elif entry.get("bounce_or_invalid") or feedback_type == "bounce":
        next_action = "replace_or_research_target"
        target_learning = "channel_or_identity_invalid"
    elif entry.get("meeting_request_present") or feedback_type == "meeting_request":
        strength = 5
        next_action = "owner_schedule_meeting"
        followup = True
        offer_learning = "strong_meeting_signal"
    elif entry.get("positive_interest_present") or feedback_type == "positive_interest":
        strength = 4
        next_action = "owner_follow_up_after_review"
        followup = True
        offer_learning = "positive_interest"
    elif entry.get("pricing_question_present") or feedback_type == "pricing_question":
        strength = 4
        next_action = "owner_answer_pricing_after_review"
        followup = True
        offer_learning = "budget_or_pricing_signal"
    elif entry.get("technical_clarification_present") or feedback_type == "technical_clarification":
        strength = 3
        next_action = "owner_answer_clarification"
        followup = True
        offer_learning = "message_clarity_gap"
    elif entry.get("referral_present") or feedback_type == "referral":
        strength = 3
        next_action = "owner_review_referral"
        followup = True
        target_learning = "buyer_route_may_be_wrong_contact"
    elif entry.get("objection_present") or feedback_type in {"objection", "negative_response"}:
        strength = 1
        next_action = "revise_offer_or_target"
        offer_learning = "objection_or_negative_signal"
    return {
        "action_id": entry.get("action_id"),
        "target_id": entry.get("target_id"),
        "target_name": entry.get("target_name"),
        "feedback_type": feedback_type,
        "paid_signal_strength": strength,
        "next_action": next_action,
        "suppression_required": suppression,
        "followup_eligible_after_owner_review": followup and not suppression,
        "offer_learning": offer_learning,
        "target_segment_learning": target_learning,
        "external_action_executed": False,
    }


def build_batch_response_classification_rules(empty_intake: Dict[str, Any]) -> Dict[str, Any]:
    per_target = [classify_entry(entry) for entry in empty_intake.get("entries", [])]
    positive_count = sum(1 for item in per_target if item["paid_signal_strength"] >= 4)
    suppression_count = sum(1 for item in per_target if item["suppression_required"])
    return {
        "artifact_id": "e18_batch_response_classification_rules",
        "batch_id": empty_intake["batch_id"],
        "classification_method": "deterministic_per_target_explicit_feedback_fields_no_llm_judge",
        "per_target": per_target,
        "batch_summary": {
            "response_count": 0,
            "positive_or_budget_signal_count": positive_count,
            "suppression_count": suppression_count,
            "batch_signal_quality": "no_feedback_imported_yet",
        },
        "offer_level_learning": "none_until_feedback_import",
        "target_segment_learning": "none_until_feedback_import",
        "external_action_executed": False,
    }
