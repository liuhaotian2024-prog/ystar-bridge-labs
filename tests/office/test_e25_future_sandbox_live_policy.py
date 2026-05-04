import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_future_sandbox_live_policy_requires_kg_feedback_and_no_external_effect():
    data = json.loads((ROOT / "operations/external_validation/e25_future_sandbox_live_policy.json").read_text())
    req = data["future_sandbox_live_milestone_requirements"]
    assert "CEO KG route selection" in req
    assert "sandbox receipt ledger" in req
    assert "CEO brain update" in req
    assert data["owner_manual_send_default_allowed"] is False
    assert data["live_requires_explicit_provider_enablement_and_tests"] is True
