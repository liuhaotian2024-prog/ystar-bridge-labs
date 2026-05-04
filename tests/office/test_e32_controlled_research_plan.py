import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_controlled_research_plan_is_public_bounded_and_safe():
    data = json.loads((ROOT / "operations/external_validation/e32_controlled_research_plan.json").read_text())
    assert data["public_only"] is True
    assert data["no_login"] is True
    assert data["no_forms"] is True
    assert data["bounded_source_count"] == 12
    assert "approved_observation_path" in data
