import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_validator_v2_separates_live_test_gate_from_production_live():
    d = json.loads((ROOT / "operations/external_validation/e27_live_readiness_validator_v2.json").read_text())
    assert d["dry_run_ready"] is True
    assert d["sandbox_ready"] is True
    assert d["live_test_gate_ready"] is True
    assert d["production_live_ready"] is False
    assert "production_live_enabled_false" in d["production_live_blocked_reasons"]
    assert "production_persistent_idempotency_not_configured" in d["production_live_blocked_reasons"]
