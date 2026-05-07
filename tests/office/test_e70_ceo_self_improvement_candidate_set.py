import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_self_improvement_candidates_are_generated_and_internal_only():
    data = json.loads((ROOT / "operations/external_validation/e70_ceo_self_improvement_candidate_set.json").read_text())
    ids = {candidate["candidate_id"] for candidate in data["candidates"]}
    assert data["candidate_count"] >= 12
    assert "create_Codex_job_proposal_generator_for_internal_code_enhancement" in ids
    assert "combined_self_bootstrap_foundation_layer" in ids
    assert all(candidate["generated_by_CEO_planner"] is True for candidate in data["candidates"])
    assert all(candidate["external_action_required"] is False for candidate in data["candidates"])
