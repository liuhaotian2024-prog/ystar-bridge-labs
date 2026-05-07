import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_owner_decision_packet_is_not_approval():
    data = json.loads((ROOT / "operations/external_validation/e70_owner_decision_packet_no_execution.json").read_text())
    assert data["packet_status"] == "owner_reviewable_no_execution"
    assert data["not_owner_approval"] is True
    assert "approve executing generated Codex job proposal as E71" in data["owner_choices"]
    assert "external skill installation" in data["actions_remaining_prohibited"]
    assert data["external_action_allowed"] is False
