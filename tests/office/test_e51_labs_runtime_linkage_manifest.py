from office.mission_command.e51_labs_runtime_linkage_manifest import build_labs_runtime_linkage_manifest


def test_e51_labs_runtime_linkage_manifest_has_writer_reader_readback():
    manifest = build_labs_runtime_linkage_manifest()
    assert manifest['current_state']['selected_route'] == 'package_governed_agent_action_proof_packet'
    assert manifest['current_state']['next_milestone'] == 'E51_package_governed_agent_action_proof_packet_for_first_user_review'
    for artifact in manifest['artifacts']:
        if artifact['severity'] == 'P0':
            assert artifact['writer']
            assert artifact['readers'] or artifact['next_runtime_readers']
            assert artifact['tests']
    assert manifest['readback_proof']['passed'] is True
    assert manifest['governance_boundary']['preserved'] is True
