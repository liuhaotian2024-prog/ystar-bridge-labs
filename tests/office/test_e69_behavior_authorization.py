import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_behavior_authorization_denies_external_and_claim_actions():
    data = json.loads((ROOT / "operations/external_validation/e69_behavior_authorization_result.json").read_text())
    assert data["passed"] is True
    assert "internal_next_action_candidate_generation" in data["allowed_actions"]
    assert "outreach" in data["denied_actions"]
    assert "owner_approval_fabrication" in data["denied_actions"]
    assert "legal_compliance_claim" in data["denied_actions"]
    assert data["external_business_execution_authorized"] is False

