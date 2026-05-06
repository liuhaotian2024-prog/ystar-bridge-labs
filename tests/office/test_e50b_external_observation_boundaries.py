from office.mission_command.e50b_external_observation_preflight import build_external_observation_preflight
from office.mission_command.e50b_public_observation import build_observation_run, build_public_source_receipts
from office.mission_command.e50b_external_commercial_semantic_graph import build_external_commercial_semantic_graph


def test_external_observation_boundary_flags_are_closed():
    preflight = build_external_observation_preflight()
    run = build_observation_run()
    assert preflight['safe_to_observe'] is True
    assert run['contacts_identified'] is False
    assert run['personal_contact_data_collected'] is False
    assert run['login_used'] is False
    assert run['forms_submitted'] is False
    assert run['messages_sent'] is False
    assert run['published'] is False
    assert run['provider_private_api_used'] is False
    assert run['customer_validation_claimed'] is False
    assert run['paid_signal_claimed'] is False


def test_receipts_and_graph_are_evidence_linked_without_contact():
    receipts = build_public_source_receipts()
    graph = build_external_commercial_semantic_graph()
    assert len(receipts) >= 12
    assert all(receipt['collected_without_contact'] for receipt in receipts)
    assert all(receipt['collected_without_login'] for receipt in receipts)
    assert graph['node_count'] >= len(receipts)
    assert 'governed_agent_action_proof_packet' in graph['routes_connected']
