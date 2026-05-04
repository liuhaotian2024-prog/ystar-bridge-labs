import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_scoring_penalizes_gates_and_fake_progress():
    data = json.loads((ROOT / "operations/external_validation/e30_action_objective_scores.json").read_text())
    assert data["top_action_id"] == "action_paid_readiness_review_signal_package"
    assert data["scored_action_count"] == 10
    assert data["fake_progress_penalty_enabled"] is True
    assert data["gate_penalty_enabled"] is True
    scores = {row["action_id"]: row["total_score"] for row in data["scores"]}
    assert scores["action_paid_readiness_review_signal_package"] > scores["action_secure_production_config_preparation"]
