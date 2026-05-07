import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_selected_self_bootstrap_decision_is_internal_and_scored():
    data = json.loads((ROOT / "operations/external_validation/e70_ceo_selected_self_bootstrap_decision.json").read_text())
    assert data["selected_self_improvement_action"] == "combined_self_bootstrap_foundation_layer"
    assert data["nearest_alternative"] == "create_Codex_job_proposal_generator_for_internal_code_enhancement"
    assert data["selection_made_by_scoring"] is True
    assert data["whether_internal_only"] is True
    assert data["external_action_allowed"] is False
