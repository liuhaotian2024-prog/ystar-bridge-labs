import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_roadmap_marks_ev5_ev8_future_owner_gated():
    data = json.loads((ROOT / "operations/external_validation/e67_owner_gated_external_validation_roadmap.json").read_text())
    assert len(data["owner_gated_future"]) == 4
    assert all(item["required_owner_approval"] is True for item in data["owner_gated_future"])
    assert data["external_action_allowed"] is False

