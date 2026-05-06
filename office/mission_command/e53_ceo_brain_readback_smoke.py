
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from .e46b_ceo_brain_adapter import load_ceo_brain_context

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))

def run_e53_ceo_brain_readback_smoke() -> dict[str, Any]:
    context = load_ceo_brain_context({'task_title': 'E53 owner review gate readback', 'task_description': 'verify pending owner decision blocks external action'})
    state = context.get('latest_owner_review_state') or {}
    checks = {
        'ceo_brain_sees_e52_proof_packet_exists': (context.get('latest_proof_packet_state') or {}).get('proof_packet_available') is True,
        'ceo_brain_sees_e53_owner_review_packet_exists': state.get('owner_review_packet_available') is True,
        'ceo_brain_sees_owner_approval_pending': state.get('owner_decision_status') == 'pending_owner_decision',
        'ceo_brain_sees_external_action_blocked': state.get('external_action_allowed') is False,
        'ceo_brain_sees_non_sent_template_not_sent': state.get('non_sent_template_sent') is False,
        'ceo_brain_sees_no_real_reviewer_identified': state.get('real_reviewer_identified') is False,
        'ceo_brain_sees_no_customer_validation_or_paid_signal': state.get('customer_validation_claimed') is False and state.get('paid_signal_claimed') is False,
        'ceo_brain_sees_next_milestone_recommendation': state.get('next_recommended_milestone') == 'E54_owner_decision_or_controlled_first_user_review_plan',
        'canonical_runtime_can_see_e53_owner_review_state': context.get('current_owner_approval_status') == 'pending_owner_decision',
    }
    return {'artifact_id': 'e53_ceo_brain_readback_smoke_result', 'owner_review_state': state, 'canonical_runtime_context_seen': True, 'checks': checks, 'passes': all(checks.values()), 'no_external_action': True}

def render_markdown(data: dict[str, Any]) -> str:
    lines = ['# E53 CEO Brain Readback Smoke', '', f"Passes: `{data['passes']}`", '', '## Checks']
    lines += [f"- {k}: {v}" for k, v in data['checks'].items()]
    lines += ['', 'No external action occurred.', '']
    return '\n'.join(lines)

def write_e53_ceo_brain_readback_smoke(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e53_ceo_brain_readback_smoke()
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e53_ceo_brain_readback_smoke_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e53_ceo_brain_readback_smoke_result.md').write_text(render_markdown(data), encoding='utf-8')
    return data

if __name__ == '__main__':
    print(json.dumps(run_e53_ceo_brain_readback_smoke(), indent=2, ensure_ascii=False))
