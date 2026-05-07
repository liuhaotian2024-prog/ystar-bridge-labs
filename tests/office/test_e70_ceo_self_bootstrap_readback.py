from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e70_ceo_self_bootstrap_readback import (
    get_generated_codex_job_proposal,
    get_selected_self_bootstrap_action,
    get_self_bootstrap_use_case_result,
    run_ceo_self_bootstrap_readback_smoke,
)


def test_e70_readback_exposes_self_bootstrap_state_to_ceo_brain():
    assert get_selected_self_bootstrap_action()["selected_self_improvement_action"] == "combined_self_bootstrap_foundation_layer"
    assert get_generated_codex_job_proposal()["generated_by_CEO_self_bootstrap_runtime"] is True
    assert get_self_bootstrap_use_case_result()["use_case_status"] == "passed"
    assert run_ceo_self_bootstrap_readback_smoke()["passes"] is True
    context = load_ceo_brain_context({"task_title": "e70 readback", "task_description": "CEO self-bootstrap"})
    assert context["current_ceo_capability_gap_count"] >= 5
    assert context["current_ceo_selected_self_improvement_action"] == "combined_self_bootstrap_foundation_layer"
    assert context["current_ceo_generated_codex_job_proposal_id"] == "e70_codex_job_E71_execute_internal_CIEU_module_integration_no_external_action"
    assert context["current_ceo_self_bootstrap_external_action_allowed"] is False
