from office.mission_command.e58_case_study_anti_drift_gate import build_e58_runtime_linkage_manifest, run_case_study_anti_drift_gate


def test_case_study_anti_drift_gate_has_writer_reader_readback():
    manifest = build_e58_runtime_linkage_manifest()
    artifacts = {item["artifact_id"]: item for item in manifest["artifacts"]}
    assert artifacts["e58_case_study"]["readers"]
    assert artifacts["e58_e59_requirements"]["next_runtime_readers"] == ["E59_external_world_intelligence_L5_convergence"]
    data = run_case_study_anti_drift_gate(manifest)
    assert data["passed"] is True
    assert data["checks"]["no_report_only_p0_closure"] is True

