import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e21_control_room_shows_dry_run_available_but_live_blocked():
    data = json.loads((ROOT / "operations/external_validation/e21_autonomous_provider_control_room.json").read_text())
    assert data["owner_manual_send_is_default"] is False
    assert len(data["dry_run_available_actions"]) == 5
    assert len(data["live_scaffolded_but_disabled_actions"]) == 5
    assert len(data["live_ready_actions"]) == 0
    assert data["live_send_blocked_reason"] == "live_provider_scaffolded_but_disabled"
    assert data["external_action_executed"] is False
