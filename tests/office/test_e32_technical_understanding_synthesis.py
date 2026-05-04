import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_technical_synthesis_connects_market_learning_to_y_star_capabilities():
    data = json.loads((ROOT / "operations/external_validation/e32_technical_understanding_synthesis.json").read_text())
    assert data["key_technical_insight_count"] >= 7
    assert any("CEO KG" in item for item in data["strongest_y_star_technical_advantages"])
    assert "hosted product UX" in data["technical_capability_map"]["weak"]
    assert data["technical_claims_blocked"]
