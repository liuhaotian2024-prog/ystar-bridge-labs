import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_control_room_surfaces_branch_correction():
    d = json.loads((ROOT / "operations/external_validation/e28r_control_room.json").read_text())
    assert d["branch_count"] == 10
    assert d["selected_active_branch"] == "revenue_mode_shortest_cash_path"
    assert d["production_live_configuration_global_default"] is False
    assert d["route_decision"]["recommended_next_milestone"] == "E29_revenue_mode_branch_selection_confirmation"
