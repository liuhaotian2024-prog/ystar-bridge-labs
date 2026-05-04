import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_control_room_does_not_default_to_owner_manual_send():
    d = json.loads((ROOT / "operations/external_validation/e27_live_test_control_room.json").read_text())
    assert d["existing_wheel_audit_completed_first"] is True
    assert d["live_readiness_validator_v2"]["live_test_gate_ready"] is True
    assert d["live_readiness_validator_v2"]["production_live_ready"] is False
    assert d["owner_manual_send_is_default"] is False
    assert d["owner_approval_required_by_risk"] == 0
