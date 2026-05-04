import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_brain_update_keeps_revenue_path_and_sets_next_horizon():
    d = json.loads((ROOT / "operations/external_validation/e28_ceo_brain_portfolio_update.json").read_text())
    assert d["selected_revenue_path"] == "rev_path_readiness_review_ai_consultancies"
    assert d["production_live_configuration_decision"] == "proceed_to_secure_production_config_preparation"
    assert d["provider_category_recommendation"] == "email_provider_adapter"
    assert "production_live_config_preparation" in d["current_strategic_bottleneck"]
    assert d["next_decision_horizon"] == "E29_secure_production_config_preparation_or_owner_defers_to_evidence_expansion"
