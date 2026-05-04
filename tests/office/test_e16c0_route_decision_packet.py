from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def route() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16c0_route_decision_packet.json").read_text())


def test_route_recommends_manual_send_as_shortest_cash_path() -> None:
    data = route()
    assert data["current_route_completed"] == "E16C0_revised_one_action_send_gated_pilot_dry_run_only"
    assert data["recommended_next_route"] == "E16B_owner_manual_send_first"
    assert data["route_options"]["E16B_owner_manual_send_first"]["status"] == "recommended_shortest_cash_path"


def test_e16c1_real_send_remains_blocked() -> None:
    data = route()
    blocked = data["route_options"]["E16C1_one_action_send_gated_pilot_after_explicit_owner_activation"]
    assert data["e16c1_real_send_blocked"] is True
    assert blocked["status"] == "blocked_until_conditions_met"
    assert "explicit owner activation" in blocked["required_before_start"]
    assert data["external_action_executed"] is False
