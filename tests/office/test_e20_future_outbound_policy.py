import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_future_outbound_policy_forbids_owner_manual_default():
    data = json.loads((ROOT / "operations/external_validation/e20_future_outbound_policy.json").read_text())
    assert data["owner_manual_send_default_allowed"] is False
    assert "risk_tier_classification" in data["required_sections"]
    assert "provider_capability_status" in data["required_sections"]
    assert data["external_action_executed"] is False
