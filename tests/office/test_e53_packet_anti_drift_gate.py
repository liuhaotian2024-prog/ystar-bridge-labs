from office.mission_command.e53_packet_anti_drift_gate import run_e53_packet_anti_drift_gate
from office.mission_command.e53_runtime_linkage_delta import build_e53_runtime_linkage_delta

def test_anti_drift_gate_passes_valid_pending_owner_state():
    data = run_e53_packet_anti_drift_gate()
    assert data["passed"] is True
    assert data["validation"]["anti_drift_gate"]["allowed"] is True

def test_anti_drift_gate_fails_missing_reader_packet():
    delta = build_e53_runtime_linkage_delta()
    for artifact in delta["artifacts"]:
        if artifact["artifact_type"] == "selected_route":
            artifact["readers"] = []
            artifact["next_runtime_readers"] = []
    data = run_e53_packet_anti_drift_gate(delta)
    assert data["passed"] is False
