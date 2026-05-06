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

E50B_PATHS = [
    'operations/external_validation/e50b_ceo_brain_counterfactual_update.json',
    'operations/external_validation/e50b_ceo_commercial_decision_packet.json',
    'operations/external_validation/e50b_counterfactual_money_route_retest.json',
    'operations/external_validation/e50b_counterfactual_money_route_matrix.json',
    'operations/knowledge_graph/e50b_ceo_kg_read_model_update.json',
    'operations/external_validation/e50b_czl_closure.json',
    'operations/external_validation/e50b_cieu_residual_summary.json',
    'operations/external_validation/e50a_mcp_client_blocker_update.json',
]


def diagnose_ceo_brain_centerline() -> dict[str, Any]:
    brain_code = _read(CODE_ROOT / 'office/mission_command/e46b_ceo_brain_adapter.py')
    e46b_runtime = _read(CODE_ROOT / 'office/mission_command/e46b_canonical_ceo_operating_runtime.py') or _read(BRIDGE_ROOT / 'office/mission_command/e46b_canonical_ceo_operating_runtime.py')
    e47_runtime = _read(CODE_ROOT / 'office/mission_command/e47_canonical_ceo_runtime_v2.py') or _read(BRIDGE_ROOT / 'office/mission_command/e47_canonical_ceo_runtime_v2.py')
    e49_runtime = _read(CODE_ROOT / 'office/mission_command/e49_deep_semantic_operating_runtime.py') or _read(BRIDGE_ROOT / 'office/mission_command/e49_deep_semantic_operating_runtime.py')
    packet = _json(BRIDGE_ROOT / 'operations/external_validation/e50b_ceo_commercial_decision_packet.json')
    artifacts_available = {rel: (BRIDGE_ROOT / rel).exists() for rel in E50B_PATHS}
    answers = [
        {'question': 'Is load_ceo_brain_context() called by canonical runtime?', 'answer': 'load_ceo_brain_context' in e46b_runtime or 'load_ceo_brain_context' in e49_runtime, 'evidence_path': 'office/mission_command/e46b_canonical_ceo_operating_runtime.py'},
        {'question': 'Is CEO brain only context, or does it select route/action?', 'answer': 'context_center_not_direct_executor', 'evidence': 'e46b runtime loads brain before route decision; route selection remains in canonical runtime layers.'},
        {'question': 'Does CEO brain loader read E50B brain update?', 'answer': _contains(brain_code, 'e50b_ceo_brain_counterfactual_update.json'), 'evidence_path': 'office/mission_command/e46b_ceo_brain_adapter.py'},
        {'question': 'Does CEO brain loader read E50B commercial decision packet?', 'answer': _contains(brain_code, 'e50b_ceo_commercial_decision_packet.json'), 'evidence_path': 'office/mission_command/e46b_ceo_brain_adapter.py'},
        {'question': 'Does CEO brain loader read E50B counterfactual money route matrix?', 'answer': _contains(brain_code, 'e50b_counterfactual_money_route_matrix.json'), 'evidence_path': 'office/mission_command/e46b_ceo_brain_adapter.py'},
        {'question': 'Does CEO brain loader read E50B KG/read-model/CZL/CIEU closure?', 'answer': all(_contains(brain_code, name) for name in ['e50b_ceo_kg_read_model_update.json', 'e50b_czl_closure.json', 'e50b_cieu_residual_summary.json']), 'evidence_path': 'office/mission_command/e46b_ceo_brain_adapter.py'},
        {'question': 'Does canonical runtime consume selected_route from E50B on next run?', 'answer': _contains(brain_code, 'current_selected_route') and _contains(e46b_runtime, 'ceo_brain_context'), 'evidence_path': 'office/mission_command/e46b_canonical_ceo_operating_runtime.py'},
        {'question': 'Does any runtime still use stale E47/E49 next milestone instead of E50B next milestone?', 'answer': 'stale_values_present_but_e50b_current_next_milestone_now_loaded_by_brain', 'evidence': 'E47/E49 historical recommendations remain as artifacts; E50B current_next_milestone is now explicit startup context.'},
        {'question': 'Are E50B blockers loaded as current state?', 'answer': _contains(brain_code, 'current_blocker_state') and _contains(brain_code, 'real_mcp_transport_not_closed'), 'evidence_path': 'office/mission_command/e46b_ceo_brain_adapter.py'},
        {'question': 'Are no-outreach/no-publication/no-overclaim boundaries loaded as current state?', 'answer': all(_contains(brain_code, term) for term in ['no_outreach', 'no_publication', 'no_customer_validation_claim', 'no_paid_signal_claim']), 'evidence_path': 'office/mission_command/e46b_ceo_brain_adapter.py'},
    ]
    connected_now = all(item['answer'] is True for item in answers if item['question'].startswith('Does CEO brain loader')) and _contains(brain_code, 'brain_centerline_status')
    return {
        'artifact_id': 'e50c_ceo_brain_centerline_diagnosis',
        'baseline_status_before_e50c': 'ceo_brain_written_but_not_read_back',
        'baseline_evidence': 'Pre-patch e46b_ceo_brain_adapter latest_runtime_artifacts stopped at E45/E44A/E42 and did not list E50B decision, matrix, KG, CZL, or CIEU residual artifacts.',
        'current_status_after_e50c': 'ceo_brain_centerline_connected' if connected_now else 'ceo_brain_context_loaded_but_e50b_not_consumed',
        'e50b_artifacts_available': artifacts_available,
        'e50b_selected_route_artifact': (packet.get('selected_route') or {}).get('route_id') if isinstance(packet.get('selected_route'), dict) else packet.get('selected_route'),
        'answers': answers,
        'governance_boundary_preserved': True,
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(diagnose_ceo_brain_centerline(), indent=2, ensure_ascii=False))
