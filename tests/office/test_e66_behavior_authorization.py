import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_behavior_authorization_allows_internal_only_and_denies_external_actions():
    data = json.loads((ROOT / "operations/external_validation/e66_behavior_authorization_result.json").read_text())
    assert data["passed"] is True
    assert "E65_model_API_invocation" in data["allowed_actions"]
    assert "outreach" in data["denied_actions"]
    assert "payment" in data["denied_actions"]
    assert data["external_business_execution_authorized"] is False

