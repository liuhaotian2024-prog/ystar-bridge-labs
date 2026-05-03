from __future__ import annotations

from office.mission_command.c3_feedback_intake_runtime import (
    build_c3_feedback_intake_template,
    build_c3_feedback_signal_fixture,
    normalize_c3_feedback_event,
    validate_c3_feedback_intake_template,
)


def test_c3_feedback_template_has_required_fields() -> None:
    template = build_c3_feedback_intake_template()
    assert validate_c3_feedback_intake_template(template) == []
    assert template["public_evidence_is_not_feedback"] is True
    assert template["no_response_requires_valid_action_ledger"] is True


def test_c3_feedback_runtime_normalizes_price_question() -> None:
    event = normalize_c3_feedback_event(
        {
            "feedback_event_id": "fb1",
            "action_id": "act1",
            "ledger_id": "ledger1",
            "raw_feedback_summary": "How much?",
            "feedback_type": "price_question",
            "reply_channel": "owner_recorded",
            "received_at": "2026-05-03T00:00:00Z",
        },
        valid_action_ledger_exists=True,
    )
    assert event["signal_strength"] == "strong"
    assert event["next_action_recommendation"] == "prepare_E15_paid_signal_review_gate"


def test_c3_feedback_runtime_marks_no_response_without_ledger_invalid() -> None:
    event = normalize_c3_feedback_event({"feedback_type": "no_response", "reply_channel": "owner_recorded"}, valid_action_ledger_exists=False)
    assert event["signal_strength"] == "invalid"


def test_c3_feedback_fixture_covers_supported_types() -> None:
    fixture = build_c3_feedback_signal_fixture()
    assert len(fixture["examples"]) >= 10
