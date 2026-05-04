import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_future_ceo_learning_policy_blocks_hardcoded_route_menus():
    data = json.loads((ROOT / "operations/external_validation/e32_future_ceo_learning_policy.json").read_text())
    policy = " ".join(data["future_policy"])
    assert "controlled real-world research" in policy
    assert "separate public evidence from customer feedback" in policy
    assert "avoid hardcoded route menus" in policy
