from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16g_risk_capability_execution_mapping.json").read_text())


def test_e16g_maps_capability_level_5_to_risk_tier_2_for_low_risk_validation() -> None:
    mapping = load()["external_validation_message_mapping"]
    assert mapping["capability_level"] == "LEVEL_5_EXTERNAL_VALIDATION_MESSAGING_WITHIN_ENVELOPE"
    assert mapping["risk_tier"] == "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"
    assert "no payment/account/form/login/publication" in mapping["conditions"]


def test_e16g_canonicalizes_execution_mode_alias() -> None:
    data = load()
    assert data["canonical_execution_mode"] == "gov_mcp_execute_after_activation"
    assert data["legacy_aliases"]["mcp_execute_after_activation"] == "gov_mcp_execute_after_activation"
    assert data["feedback_cieu_eligibility"]["core_cieu_writeback"] == "hard_gated"
