from office.mission_command.e56_internal_loop_evidence_writeback import build_internal_loop_evidence_packet


def test_evidence_writeback_has_kg_czl_cieu_paths():
    data = build_internal_loop_evidence_packet()
    assert data["selected_action"] == "run_internal_operating_loop_self_test"
    assert data["KG_update"].endswith("e56_ceo_kg_read_model_update.json")
    assert data["CZL_closure"].endswith("e56_czl_closure.json")
    assert data["CIEU_residual"].endswith("e56_cieu_residual_summary.json")

