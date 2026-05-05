import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_unique_fitness_is_method_level_not_asset_list_only():
    data = json.loads((ROOT / "operations/external_validation/e32_y_star_unique_fitness_analysis.json").read_text())
    assert "epistemic boundary" in data["strongest_unique_fitness"]
    assert data["weakest_credibility_gap"] == "No external buyer has validated or paid for the MVP yet."
    assert any(f["fitness_id"] == "action_legitimacy" for f in data["unique_fitnesses"])
