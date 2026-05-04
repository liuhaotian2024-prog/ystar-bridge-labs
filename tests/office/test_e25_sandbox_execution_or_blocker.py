import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_sandbox_execution_has_no_external_effect_and_no_live_receipt():
    data = json.loads((ROOT / "operations/external_validation/e25_sandbox_execution_results.json").read_text())
    assert data["sandbox_executed_count"] == 1
    assert data["sandbox_blocked_count"] == 0
    assert data["live_receipt_count"] == 0
    row = data["execution_results"][0]
    assert row["no_external_effect"] is True
    assert row["provider_api_called"] is False
    assert row["live_receipt_created"] is False
