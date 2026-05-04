import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_unique_advantage_analysis_names_differentiators_and_gaps():
    data = json.loads((ROOT / "operations/external_validation/e32_unique_advantage_weakness_analysis.json").read_text())
    assert data["strongest_differentiator_count"] >= 7
    assert data["weakness_count"] >= 7
    assert data["credibility_gaps"]
    assert data["packaging_gaps"]
    assert "full GRC platform" in data["where_y_star_should_not_compete_now"]
