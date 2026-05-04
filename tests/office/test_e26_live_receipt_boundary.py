import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_live_receipt_boundary_creates_no_live_receipts():
    d=json.loads((ROOT/"operations/external_validation/e26_live_receipt_boundary.json").read_text())
    assert d["live_receipts_created_count"]==0
    assert d["dry_run_cannot_create_live_receipt"] is True
    assert d["sandbox_cannot_create_live_receipt"] is True
    assert d["live_receipt_requires_external_effect_true"] is True
