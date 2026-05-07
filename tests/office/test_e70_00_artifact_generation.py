from office.mission_command.e70_ceo_self_bootstrap_planner import write_all_e70_artifacts


def test_e70_artifacts_generate_end_to_end():
    gate = write_all_e70_artifacts()
    assert gate["gate_passed"] is True
    assert gate["final_status"] == "e70_ceo_self_bootstrap_ready_and_codex_job_proposal_generated"
