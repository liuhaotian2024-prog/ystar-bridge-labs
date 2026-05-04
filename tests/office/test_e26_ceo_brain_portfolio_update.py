import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_ceo_brain_updates_bottleneck_and_keeps_path_selected():
    d=json.loads((ROOT/"operations/external_validation/e26_ceo_brain_portfolio_update.json").read_text())
    assert d["state_type"]=="working_shadow_not_canonical_truth"
    assert d["selected_revenue_path"]=="rev_path_readiness_review_ai_consultancies"
    assert "live canary is planned but blocked" in d["current_strategic_bottleneck"]
    assert d["portfolio_update"]["selected_path_remains_selected"] is True
