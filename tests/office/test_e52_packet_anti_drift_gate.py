from office.mission_command.e52_packet_anti_drift_gate import run_packet_anti_drift_gate
from office.mission_command.e52_runtime_linkage_delta import build_runtime_linkage_delta


def test_e52_packet_anti_drift_gate_passes_valid_and_fails_missing_reader():
    assert run_packet_anti_drift_gate()['passed'] is True
    broken = build_runtime_linkage_delta()
    for artifact in broken['artifacts']:
        if artifact['path'].endswith('proof_packet.json'):
            artifact['readers'] = []
            artifact['next_runtime_readers'] = []
    broken['readback_proof']['passed'] = False
    broken['readback_proof']['missing_reads'] = ['proof_packet.json']
    assert run_packet_anti_drift_gate(broken)['passed'] is False
