from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))


def _read_text(path: Path, limit: int = 800000) -> str:
    try:
        data = path.read_text(encoding='utf-8', errors='ignore')
        return data[:limit]
    except Exception:
        return ''


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _contains(text: str, needles: list[str]) -> bool:
    low = text.lower()
    return any(needle.lower() in low for needle in needles)

from .e50b_counterfactual_runtime_adapter import build_counterfactual_route_matrix

TASK_TEXT = 'What is the fastest credible route for Y*Bridge Labs to make real money or obtain the strongest near-term real user / usage / paid signal, after E50A tool-layer proof closure and counterfactual runtime reconnection?'


def _load_e49_scores() -> dict[str, Any]:
    path = BRIDGE_ROOT / 'operations/external_validation/e49_semantic_route_score_matrix.json'
    return _read_json(path) if path.exists() else {'missing': True, 'path': str(path)}


def _load_e50a_status() -> dict[str, Any]:
    for rel in [
        'operations/external_validation/e50a_mcp_client_blocker_update.json',
        'operations/external_validation/e50a_local_tool_layer_proof_result.json',
    ]:
        path = BRIDGE_ROOT / rel
        if path.exists():
            return {'path': rel, 'data': _read_json(path)}
    return {'path': '', 'data': {'new_status': 'missing_e50a_status'}}


def run_counterfactual_money_route_retest() -> dict[str, Any]:
    e49 = _load_e49_scores()
    e50a = _load_e50a_status()
    matrix = build_counterfactual_route_matrix(TASK_TEXT)
    selected_route = next(route for route in matrix['routes'] if route['route_id'] == matrix['selected_route'])
    nearest = next(route for route in matrix['routes'] if route['route_id'] == matrix['nearest_rejected_or_deferred_route'])
    e50a_status = e50a.get('data', {}).get('new_status') or e50a.get('data', {}).get('final_status') or e50a.get('data', {}).get('classification')
    return {
        'artifact_id': 'e50b_counterfactual_money_route_retest',
        'e50a_status_consumed': e50a_status,
        'e50a_status_path': e50a.get('path'),
        'e49_score_source_available': not e49.get('missing', False),
        'e49_selected_route': (e49.get('selected_route') or {}).get('route_id') if isinstance(e49.get('selected_route'), dict) else e49.get('selected_route'),
        'counterfactual_matrix_id': matrix['matrix_id'],
        'selected_route': selected_route,
        'nearest_rejected_or_deferred_route': nearest,
        'why_selected_beats_nearest': selected_route['why_better_than_nearest_alternative'],
        'route_decisions': {route['route_id']: route['decision'] for route in matrix['routes']},
        'no_external_action': True,
        'customer_validation_claimed': False,
        'paid_signal_claimed': False,
    }


if __name__ == '__main__':
    print(json.dumps(run_counterfactual_money_route_retest(), indent=2, ensure_ascii=False))
