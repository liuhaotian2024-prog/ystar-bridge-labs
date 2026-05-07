import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_scorecards_mark_ev5_ev8_unachieved_owner_gated():
    data = json.loads((ROOT / "operations/external_validation/e67_route_external_validation_scorecards.json").read_text())
    assert data["route_count"] >= 5
    assert data["EV5_EV8_achieved"] is False
    primary = next(card for card in data["scorecards"] if card["route_id"] == "governed_business_operations_blueprint_for_agent_teams")
    assert primary["EV5_plus_blocked_owner_gated_status"] == "EV5_EV6_EV7_EV8_unachieved_owner_gated"
    assert "EV7 paid signal" in primary["missing_evidence"]

