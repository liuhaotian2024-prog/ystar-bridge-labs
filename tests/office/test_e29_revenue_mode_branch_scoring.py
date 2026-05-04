import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_branch_scoring_scores_all_modes_without_erasing_backups():
    data = json.loads((ROOT / "operations/external_validation/e29_revenue_mode_branch_scoring.json").read_text())
    assert data["branch_count"] == 10
    assert data["opaque_llm_judge_used"] is False
    assert data["top_scored_branch"] == "revenue_mode_shortest_cash_path"
    assert data["score_summary"]["revenue_mode_shortest_cash_path"] == 88
    assert data["score_summary"]["revenue_mode_ceo_agent_runtime_product"] >= 80
    assert data["backup_branches_preserved"] is True
