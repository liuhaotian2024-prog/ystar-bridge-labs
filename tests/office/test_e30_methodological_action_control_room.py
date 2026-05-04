import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_control_room_says_why_not_hardcoded():
    data = json.loads((ROOT / "operations/external_validation/e30_methodological_action_control_room.json").read_text())
    assert data["selected_route"] == "paid_readiness_review_signal_package"
    assert data["generated_action_space_count"] == 10
    assert "scored as candidates" in data["why_not_hardcoded"]
    assert data["owner_or_security_approval_required_now"] is False
    assert data["production_live_remains_disabled"] is True
