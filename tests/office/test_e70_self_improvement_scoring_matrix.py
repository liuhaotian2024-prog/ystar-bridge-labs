import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_self_improvement_scoring_selects_by_scores_not_static_text():
    data = json.loads((ROOT / "operations/external_validation/e70_self_improvement_scoring_matrix.json").read_text())
    rows = data["rows"]
    assert data["selection_made_by_scoring"] is True
    assert data["top_candidate"] == "combined_self_bootstrap_foundation_layer"
    assert rows[0]["candidate_id"] == data["top_candidate"]
    assert rows[0]["total_score"] >= rows[1]["total_score"]
    assert "future_Codex_job_generation_value" in rows[0]["axis_scores"]
