import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_mvp_selector_chooses_black_box_and_preserves_backups():
    data = json.loads((ROOT / "operations/external_validation/e32_shock_level_mvp_selection.json").read_text())
    assert data["selected_mvp"] == "mvp_agent_action_black_box"
    assert len(data["backup_mvps"]) >= 3
    assert "fixed-fee Agent Action Legitimacy Audit" in data["first_monetization_route"]
    assert data["exact_owner_facing_decision"]
