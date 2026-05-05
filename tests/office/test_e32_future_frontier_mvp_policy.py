import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_future_frontier_mvp_policy_blocks_route_menu_regression():
    data = json.loads((ROOT / "operations/external_validation/e32_future_frontier_mvp_policy.json").read_text())
    policy = " ".join(data["future_policy"])
    assert "ecosystem archaeology" in policy
    assert "world fractures" in policy
    assert "avoid route menus" in policy
