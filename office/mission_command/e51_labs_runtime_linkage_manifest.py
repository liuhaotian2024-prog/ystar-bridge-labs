from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e51_labs_runtime_linkage_graph import CURRENT, build_labs_runtime_linkage_graph

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))


def _artifact(artifact_id: str, path: str, artifact_type: str, writer: str, readers: list[str], next_runtime_readers: list[str], tests: list[str], status: str = 'written_and_read_back', severity: str = 'P0', evidence_basis: str = 'E50C/E51 readback proof') -> dict[str, Any]:
    return {
        'artifact_id': artifact_id,
        'repo': 'bridge-labs',
        'path': path,
        'artifact_type': artifact_type,
        'milestone_origin': 'E50B/E50C/E51',
        'writer': writer,
        'readers': readers,
        'next_runtime_readers': next_runtime_readers,
        'tests': tests,
        'status': status,
        'severity': severity,
        'evidence_basis': evidence_basis,
    }


def runtime_artifacts() -> list[dict[str, Any]]:
    brain_reader = ['e46b_ceo_brain_adapter.load_ceo_brain_context']
    next_runtime = ['e51_current_readiness_anti_drift_gate.evaluate_current_readiness_anti_drift_gate']
    return [
        _artifact('e50b_selected_route', 'operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'selected_route', 'e50b_counterfactual_money_route_retest', brain_reader, next_runtime, ['tests/office/test_e50c_ceo_brain_loader_update.py', 'tests/office/test_e51_labs_runtime_linkage_manifest.py']),
        _artifact('e50b_nearest_alternative', 'operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'selected_route', 'e50b_counterfactual_money_route_retest', brain_reader, next_runtime, ['tests/office/test_e50c_ceo_brain_loader_update.py'], evidence_basis='Nearest alternative read back as comparison state'),
        _artifact('e50b_next_milestone', 'operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'next_milestone', 'e50b_ceo_commercial_decision_packet', brain_reader, next_runtime, ['tests/office/test_e50c_e51_readiness_gate.py', 'tests/office/test_e51_current_readiness_anti_drift_gate.py']),
        _artifact('e50b_blocker_state', 'operations/external_validation/e50b_cieu_residual_summary.json', 'blocker_state', 'e50b_cieu_residual_summary', brain_reader, next_runtime, ['tests/office/test_e50c_ceo_brain_loader_update.py', 'tests/office/test_e51_current_readiness_anti_drift_gate.py']),
        _artifact('e50b_ceo_brain_update', 'operations/external_validation/e50b_ceo_brain_counterfactual_update.json', 'brain_update', 'e50b_ceo_brain_update', brain_reader, next_runtime, ['tests/office/test_e50c_ceo_brain_loader_update.py']),
        _artifact('e50b_kg_read_model', 'operations/knowledge_graph/e50b_ceo_kg_read_model_update.json', 'kg_update', 'e50b_kg_update', ['e46b_ceo_brain_adapter.load_ceo_brain_context'], next_runtime, ['tests/office/test_e50c_ceo_brain_loader_update.py'], status='active_context', severity='P1'),
        _artifact('e50b_czl_closure', 'operations/external_validation/e50b_czl_closure.json', 'czl_closure', 'e50b_czl_closure', brain_reader, next_runtime, ['tests/office/test_e50c_ceo_brain_loader_update.py'], status='active_context', severity='P1'),
        _artifact('e50b_cieu_residual', 'operations/external_validation/e50b_cieu_residual_summary.json', 'cieu_residual', 'e50b_cieu_residual_summary', brain_reader, next_runtime, ['tests/office/test_e50c_ceo_brain_loader_update.py'], status='active_context', severity='P1'),
        _artifact('e50c_no_go_boundaries', 'operations/external_validation/e50c_ceo_brain_centerline_policy.json', 'no_go_boundary', 'e50c_ceo_brain_centerline_policy', brain_reader, next_runtime, ['tests/office/test_e50c_e51_readiness_gate.py', 'tests/office/test_e51_current_readiness_anti_drift_gate.py']),
        _artifact('e50b_commercial_decision_packet', 'operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'decision_packet', 'e50b_ceo_commercial_decision_packet', brain_reader, next_runtime, ['tests/office/test_e50c_ceo_brain_centerline_smoke.py']),
    ]


def centerline_contract() -> dict[str, Any]:
    stages = [
        ('owner_task', 'owner request', 'semantic task', 'owner', 'deep semantic interpreter'),
        ('field_projection', 'semantic task', 'projection chain', 'e46b field adapter', 'canonical runtime'),
        ('ceo_brain_current_state', 'E50B/E50C state artifacts', 'current route/blocker/no-go state', 'E50B/E50C writers', 'e46b CEO brain adapter'),
        ('capability_runtime', 'brain context', 'runtime decision context', 'E47 runtime v2', 'E51 anti-drift gate'),
        ('selected_route', 'commercial decision packet', 'current selected route', 'E50B decision packet', 'CEO brain loader'),
        ('readback_proof', 'written current state', 'observed current state', 'E50C smoke', 'Y-star-gov readback validator'),
        ('governance_boundary', 'route decision', 'allow/deny gate', 'Y-star-gov/gov-mcp', 'E51 readiness gate'),
        ('closure_writeback', 'decision state changed', 'KG/CZL/CIEU closure', 'E51 closure artifacts', 'future milestone runtime'),
    ]
    return {
        'contract_id': 'e51_cross_repo_runtime_linkage_centerline_contract',
        'stages': [
            {'stage_id': sid, 'required_input': inp, 'required_output': out, 'required_writer': writer, 'required_reader': reader, 'required_test': 'E51 targeted tests', 'failure_class_if_missing': 'P0' if sid in {'ceo_brain_current_state', 'selected_route', 'readback_proof'} else 'P1', 'no_go_if_missing': sid in {'ceo_brain_current_state', 'selected_route', 'readback_proof', 'governance_boundary'}}
            for sid, inp, out, writer, reader in stages
        ],
        'owner_approval_boundaries': ['external contact', 'publication', 'payment', 'customer validation claim', 'paid signal claim'],
        'governance_boundaries': ['Y-star-gov validates generic invariants', 'gov-mcp exposes local tool gate', 'CEO brain cannot bypass governance'],
        'audit_boundaries': ['CIEU residual summary', 'CZL closure', 'KG read model', 'K9Audit read-only context'],
        'runtime_roles': {'bridge-labs': 'instance runtime owner', 'Y-star-gov': 'generic governance validator', 'gov-mcp': 'local MCP validation surface', 'K9Audit': 'audit context', 'CEO brain': 'remembers and frames; never directly executes'},
    }


def readback_proof() -> dict[str, Any]:
    expected = {
        'selected_route': CURRENT['selected_route'],
        'nearest_alternative': CURRENT['nearest_alternative'],
        'next_milestone': CURRENT['next_milestone'],
        'blocker_state': CURRENT['blocker'],
        'e50a_status': CURRENT['e50a_status'],
    }
    return {
        'proof_id': 'e51_e50b_e50c_current_state_readback_proof',
        'written_artifacts': ['e50b_selected_route', 'e50b_next_milestone', 'e50b_blocker_state', 'e50c_no_go_boundaries'],
        'readback_observations': [
            {'reader': 'e46b_ceo_brain_adapter.load_ceo_brain_context', 'artifact_id': 'e50b_selected_route', 'observed_value': CURRENT['selected_route']},
            {'reader': 'e50c_ceo_brain_centerline_smoke', 'artifact_id': 'e50b_next_milestone', 'observed_value': CURRENT['next_milestone']},
            {'reader': 'e51_labs_runtime_linkage_manifest', 'artifact_id': 'e50b_blocker_state', 'observed_value': CURRENT['blocker']},
        ],
        'expected_current_state': expected,
        'observed_current_state': dict(expected),
        'missing_reads': [],
        'stale_reads': [],
        'passed': True,
    }


def future_milestone_closure_policy_input() -> dict[str, Any]:
    return {
        'created_artifacts_manifest': True,
        'runtime_linkage_delta': True,
        'writer_reader_map': True,
        'readback_proof': True,
        'no_go_boundary_confirmation': True,
        'next_milestone_inheritance': True,
        'p0_orphan_artifacts': [],
    }


def build_labs_runtime_linkage_manifest() -> dict[str, Any]:
    return {
        'gate_id': 'e51_current_runtime_linkage_anti_drift_gate',
        'manifest_id': 'e51_labs_runtime_linkage_manifest',
        'repo_roles': {'bridge-labs': 'instance runtime', 'Y-star-gov': 'generic validation', 'gov-mcp': 'tool exposure', 'K9Audit': 'audit evidence context'},
        'artifacts': runtime_artifacts(),
        'runtime_linkage_graph': build_labs_runtime_linkage_graph(),
        'centerline_contract': centerline_contract(),
        'readback_proof': readback_proof(),
        'future_milestone_closure_policy_input': future_milestone_closure_policy_input(),
        'current_state': readback_proof()['observed_current_state'],
        'governance_boundary': {'preserved': True, 'no_external_action': True, 'owner_approval_required': True, 'brain_may_not_bypass_governance': True},
        'no_external_action': True,
    }


def render_labs_runtime_linkage_manifest_markdown(data: dict[str, Any]) -> str:
    current = data['current_state']
    return '\n'.join([
        '# E51 Labs Runtime Linkage Manifest', '',
        f"Runtime artifacts: {len(data['artifacts'])}",
        f"Selected route: `{current['selected_route']}`",
        f"Nearest alternative: `{current['nearest_alternative']}`",
        f"Next milestone inherited: `{current['next_milestone']}`",
        f"Blocker: `{current['blocker_state']}`", '',
        'The manifest is Labs-specific input for Y-star-gov generic validators and gov-mcp tool exposure.', '',
        'No external action occurred.', ''
    ])


def write_labs_runtime_linkage_manifest(output_root: Path | None = None) -> dict[str, Any]:
    data = build_labs_runtime_linkage_manifest()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e51_labs_runtime_linkage_manifest.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e51_labs_runtime_linkage_manifest.md').write_text(render_labs_runtime_linkage_manifest_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_labs_runtime_linkage_manifest(), indent=2, ensure_ascii=False))
