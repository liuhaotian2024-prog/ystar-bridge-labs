from __future__ import annotations

from pathlib import Path

from office.mission_command.e15a_owner_confirmation_packet import build_e15a_owner_send_confirmation_fixture
from office.mission_command.e15a_owner_execution_console import build_e15a_owner_execution_console
from office.mission_command.e15a_target_replacement_router import (
    build_e15a_target_replacement_plan,
    route_e15a_target,
    validate_e15a_target_replacement_plan,
)


ROOT = Path(__file__).resolve().parents[2]


def test_e15a_replacement_plan_keeps_ready_primary_and_has_fallbacks() -> None:
    console = build_e15a_owner_execution_console(ROOT)
    fixture = build_e15a_owner_send_confirmation_fixture(console)
    plan = build_e15a_target_replacement_plan(console, fixture)
    assert validate_e15a_target_replacement_plan(plan) == []
    assert {row["route"] for row in plan["primary_routes"]} == {"keep_primary"}
    assert len(plan["fallback_pool"]) == 2


def test_e15a_router_handles_skipped_suppressed_and_missing_target() -> None:
    console = build_e15a_owner_execution_console(ROOT)
    action = console["primary_actions"][0]
    assert route_e15a_target(action, {"send_status": "skipped_by_owner"})["route"] == "replace_with_fallback"
    assert route_e15a_target(action, {"send_status": "suppressed_by_owner"})["route"] == "suppress_target"
    broken = dict(action)
    broken["message_to_send"] = ""
    assert route_e15a_target(broken, {"send_status": "not_sent"})["route"] == "require_more_research"
