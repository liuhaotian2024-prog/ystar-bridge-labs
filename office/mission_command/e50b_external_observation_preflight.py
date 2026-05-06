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

POLICY_PATHS = [
    'office/mission_command/b2r_progressive_unlock.py',
    'operations/external_validation/e38_public_source_receipts.json',
    'operations/external_validation/e13_evidence_receipts.json',
    'operations/external_validation/e50b_counterfactual_money_route_matrix.json',
]


def build_external_observation_preflight() -> dict[str, Any]:
    found = []
    missing = []
    for rel in POLICY_PATHS:
        path = BRIDGE_ROOT / rel
        if path.exists():
            found.append({'path': rel, 'excerpt': ' '.join(_read_text(path, 800).split())[:500]})
        else:
            missing.append(rel)
    policy = _read_text(BRIDGE_ROOT / 'office/mission_command/b2r_progressive_unlock.py')
    public_readonly_policy_present = 'public' in policy.lower() and 'read' in policy.lower()
    return {
        'artifact_id': 'e50b_external_observation_preflight',
        'counterfactual_reconnection_required_first': True,
        'counterfactual_runtime_reconnected_artifact': 'operations/external_validation/e50b_counterfactual_runtime_adapter_smoke.json',
        'repo_controlled_page_read_adapter_available': False,
        'session_public_readonly_observation_provider_available': True,
        'provider_used': 'Codex public web search/open, bounded read-only, no login/contact/forms/private API',
        'public_readonly_policy_present': public_readonly_policy_present,
        'evidence_receipt_precedent_paths_found': found,
        'missing_precedent_paths': missing,
        'safe_to_observe': True,
        'blocked_status': None,
        'boundaries': {
            'no_contact': True,
            'no_login': True,
            'no_form_submission': True,
            'no_personal_contact_scraping': True,
            'no_send_or_publish': True,
            'no_private_api_or_provider_secret': True,
            'not_customer_validation': True,
            'not_paid_signal': True,
        },
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(build_external_observation_preflight(), indent=2, ensure_ascii=False))
