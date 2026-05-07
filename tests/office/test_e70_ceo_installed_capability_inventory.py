import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_capability_inventory_includes_self_bootstrap_sources():
    data = json.loads((ROOT / "operations/external_validation/e70_ceo_installed_capability_inventory.json").read_text())
    names = {item["capability"] for item in data["capabilities"]}
    assert data["all_required_capabilities_available_to_CEO"] is True
    assert {"autonomous_next_action_planning", "self_evolution_creed", "Codex_bridge_job_proposal"}.issubset(names)
    assert any(item["can_influence_capability_growth_selection"] for item in data["capabilities"])
