import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_installed_capability_inventory_shows_ceo_can_use_e65_e67_e68_e66():
    data = json.loads((ROOT / "operations/external_validation/e69_ceo_installed_capability_inventory.json").read_text())
    assert data["all_required_capabilities_available_to_CEO"] is True
    caps = {item["source"]: item for item in data["capabilities"]}
    assert {"E65", "E67", "E68", "E66"}.issubset(caps)
    assert all(item["can_influence_next_action_selection"] for item in data["capabilities"])

