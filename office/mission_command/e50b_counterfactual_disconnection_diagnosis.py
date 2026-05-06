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

from .e50b_counterfactual_asset_inventory import build_counterfactual_asset_inventory


def _has_all(text: str, terms: list[str]) -> bool:
    low = text.lower()
    return all(term.lower() in low for term in terms)


def _evidence(path: str, terms: list[str]) -> dict[str, Any]:
    text = _read_text(BRIDGE_ROOT / path)
    return {
        'path': path,
        'terms_checked': terms,
        'present': {term: (term.lower() in text.lower()) for term in terms},
        'excerpt': ' '.join(text[:600].split()),
    }


def diagnose_counterfactual_disconnection() -> dict[str, Any]:
    inventory = build_counterfactual_asset_inventory()
    scorer = _read_text(BRIDGE_ROOT / 'office/mission_command/e49_semantic_route_scorer.py')
    semantic_runtime = _read_text(BRIDGE_ROOT / 'office/mission_command/e49_deep_semantic_operating_runtime.py')
    brain = _read_text(BRIDGE_ROOT / 'office/mission_command/e46b_ceo_brain_adapter.py')
    v2 = _read_text(BRIDGE_ROOT / 'office/mission_command/e47_canonical_ceo_runtime_v2.py')
    router = _read_text(BRIDGE_ROOT / 'office/mission_command/counterfactual_router.py')

    questions = [
        {
            'question_id': 'e49_consumes_gov005_counterfactual_format',
            'answer': _has_all(scorer, ['GOV-005', 'Xt', 'Y*']),
            'evidence': _evidence('office/mission_command/e49_semantic_route_scorer.py', ['GOV-005', 'Xt', 'Y*', 'counterfactual']),
            'impact': 'Route scores omit the existing proposal discipline that forces explicit current state, target and intervention.',
        },
        {
            'question_id': 'e49_consumes_autonomous_loop_counterfactual_logic',
            'answer': _has_all(scorer, ['autonomous_loop', 'counterfactual']),
            'evidence': _evidence('office/mission_command/e49_semantic_route_scorer.py', ['autonomous_loop', 'counterfactual', 'Rt+1']),
            'impact': 'Autonomous-loop wisdom remains outside the commercial decision engine.',
        },
        {
            'question_id': 'e49_route_has_xt_y_star_u_predicted_y_rt',
            'answer': _has_all(scorer, ['Xt_current_state', 'Y_star_target', 'U_intervention', 'predicted_Yt_plus_1', 'predicted_Rt_plus_1']),
            'evidence': _evidence('office/mission_command/e49_semantic_route_scorer.py', ['Xt_current_state', 'Y_star_target', 'U_intervention', 'predicted_Yt_plus_1', 'predicted_Rt_plus_1']),
            'impact': 'Routes are typed semantically but not counterfactually.',
        },
        {
            'question_id': 'e49_distinguishes_counterfactual_route_classes',
            'answer': _has_all(scorer, ['nearest_rejected', 'deferred', 'quarantined', 'denied']),
            'evidence': _evidence('office/mission_command/e49_semantic_route_scorer.py', ['nearest_rejected', 'deferred', 'quarantined', 'denied']),
            'impact': 'Selection does not preserve the nearest rejected/deferred alternative as a learning object.',
        },
        {
            'question_id': 'ceo_brain_loads_counterfactual_structured_field',
            'answer': _has_all(brain, ['counterfactual', 'structured']),
            'evidence': _evidence('office/mission_command/e46b_ceo_brain_adapter.py', ['counterfactual', 'structured', 'wisdom_search']),
            'impact': 'Counterfactual wisdom can be context, but it is not loaded as an active decision field.',
        },
        {
            'question_id': 'canonical_runtime_v2_calls_counterfactual_adapter',
            'answer': 'counterfactual' in v2.lower() and 'adapter' in v2.lower(),
            'evidence': _evidence('office/mission_command/e47_canonical_ceo_runtime_v2.py', ['counterfactual', 'adapter']),
            'impact': 'The v2 mainline can pass coverage while skipping counterfactual comparison.',
        },
        {
            'question_id': 'previous_sandbox_learnings_used_in_current_commercial_decision',
            'answer': 'sandbox' in scorer.lower() and 'retrospective' in scorer.lower(),
            'evidence': _evidence('office/mission_command/e49_semantic_route_scorer.py', ['sandbox', 'retrospective']),
            'impact': 'Sandbox replay assets are not active in current commercial route choice.',
        },
        {
            'question_id': 'machine_readable_counterfactual_route_matrix_exists_before_e50b',
            'answer': (BRIDGE_ROOT / 'operations/external_validation/e50b_counterfactual_money_route_matrix.json').exists(),
            'evidence': {'path': 'operations/external_validation/e50b_counterfactual_money_route_matrix.json'},
            'impact': 'E50B must create this artifact if it is absent.',
        },
    ]
    true_count = sum(1 for item in questions if item['answer'] is True)
    assets_present = inventory['asset_count'] > 0 and bool(router)
    if assets_present and true_count < 3:
        final_status = 'counterfactual_assets_present_but_runtime_disconnected'
    elif assets_present:
        final_status = 'counterfactual_wisdom_loaded_but_not_decision_active'
    else:
        final_status = 'counterfactual_assets_missing'
    return {
        'artifact_id': 'e50b_counterfactual_disconnection_diagnosis',
        'final_status': final_status,
        'questions': questions,
        'asset_count': inventory['asset_count'],
        'counterfactual_router_present': bool(router),
        'fix_required': final_status != 'counterfactual_runtime_connected',
        'fix_implemented_in_e50b': 'Add bridge-labs runtime adapter that translates existing GOV-005/CEO wisdom assets into a machine-readable counterfactual route matrix.',
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(diagnose_counterfactual_disconnection(), indent=2, ensure_ascii=False))
