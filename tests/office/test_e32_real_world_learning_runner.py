import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_real_world_learning_executed_without_side_effects():
    data = json.loads((ROOT / "operations/external_validation/e32_real_world_learning_run.json").read_text())
    assert data["learning_status"] == "executed"
    assert data["source_count"] == 12
    assert data["receipt_count"] == 12
    assert data["no_customer_contact"] is True
    assert data["no_message_sent"] is True
    assert data["external_side_effects"] is False
    assert data["production_live_receipt_count"] == 0
