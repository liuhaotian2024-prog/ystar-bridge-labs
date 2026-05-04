from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(name: str) -> dict:
    return json.loads((ROOT / "operations/external_validation" / name).read_text())


def test_e16c0_selects_exactly_one_lowest_risk_action() -> None:
    data = load("e16c0_selected_one_action_pilot.json")
    action = data["selected_action"]
    assert data["selected_action_count"] == 1
    assert action["action_id"] == "c2_action_primary_001_cand_alicelabs_alicelabs"
    assert action["capability_domain"] == "external_validation_message"
    assert action["capability_level"] == 5
    assert action["risk_tier"] == "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"
    assert action["target_identity_sufficient"] is True
    assert len(action["idempotency_key"]) == 64
    assert data["external_action_executed"] is False


def test_e16c0_preserves_not_selected_queue_actions() -> None:
    data = load("e16c0_selected_one_action_pilot.json")
    assert len(data["not_selected_action_ids"]) == 2
    assert "c2_action_primary_002_cand_botsquash_botsquash" in data["not_selected_action_ids"]
