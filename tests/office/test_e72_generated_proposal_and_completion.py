import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e72_generated_codex_proposal_is_residual_driven():
    proposal = json.loads((ROOT / "operations/external_validation/e72_generated_codex_job_proposal.json").read_text())
    assert proposal["generated_from_E72_residuals"] is True
    assert proposal["proposed_milestone_id"] == "E73_CIEU_hash_chain_structural_verifier_bridge_labs_adapter"
    assert proposal["owner_approval_status"] == "pending_owner_decision"
    assert proposal["external_action_allowed"] is False
    scores = proposal["candidate_scores"]
    assert scores[0]["candidate_id"] == proposal["proposed_milestone_id"]
    assert scores[0]["total_score"] >= scores[1]["total_score"]


def test_e72_completion_and_no_overclaim_pass():
    gate = json.loads((ROOT / "operations/external_validation/e72_completion_gate_result.json").read_text())
    no_overclaim = json.loads((ROOT / "operations/external_validation/e72_no_overclaim_validation_result.json").read_text())
    assert gate["gate_passed"] is True
    assert gate["final_status"] == "e72_k9_cieu_hash_chain_context_integrated_into_audit_module"
    assert gate["read_only_repo_status_unchanged"] is True
    assert gate["next_recommended_milestone"] == "E73_CIEU_hash_chain_structural_verifier_bridge_labs_adapter"
    assert gate["external_action_allowed"] is False
    assert no_overclaim["passed"] is True
    assert no_overclaim["violations"] == []

