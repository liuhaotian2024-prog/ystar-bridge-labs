import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_route_decision_recommends_manual_batch_ready_and_blocks_provider_send():
    data = json.loads((ROOT / "operations/external_validation/e18_route_decision_packet.json").read_text())
    assert data["recommended_route"] == "manual_send_batch_ready"
    assert data["real_provider_send_blocked"] is True
    assert "keep_real_provider_send_blocked" in data["route_options"]
    assert data["external_action_executed"] is False
