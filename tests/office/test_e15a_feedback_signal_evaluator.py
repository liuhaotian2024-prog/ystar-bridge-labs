from __future__ import annotations

from office.mission_command.e15a_feedback_signal_evaluator import (
    build_e15a_feedback_signal_evaluation_fixture,
    evaluate_e15a_feedback_signal,
    validate_e15a_feedback_signal_fixture,
)


def test_e15a_signal_fixture_covers_core_feedback_cases() -> None:
    fixture = build_e15a_feedback_signal_evaluation_fixture()
    assert validate_e15a_feedback_signal_fixture(fixture) == []
    case_types = {case["feedback_type"] for case in fixture["cases"]}
    assert {"no_response", "positive_interest", "price_question", "unsubscribe_or_do_not_contact"} <= case_types


def test_e15a_signal_routes_price_and_unsubscribe_correctly() -> None:
    price = evaluate_e15a_feedback_signal({"feedback_type": "price_question", "paid_signal_candidate": True}, valid_sent_ledger_exists=True)
    unsubscribe = evaluate_e15a_feedback_signal({"feedback_type": "unsubscribe_or_do_not_contact"}, valid_sent_ledger_exists=True)
    assert price["next_action_route"].startswith("E15D")
    assert price["suppression_required"] is False
    assert unsubscribe["target_route"] == "suppress_target"
    assert unsubscribe["suppression_required"] is True


def test_e15a_no_response_requires_valid_sent_ledger() -> None:
    signal = evaluate_e15a_feedback_signal({"feedback_type": "no_response"}, valid_sent_ledger_exists=False)
    assert signal["normalized_signal"] == "invalid_no_response_without_action"
