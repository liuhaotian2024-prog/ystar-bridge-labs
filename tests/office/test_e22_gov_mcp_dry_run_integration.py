import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_gov_mcp_dry_run_integration_generates_no_effect_receipts():
    data = load("operations/external_validation/e22_gov_mcp_dry_run_results.json")
    assert data["integration_mode"] == "direct_gov_mcp_import"
    assert data["dry_run_executed_count"] == 5
    assert data["dry_run_blocked_count"] == 0
    for row in data["dry_run_results"]:
        assert row["dry_run_executed"] is True
        assert row["receipt_type"] == "dry_run_receipt"
        assert row["provider_mode"] == "dry_run"
        assert row["external_provider_called"] is False
        assert row["real_message_sent"] is False
        assert row["live_receipt_created"] is False
