from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .e51_labs_runtime_linkage_manifest import build_labs_runtime_linkage_manifest

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))


def _ensure_path() -> None:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))


def validate_labs_manifest_through_y_star_gov(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    _ensure_path()
    from ystar.governance.anti_drift_gate import evaluate_anti_drift_gate, validate_future_milestone_closure_packet
    from ystar.governance.centerline_contract import validate_centerline_contract
    from ystar.governance.readback_proof import validate_readback_proof
    from ystar.governance.runtime_linkage import validate_runtime_linkage_graph

    payload = manifest or build_labs_runtime_linkage_manifest()
    graph = validate_runtime_linkage_graph(payload['runtime_linkage_graph'])
    contract = validate_centerline_contract(payload['centerline_contract'])
    proof = validate_readback_proof(payload['readback_proof'])
    gate = evaluate_anti_drift_gate(payload)
    policy = validate_future_milestone_closure_packet(payload['future_milestone_closure_policy_input'])
    passed = all(item.get('valid') is True for item in [graph, contract, proof, policy]) and gate.get('allowed') is True
    return {
        'artifact_id': 'e51_y_star_gov_linkage_validation_result',
        'y_star_gov_root': str(Y_GOV_ROOT),
        'runtime_graph': graph,
        'centerline_contract': contract,
        'readback_proof': proof,
        'anti_drift_gate': gate,
        'future_milestone_closure_policy': policy,
        'passed': passed,
        'no_external_action': True,
    }


def render_validation_markdown(data: dict[str, Any]) -> str:
    gate = data['anti_drift_gate']
    return '\n'.join(['# E51 Y-star-gov Linkage Validation', '', f"Passed: `{data['passed']}`", f"Anti-drift status: `{gate.get('status')}`", f"Validated artifacts: `{gate.get('validated_artifact_count')}`", f"P0 failures: `{gate.get('p0_failure_count')}`", '', 'No external action occurred.', ''])


def write_y_star_gov_validation_result(output_root: Path | None = None) -> dict[str, Any]:
    data = validate_labs_manifest_through_y_star_gov()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e51_y_star_gov_linkage_validation_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e51_y_star_gov_linkage_validation_result.md').write_text(render_validation_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(validate_labs_manifest_through_y_star_gov(), indent=2, ensure_ascii=False))
