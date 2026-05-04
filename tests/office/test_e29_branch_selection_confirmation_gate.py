import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_branch_selection_confirms_shortest_cash_as_near_term_not_hardcode():
    data = json.loads((ROOT / "operations/external_validation/e29_branch_selection_confirmation_gate.json").read_text())
    assert data["selection_decision"] == "confirm_current_active_branch"
    assert data["active_branch"] == "revenue_mode_shortest_cash_path"
    assert data["backup_branch_count"] == 6
    assert data["deferred_branch_count"] == 3
    assert data["blocked_branch_count"] == 0
    assert data["production_live_configuration_global_default"] is False
