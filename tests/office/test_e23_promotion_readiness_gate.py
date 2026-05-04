import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_promotion_readiness_gate_blocks_live_for_provider_and_tests():
    data=load("operations/external_validation/e23_promotion_readiness_gate.json")
    counts=data["counts"]
    assert counts["live_ready"] == 0
    assert counts["live_blocked_provider_disabled"] == 7
    assert counts["live_blocked_missing_live_tests"] == 7
    assert counts["live_blocked_owner_approval_required_by_risk"] == 0
    assert any("live_blocked_suppression" in row["statuses"] for row in data["rows"])
