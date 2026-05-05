import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_ceo_brain_update_sets_frontier_mvp_and_next_horizon():
    data = json.loads((ROOT / "operations/external_validation/e32_ceo_brain_frontier_mvp_update.json").read_text())
    assert data["selected_mvp"] == "mvp_agent_action_black_box"
    assert "buyer-visible demo" in data["strategic_bottleneck"]
    assert data["next_decision_horizon"] == "E33_agent_action_black_box_demo_packet_and_owner_validation_route"
    assert data["production_live_receipt_count"] == 0
