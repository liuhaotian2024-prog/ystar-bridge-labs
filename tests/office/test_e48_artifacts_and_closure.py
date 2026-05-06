import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name: str):
    return json.loads((ROOT / 'operations' / 'external_validation' / name).read_text(encoding='utf-8'))


def test_e48_artifacts_record_truthful_blocker_and_closure():
    proof = load('e48_server_client_proof_result.json')
    closure = load('e48_czl_closure.json')
    owner = load('e48_owner_decision_packet.json')
    transcript = load('e48_first_value_codegrounded_proof_transcript.json')
    assert proof['governed_allow_deny_proof_generated'] is True
    assert proof['local_server_client_demo_closed'] is False
    assert closure['governed_allow_deny_proof_generated'] is True
    assert closure['ready_for_owner_approved_external_attempt'] is False
    assert owner['recommended_next_milestone'] == 'E49_build_minimal_gov_mcp_local_test_client'
    assert transcript['what_this_does_not_prove']['full_mcp_server_client_tool_invocation'] is True
    for key, value in closure['forbidden_external_actions'].items():
        assert value is False, key


def test_e48_no_duplicate_runtime_layers_claimed():
    alignment = load('e48_cross_repo_alignment.json')
    assert alignment['duplicate_governance_kernel_created'] is False
    assert alignment['duplicate_mcp_execution_layer_created'] is False
    assert alignment['second_ceo_brain_created'] is False
    assert alignment['second_ceo_kg_created'] is False
