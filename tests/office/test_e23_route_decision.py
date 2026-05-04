import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_route_decision_recommends_sandbox_enablement_and_keeps_live_blocked():
    data=load("operations/external_validation/e23_route_decision_packet.json")
    assert data["recommended_route"] == "E24_live_provider_sandbox_enablement"
    assert data["live_ready_count"] == 0
    assert data["live_blocked_provider_disabled"] == 7
    assert data["keep_live_send_blocked"] is True
