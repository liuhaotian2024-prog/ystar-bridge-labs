from __future__ import annotations

from typing import Any, Dict, List, Mapping

from office.mission_command.c2_feedback_loop import evaluate_c2_feedback


E15A_FIXTURE_TYPES = [
    "no_response",
    "positive_interest",
    "price_question",
    "unsubscribe_or_do_not_contact",
]


def evaluate_e15a_feedback_signal(feedback_event: Mapping[str, Any], *, valid_sent_ledger_exists: bool) -> Dict[str, Any]:
    c2_signal = evaluate_c2_feedback(
        {
            "feedback_type": feedback_event.get("feedback_type"),
            "feedback_source": feedback_event.get("feedback_source", "owner_recorded"),
            "paid_signal_candidate": feedback_event.get("paid_signal_candidate", False),
        },
        valid_action_ledger_exists=valid_sent_ledger_exists,
    ).to_dict()
    feedback_type = c2_signal["feedback_type"]
    if feedback_type == "price_question":
        target_route = "keep_target_open"
        offer_route = "prepare_paid_signal_review"
        next_action_route = "E15D_gov_mcp_controlled_execution_pilot_after_owner_review"
    elif feedback_type in {"positive_interest", "request_for_details", "referral"}:
        target_route = "keep_target_open"
        offer_route = "continue_current_offer"
        next_action_route = "prepare_governed_followup_decision"
    elif feedback_type == "unsubscribe_or_do_not_contact":
        target_route = "suppress_target"
        offer_route = "continue_offer_but_respect_suppression"
        next_action_route = "E15E_suppression_and_batch_replacement"
    elif feedback_type == "no_response":
        target_route = "wait_or_replace_after_timeout"
        offer_route = "insufficient_signal"
        next_action_route = "rotate_to_fallback_or_wait"
    elif feedback_type in {"negative_not_relevant", "negative_timing"}:
        target_route = "suppress_or_resegment_target"
        offer_route = "revise_offer_or_target_filter"
        next_action_route = "E15B_offer_revision_before_send"
    else:
        target_route = "require_owner_review"
        offer_route = "insufficient_or_invalid_signal"
        next_action_route = "request_clarification_or_mark_invalid"
    return {
        "feedback_type": feedback_event.get("feedback_type"),
        "normalized_signal": feedback_type,
        "signal_strength": c2_signal["signal_strength"],
        "sales_implication": c2_signal["sales_implication"],
        "governance_implication": c2_signal["governance_implication"],
        "target_route": target_route,
        "offer_route": offer_route,
        "next_action_route": next_action_route,
        "owner_escalation_required": c2_signal["owner_escalation_required"],
        "suppression_required": target_route == "suppress_target",
        "offer_revision_required": c2_signal["offer_revision_required"],
        "allowed_next_step": c2_signal["allowed_next_step"],
        "blocked_next_step": c2_signal["blocked_next_step"],
    }


def build_e15a_feedback_signal_evaluation_fixture() -> Dict[str, Any]:
    cases = []
    for feedback_type in E15A_FIXTURE_TYPES:
        cases.append(
            evaluate_e15a_feedback_signal(
                {
                    "feedback_type": feedback_type,
                    "feedback_source": "owner_recorded",
                    "paid_signal_candidate": feedback_type == "price_question",
                },
                valid_sent_ledger_exists=True,
            )
        )
    invalid_no_response = evaluate_e15a_feedback_signal(
        {"feedback_type": "no_response", "feedback_source": "owner_recorded"},
        valid_sent_ledger_exists=False,
    )
    return {
        "fixture_id": "e15a_feedback_signal_evaluation_fixture",
        "cases": cases,
        "invalid_no_response_without_sent_ledger": invalid_no_response,
        "public_evidence_is_not_feedback": True,
    }


def validate_e15a_feedback_signal_fixture(fixture: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    case_types = {case.get("feedback_type") for case in fixture.get("cases", [])}
    for feedback_type in E15A_FIXTURE_TYPES:
        if feedback_type not in case_types:
            errors.append(f"missing_fixture_case_{feedback_type}")
    for case in fixture.get("cases", []):
        for key in [
            "normalized_signal",
            "signal_strength",
            "sales_implication",
            "governance_implication",
            "target_route",
            "offer_route",
            "next_action_route",
            "owner_escalation_required",
            "suppression_required",
            "offer_revision_required",
        ]:
            if key not in case:
                errors.append(f"{case.get('feedback_type')}:missing_{key}")
    if fixture.get("invalid_no_response_without_sent_ledger", {}).get("normalized_signal") != "invalid_no_response_without_action":
        errors.append("no_response_without_sent_ledger_must_be_invalid")
    return list(dict.fromkeys(errors))
