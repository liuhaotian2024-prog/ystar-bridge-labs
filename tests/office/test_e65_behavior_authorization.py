import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_behavior_authorization_denies_external_execution():
    data = json.loads((ROOT / "operations/external_validation/e65_behavior_authorization_result.json").read_text())
    assert data["passed"] is True
    assert data["external_business_execution_authorized"] is False
    denied = set(data["denied_actions"])
    assert "outreach" in denied
    assert "customer_validation_claim" in denied
    assert "paid_signal_claim" in denied
    assert "global_optimality_proven_claim" in denied
