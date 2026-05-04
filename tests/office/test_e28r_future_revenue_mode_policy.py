import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_future_policy_requires_branch_selection_first():
    d = json.loads((ROOT / "operations/external_validation/e28r_future_revenue_mode_policy.json").read_text())
    assert "revenue mode branch registry review" in d["required_before_route_assumption"]
    assert "route decision with valid alternatives" in d["required_before_route_assumption"]
    assert d["production_live_config_may_be_recommended_only_if"].startswith("the selected active branch")
    assert d["owner_manual_send_default_allowed"] is False
