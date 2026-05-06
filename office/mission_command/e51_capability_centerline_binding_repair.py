from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .e51_capability_centerline_binding_audit import build_capability_centerline_binding_audit

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))
GOV_MCP_ROOT = Path(os.environ.get('GOV_MCP_ROOT', '/Users/haotianliu/.openclaw/workspace/gov-mcp'))


def _ensure_paths() -> None:
    for root in [Y_GOV_ROOT, GOV_MCP_ROOT]:
        if root.exists() and str(root) not in sys.path:
            sys.path.insert(0, str(root))


def capability_centerline_contract() -> dict[str, Any]:
    return {
        'contract_id': 'e51_capability_centerline_contract',
        'class_rules': {
            'cognitive_capability': {'required_centerline': ['CEO_brain']},
            'behavior_control_capability': {'required_centerline': ['canonical_action_runtime', 'Y_star_gov_boundary']},
            'evidence_closure_capability': {'required_centerline': ['KG_CZL_CIEU_K9_evidence']},
            'boundary_capability': {'required_centerline': ['Y_star_gov_boundary']},
            'reference_only_artifact': {'required_centerline': ['reference_only']},
        },
        'required_gates': ['Y-star-gov capability binding gate', 'gov-mcp capability centerline gate', 'Bridge Labs current readiness anti-drift gate'],
        'owner_approval_boundaries': ['external contact', 'publication', 'payment', 'customer validation claim', 'paid signal claim'],
        'no_external_action': True,
    }


def _parse(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        return json.loads(value)
    return value


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn
        return decorator


def _broken_cognitive_payload(valid_payload: dict[str, Any]) -> dict[str, Any]:
    broken = json.loads(json.dumps(valid_payload))
    for record in broken['capability_bindings']:
        if record['functional_class'] == 'cognitive_capability' and record['severity'] == 'P0':
            record['actual_binding'] = ['reference_only']
            record['binding_status'] = 'missing_binding'
            record['actual_reader'] = ''
            break
    return broken


def _broken_behavior_payload(valid_payload: dict[str, Any]) -> dict[str, Any]:
    broken = json.loads(json.dumps(valid_payload))
    for record in broken['capability_bindings']:
        if record['functional_class'] == 'behavior_control_capability' and record['severity'] == 'P0':
            record['actual_binding'] = ['Y_star_gov_boundary']
            record['binding_status'] = 'wrong_centerline'
            break
    return broken


def _broken_reference_payload(valid_payload: dict[str, Any]) -> dict[str, Any]:
    broken = json.loads(json.dumps(valid_payload))
    for record in broken['capability_bindings']:
        if record['functional_class'] == 'reference_only_artifact':
            record['consumed_as_current'] = True
            break
    return broken


def build_capability_centerline_binding_repair_result() -> dict[str, Any]:
    _ensure_paths()
    from ystar.governance.capability_centerline_binding import evaluate_capability_binding_gate
    from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools

    audit = build_capability_centerline_binding_audit()
    payload = {
        'gate_id': 'e51_capability_centerline_binding_gate',
        'capability_centerline_contract': capability_centerline_contract(),
        'capability_bindings': audit['records'],
        'no_external_action': True,
    }
    y_star_gate = evaluate_capability_binding_gate(payload)
    fake = FakeMCP()
    register_runtime_linkage_tools(fake)
    gov_tool = fake.tools['gov_enforce_capability_centerline_gate']
    gov_allow = _parse(gov_tool(json.dumps(payload)))
    gov_cognitive_deny = _parse(gov_tool(_broken_cognitive_payload(payload)))
    gov_behavior_deny = _parse(gov_tool(_broken_behavior_payload(payload)))
    gov_reference_deny = _parse(gov_tool(_broken_reference_payload(payload)))
    checks = {
        'capability_centerline_binding_gate_passed': y_star_gate['allowed'] is True and gov_allow['status'] == 'ALLOW',
        'no_active_cognitive_capability_outside_brain': all(not (record['functional_class'] == 'cognitive_capability' and record['binding_status'] != 'reference_only_ok' and 'CEO_brain' not in record['actual_binding']) for record in audit['records']),
        'no_behavior_capability_bypassing_action_runtime': all(not (record['functional_class'] == 'behavior_control_capability' and 'canonical_action_runtime' not in record['actual_binding']) for record in audit['records']),
        'no_current_state_evidence_without_readback': all(not (record['functional_class'] == 'evidence_closure_capability' and record.get('affects_current_state') and 'KG_CZL_CIEU_K9_evidence' not in record['actual_binding']) for record in audit['records']),
        'no_reference_only_artifact_consumed_as_current': all(not (record['functional_class'] == 'reference_only_artifact' and record.get('consumed_as_current')) for record in audit['records']),
        'gov_mcp_denies_cognitive_missing_brain': gov_cognitive_deny['status'] == 'DENY',
        'gov_mcp_denies_behavior_bypass': gov_behavior_deny['status'] == 'DENY',
        'gov_mcp_denies_reference_only_current_read': gov_reference_deny['status'] == 'DENY',
    }
    return {
        'artifact_id': 'e51_capability_centerline_binding_repair_result',
        'audit_record_count': audit['record_count'],
        'functional_class_counts': audit['functional_class_counts'],
        'capability_centerline_contract': capability_centerline_contract(),
        'repaired_bindings': audit['records'],
        'y_star_gov_gate': y_star_gate,
        'gov_mcp_allow_proof': gov_allow,
        'gov_mcp_deny_proofs': {
            'cognitive_missing_brain_binding': gov_cognitive_deny,
            'behavior_bypassing_action_runtime': gov_behavior_deny,
            'reference_only_consumed_as_current': gov_reference_deny,
        },
        'checks': checks,
        'passed': all(checks.values()),
        'no_external_action': True,
    }


def render_capability_centerline_binding_repair_markdown(data: dict[str, Any]) -> str:
    lines = ['# E51 Capability Centerline Binding Repair Result', '', f"Passed: `{data['passed']}`", f"Audit records: {data['audit_record_count']}", '', '## Checks']
    lines += [f'- {key}: {value}' for key, value in data['checks'].items()]
    lines += ['', f"Y-star-gov gate: `{data['y_star_gov_gate']['status']}`", f"gov-mcp valid payload: `{data['gov_mcp_allow_proof']['status']}`", '', 'No external action occurred.', '']
    return '\n'.join(lines)


def write_capability_centerline_binding_repair_result(output_root: Path | None = None) -> dict[str, Any]:
    data = build_capability_centerline_binding_repair_result()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e51_capability_centerline_binding_repair_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e51_capability_centerline_binding_repair_result.md').write_text(render_capability_centerline_binding_repair_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_capability_centerline_binding_repair_result(), indent=2, ensure_ascii=False))
