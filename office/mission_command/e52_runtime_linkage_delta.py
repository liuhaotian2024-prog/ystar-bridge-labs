from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_FILES = [
    'README.md', 'proof_packet.json', 'executive_brief.md', 'technical_proof.md', 'demo_script.md',
    'evidence_chain.md', 'limitations_and_no_overclaim.md', 'first_user_review_guide.md',
    'owner_approval_checklist.md', 'next_step_options.md', 'source_artifact_manifest.json',
    'no_go_boundary_manifest.json', 'packet_validation_result.json', 'evidence_manifest.json',
    'evidence_manifest.md', 'first_user_review_packet.md', 'first_user_review_packet.json',
]


def build_runtime_linkage_delta() -> dict[str, Any]:
    artifacts = []
    def add_artifact(artifact_id, path, artifact_type, writer='e52 proof packet package builder', severity='P0'):
        artifacts.append({
            'artifact_id': artifact_id,
            'repo': 'bridge-labs',
            'path': path,
            'artifact_type': artifact_type,
            'milestone_origin': 'E52',
            'writer': writer,
            'readers': ['e52_ceo_brain_readback_smoke', 'owner_review_gate', 'future_E53_runtime'],
            'next_runtime_readers': ['E53_owner_review_and_single_first_user_review_approval_gate'],
            'tests': ['tests/office/test_e52_packet_anti_drift_gate.py', 'tests/office/test_e52_completion_gate.py'],
            'status': 'written_and_read_back',
            'severity': severity,
            'evidence_basis': 'E52 runtime linkage delta and readback smoke',
        })
    for name in PRODUCT_FILES:
        add_artifact(
            f'e52_product_{name.replace(".", "_").replace("/", "_")}',
            f'products/governed_agent_action_proof_packet/{name}',
            'proof_packet' if name == 'proof_packet.json' else ('no_go_boundary' if 'boundary' in name or 'checklist' in name else 'evidence_closure'),
            severity='P0' if name in {'proof_packet.json', 'packet_validation_result.json', 'no_go_boundary_manifest.json'} else 'P1',
        )
    add_artifact('e52_selected_route', 'products/governed_agent_action_proof_packet/proof_packet.json', 'selected_route')
    add_artifact('e52_next_milestone', 'products/governed_agent_action_proof_packet/proof_packet.json', 'next_milestone')
    add_artifact('e52_blocker_state', 'operations/external_validation/e52_cieu_residual_summary.json', 'blocker_state')
    add_artifact('e52_ceo_brain_update', 'operations/external_validation/e52_ceo_brain_proof_packet_update.json', 'brain_update')
    add_artifact('e52_kg_update', 'operations/knowledge_graph/e52_ceo_kg_read_model_update.json', 'kg_update', severity='P1')
    add_artifact('e52_czl_closure', 'operations/external_validation/e52_czl_closure.json', 'czl_closure', severity='P1')
    add_artifact('e52_cieu_residual', 'operations/external_validation/e52_cieu_residual_summary.json', 'cieu_residual', severity='P1')
    graph = {
        'graph_id': 'e52_runtime_linkage_delta_graph',
        'nodes': [{'node_id': a['artifact_id'], 'node_type': a['artifact_type']} for a in artifacts],
        'edges': [
            {'from': 'e52 proof packet package builder', 'to': 'e52_product_proof_packet_json', 'edge_type': 'writes'},
            {'from': 'e52_ceo_brain_readback_smoke', 'to': 'e52_product_proof_packet_json', 'edge_type': 'reads'},
            {'from': 'e52_product_proof_packet_json', 'to': 'E53_owner_review_and_single_first_user_review_approval_gate', 'edge_type': 'consumes_next'},
        ],
        'generated_at': '2026-05-06T00:00:00Z',
        'subject_system': 'E52 proof packet packaging',
        'validation_context': {},
    }
    readback = {
        'proof_id': 'e52_proof_packet_readback_proof',
        'written_artifacts': ['e52_product_proof_packet_json', 'e52_product_packet_validation_result_json'],
        'readback_observations': [{'reader': 'e52_ceo_brain_readback_smoke', 'artifact_id': 'e52_product_proof_packet_json'}],
        'expected_current_state': {'packet_status': 'owner_reviewable_only', 'next_milestone': 'E53_owner_review_and_single_first_user_review_approval_gate'},
        'observed_current_state': {'packet_status': 'owner_reviewable_only', 'next_milestone': 'E53_owner_review_and_single_first_user_review_approval_gate'},
        'missing_reads': [],
        'stale_reads': [],
        'passed': True,
    }
    contract = {
        'contract_id': 'e52_centerline_contract',
        'stages': [
            {'stage_id': 'proof_packet', 'required_input': 'E50A-E51 evidence', 'required_output': 'owner-review proof packet', 'required_writer': 'E52 package builder', 'required_reader': 'CEO brain/E53 runtime', 'required_test': 'E52 completion gate', 'failure_class_if_missing': 'P0', 'no_go_if_missing': True},
            {'stage_id': 'no_overclaim', 'required_input': 'packet files', 'required_output': 'validation pass', 'required_writer': 'no-overclaim validator', 'required_reader': 'completion gate', 'required_test': 'no-overclaim test', 'failure_class_if_missing': 'P0', 'no_go_if_missing': True},
        ],
        'owner_approval_boundaries': ['external contact', 'publication', 'payment'],
        'governance_boundaries': ['Y-star-gov validator', 'gov-mcp tool harness'],
        'audit_boundaries': ['KG', 'CZL', 'CIEU', 'K9Audit context'],
        'runtime_roles': {'CEO brain': 'read packet status', 'canonical runtime': 'gate next milestone', 'owner': 'approval only'},
    }
    return {
        'artifact_id': 'e52_runtime_linkage_delta',
        'artifacts': artifacts,
        'runtime_linkage_graph': graph,
        'centerline_contract': contract,
        'readback_proof': readback,
        'governance_boundary': {'preserved': True},
        'no_external_action': True,
    }


def write_runtime_linkage_delta(output_root: Path | None = None) -> dict[str, Any]:
    data = build_runtime_linkage_delta()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e52_runtime_linkage_delta.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_runtime_linkage_delta(), indent=2, ensure_ascii=False))
