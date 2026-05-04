import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_blocker_matrix_keeps_production_live_disabled_and_receipts_zero():
    d = json.loads((ROOT / "operations/external_validation/e28_production_live_blocker_matrix.json").read_text())
    assert d["production_live_ready"] is False
    assert d["production_live_enabled"] is False
    assert d["production_live_receipt_count"] == 0
    assert "production_live_enabled_false" in d["primary_blockers"]
    assert "real_feedback_evidence_absent" in d["primary_blockers"]
