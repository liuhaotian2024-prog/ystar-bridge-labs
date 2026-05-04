import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_guardrail_preserves_route_alternatives_and_triggers():
    data = json.loads((ROOT / "operations/external_validation/e29_multi_branch_portfolio_guardrail.json").read_text())
    assert data["shortest_cash_path_is_not_permanent_architecture"] is True
    assert data["production_live_is_not_global_default"] is True
    assert "new_customer_feedback" in data["branch_re_evaluation_triggers"]
    assert "productization_prototype" in data["route_alternatives_preserved"]
