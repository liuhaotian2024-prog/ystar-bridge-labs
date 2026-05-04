import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_sandbox_control_room_is_single_decision_surface_not_manual_send_default():
    data = json.loads((ROOT / "operations/external_validation/e25_sandbox_control_room.json").read_text())
    assert data["control_room_type"] == "ceo_kg_provider_sandbox_feedback_loop"
    assert data["sandbox_execution_result"]["executed"] == 1
    assert data["sandbox_execution_result"]["live_receipts"] == 0
    assert data["owner_manual_send_is_default"] is False
    assert data["owner_approval_required_by_risk"] == []
