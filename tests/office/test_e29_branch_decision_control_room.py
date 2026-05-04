import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_control_room_reports_route_without_external_action():
    data = json.loads((ROOT / "operations/external_validation/e29_branch_decision_control_room.json").read_text())
    assert data["selected_active_branch"] == "revenue_mode_shortest_cash_path"
    assert data["selected_branch_route"] == "secure_production_config_preparation"
    assert data["owner_manual_send_default"] is False
    assert data["external_action_executed"] is False
