import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_offer_blueprint_is_internal_draft_for_selected_route():
    data = json.loads((ROOT / "operations/external_validation/e66_selected_route_offer_blueprint.json").read_text())
    assert data["offer_identity"]["offer_name"] == "Governed Business Operations Blueprint for Agent Teams"
    assert data["offer_identity"]["selected_route"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["offer_identity"]["status"] == "draft_only_internal"
    assert data["customer_validation_claimed"] is False
    assert data["pricing_validation_claimed"] is False

