from office.mission_command.e59_external_intelligence_anti_drift_gate import clone_manifest, run_external_intelligence_anti_drift_gate


def test_e59_anti_drift_gate_passes_and_denies_missing_receipt_reader():
    data = run_external_intelligence_anti_drift_gate()
    assert data["passed"] is True
    assert data["checks"]["source_receipts_have_readers"] is True
    broken = clone_manifest()
    for artifact in broken["artifacts"]:
        if artifact["artifact_id"] == "e59_source_receipts":
            artifact["readers"] = []
            artifact["next_runtime_readers"] = []
    denied = run_external_intelligence_anti_drift_gate(broken)
    assert denied["passed"] is False

