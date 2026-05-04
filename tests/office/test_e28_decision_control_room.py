import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_control_room_has_decision_without_owner_manual_default():
    d = json.loads((ROOT / "operations/external_validation/e28_decision_control_room.json").read_text())
    assert d["existing_wheel_audit_completed_first"] is True
    assert d["production_live_decision_gate"]["recommended_route"] == "proceed_to_secure_production_config_preparation"
    assert d["production_live_blocker_matrix"]["production_live_ready"] is False
    assert d["owner_manual_send_is_default"] is False
    assert d["owner_approval_required_by_risk"] == 0
