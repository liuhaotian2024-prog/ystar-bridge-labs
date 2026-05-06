from office.mission_command.e52_proof_packet_boundary import build_proof_packet_boundary


def test_e52_boundary_defines_allowed_and_forbidden_language():
    data = build_proof_packet_boundary()
    assert data['product_name'] == 'Governed Agent Action Proof Packet'
    assert 'not_real_mcp_transport' in data['current_proof_level']
    assert 'no customer validation' in data['explicit_limitations']
