from __future__ import annotations

from office.mission_command.c2_feedback_loop import (
    build_c2_feedback_ingestion_template,
    build_c2_signal_loop_fixture,
    evaluate_c2_feedback,
    validate_c2_feedback_template,
)


def test_c2_feedback_template_requires_action_and_rejects_public_evidence() -> None:
    template = build_c2_feedback_ingestion_template()
    assert validate_c2_feedback_template(template) == []
    assert template["public_evidence_is_not_validation_feedback"] is True
    assert template["no_response_requires_valid_action_ledger"] is True


def test_c2_feedback_no_response_requires_valid_action_ledger() -> None:
    signal = evaluate_c2_feedback({"feedback_type": "no_response", "feedback_source": "owner_recorded"}, valid_action_ledger_exists=False)
    assert signal.signal_strength == "invalid"
    assert signal.allowed_next_step == "record_limitation"


def test_c2_feedback_price_question_becomes_paid_signal_candidate() -> None:
    signal = evaluate_c2_feedback({"feedback_type": "price_question", "feedback_source": "reply"}, valid_action_ledger_exists=True)
    assert signal.feedback_type == "price_question"
    assert signal.next_action_recommendation == "prepare_E15_paid_signal_review_gate"
    assert signal.blocked_next_step == "claim_revenue_or_collect_payment"


def test_c2_feedback_positive_and_negative_paths() -> None:
    positive = evaluate_c2_feedback({"feedback_type": "positive_interest", "feedback_source": "reply"}, valid_action_ledger_exists=True)
    negative = evaluate_c2_feedback({"feedback_type": "negative_not_relevant", "feedback_source": "reply"}, valid_action_ledger_exists=True)
    assert positive.allowed_next_step == "draft_followup_for_Y_gov_preflight"
    assert negative.offer_revision_required is True


def test_c2_feedback_opt_out_suppresses_and_escalates_owner() -> None:
    signal = evaluate_c2_feedback({"feedback_type": "unsubscribe_or_do_not_contact", "feedback_source": "reply"}, valid_action_ledger_exists=True)
    assert signal.allowed_next_step == "write_suppression_receipt"
    assert signal.blocked_next_step == "follow_up"
    assert signal.owner_escalation_required is True


def test_c2_signal_loop_fixture_covers_invalid_examples() -> None:
    fixture = build_c2_signal_loop_fixture()
    assert len(fixture["classifications"]) >= 10
    assert len(fixture["invalid_examples"]) == 2
