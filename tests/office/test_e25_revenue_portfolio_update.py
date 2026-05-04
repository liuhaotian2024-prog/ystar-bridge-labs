import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_revenue_portfolio_keeps_selected_path_and_blocks_live():
    data = json.loads((ROOT / "operations/external_validation/e25_revenue_portfolio_update.json").read_text())
    assert data["selected_path_remains_selected"] is True
    assert data["live_sandbox_ready_paths"] == ["rev_path_readiness_review_ai_consultancies"]
    assert data["live_ready_count"] == 0
    assert data["live_blocked_count"] == 1
