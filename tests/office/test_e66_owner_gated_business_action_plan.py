import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_owner_gated_plan_blocks_external_execution():
    data = json.loads((ROOT / "operations/external_validation/e66_owner_gated_business_action_plan_no_execution.json").read_text())
    assert "external review" in data["requires_owner_approval"]
    assert "payment/invoice" in data["requires_owner_approval"]
    assert data["external_action_allowed"] is False
    assert data["owner_decision_status"] == "pending_owner_decision"

