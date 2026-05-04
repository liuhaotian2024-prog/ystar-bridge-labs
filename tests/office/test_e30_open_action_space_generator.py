import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_open_action_space_is_not_menu_limited():
    data = json.loads((ROOT / "operations/external_validation/e30_open_commercial_action_space.json").read_text())
    ids = {c["action_id"] for c in data["candidates"]}
    assert data["candidate_action_count"] == 10
    assert "action_paid_readiness_review_signal_package" in ids
    assert "action_secure_production_config_preparation" in ids
    assert "action_governance_audit_sample_teardown" in ids
    assert data["generation_method"].startswith("derived from current state")
