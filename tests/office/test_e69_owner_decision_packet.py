import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_owner_decision_packet_is_not_approval_and_no_execution():
    data = json.loads((ROOT / "operations/external_validation/e69_owner_decision_packet_no_execution.json").read_text())
    assert data["packet_status"] == "owner_reviewable_no_execution"
    assert data["not_owner_approval"] is True
    assert "approve internal CIEU module integration" in data["owner_choices"]
    assert "outreach" in data["exact_actions_remain_prohibited"]
    assert data["owner_decision_status"] == "pending_owner_decision"
    assert data["external_action_allowed"] is False

