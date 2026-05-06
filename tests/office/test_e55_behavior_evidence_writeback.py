from office.mission_command.e55_behavior_evidence_writeback import build_behavior_evidence_writeback

def test_behavior_result_writes_evidence_paths():
    data = build_behavior_evidence_writeback()
    assert data["writeback_status"] == "passed"
    assert data["KG_update"].endswith("e55_ceo_kg_read_model_update.json")
    assert data["brain_readback_required"] is True
