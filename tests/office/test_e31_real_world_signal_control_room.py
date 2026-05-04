import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_control_room_shows_package_and_blockers():
    data = json.loads((ROOT / "operations/external_validation/e31_real_world_signal_control_room.json").read_text())
    assert data["real_public_observation_occurred"] is True
    assert data["sources_observed"] == 8
    assert data["paid_readiness_review_signal_package"] == "created_no_send"
    assert "customer contact" in data["remains_blocked"]
