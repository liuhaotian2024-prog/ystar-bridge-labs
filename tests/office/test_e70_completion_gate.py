import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_completion_gate_passes_for_self_bootstrap_runtime():
    data = json.loads((ROOT / "operations/external_validation/e70_completion_gate_result.json").read_text())
    assert data["gate_passed"] is True
    assert data["final_status"] == "e70_ceo_self_bootstrap_ready_and_codex_job_proposal_generated"
    assert data["selected_self_bootstrap_action"] == "combined_self_bootstrap_foundation_layer"
    assert data["self_improvement_candidate_count"] >= 12
    assert data["recommended_next_milestone"] == "E71_execute_CEO_generated_codex_job_proposal_no_external_action"
    assert data["external_action_allowed"] is False
