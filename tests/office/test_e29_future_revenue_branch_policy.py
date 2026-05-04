import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_future_policy_requires_branch_selection_before_route_assumption():
    data = json.loads((ROOT / "operations/external_validation/e29_future_revenue_branch_policy.json").read_text())
    assert "revenue mode branch check" in data["required_before_route_assumption"]
    assert "production live is always next" in data["future_milestones_must_not_assume"]
    assert data["near_term_shortest_cash_priority_allowed_only_as"] == "branch_scoped_implementation_priority"
    assert data["owner_manual_send_default_allowed"] is False
