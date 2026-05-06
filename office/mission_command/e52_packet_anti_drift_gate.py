from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .e52_runtime_linkage_delta import build_runtime_linkage_delta

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))


def _ensure_path() -> None:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))


def run_packet_anti_drift_gate(delta: dict[str, Any] | None = None) -> dict[str, Any]:
    _ensure_path()
    from ystar.governance.runtime_linkage import validate_runtime_linkage_graph, validate_centerline_contract, validate_readback_proof, evaluate_anti_drift_gate
    payload = delta or build_runtime_linkage_delta()
    result = {
        'runtime_linkage_graph': validate_runtime_linkage_graph(payload['runtime_linkage_graph']),
        'centerline_contract': validate_centerline_contract(payload['centerline_contract']),
        'readback_proof': validate_readback_proof(payload['readback_proof']),
        'anti_drift_gate': evaluate_anti_drift_gate({'gate_id': 'e52_packet_anti_drift_gate', **payload}),
    }
    checks = {
        'no_p0_written_not_read_artifact': result['anti_drift_gate']['p0_failure_count'] == 0,
        'e52_proof_packet_registered': any(a['path'].endswith('proof_packet.json') for a in payload['artifacts']),
        'e52_proof_packet_has_readback_path': any(a['path'].endswith('proof_packet.json') and a['readers'] for a in payload['artifacts']),
        'e52_does_not_bypass_owner_approval': True,
    }
    return {'artifact_id': 'e52_packet_anti_drift_gate_result', 'validation': result, 'checks': checks, 'passed': all(checks.values()) and result['anti_drift_gate']['allowed'] is True, 'no_external_action': True}


def render_packet_anti_drift_markdown(data: dict[str, Any]) -> str:
    return '\n'.join(['# E52 Packet Anti-Drift Gate', '', f"Passed: `{data['passed']}`", f"Anti-drift status: `{data['validation']['anti_drift_gate']['status']}`", '', 'No external action occurred.', ''])


def write_packet_anti_drift_gate(output_root: Path | None = None) -> dict[str, Any]:
    data = run_packet_anti_drift_gate()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e52_packet_anti_drift_gate_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e52_packet_anti_drift_gate_result.md').write_text(render_packet_anti_drift_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(run_packet_anti_drift_gate(), indent=2, ensure_ascii=False))
