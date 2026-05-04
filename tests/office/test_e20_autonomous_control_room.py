import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_control_room_no_longer_defaults_to_owner_manual_send():
    data = json.loads((ROOT / "operations/external_validation/e20_autonomous_control_room.json").read_text())
    assert data["default_model"] == "agent_autonomous_by_risk_tier_not_owner_manual_by_default"
    assert len(data["actions_agent_could_do_after_provider_implementation"]) >= 1
    assert len(data["actions_requiring_owner_approval"]) == 0
    assert "live provider adapter missing" in data["provider_blockers"]
    assert data["external_action_executed"] is False
