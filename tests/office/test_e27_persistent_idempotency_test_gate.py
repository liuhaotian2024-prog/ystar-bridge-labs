import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_live_test_idempotency_ready_but_production_not_ready():
    d = json.loads((ROOT / "operations/external_validation/e27_persistent_idempotency_test_gate.json").read_text())
    assert d["live_test_persistent_ready"] is True
    assert d["production_persistent_ready"] is False
    assert d["store_type"] == "file_backed_json_test_profile"
    assert d["duplicate_protection_passed"] is True
    assert d["corrupted_store_blocked"] is True
    assert d["missing_store_blocked"] is True
    assert "blocks_production_live" in d["production_live_promotion_impact"]
