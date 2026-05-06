from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
CODE_ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path, limit: int = 800000) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')[:limit]
    except Exception:
        return ''


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _contains(text: str, needle: str) -> bool:
    return needle.lower() in text.lower()

from .e46b_ceo_brain_adapter import load_ceo_brain_context
from .e46b_canonical_ceo_operating_runtime import run_canonical_ceo_operating_runtime

TASK = {
    'task_id': 'e50c_centerline_smoke',
    'task_title': 'E50C CEO brain centerline smoke',
    'task_description': 'Prepare E51 proof packet packaging only after loading E50B current decision state from CEO brain.',
}


def run_ceo_brain_centerline_smoke() -> dict[str, Any]:
    brain = load_ceo_brain_context(TASK)
    canonical = run_canonical_ceo_operating_runtime(TASK, mode='brain_centerline_smoke')
    runtime_brain = canonical.get('ceo_brain_context', {})
    boundaries = brain.get('current_no_go_boundaries', {})
    expected = {
        'selected_route_loaded': brain.get('current_selected_route') == 'package_governed_agent_action_proof_packet',
        'nearest_alternative_loaded': brain.get('current_nearest_alternative') == 'external_commercial_observation_now',
        'next_milestone_loaded': brain.get('current_next_milestone') == 'E51_package_governed_agent_action_proof_packet_for_first_user_review',
        'blocker_loaded': 'real_mcp_transport_not_closed' in str(brain.get('current_blocker_state', '')) and brain.get('current_e50a_status') == 'tool_layer_allow_deny_closed',
        'boundaries_loaded': all(boundaries.get(key) is True for key in ['no_outreach', 'no_publication', 'no_customer_validation_claim', 'no_paid_signal_claim', 'owner_approval_required_before_external_action']),
        'canonical_runtime_saw_brain_context': runtime_brain.get('current_selected_route') == brain.get('current_selected_route'),
    }
    return {
        'artifact_id': 'e50c_ceo_brain_centerline_smoke_result',
        'task': TASK,
        'brain_centerline_status': brain.get('brain_centerline_status'),
        'current_selected_route': brain.get('current_selected_route'),
        'current_nearest_alternative': brain.get('current_nearest_alternative'),
        'current_next_milestone': brain.get('current_next_milestone'),
        'current_blocker_state': brain.get('current_blocker_state'),
        'current_e50a_status': brain.get('current_e50a_status'),
        'current_e50b_status': brain.get('current_e50b_status'),
        'current_no_go_boundaries': boundaries,
        'canonical_runtime_consumption': {
            'canonical_runtime_invoked': True,
            'canonical_brain_context_selected_route': runtime_brain.get('current_selected_route'),
            'canonical_brain_context_next_milestone': runtime_brain.get('current_next_milestone'),
            'canonical_route_decision': canonical.get('route_decision', {}),
            'no_external_action': canonical.get('no_external_action'),
        },
        'assertions': expected,
        'passes': all(expected.values()),
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(run_ceo_brain_centerline_smoke(), indent=2, ensure_ascii=False))
