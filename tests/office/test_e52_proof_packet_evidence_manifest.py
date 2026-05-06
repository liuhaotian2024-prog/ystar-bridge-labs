from office.mission_command.e52_proof_packet_evidence_manifest import build_evidence_manifest


def test_e52_evidence_manifest_includes_core_milestones():
    data = build_evidence_manifest()
    milestones = {item['source_milestone'] for item in data['evidence_items']}
    assert {'E50A','E50B','E50C','E51','E51 Phase 2.5'}.issubset(milestones)
    assert data['customer_validation_claimed'] is False
    assert data['paid_signal_claimed'] is False
