import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_control_room_unifies_audit_canary_and_blockers():
    d=json.loads((ROOT/"operations/external_validation/e26_live_readiness_control_room.json").read_text())
    assert d["existing_wheel_audit_completed_first"] is True
    assert d["one_action_canary_plan"]["canary_executed"] is False
    assert d["live_readiness_validator_result"]["live_ready"] is False
    assert d["owner_manual_send_is_default"] is False
