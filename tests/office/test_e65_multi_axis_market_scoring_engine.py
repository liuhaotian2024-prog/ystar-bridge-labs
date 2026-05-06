import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_multi_axis_scoring_engine_has_profiles_and_axes():
    data = json.loads((ROOT / "operations/external_validation/e65_multi_axis_market_scoring_engine.json").read_text())
    assert data["axis_count"] >= 14
    profiles = set(data["allowed_weight_profiles"])
    assert "fastest_cash_profile" in profiles
    assert "strategic_defensibility_profile" in profiles
    assert "balanced_CEO_profile" in profiles
    assert "owner_preference_override_profile" in profiles
