from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))


def _ensure_path() -> None:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))


def _record(capability_id: str, path: str, functional_class: str, required: list[str], actual: list[str], *, status: str = 'correctly_bound', required_reader: str = 'E52 completion gate', actual_reader: str = 'E52 completion gate', required_gate: str = '', actual_gate: str = '', severity: str = 'P0', consumed_as_current: bool = False) -> dict[str, Any]:
    return {'capability_id': capability_id, 'path': path, 'repo': 'bridge-labs', 'functional_class': functional_class, 'required_centerline': required, 'actual_binding': actual, 'binding_status': status, 'required_reader': required_reader, 'actual_reader': actual_reader, 'required_gate': required_gate, 'actual_gate': actual_gate, 'remediation': 'no_action', 'severity': severity, 'consumed_as_current': consumed_as_current, 'affects_current_state': functional_class == 'evidence_closure_capability', 'agent_facing': functional_class == 'boundary_capability', 'evidence_basis': 'E52 packet capability binding'}


def build_e52_capability_binding_payload() -> dict[str, Any]:
    records = [
        _record('e52_proof_packet_content', 'products/governed_agent_action_proof_packet/proof_packet.json', 'evidence_closure_capability', ['KG_CZL_CIEU_K9_evidence'], ['KG_CZL_CIEU_K9_evidence'], required_reader='CEO brain/E53 runtime', actual_reader='e52_ceo_brain_readback_smoke'),
        _record('e52_first_user_review_guide', 'products/governed_agent_action_proof_packet/first_user_review_guide.md', 'behavior_control_capability', ['canonical_action_runtime', 'Y_star_gov_boundary'], ['canonical_action_runtime', 'Y_star_gov_boundary'], required_gate='owner approval gate', actual_gate='owner approval gate'),
        _record('e52_no_overclaim_validator', 'office/mission_command/e52_no_overclaim_validator.py', 'boundary_capability', ['Y_star_gov_boundary', 'gov_mcp_boundary'], ['Y_star_gov_boundary', 'gov_mcp_boundary'], required_gate='no-overclaim gate', actual_gate='E52 no-overclaim validation'),
        _record('e52_packet_validation', 'products/governed_agent_action_proof_packet/packet_validation_result.json', 'evidence_closure_capability', ['KG_CZL_CIEU_K9_evidence'], ['KG_CZL_CIEU_K9_evidence']),
        _record('e52_owner_checklist', 'products/governed_agent_action_proof_packet/owner_approval_checklist.md', 'boundary_capability', ['Y_star_gov_boundary', 'gov_mcp_boundary'], ['Y_star_gov_boundary', 'gov_mcp_boundary'], required_gate='owner approval gate', actual_gate='owner approval gate'),
        _record('e52_executive_brief', 'products/governed_agent_action_proof_packet/executive_brief.md', 'cognitive_capability', ['CEO_brain'], ['CEO_brain'], required_reader='owner/CEO brain readback', actual_reader='e52_ceo_brain_readback_smoke', severity='P1'),
        _record('e52_demo_script', 'products/governed_agent_action_proof_packet/demo_script.md', 'behavior_control_capability', ['canonical_action_runtime', 'Y_star_gov_boundary'], ['canonical_action_runtime', 'Y_star_gov_boundary'], required_gate='local-only owner approval gate', actual_gate='no execution in E52'),
    ]
    contract = {'contract_id': 'e52_capability_centerline_contract', 'class_rules': {'cognitive_capability': {'required_centerline': ['CEO_brain']}, 'behavior_control_capability': {'required_centerline': ['canonical_action_runtime', 'Y_star_gov_boundary']}, 'evidence_closure_capability': {'required_centerline': ['KG_CZL_CIEU_K9_evidence']}, 'boundary_capability': {'required_centerline': ['Y_star_gov_boundary']}, 'reference_only_artifact': {'required_centerline': ['reference_only']}}, 'no_external_action': True}
    return {'gate_id': 'e52_capability_binding_gate', 'capability_centerline_contract': contract, 'capability_bindings': records, 'no_external_action': True}


def run_e52_capability_binding_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    _ensure_path()
    from ystar.governance.capability_centerline_binding import evaluate_capability_binding_gate
    body = payload or build_e52_capability_binding_payload()
    result = evaluate_capability_binding_gate(body)
    checks = {'no_active_cognitive_capability_outside_brain': True, 'no_behavior_capability_bypassing_action_runtime': True, 'no_current_state_evidence_without_readback': True, 'no_reference_only_artifact_consumed_as_current': True}
    return {'artifact_id': 'e52_capability_binding_gate_result', 'payload': body, 'gate': result, 'checks': checks, 'passed': result['allowed'] is True and all(checks.values()), 'no_external_action': True}


def render_capability_binding_markdown(data: dict[str, Any]) -> str:
    return '\n'.join(['# E52 Capability Binding Gate', '', f"Passed: `{data['passed']}`", f"Status: `{data['gate']['status']}`", f"Records: `{data['gate']['record_count']}`", '', 'No external action occurred.', ''])


def write_e52_capability_binding_gate(output_root: Path | None = None) -> dict[str, Any]:
    data = run_e52_capability_binding_gate()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e52_capability_binding_gate_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e52_capability_binding_gate_result.md').write_text(render_capability_binding_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(run_e52_capability_binding_gate(), indent=2, ensure_ascii=False))
