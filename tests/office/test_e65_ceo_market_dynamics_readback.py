import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_ceo_market_dynamics_readback_passes():
    data = json.loads((ROOT / "operations/external_validation/e65_ceo_market_dynamics_readback_smoke_result.json").read_text())
    assert data["passes"] is True
    state = data["observed_state"]
    assert state["primary_route"] == "governed_business_operations_blueprint_for_agent_teams"
    assert state["first_cash_wedge"] == "governed_business_operations_blueprint_for_agent_teams"
    assert state["fallback_route"] == "founder_operator_decision_brief_service"
    assert state["external_action_allowed"] is False
