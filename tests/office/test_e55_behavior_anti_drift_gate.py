from office.mission_command.e55_behavior_anti_drift_gate import run_behavior_anti_drift_gate

def test_behavior_anti_drift_gate_passes_valid_manifest():
    data = run_behavior_anti_drift_gate()
    assert data["passed"] is True
    assert data["checks"]["dry_run_executor_has_evidence_closure"] is True
