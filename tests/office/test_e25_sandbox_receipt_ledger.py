import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_sandbox_receipt_ledger_distinguishes_receipt_types():
    data = json.loads((ROOT / "operations/external_validation/e25_sandbox_receipt_ledger.json").read_text())
    assert data["sandbox_receipt_count"] == 1
    assert data["live_receipt_count"] == 0
    assert data["dry_run_receipt_count"] == 0
    assert data["receipts"][0]["receipt_type"] == "sandbox_receipt"
    assert data["receipts"][0]["not_a_live_receipt"] is True
