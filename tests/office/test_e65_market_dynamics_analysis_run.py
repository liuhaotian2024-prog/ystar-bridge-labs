import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_market_dynamics_analysis_run_has_portfolio_rankings_and_uncertainty():
    data = json.loads((ROOT / "operations/external_validation/e65_market_dynamics_analysis_run.json").read_text())
    assert data["analysis_status"] == "completed"
    assert data["analyzed_route_count"] >= 10
    portfolio = data["recommended_portfolio"]
    assert portfolio["primary_route"] == "governed_business_operations_blueprint_for_agent_teams"
    assert portfolio["fallback_route"] == "founder_operator_decision_brief_service"
    assert data["missing_evidence"]
    assert data["customer_validation_claimed"] is False
