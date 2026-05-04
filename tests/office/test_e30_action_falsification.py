import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_falsification_keeps_selected_candidate_honest():
    data = json.loads((ROOT / "operations/external_validation/e30_action_falsification_analysis.json").read_text())
    assert data["top_candidate_count"] == 5
    assert data["selected_candidate_id"] == "action_paid_readiness_review_signal_package"
    assert data["selected_candidate_survived_falsification"] is True
    assert "internal polish" in data["main_objection_to_selected"]
