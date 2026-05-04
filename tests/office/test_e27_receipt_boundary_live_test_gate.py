import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_live_test_receipt_is_distinct_and_no_production_live_receipts_exist():
    d = json.loads((ROOT / "operations/external_validation/e27_receipt_boundary_live_test_gate.json").read_text())
    assert d["receipt_boundary_ready"] is True
    assert d["live_test_receipt_distinct_from_production_live_receipt"] is True
    assert d["live_test_receipt_count"] == 1
    assert d["production_live_receipt_count"] == 0
    assert d["live_test_receipt_external_effect"] is False
