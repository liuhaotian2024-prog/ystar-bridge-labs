import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_broad_market_universe_has_open_world_and_unique_routes():
    data = json.loads((ROOT / "operations/external_validation/e65_broad_market_universe.json").read_text())
    classifications = {d["AI_non_AI_hybrid_classification"] for d in data["domains"]}
    route_ids = {d["domain_id"] for d in data["domains"]}
    assert data["domain_count"] >= 30
    assert {"AI", "non-AI", "hybrid", "AI-enabled non-AI product"} & classifications
    assert "founder_operator_decision_brief_service" in route_ids
    assert "governed_business_operations_blueprint_for_agent_teams" in route_ids
    assert "AI_agent_company_runtime_harness_deployment_blueprint" in route_ids
