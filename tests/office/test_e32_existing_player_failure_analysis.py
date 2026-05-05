import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_existing_player_failure_analysis_covers_fragmentation_gap():
    data = json.loads((ROOT / "operations/external_validation/e32_existing_player_failure_analysis.json").read_text())
    categories = {p["category"] for p in data["player_categories"]}
    assert "agent_frameworks" in categories
    assert "observability_evaluation_vendors" in categories
    assert "identity_security_vendors" in categories
    assert "intent to action" in data["core_failure_summary"]
