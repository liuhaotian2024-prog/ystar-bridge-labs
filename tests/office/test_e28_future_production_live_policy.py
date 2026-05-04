import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_future_policy_requires_audit_no_secrets_and_risk_bound_owner_check():
    d = json.loads((ROOT / "operations/external_validation/e28_future_production_live_policy.json").read_text())
    assert "existing-wheel audit" in d["every_future_production_live_milestone_must_start_with"]
    assert "secure credential-source contract" in d["future_production_live_configuration_or_canary_requirements"]
    assert "no committed secrets proof" in d["future_production_live_configuration_or_canary_requirements"]
    assert d["owner_manual_send_default_allowed"] is False
