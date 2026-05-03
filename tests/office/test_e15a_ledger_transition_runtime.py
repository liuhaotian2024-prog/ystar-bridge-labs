from __future__ import annotations

from pathlib import Path

from office.mission_command.e15a_ledger_transition_runtime import (
    build_e15a_ledger_state_after_owner_handoff,
    build_e15a_ledger_transition_template,
    validate_e15a_ledger_state_after_owner_handoff,
)
from office.mission_command.e15a_owner_confirmation_packet import build_e15a_owner_send_confirmation_fixture
from office.mission_command.e15a_owner_execution_console import build_e15a_owner_execution_console


ROOT = Path(__file__).resolve().parents[2]


def test_e15a_ledger_template_has_required_transitions() -> None:
    template = build_e15a_ledger_transition_template()
    transitions = set(template["transitions"])
    assert "owner_handoff_ready -> waiting_owner_send" in transitions
    assert "waiting_owner_send -> sent_confirmed_by_owner" in transitions
    assert "feedback_received -> requires_offer_revision" in transitions
    assert template["no_fake_sent"] is True


def test_e15a_ledger_state_only_moves_to_waiting_owner_send() -> None:
    console = build_e15a_owner_execution_console(ROOT)
    fixture = build_e15a_owner_send_confirmation_fixture(console)
    state = build_e15a_ledger_state_after_owner_handoff(console, fixture)
    assert validate_e15a_ledger_state_after_owner_handoff(state) == []
    assert {row["state"] for row in state["rows"]} == {"waiting_owner_send"}
    assert all(row["sent_confirmed_by_owner"] is False for row in state["rows"])
