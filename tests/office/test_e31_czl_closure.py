import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_czl_closure_proves_no_contact_or_live_side_effects():
    data = json.loads((ROOT / "operations/external_validation/e31_czl_closure.json").read_text())
    assert data["real_world_observation_status"] == "executed"
    assert data["customer_contact_occurred"] is False
    assert data["message_sent"] is False
    assert data["production_live_enabled"] is False
    assert data["production_live_receipt_count"] == 0
    assert data["fake_evidence_created"] is False
