import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_behavior_authorization_denies_human_and_paid_validation_actions():
    data = json.loads((ROOT / "operations/external_validation/e67_behavior_authorization_result.json").read_text())
    assert data["passed"] is True
    assert "non_contact_public_read_validation" in data["allowed_actions"]
    assert "customer_validation_claim" in data["denied_actions"]
    assert "EV5_EV6_EV7_EV8_achieved_claim" in data["denied_actions"]
    assert data["external_business_execution_authorized"] is False

