import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_l5_use_case_runs_closed_loop_and_measures_residuals():
    data = json.loads((ROOT / "operations/external_validation/e70_self_bootstrap_l5_use_case_result.json").read_text())
    assert data["use_case_status"] == "passed"
    assert data["generated_candidate_count"] >= 12
    assert data["selected_self_bootstrap_action"] == "combined_self_bootstrap_foundation_layer"
    assert data["referenced_business_action"] == "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution"
    assert data["generated_codex_job_proposal_id"]
    assert data["measured_Y_t_plus_1"]
    assert data["measured_R_t_plus_1"]
    assert data["no_external_action"] is True
    assert data["no_overclaim"] is True
