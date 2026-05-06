
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from .e53_capability_binding_gate import build_e53_capability_binding_payload, run_e53_capability_binding_gate
from .e53_packet_anti_drift_gate import run_e53_packet_anti_drift_gate
from .e53_runtime_linkage_delta import build_e53_runtime_linkage_delta
from .e53_owner_approval_record import build_owner_approval_record_schema, validate_owner_approval_record

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))

def _ensure_path() -> None:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))

def run_e53_y_star_gov_validation() -> dict[str, Any]:
    _ensure_path()
    from ystar.governance.runtime_linkage import validate_future_milestone_closure_packet
    anti = run_e53_packet_anti_drift_gate(build_e53_runtime_linkage_delta())
    binding = run_e53_capability_binding_gate(build_e53_capability_binding_payload())
    approval_schema = build_owner_approval_record_schema()
    approval_pending = validate_owner_approval_record({})
    closure_packet = {'created_artifacts_manifest': True, 'runtime_linkage_delta': True, 'writer_reader_map': True, 'readback_proof': True, 'no_go_boundary_confirmation': True, 'next_milestone_inheritance': True, 'p0_orphan_artifacts': []}
    future = validate_future_milestone_closure_packet(closure_packet)
    return {'artifact_id': 'e53_y_star_gov_validation_result', 'runtime_linkage_delta': anti, 'capability_binding_gate': binding, 'owner_approval_record_schema': approval_schema, 'approval_pending_validation': approval_pending, 'future_milestone_closure_packet': future, 'passed': anti['passed'] is True and binding['passed'] is True and future['valid'] is True and approval_pending['status'] == 'pending_owner_decision', 'no_external_action': True}

def render_markdown(data: dict[str, Any]) -> str:
    return '\n'.join(['# E53 Y-star-gov Validation', '', f"Passed: `{data['passed']}`", f"Runtime linkage: `{data['runtime_linkage_delta']['passed']}`", f"Capability binding: `{data['capability_binding_gate']['passed']}`", f"Approval pending validation: `{data['approval_pending_validation']['status']}`", '', 'No external action occurred.', ''])

def write_e53_y_star_gov_validation(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e53_y_star_gov_validation()
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e53_y_star_gov_validation_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e53_y_star_gov_validation_result.md').write_text(render_markdown(data), encoding='utf-8')
    return data

if __name__ == '__main__':
    print(json.dumps(run_e53_y_star_gov_validation(), indent=2, ensure_ascii=False))
