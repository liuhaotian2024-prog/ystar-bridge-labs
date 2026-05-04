import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_control_room_consolidates_batch_kpi_and_ecosystem_state():
    data = json.loads((ROOT / "operations/external_validation/e19_revenue_validation_control_room.json").read_text())
    assert data["control_room_type"] == "single_owner_revenue_validation_surface"
    assert data["batch_id"] == "e18_first_revenue_validation_batch"
    assert data["kpi_state"]["target_count"] >= 7
    assert data["ecosystem_alignment_state"]
    assert "approve_manual_send_for_candidate" in data["owner_decision_options"]
    assert data["external_action_executed"] is False


def test_control_room_markdown_is_owner_readable():
    text = (ROOT / "operations/external_validation/e19_revenue_validation_control_room.md").read_text()
    assert "E19 Revenue Validation Control Room" in text
    assert "Owner Decisions" in text
    assert "Candidates" in text
