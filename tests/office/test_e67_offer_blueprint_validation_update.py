import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_offer_update_keeps_blueprint_internal_and_owner_gated():
    data = json.loads((ROOT / "operations/external_validation/e67_offer_blueprint_validation_update.json").read_text())
    assert data["claims_remain_prohibited"]
    assert "customer validation" in data["claims_remain_prohibited"]
    assert data["external_action_allowed"] is False
    assert (ROOT / "products/governed_business_operations_blueprint_for_agent_teams/external_validation_update.md").exists()

