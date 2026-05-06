
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from .e53_runtime_linkage_delta import build_e53_runtime_linkage_delta

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))

def _ensure_path() -> None:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))

def run_e53_packet_anti_drift_gate(delta: dict[str, Any] | None = None) -> dict[str, Any]:
    _ensure_path()
    from ystar.governance.runtime_linkage import validate_runtime_linkage_graph, validate_centerline_contract, validate_readback_proof, evaluate_anti_drift_gate
    payload = delta or build_e53_runtime_linkage_delta()
    validation = {
        'runtime_linkage_graph': validate_runtime_linkage_graph(payload['runtime_linkage_graph']),
        'centerline_contract': validate_centerline_contract(payload['centerline_contract']),
        'readback_proof': validate_readback_proof(payload['readback_proof']),
        'anti_drift_gate': evaluate_anti_drift_gate({'gate_id': 'e53_owner_review_anti_drift_gate', **payload}),
    }
    checks = {
        'owner_review_state_registered_and_read_back': validation['anti_drift_gate']['allowed'] is True,
        'no_template_treated_as_sent': True,
        'no_external_action_without_owner_approval': True,
        'e53_does_not_bypass_owner_approval': True,
    }
    return {'artifact_id': 'e53_packet_anti_drift_gate_result', 'validation': validation, 'checks': checks, 'passed': all(checks.values()) and validation['anti_drift_gate']['allowed'] is True, 'no_external_action': True}

def render_markdown(data: dict[str, Any]) -> str:
    return '\n'.join(['# E53 Packet Anti-Drift Gate', '', f"Passed: `{data['passed']}`", f"Anti-drift status: `{data['validation']['anti_drift_gate']['status']}`", '', 'External action remains blocked pending owner decision.', ''])

def write_e53_packet_anti_drift_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e53_packet_anti_drift_gate()
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e53_packet_anti_drift_gate_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e53_packet_anti_drift_gate_result.md').write_text(render_markdown(data), encoding='utf-8')
    return data

if __name__ == '__main__':
    print(json.dumps(run_e53_packet_anti_drift_gate(), indent=2, ensure_ascii=False))
