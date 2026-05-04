import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_future_policy_preserves_audit_and_no_owner_manual_default():
    d = json.loads((ROOT / "operations/external_validation/e27_future_live_test_canary_policy.json").read_text())
    assert "existing-wheel audit" in d["every_future_milestone_must_start_with"]
    assert "production persistent idempotency ready" in d["future_live_canary_requirements"]
    assert d["owner_manual_send_default_allowed"] is False
