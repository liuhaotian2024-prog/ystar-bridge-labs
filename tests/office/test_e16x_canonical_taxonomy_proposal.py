from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16x_canonical_taxonomy_proposal.json").read_text())


def test_e16x_taxonomy_separates_capability_level_from_risk_tier() -> None:
    data = load()
    mapping = data["canonical_mapping"]["external_validation_message"]
    assert mapping["capability_level"] == "LEVEL_5_EXTERNAL_VALIDATION_MESSAGING_WITHIN_ENVELOPE"
    assert mapping["risk_tier_when_low_volume_transparent_non_binding"] == "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"


def test_e16x_taxonomy_normalizes_execution_mode_alias() -> None:
    data = load()
    assert "gov_mcp_execute_after_activation" in data["execution_mode"]
    assert data["execution_mode_aliases"]["mcp_execute_after_activation"] == "gov_mcp_execute_after_activation"
    assert "TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK" in data["risk_tier"]
