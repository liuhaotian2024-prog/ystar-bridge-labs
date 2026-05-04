import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_commercial_route_recommends_owner_manual_batch_and_blocks_provider_send():
    data = json.loads((ROOT / "operations/external_validation/e19_commercial_route_decision_packet.json").read_text())
    assert data["recommended_route"] == "E19_owner_manual_batch_ready"
    assert data["real_provider_send_blocked"] is True
    assert "E20_real_feedback_import_loop" in data["route_options"]
    assert data["external_action_executed"] is False
