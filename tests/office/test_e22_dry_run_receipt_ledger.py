import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_dry_run_receipt_ledger_has_no_live_receipts():
    data = load("operations/external_validation/e22_dry_run_receipt_ledger.json")
    assert data["dry_run_receipt_count"] == 5
    assert data["live_receipt_count"] == 0
    assert data["replay_receipt_count"] == 1
    for row in data["ledger_entries"]:
        assert row.get("real_message_sent") is False
        assert row.get("live_receipt_created") is False
