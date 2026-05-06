from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))
GOV_MCP_ROOT = Path(os.environ.get('GOV_MCP_ROOT', '/Users/haotianliu/.openclaw/workspace/gov-mcp'))
K9_ROOT = Path(os.environ.get('K9AUDIT_ROOT', '/Users/haotianliu/.openclaw/workspace/K9Audit'))

CENTERLINES = {
    'cognitive_capability': ['CEO_brain'],
    'behavior_control_capability': ['canonical_action_runtime', 'Y_star_gov_boundary'],
    'evidence_closure_capability': ['KG_CZL_CIEU_K9_evidence'],
    'boundary_capability': ['Y_star_gov_boundary'],
    'reference_only_artifact': ['reference_only'],
}


def _record(capability_id: str, path: str, repo: str, functional_class: str, *, actual_binding: list[str] | None = None, binding_status: str = 'correctly_bound', required_reader: str = '', actual_reader: str = '', required_gate: str = '', actual_gate: str = '', remediation: str = 'no_action', severity: str = 'P2', affects_current_state: bool = False, agent_facing: bool = False, consumed_as_current: bool = False, evidence_basis: str = '') -> dict[str, Any]:
    required = CENTERLINES[functional_class]
    return {
        'capability_id': capability_id,
        'path': path,
        'repo': repo,
        'functional_class': functional_class,
        'required_centerline': required if functional_class != 'boundary_capability' or not agent_facing else ['Y_star_gov_boundary', 'gov_mcp_boundary'],
        'actual_binding': actual_binding if actual_binding is not None else (required if functional_class != 'boundary_capability' or not agent_facing else ['Y_star_gov_boundary', 'gov_mcp_boundary']),
        'binding_status': binding_status,
        'required_reader': required_reader,
        'actual_reader': actual_reader,
        'required_gate': required_gate,
        'actual_gate': actual_gate,
        'remediation': remediation,
        'severity': severity,
        'affects_current_state': affects_current_state,
        'agent_facing': agent_facing,
        'consumed_as_current': consumed_as_current,
        'evidence_basis': evidence_basis or 'E51 capability centerline audit',
    }


def build_capability_centerline_binding_audit() -> dict[str, Any]:
    records = [
        # Cognitive centerline.
        _record('wisdom_search', 'scripts/wisdom_search.py', 'bridge-labs', 'cognitive_capability', required_reader='e46b_ceo_brain_adapter.load_ceo_brain_context', actual_reader='e46b_ceo_brain_adapter.load_ceo_brain_context', severity='P1', evidence_basis='Wisdom search is called by CEO brain adapter.'),
        _record('ceo_wisdom_memory', 'knowledge/ceo/wisdom/meta/autonomous_loop_algorithm.md', 'bridge-labs', 'cognitive_capability', required_reader='e46b_ceo_brain_adapter.load_ceo_brain_context', actual_reader='e46b_ceo_brain_adapter.load_ceo_brain_context', severity='P1'),
        _record('e44a_cognition_cascade', 'office/mission_command/e44a_full_history_preflight_v2.py', 'bridge-labs', 'cognitive_capability', required_reader='canonical CEO runtime cognition stage', actual_reader='E47/E49/E51 runtime context', severity='P1'),
        _record('e46b_ceo_brain_adapter', 'office/mission_command/e46b_ceo_brain_adapter.py', 'bridge-labs', 'cognitive_capability', required_reader='canonical CEO runtime', actual_reader='e46b/e47/e49/e50c/e51 runtime smoke', severity='P0'),
        _record('e49_deep_semantic_runtime', 'office/mission_command/e49_deep_semantic_operating_runtime.py', 'bridge-labs', 'cognitive_capability', required_reader='CEO brain/canonical semantic runtime', actual_reader='E49/E51 tests and route scorer', severity='P1'),
        _record('e50b_counterfactual_runtime', 'office/mission_command/e50b_counterfactual_runtime_adapter.py', 'bridge-labs', 'cognitive_capability', required_reader='CEO brain/current route decision context', actual_reader='E50B decision packet and E50C brain readback', severity='P0'),
        _record('e50b_current_commercial_decision', 'operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'bridge-labs', 'cognitive_capability', required_reader='e46b_ceo_brain_adapter.load_ceo_brain_context', actual_reader='e46b_ceo_brain_adapter.load_ceo_brain_context', severity='P0', affects_current_state=True),
        # Behavior/action centerline.
        _record('canonical_ceo_runtime_v1_1', 'office/mission_command/e46b_canonical_ceo_operating_runtime.py', 'bridge-labs', 'behavior_control_capability', required_reader='E51 anti-drift gate', actual_reader='E51 anti-drift gate', required_gate='Y-star-gov/gov-mcp anti-drift gate', actual_gate='E51 current readiness gate', severity='P0'),
        _record('canonical_ceo_runtime_v2', 'office/mission_command/e47_canonical_ceo_runtime_v2.py', 'bridge-labs', 'behavior_control_capability', required_reader='E51 anti-drift gate', actual_reader='E51 anti-drift gate', required_gate='Y-star-gov/gov-mcp anti-drift gate', actual_gate='E51 current readiness gate', severity='P0'),
        _record('e45_local_demo_runner', 'office/mission_command/e45_real_local_first_value_demo_runner.py', 'bridge-labs', 'behavior_control_capability', required_reader='canonical CEO runtime', actual_reader='E47/E48/E51 context', required_gate='Y-star-gov/governance boundary', actual_gate='local dry-run/no external action gate', severity='P1'),
        _record('e50a_gov_mcp_tool_layer_harness', 'office/mission_command/e50a_fake_fastmcp_harness.py', 'bridge-labs', 'behavior_control_capability', actual_binding=['canonical_action_runtime', 'Y_star_gov_boundary', 'gov_mcp_boundary'], required_reader='E50B/E50C/E51 runtime state', actual_reader='E50B/E50C/E51 runtime state', required_gate='gov-mcp fake harness/no real client mutation gate', actual_gate='E50A/E51 tests', severity='P0'),
        _record('e50b_public_observation_adapter', 'office/mission_command/e50b_public_observation.py', 'bridge-labs', 'behavior_control_capability', required_reader='canonical CEO runtime', actual_reader='E50B route retest and E51 evidence packet', required_gate='public-read-only/no contact boundary', actual_gate='E50B observation boundary tests', severity='P1'),
        # Evidence/closure centerline.
        _record('e50b_kg_read_model_update', 'operations/knowledge_graph/e50b_ceo_kg_read_model_update.json', 'bridge-labs', 'evidence_closure_capability', required_reader='CEO brain readback', actual_reader='e46b CEO brain adapter current state', severity='P0', affects_current_state=True),
        _record('e50b_czl_closure', 'operations/external_validation/e50b_czl_closure.json', 'bridge-labs', 'evidence_closure_capability', required_reader='CEO brain readback', actual_reader='e46b CEO brain adapter current state', severity='P0', affects_current_state=True),
        _record('e50b_cieu_residual_summary', 'operations/external_validation/e50b_cieu_residual_summary.json', 'bridge-labs', 'evidence_closure_capability', required_reader='CEO brain readback', actual_reader='e46b CEO brain adapter current state', severity='P0', affects_current_state=True),
        _record('e50b_public_source_receipts', 'operations/external_validation/e50b_public_source_receipts.jsonl', 'bridge-labs', 'evidence_closure_capability', required_reader='commercial decision packet evidence summary', actual_reader='E50B/E51 evidence packet', severity='P2'),
        _record('k9audit_read_only_context', 'README.md', 'K9Audit', 'evidence_closure_capability', required_reader='E51 audit context', actual_reader='E51 runtime archaeology/evidence packet', severity='P2'),
        # Boundary centerline.
        _record('e50c_no_go_boundary_policy', 'operations/external_validation/e50c_ceo_brain_centerline_policy.json', 'bridge-labs', 'boundary_capability', actual_binding=['Y_star_gov_boundary', 'gov_mcp_boundary', 'CEO_brain'], required_reader='CEO brain and anti-drift gate', actual_reader='E50C/E51 gates', required_gate='Y-star-gov/gov-mcp anti-drift gate', actual_gate='E51 capability binding gate', severity='P0', agent_facing=True),
        _record('y_star_gov_capability_binding_validator', 'ystar/governance/capability_centerline_binding.py', 'Y-star-gov', 'boundary_capability', actual_binding=['Y_star_gov_boundary'], required_reader='Bridge Labs validator runner', actual_reader='E51 binding repair runner', required_gate='Y-star-gov invariant', actual_gate='Y-star-gov targeted tests', severity='P0'),
        _record('gov_mcp_capability_binding_tools', 'gov_mcp/runtime_linkage_tools.py', 'gov-mcp', 'boundary_capability', actual_binding=['Y_star_gov_boundary', 'gov_mcp_boundary'], required_reader='E51 binding repair harness', actual_reader='E51 binding repair harness', required_gate='gov-mcp tool gate', actual_gate='FakeMCP ALLOW/DENY tests', severity='P0', agent_facing=True),
        # Historical/current stale references.
        _record('e43_original_first_value_route', 'operations/external_validation/e43_selected_first_value_path.json', 'bridge-labs', 'reference_only_artifact', actual_binding=['reference_only'], binding_status='reference_only_ok', remediation='mark_reference_only', severity='P2', evidence_basis='Superseded by E50B/E50C current route state.'),
        _record('e49_money_route_decision', 'operations/external_validation/e49_selected_money_route_semantic_decision.json', 'bridge-labs', 'reference_only_artifact', actual_binding=['reference_only'], binding_status='reference_only_ok', remediation='mark_reference_only', severity='P2', evidence_basis='Superseded by E50B counterfactual commercial decision.'),
    ]
    counts = Counter(record['functional_class'] for record in records)
    status_counts = Counter(record['binding_status'] for record in records)
    gaps = [record for record in records if record['binding_status'] in {'missing_binding', 'wrong_centerline', 'unknown'}]
    return {
        'artifact_id': 'e51_capability_centerline_binding_audit',
        'generated_at': '2026-05-06T00:00:00Z',
        'record_count': len(records),
        'functional_class_counts': dict(counts),
        'binding_status_counts': dict(status_counts),
        'records': records,
        'p0_gaps_before_repair': [record for record in gaps if record['severity'] == 'P0'],
        'all_required_functional_classes_represented': set(counts) == set(CENTERLINES),
        'no_external_action': True,
    }


def render_capability_centerline_binding_audit_markdown(data: dict[str, Any]) -> str:
    lines = ['# E51 Capability Centerline Binding Audit', '', f"Records: {data['record_count']}", '', '## Functional Classes']
    lines += [f'- {key}: {value}' for key, value in sorted(data['functional_class_counts'].items())]
    lines += ['', '## Binding Status Counts']
    lines += [f'- {key}: {value}' for key, value in sorted(data['binding_status_counts'].items())]
    lines += ['', f"P0 gaps before repair: {len(data['p0_gaps_before_repair'])}", '', 'No external action occurred.', '']
    return '\n'.join(lines)


def write_capability_centerline_binding_audit(output_root: Path | None = None) -> dict[str, Any]:
    data = build_capability_centerline_binding_audit()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e51_capability_centerline_binding_audit.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e51_capability_centerline_binding_audit.md').write_text(render_capability_centerline_binding_audit_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_capability_centerline_binding_audit(), indent=2, ensure_ascii=False))
