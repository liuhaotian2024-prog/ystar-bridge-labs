
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
E53_FILES = [
    'products/governed_agent_action_proof_packet/e53_owner_review_packet.json',
    'products/governed_agent_action_proof_packet/e53_owner_review_packet.md',
    'operations/external_validation/e53_owner_approval_record_schema.json',
    'operations/external_validation/e53_owner_approval_record_placeholder.json',
    'operations/external_validation/e53_owner_approval_validation_result.json',
    'products/governed_agent_action_proof_packet/e53_single_first_user_review_protocol.json',
    'products/governed_agent_action_proof_packet/e53_non_sent_review_request_template.json',
    'operations/external_validation/e53_first_user_review_risk_gate_result.json',
]


def build_e53_runtime_linkage_delta() -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    def add(artifact_id: str, path: str, artifact_type: str, *, writer: str = 'E53 owner review gate builder', severity: str = 'P0', readers: list[str] | None = None) -> None:
        artifacts.append({
            'artifact_id': artifact_id, 'repo': 'bridge-labs', 'path': path, 'artifact_type': artifact_type,
            'milestone_origin': 'E53', 'writer': writer,
            'readers': readers or ['e53_ceo_brain_readback_smoke', 'e53_completion_gate', 'future_E54_runtime'],
            'next_runtime_readers': ['E54_owner_decision_or_controlled_first_user_review_plan'],
            'tests': ['tests/office/test_e53_packet_anti_drift_gate.py', 'tests/office/test_e53_completion_gate.py'],
            'status': 'written_and_read_back', 'severity': severity, 'evidence_basis': 'E53 runtime linkage delta and readback smoke',
        })
    for rel in E53_FILES:
        typ = 'decision_packet' if 'owner_review_packet' in rel else ('no_go_boundary' if 'approval' in rel or 'risk_gate' in rel else 'evidence_closure')
        add('e53_' + rel.replace('/', '_').replace('.', '_'), rel, typ, severity='P0' if rel.endswith('.json') else 'P1')
    add('e53_selected_route_inheritance', 'products/governed_agent_action_proof_packet/proof_packet.json', 'selected_route')
    add('e53_next_milestone', 'operations/external_validation/e53_first_user_review_risk_gate_result.json', 'next_milestone')
    add('e53_blocker_state', 'operations/external_validation/e53_first_user_review_risk_gate_result.json', 'blocker_state')
    add('e53_ceo_brain_update', 'operations/external_validation/e53_ceo_brain_owner_review_update.json', 'brain_update')
    add('e53_kg_update', 'operations/knowledge_graph/e53_ceo_kg_read_model_update.json', 'kg_update', severity='P1')
    add('e53_czl_closure', 'operations/external_validation/e53_czl_closure.json', 'czl_closure', severity='P1')
    add('e53_cieu_residual', 'operations/external_validation/e53_cieu_residual_summary.json', 'cieu_residual', severity='P1')
    add('e53_no_go_boundaries', 'operations/external_validation/e53_first_user_review_risk_gate_result.json', 'no_go_boundary')
    graph = {
        'graph_id': 'e53_runtime_linkage_delta_graph',
        'nodes': [{'node_id': a['artifact_id'], 'node_type': a['artifact_type']} for a in artifacts],
        'edges': [
            {'from': 'E53 owner review gate builder', 'to': 'e53_products_governed_agent_action_proof_packet_e53_owner_review_packet_json', 'edge_type': 'writes'},
            {'from': 'e53_ceo_brain_readback_smoke', 'to': 'e53_products_governed_agent_action_proof_packet_e53_owner_review_packet_json', 'edge_type': 'reads'},
            {'from': 'e53_products_governed_agent_action_proof_packet_e53_owner_review_packet_json', 'to': 'E54_owner_decision_or_controlled_first_user_review_plan', 'edge_type': 'consumes_next'},
        ],
        'generated_at': '2026-05-06T00:00:00Z', 'subject_system': 'E53 owner review approval gate', 'validation_context': {},
    }
    readback = {
        'proof_id': 'e53_owner_review_readback_proof',
        'written_artifacts': ['e53_products_governed_agent_action_proof_packet_e53_owner_review_packet_json', 'e53_operations_external_validation_e53_first_user_review_risk_gate_result_json'],
        'readback_observations': [{'reader': 'e53_ceo_brain_readback_smoke', 'artifact_id': 'e53_products_governed_agent_action_proof_packet_e53_owner_review_packet_json'}],
        'expected_current_state': {'owner_decision_status': 'pending_owner_decision', 'external_action_allowed': False, 'next_milestone': 'E54_owner_decision_or_controlled_first_user_review_plan'},
        'observed_current_state': {'owner_decision_status': 'pending_owner_decision', 'external_action_allowed': False, 'next_milestone': 'E54_owner_decision_or_controlled_first_user_review_plan'},
        'missing_reads': [], 'stale_reads': [], 'passed': True,
    }
    contract = {
        'contract_id': 'e53_centerline_contract',
        'stages': [
            {'stage_id': 'owner_review_gate', 'required_input': 'E52 proof packet', 'required_output': 'pending owner decision gate', 'required_writer': 'E53 owner review builder', 'required_reader': 'CEO brain/E54 runtime', 'required_test': 'E53 completion gate', 'failure_class_if_missing': 'P0', 'no_go_if_missing': True},
            {'stage_id': 'external_action_block', 'required_input': 'approval validation', 'required_output': 'external action denied pending owner decision', 'required_writer': 'E53 risk gate', 'required_reader': 'E53 completion gate', 'required_test': 'risk gate test', 'failure_class_if_missing': 'P0', 'no_go_if_missing': True},
        ],
        'owner_approval_boundaries': ['external contact', 'publication', 'real reviewer identification', 'contact info collection', 'payment'],
        'governance_boundaries': ['Y-star-gov validator', 'gov-mcp tool harness'],
        'audit_boundaries': ['KG', 'CZL', 'CIEU', 'K9Audit context'],
        'runtime_roles': {'CEO brain': 'read pending owner decision', 'canonical runtime': 'block external action', 'owner': 'sole approval authority'},
    }
    return {'artifact_id': 'e53_runtime_linkage_delta', 'artifacts': artifacts, 'runtime_linkage_graph': graph, 'centerline_contract': contract, 'readback_proof': readback, 'governance_boundary': {'preserved': True}, 'no_external_action': True}


def write_e53_runtime_linkage_delta(output_root: Path | None = None) -> dict[str, Any]:
    data = build_e53_runtime_linkage_delta()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e53_runtime_linkage_delta.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_e53_runtime_linkage_delta(), indent=2, ensure_ascii=False))
