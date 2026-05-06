import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def test_e49_artifacts_exist_and_selected_route_has_semantics():
    graph = load('operations/external_validation/e49_semantic_graph.json')
    retest = load('operations/external_validation/e49_money_route_deep_semantic_retest.json')
    selected = load('operations/external_validation/e49_selected_money_route_semantic_decision.json')
    closure = load('operations/external_validation/e49_czl_closure.json')
    assert graph['no_orphan_selected_route'] is True
    assert retest['selected_route_id'] == 'governed_agent_action_proof_packet'
    assert selected['selected_as'] == 'service_wedge_anchored_by_proof_artifact'
    assert selected['missing_mcp_client_path_blocks_external_attempt'] is True
    assert closure['next_milestone'] == 'E50_build_minimal_gov_mcp_local_test_client'
    for key, value in closure['forbidden_external_actions'].items():
        assert value is False, key


def test_e49_no_duplicate_layers_claimed():
    closure = load('operations/external_validation/e49_czl_closure.json')
    assert closure['duplicate_governance_kernel_created'] is False
    assert closure['duplicate_mcp_execution_layer_created'] is False
    assert closure['duplicate_audit_layer_created'] is False
    assert closure['second_ceo_brain_created'] is False
    assert closure['second_ceo_kg_created'] is False
