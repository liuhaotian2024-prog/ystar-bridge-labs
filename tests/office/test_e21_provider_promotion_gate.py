import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e21_promotion_gate_blocks_live_until_live_ready():
    data = json.loads((ROOT / "operations/external_validation/e21_provider_promotion_gate.json").read_text())
    assert data["promotion_allowed_count"] == 0
    assert data["promotion_blocked_count"] == 7
    assert data["live_execution_enabled_in_e21"] is False
    assert any("live_provider_scaffolded_but_disabled" in row["reason_codes"] for row in data["rows"])
    assert data["external_action_executed"] is False
