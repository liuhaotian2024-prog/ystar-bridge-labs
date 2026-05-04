import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_autonomous_dry_run_control_room_summarizes_execution_without_manual_default():
    data = load("operations/external_validation/e22_autonomous_dry_run_control_room.json")
    assert len(data["dry_run_actions_selected"]) == 5
    assert len(data["dry_run_actions_executed"]) == 5
    assert len(data["blocked_actions"]) == 0
    assert data["dry_run_receipt_ledger_summary"]["live_receipt_count"] == 0
    assert data["owner_manual_send_is_default"] is False
