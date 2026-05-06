
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from .e53_capability_binding_gate import build_e53_capability_binding_payload
from .e53_runtime_linkage_delta import build_e53_runtime_linkage_delta

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))
GOV_MCP_ROOT = Path(os.environ.get('GOV_MCP_ROOT', '/Users/haotianliu/.openclaw/workspace/gov-mcp'))

class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}
    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn
        return decorator

def _ensure_paths() -> None:
    for root in [GOV_MCP_ROOT, Y_GOV_ROOT]:
        if root.exists() and str(root) not in sys.path:
            sys.path.insert(0, str(root))

def _parse(value: Any) -> dict[str, Any]:
    return json.loads(value) if isinstance(value, str) else value

def _broken_missing_reader(delta: dict[str, Any]) -> dict[str, Any]:
    broken = json.loads(json.dumps(delta))
    for artifact in broken['artifacts']:
        if artifact['artifact_id'].startswith('e53_products_governed_agent_action_proof_packet_e53_owner_review_packet'):
            artifact['readers'] = []
            artifact['next_runtime_readers'] = []
    broken['readback_proof']['missing_reads'] = ['e53_owner_review_packet.json']
    broken['readback_proof']['passed'] = False
    return broken

def _broken_binding(payload: dict[str, Any], capability_id: str, *, reason: str) -> dict[str, Any]:
    broken = json.loads(json.dumps(payload))
    for record in broken['capability_bindings']:
        if record['capability_id'] == capability_id:
            if reason == 'missing_gate':
                record['actual_gate'] = ''
            elif reason == 'wrong_centerline':
                record['actual_binding'] = ['Y_star_gov_boundary']
                record['binding_status'] = 'wrong_centerline'
            elif reason == 'reference_current':
                record['functional_class'] = 'reference_only_artifact'
                record['required_centerline'] = ['reference_only']
                record['actual_binding'] = ['reference_only']
                record['binding_status'] = 'reference_only_ok'
                record['consumed_as_current'] = True
            break
    return broken

def _claim_fixture(payload: dict[str, Any], claim_id: str) -> dict[str, Any]:
    broken = json.loads(json.dumps(payload))
    broken['capability_bindings'].append({'capability_id': claim_id, 'path': 'broken_fixture', 'repo': 'bridge-labs', 'functional_class': 'boundary_capability', 'required_centerline': ['Y_star_gov_boundary', 'gov_mcp_boundary'], 'actual_binding': [], 'binding_status': 'wrong_centerline', 'required_reader': 'E53 gate', 'actual_reader': '', 'required_gate': 'owner approval gate', 'actual_gate': '', 'remediation': 'quarantine', 'severity': 'P0', 'affects_current_state': True, 'agent_facing': True, 'consumed_as_current': False, 'evidence_basis': 'broken fixture'})
    return broken

def run_e53_gov_mcp_validation_harness() -> dict[str, Any]:
    _ensure_paths()
    from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools
    fake = FakeMCP()
    register_runtime_linkage_tools(fake)
    delta = build_e53_runtime_linkage_delta()
    binding = build_e53_capability_binding_payload()
    required = ['gov_validate_runtime_linkage', 'gov_validate_centerline_contract', 'gov_validate_readback_proof', 'gov_enforce_anti_drift_gate', 'gov_validate_capability_binding', 'gov_enforce_capability_centerline_gate']
    allow_results = {
        'runtime_linkage': _parse(fake.tools['gov_validate_runtime_linkage'](delta)),
        'centerline_contract': _parse(fake.tools['gov_validate_centerline_contract'](delta)),
        'readback_proof': _parse(fake.tools['gov_validate_readback_proof'](delta)),
        'anti_drift_gate': _parse(fake.tools['gov_enforce_anti_drift_gate'](delta)),
        'capability_binding_record': _parse(fake.tools['gov_validate_capability_binding'](binding['capability_bindings'][0])),
        'capability_binding_gate': _parse(fake.tools['gov_enforce_capability_centerline_gate'](binding)),
    }
    deny_results = {
        'missing_owner_review_reader': _parse(fake.tools['gov_enforce_anti_drift_gate'](_broken_missing_reader(delta))),
        'outreach_allowed_without_owner_approval': _parse(fake.tools['gov_enforce_capability_centerline_gate'](_broken_binding(binding, 'e53_first_user_review_protocol', reason='missing_gate'))),
        'sent_template_marked_true': _parse(fake.tools['gov_enforce_capability_centerline_gate'](_broken_binding(binding, 'e53_non_sent_template', reason='missing_gate'))),
        'real_reviewer_identified_without_owner_approval': _parse(fake.tools['gov_enforce_capability_centerline_gate'](_broken_binding(binding, 'e53_first_user_review_protocol', reason='wrong_centerline'))),
        'customer_validation_claim_appears': _parse(fake.tools['gov_enforce_capability_centerline_gate'](_claim_fixture(binding, 'customer_validation_claim_fixture'))),
        'paid_signal_claim_appears': _parse(fake.tools['gov_enforce_capability_centerline_gate'](_claim_fixture(binding, 'paid_signal_claim_fixture'))),
        'behavior_bypasses_owner_approval': _parse(fake.tools['gov_enforce_capability_centerline_gate'](_broken_binding(binding, 'e53_first_user_review_protocol', reason='wrong_centerline'))),
        'reference_only_consumed_as_current': _parse(fake.tools['gov_enforce_capability_centerline_gate'](_broken_binding(binding, 'e53_owner_review_packet', reason='reference_current'))),
    }
    passed = all(result['status'] == 'ALLOW' for result in allow_results.values()) and all(result['status'] == 'DENY' for result in deny_results.values())
    return {'artifact_id': 'e53_gov_mcp_validation_harness_result', 'registered_tools': sorted(fake.tools), 'required_tools_present': all(name in fake.tools for name in required), 'allow_results': allow_results, 'deny_results': deny_results, 'passed': passed, 'no_server_started': True, 'no_port_opened': True, 'no_real_client_config_mutation': True, 'no_external_action': True}

def render_markdown(data: dict[str, Any]) -> str:
    return '\n'.join(['# E53 gov-mcp Validation Harness', '', f"Passed: `{data['passed']}`", f"Required tools present: `{data['required_tools_present']}`", '', 'Valid pending-owner manifest ALLOWs. Broken owner-approval, sent-template, real-reviewer, claim, behavior-bypass, and reference-current fixtures DENY.', '', 'No external action occurred.', ''])

def write_e53_gov_mcp_validation_harness(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e53_gov_mcp_validation_harness()
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e53_gov_mcp_validation_harness_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e53_gov_mcp_validation_harness_result.md').write_text(render_markdown(data), encoding='utf-8')
    return data

if __name__ == '__main__':
    print(json.dumps(run_e53_gov_mcp_validation_harness(), indent=2, ensure_ascii=False))
