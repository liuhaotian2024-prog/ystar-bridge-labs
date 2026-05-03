from __future__ import annotations

from pathlib import Path

from office.mission_command.e15a_feedback_capture_pack import build_e15a_feedback_capture_form, validate_e15a_feedback_capture_form
from office.mission_command.e15a_owner_execution_console import build_e15a_owner_execution_console


ROOT = Path(__file__).resolve().parents[2]


def test_e15a_feedback_form_has_minimal_owner_fields() -> None:
    form = build_e15a_feedback_capture_form(build_e15a_owner_execution_console(ROOT))
    assert validate_e15a_feedback_capture_form(form) == []
    fields = form["fields"]
    for key in ["action_id", "ledger_id", "feedback_event_id", "raw_feedback_summary", "feedback_type"]:
        assert key in fields


def test_e15a_feedback_form_rejects_public_evidence_and_fake_no_response() -> None:
    form = build_e15a_feedback_capture_form(build_e15a_owner_execution_console(ROOT))
    assert form["public_evidence_is_not_feedback"] is True
    assert form["no_response_requires_valid_sent_ledger"] is True
    assert form["external_action_executed_by_agent"] is False
