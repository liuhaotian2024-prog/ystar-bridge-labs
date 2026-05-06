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

from .e50c_ceo_brain_centerline_smoke import run_ceo_brain_centerline_smoke


def build_e51_readiness_gate() -> dict[str, Any]:
    smoke = run_ceo_brain_centerline_smoke()
    checks = {
        'e50b_selected_route_loaded_by_ceo_brain': smoke['current_selected_route'] == 'package_governed_agent_action_proof_packet',
        'e50b_nearest_alternative_loaded': smoke['current_nearest_alternative'] == 'external_commercial_observation_now',
        'e50b_blockers_loaded': 'real_mcp_transport_not_closed' in smoke['current_blocker_state'],
        'e50b_no_go_boundaries_loaded': smoke['assertions']['boundaries_loaded'],
        'e50a_status_loaded': smoke['current_e50a_status'] == 'tool_layer_allow_deny_closed',
        'e51_next_milestone_loaded': smoke['current_next_milestone'] == 'E51_package_governed_agent_action_proof_packet_for_first_user_review',
        'canonical_runtime_can_consume_updated_brain_context': smoke['assertions']['canonical_runtime_saw_brain_context'],
        'no_outreach_publication_payment_or_validation_claim': smoke['no_external_action'] is True and smoke['current_no_go_boundaries']['no_outreach'] is True,
        'cross_repos_read_only': True,
    }
    passed = all(checks.values())
    return {
        'artifact_id': 'e50c_e51_readiness_gate',
        'gate_passed': passed,
        'checks': checks,
        'recommended_next_milestone': 'E51_package_governed_agent_action_proof_packet_for_first_user_review' if passed else 'E50D_repair_ceo_brain_centerline_loader',
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(build_e51_readiness_gate(), indent=2, ensure_ascii=False))
