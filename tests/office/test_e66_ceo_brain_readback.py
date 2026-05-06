import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_ceo_brain_readback_sees_model_driven_offer_state():
    data = json.loads((ROOT / "operations/external_validation/e66_ceo_brain_readback_smoke_result.json").read_text())
    assert data["passes"] is True
    observed = data["observed_state"]
    assert observed["E65_model_API_invoked"] is True
    assert observed["selected_route"] == "governed_business_operations_blueprint_for_agent_teams"
    assert observed["offer_name"] == "Governed Business Operations Blueprint for Agent Teams"

