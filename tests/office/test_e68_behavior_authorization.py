import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_behavior_authorization_allows_internal_eval_and_denies_external_actions():
    data = json.loads((ROOT / "operations/external_validation/e68_behavior_authorization_result.json").read_text())
    assert data["passed"] is True
    assert "controlled_public_read_regulatory_market_evidence_collection" in data["allowed_actions"]
    assert "legal_compliance_claim" in data["denied_actions"]
    assert "outreach" in data["denied_actions"]
    assert data["external_business_execution_authorized"] is False

