import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_world_fracture_map_names_institutional_void_and_buyer_pain():
    data = json.loads((ROOT / "operations/external_validation/e32_world_fracture_institutional_void_map.json").read_text())
    assert data["primary_fracture"] == "agent_action_legitimacy_gap"
    assert "intent" in data["institutional_void"]
    assert "authorized" in data["urgent_buyer_pain"]
    assert data["public_research_is_not_customer_validation"] is True
