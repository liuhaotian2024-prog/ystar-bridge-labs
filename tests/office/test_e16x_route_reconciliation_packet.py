from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16x_route_reconciliation_packet.json").read_text())


def test_e16x_route_reconciliation_recommends_gov_mcp_promotion_first() -> None:
    data = load()
    assert data["recommended_route"] == "E16G_cross_repo_gov_mcp_adapter_promotion_first"
    assert data["secondary_route"] == "E16B_owner_manual_send_first"
    assert data["e16c0_should_proceed"] is False
    assert "dry-run only" in data["e16c0_reconciliation"]


def test_e16x_route_packet_preserves_no_real_send_boundary() -> None:
    routes = load()["routes"]
    assert routes["E16C1_owner_activated_one_action_send_gated_pilot"]["status"] == "blocked_now"
    assert "real send before promotion" in routes["E16G_cross_repo_gov_mcp_adapter_promotion_first"]["blocked_actions"]
