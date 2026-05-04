import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_e22_route_decision_recommends_live_provider_enablement_after_dry_run():
    data = load("operations/external_validation/e22_route_decision_packet.json")
    assert data["recommended_route"] == "E23_live_provider_enablement_plan"
    assert data["dry_run_executed_count"] == 5
    assert data["live_blocked_count"] == 7
    assert data["keep_live_send_blocked"] is True
