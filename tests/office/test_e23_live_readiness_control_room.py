import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_live_readiness_control_room_keeps_owner_manual_non_default():
    data=load("operations/external_validation/e23_live_readiness_control_room.json")
    assert len(data["dry_run_executed_candidates"]) == 5
    assert data["suppression_registry_status"]["production_suppressed_target_count"] == 1
    assert data["compliance_registry_status"]["owner_approval_required_by_risk_count"] == 0
    assert data["live_promotion_status"]["live_ready"] == 0
    assert data["owner_manual_send_is_default"] is False
