from office.mission_command.e70_ceo_capability_growth_model import (
    explain_self_bootstrap_boundaries,
    generate_capability_growth_candidates,
    generate_codex_job_proposal,
    get_capability_gap_registry,
    list_local_skill_candidates,
    load_e70_self_bootstrap_state_for_brain,
    map_goal_to_capability_requirements,
    measure_capability_growth_result,
)


GOAL_ID = "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint"


def test_e70_capability_growth_model_exposes_required_api():
    state = load_e70_self_bootstrap_state_for_brain()
    assert state["selected_self_bootstrap_action"] == "combined_self_bootstrap_foundation_layer"
    assert get_capability_gap_registry()["gap_count"] >= 5
    assert map_goal_to_capability_requirements(GOAL_ID)["matches"]
    assert generate_capability_growth_candidates(GOAL_ID)["candidate_count"] >= 12
    assert generate_codex_job_proposal("gap_codex_job_proposal_generation_absent")["external_action_allowed"] is False
    assert list_local_skill_candidates()["external_skill_package_install_prohibited_without_owner_approval"] is True
    assert measure_capability_growth_result("combined_self_bootstrap_foundation_layer")["measurement_status"] == "measured_internal_improvement"
    assert explain_self_bootstrap_boundaries()["external_action_allowed"] is False
