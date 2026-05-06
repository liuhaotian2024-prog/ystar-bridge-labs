from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))

REQUIRED_CLOSURE_FIELDS = [
    'created_artifacts_manifest', 'runtime_linkage_delta', 'writer_reader_map', 'readback_proof',
    'selected_route_inheritance_check', 'ceo_brain_current_state_update', 'kg_czl_cieu_closure',
    'y_star_gov_validation_result', 'gov_mcp_anti_drift_gate_result', 'no_go_boundary_confirmation',
    'no_report_only_p0_guarantee', 'next_milestone_inheritance_field',
]

BLOCKING_FAILURES = [
    'decision packet has no runtime reader',
    'brain update not consumed by brain loader',
    'KG update not reflected in read model',
    'route update not inherited by next milestone',
    'closure lacks CIEU/CZL linkage',
    'proof only checks file existence',
    'strategy/route/blocker changed without CEO brain current-state update',
    'Y-star-gov/gov-mcp validation bypassed',
    'P0 orphan artifacts remain',
]


def build_future_milestone_closure_policy() -> dict[str, Any]:
    return {
        'artifact_id': 'e51_future_milestone_closure_policy',
        'required_fields': REQUIRED_CLOSURE_FIELDS,
        'blocking_failures': BLOCKING_FAILURES,
        'completion_rule': 'A milestone is not complete until writer/reader/readback/gate evidence exists for every decision-state artifact.',
        'y_star_gov_required': True,
        'gov_mcp_required': True,
        'no_report_only_p0': True,
        'owner_approval_required_for_external_action': True,
        'no_external_action': True,
    }


def render_future_milestone_closure_policy_markdown(data: dict[str, Any]) -> str:
    lines = ['# E51 Future Milestone Closure Policy', '', data['completion_rule'], '', '## Required Fields']
    lines += [f'- {item}' for item in data['required_fields']]
    lines += ['', '## Blocking Failures']
    lines += [f'- {item}' for item in data['blocking_failures']]
    lines += ['', 'No external action occurred.', '']
    return '\n'.join(lines)


def write_future_milestone_closure_policy(output_root: Path | None = None) -> dict[str, Any]:
    data = build_future_milestone_closure_policy()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e51_future_milestone_closure_policy.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e51_future_milestone_closure_policy.md').write_text(render_future_milestone_closure_policy_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_future_milestone_closure_policy(), indent=2, ensure_ascii=False))
