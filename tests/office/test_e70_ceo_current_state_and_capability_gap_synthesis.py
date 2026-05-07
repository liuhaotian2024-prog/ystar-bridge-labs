import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_state_gap_synthesis_names_missing_self_bootstrap_capabilities():
    data = json.loads((ROOT / "operations/external_validation/e70_ceo_current_state_and_capability_gap_synthesis.json").read_text())
    capability = data["current_CEO_capability_state"]
    assert data["active_goal"] == "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint"
    assert capability["E69_business_next_action_generation_exists"] is True
    assert capability["missing_self_improvement_candidate_generation"] is True
    assert capability["missing_automatic_Codex_job_proposal_generation"] is True
    assert "install external packages or skills" in data["CEO_cannot_do_without_owner_approval"]
