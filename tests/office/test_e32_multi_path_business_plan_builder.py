import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_multi_path_business_plans_cover_required_strategy_branches():
    data = json.loads((ROOT / "operations/external_validation/e32_multi_path_business_plans.json").read_text())
    assert data["complete_plan_count"] >= 5
    categories = {p["category"] for p in data["plans"]}
    assert "near_term_cash_path" in categories
    assert "governance_infrastructure_path" in categories
    assert "partner_channel_path" in categories
    assert "ceo_agent_runtime_product_path" in categories
