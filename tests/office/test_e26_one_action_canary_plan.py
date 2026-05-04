import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_canary_plan_created_but_not_executed():
    d=json.loads((ROOT/"operations/external_validation/e26_one_action_canary_plan.json").read_text())
    assert d["canary_plan_created"] is True
    assert d["canary_executed"] is False
    assert d["customer_contacted"] is False
    assert d["live_receipt_created"] is False
    assert d["owner_approval_required_by_risk"] is False
