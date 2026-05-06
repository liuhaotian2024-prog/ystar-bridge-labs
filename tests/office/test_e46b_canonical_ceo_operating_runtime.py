from office.mission_command.e46b_canonical_ceo_operating_runtime import run_canonical_ceo_operating_runtime


def test_canonical_ceo_operating_runtime_runs_spine():
    result = run_canonical_ceo_operating_runtime({"task_id": "test", "task_title": "first real user", "task_description": "prepare fastest credible first user value path"})
    assert result["projection_chain"]["projection_maturity"] == "partial_adapter"
    assert result["ceo_brain_context"]["active_task_time_source"]
    assert result["invoked_capabilities"]["e42_match_count"] > 0
    assert result["invoked_capabilities"]["e44a_stage_count"] >= 10
    assert result["commercial_wrapper_comparison"]
    assert result["closure_packet"]["projection_chain_created"] is True
    assert result["governance_boundary"]["Y_star_gov_owns_kernel"] is True
    assert result["no_external_action"] is True
