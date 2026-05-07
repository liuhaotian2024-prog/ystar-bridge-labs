import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_archaeology_reuses_existing_assets_and_discovers_creed():
    data = json.loads((ROOT / "operations/external_validation/e70_self_bootstrap_repository_archaeology_inventory.json").read_text())
    assert data["old_self_evolution_creed_assets"]["creed_discovered"] is True
    assert data["old_self_evolution_creed_assets"]["commit_available_in_local_history"] is True
    assert "office/mission_command/e69_ceo_next_action_planner.py" in data["E69_autonomous_next_action_planner_assets_reused"]
    assert "E69 business planner generated next actions but not self-improvement candidates" in data["disconnected_self_improvement_assets"]
    assert "E65 market dynamics model" in data["what_must_not_be_rebuilt"]
