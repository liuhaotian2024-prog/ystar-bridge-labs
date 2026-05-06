from office.mission_command.e54_brain_l5_anti_drift_gate import run_brain_l5_anti_drift_gate, build_e54_runtime_linkage_manifest

def test_anti_drift_gate_passes_and_denies_stale_current_state():
    data=run_brain_l5_anti_drift_gate(); assert data['passed'] is True
    broken=build_e54_runtime_linkage_manifest(); broken['readback_proof']['stale_reads']=['old_e49_route_decision']; broken['readback_proof']['passed']=False
    assert run_brain_l5_anti_drift_gate(broken)['passed'] is False
