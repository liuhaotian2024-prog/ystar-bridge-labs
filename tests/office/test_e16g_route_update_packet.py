from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16g_e16_route_update_packet.json").read_text())


def test_e16g_route_update_moves_to_revised_dry_run_only_e16c0() -> None:
    data = load()
    assert data["prior_recommended_route"] == "E16G_cross_repo_gov_mcp_adapter_promotion_first"
    assert data["recommended_next_route"] == "E16C0_revised_one_action_send_gated_pilot_dry_run_only"
    assert data["secondary_route"] == "E16B_owner_manual_send_first"


def test_e16g_route_update_blocks_real_send_and_e16c1_now() -> None:
    blocked = load()["blocked_routes"]
    assert "E16C1_owner_activated_one_action_send_gated_pilot" in blocked
    assert blocked["real_provider_send"] == "blocked; no real provider adapter call in E16G"
