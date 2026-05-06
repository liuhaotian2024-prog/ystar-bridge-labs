from office.mission_command.e48_server_client_proof_runner import run_server_client_proof


def test_e48_server_client_proof_is_honest_about_transport_blocker():
    data = run_server_client_proof()
    assert data['governed_allow_deny_proof_generated'] is True
    assert data['allow_result']['decision'] == 'ALLOW'
    assert data['deny_result']['decision'] == 'DENY'
    assert data['cleanup_result']['process_left_running'] is False
    assert data['cleanup_result']['port_left_occupied'] is False
    assert data['no_real_client_config_mutation']['gov_mcp_install_invoked'] is False
    assert data['ready_for_owner_approved_external_attempt'] is False
    assert data['server_client_transport_blocker'] != 'none'
    assert data['no_external_action'] is True
