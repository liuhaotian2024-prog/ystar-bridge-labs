import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_ceo_brain_updates_bottleneck_without_canonical_truth_write():
    data = json.loads((ROOT / "operations/external_validation/e25_ceo_brain_update.json").read_text())
    assert data["state_type"] == "working_shadow_not_canonical_truth"
    assert data["selected_revenue_path_after_sandbox"] == "rev_path_readiness_review_ai_consultancies"
    assert "live remains blocked" in data["current_strategic_bottleneck"]
    assert data["truth_boundaries"]["market_truth"] == "not claimed"
