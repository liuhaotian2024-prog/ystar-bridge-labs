import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_brain_keeps_selected_path_and_updates_bottleneck():
    d = json.loads((ROOT / "operations/external_validation/e27_ceo_brain_portfolio_update.json").read_text())
    assert d["selected_revenue_path"] == "rev_path_readiness_review_ai_consultancies"
    assert d["live_test_readiness"] == "live_test_gate_ready"
    assert d["production_live_readiness"] == "production_live_blocked"
    assert "production_live_blocked" in d["current_strategic_bottleneck"]
    assert d["next_decision_horizon"] == "E28_production_live_configuration_decision_gate_or_evidence_expansion"
