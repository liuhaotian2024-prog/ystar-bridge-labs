from __future__ import annotations

from pathlib import Path

from office.mission_command.e15a_owner_confirmation_packet import (
    build_e15a_owner_send_confirmation_fixture,
    build_e15a_owner_send_confirmation_template,
    validate_e15a_owner_send_confirmation_fixture,
)
from office.mission_command.e15a_owner_execution_console import build_e15a_owner_execution_console


ROOT = Path(__file__).resolve().parents[2]


def test_e15a_confirmation_template_supports_sent_skipped_replaced_suppressed() -> None:
    console = build_e15a_owner_execution_console(ROOT)
    template = build_e15a_owner_send_confirmation_template(console)
    status_values = set(template["status_values"])
    assert {"not_sent", "sent_confirmed_by_owner", "skipped_by_owner", "replaced_by_fallback", "suppressed_by_owner"} <= status_values
    assert template["external_action_executed_by_agent"] is False


def test_e15a_confirmation_fixture_never_fakes_sent() -> None:
    console = build_e15a_owner_execution_console(ROOT)
    fixture = build_e15a_owner_send_confirmation_fixture(console)
    assert validate_e15a_owner_send_confirmation_fixture(fixture) == []
    assert fixture["sent_confirmed_by_owner"] is False
    assert fixture["awaiting_owner_confirmation"] is True
    assert all(row["send_status"] == "not_sent" for row in fixture["rows"])
