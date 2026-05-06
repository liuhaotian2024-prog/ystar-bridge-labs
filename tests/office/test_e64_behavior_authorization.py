import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_behavior_authorization_denies_external_execution():
    data = json.loads((ROOT / "operations/external_validation/e64_behavior_authorization_result.json").read_text())
    assert data["passed"] is True
    assert data["external_business_execution_authorized"] is False
    denied = set(data["denied_actions"])
    assert "outreach" in denied
    assert "publication" in denied
    assert "payment" in denied
    assert "customer_validation_claim" in denied
