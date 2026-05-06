import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_selected_route_confirmed_by_model_outputs():
    data = json.loads((ROOT / "operations/external_validation/e66_model_driven_selected_route_decision.json").read_text())
    assert data["decision"] == "confirm_E65_route"
    assert data["selected_route_for_blueprint"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["selected_route_changed"] is False
    assert data["decision_stability_score"] == 60.0

