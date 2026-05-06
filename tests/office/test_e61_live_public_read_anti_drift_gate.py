from office.mission_command.e61_live_public_read_anti_drift_gate import run_live_public_read_anti_drift_gate


def test_e61_anti_drift_gate_has_receipt_and_next_runtime_readers():
    data = run_live_public_read_anti_drift_gate()
    assert data["passed"] is True
    assert data["checks"]["receipts_have_reader"] is True
    assert data["checks"]["readiness_delta_has_next_runtime_reader"] is True
