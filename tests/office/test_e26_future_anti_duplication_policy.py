import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_future_policy_requires_audit_and_live_canary_prereqs():
    d=json.loads((ROOT/"operations/external_validation/e26_future_anti_duplication_policy.json").read_text())
    assert "existing-wheel audit" in d["future_milestone_start_requirements"]
    assert "persistent idempotency persistent_ready" in d["future_live_canary_requirements"]
    assert d["owner_manual_send_default_allowed"] is False
