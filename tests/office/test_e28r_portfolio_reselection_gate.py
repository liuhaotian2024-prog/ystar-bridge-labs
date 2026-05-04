import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_portfolio_gate_scopes_production_live_to_active_branch():
    d = json.loads((ROOT / "operations/external_validation/e28r_portfolio_reselection_gate.json").read_text())
    assert d["gate_result"] == "branch_selection_required_before_route_assumption"
    assert d["selected_active_branch"] == "revenue_mode_shortest_cash_path"
    assert d["production_live_configuration_global_default"] is False
    assert d["production_live_recommendation_scope"] == "only_if_revenue_mode_shortest_cash_path_remains_active"
    assert "productization_prototype" in d["valid_alternative_routes"]
