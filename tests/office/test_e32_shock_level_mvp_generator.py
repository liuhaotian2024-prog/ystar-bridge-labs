import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_mvp_generator_produces_multiple_scored_candidates():
    data = json.loads((ROOT / "operations/external_validation/e32_shock_level_mvp_candidates.json").read_text())
    assert data["generated_from_methodology_not_menu"] is True
    assert data["candidates_generated"] >= 5
    assert all(c["score"] for c in data["candidates"])
    assert any(c["candidate_id"] == "mvp_agent_action_black_box" for c in data["candidates"])
