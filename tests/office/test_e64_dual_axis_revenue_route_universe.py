import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_route_universe_has_market_and_ybridge_axes():
    data = json.loads((ROOT / "operations/external_validation/e64_dual_axis_revenue_route_universe.json").read_text())
    route_ids = {route["route_id"] for route in data["routes"]}
    assert data["route_family_count"] >= 15
    assert data["market_optimal_route_count"] >= 10
    assert data["YBridge_unique_route_count"] + data["hybrid_route_count"] >= 10
    assert "founder_operator_decision_brief_service" in route_ids
    assert "AI_agent_company_runtime_harness_deployment_blueprint" in route_ids
    assert "governed_business_operations_blueprint_for_agent_teams" in route_ids
