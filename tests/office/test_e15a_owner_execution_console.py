from __future__ import annotations

from pathlib import Path

from office.mission_command.e15a_owner_execution_console import (
    build_e15a_owner_execution_console,
    validate_e15a_owner_execution_console,
)


ROOT = Path(__file__).resolve().parents[2]


def test_e15a_console_reuses_c3_batch_ids_and_targets() -> None:
    console = build_e15a_owner_execution_console(ROOT)
    assert validate_e15a_owner_execution_console(console) == []
    assert console["primary_action_count"] == 3
    assert console["fallback_action_count"] == 2
    assert {item["role"] for item in console["primary_actions"]} == {"primary"}
    assert all(item["action_id"].startswith("c2_action_primary_") for item in console["primary_actions"])


def test_e15a_console_is_owner_executable_not_agent_send() -> None:
    console = build_e15a_owner_execution_console(ROOT)
    assert console["external_action_executed_by_agent"] is False
    assert "Aiden autonomous send" in console["not_approved"]
    first = console["primary_actions"][0]
    assert "copy" not in first["owner_minimal_fill_after_action"]["send_status"].lower()
    assert first["message_to_send"].startswith("Subject:")
    assert "AI-assisted" in first["message_to_send"]
