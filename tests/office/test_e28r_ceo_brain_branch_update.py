import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_brain_tracks_active_backup_deferred_and_scope():
    d = json.loads((ROOT / "operations/external_validation/e28r_ceo_brain_branch_update.json").read_text())
    assert d["selected_active_branch"] == "revenue_mode_shortest_cash_path"
    assert "revenue_mode_governance_infrastructure" in d["backup_branches"]
    assert "revenue_mode_enterprise_pilot" in d["deferred_branches"]
    assert d["production_live_configuration_global_default"] is False
    assert d["next_decision_horizon"] == "E29_revenue_mode_branch_selection_confirmation"
