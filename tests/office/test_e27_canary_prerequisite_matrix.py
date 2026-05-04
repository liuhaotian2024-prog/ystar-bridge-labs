import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_canary_matrix_is_created_not_executed():
    d = json.loads((ROOT / "operations/external_validation/e27_canary_prerequisite_matrix.json").read_text())
    assert d["canary_matrix_created"] is True
    assert d["canary_executed"] is False
    assert d["production_live_enabled"] is False
    assert d["production_live_receipt_count"] == 0
    assert d["real_customer_contact"] is False
    assert d["live_ready_action_count"] == 0
    assert d["live_blocked_action_count"] == 1
