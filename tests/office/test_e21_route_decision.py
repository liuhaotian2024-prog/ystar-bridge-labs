import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e21_route_decision_recommends_autonomous_dry_run_batch_before_live():
    data = json.loads((ROOT / "operations/external_validation/e21_route_decision_packet.json").read_text())
    assert data["recommended_route"] == "E22_autonomous_dry_run_batch_execution"
    assert data["dry_run_available_count"] == 5
    assert data["promotion_allowed_count"] == 0
    assert data["keep_live_send_blocked"] is True
    assert data["external_action_executed"] is False
