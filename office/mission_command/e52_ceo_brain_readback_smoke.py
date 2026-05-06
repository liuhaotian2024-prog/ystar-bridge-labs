from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e46b_ceo_brain_adapter import load_ceo_brain_context
from .e46b_canonical_ceo_operating_runtime import run_canonical_ceo_operating_runtime

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
TASK = {'task_id': 'e52_ceo_brain_readback_smoke', 'task_title': 'E52 proof packet readback smoke', 'task_description': 'Verify CEO brain sees proof packet packaged for owner review only before next routing.'}


def run_ceo_brain_readback_smoke() -> dict[str, Any]:
    brain = load_ceo_brain_context(TASK)
    proof = brain.get('latest_proof_packet_state', {})
    canonical = run_canonical_ceo_operating_runtime(TASK, mode='e52_readback_smoke')
    checks = {
        'ceo_brain_sees_proof_packet_exists': proof.get('proof_packet_available') is True,
        'ceo_brain_sees_owner_reviewable_only': proof.get('packet_status') == 'owner_reviewable_only',
        'ceo_brain_sees_no_outreach_publication_allowed': proof.get('outreach_status') == 'not_contacted' and proof.get('publication_status') == 'not_published',
        'ceo_brain_sees_no_customer_validation_or_paid_signal': proof.get('customer_validation_claimed') is False and proof.get('paid_signal_claimed') is False,
        'ceo_brain_sees_next_milestone_recommendation': proof.get('next_recommended_milestone') == 'E53_owner_review_and_single_first_user_review_approval_gate',
        'canonical_runtime_can_see_brain_context': bool(canonical.get('ceo_brain_context')),
    }
    return {'artifact_id': 'e52_ceo_brain_readback_smoke_result', 'proof_packet_state': proof, 'canonical_runtime_context_seen': bool(canonical.get('ceo_brain_context')), 'checks': checks, 'passes': all(checks.values()), 'no_external_action': True}


def render_brain_readback_markdown(data: dict[str, Any]) -> str:
    return '\n'.join(['# E52 CEO Brain Readback Smoke', '', f"Passes: `{data['passes']}`", f"Packet status: `{data['proof_packet_state'].get('packet_status')}`", f"Next milestone: `{data['proof_packet_state'].get('next_recommended_milestone')}`", '', 'No external action occurred.', ''])


def write_ceo_brain_readback_smoke(output_root: Path | None = None) -> dict[str, Any]:
    data = run_ceo_brain_readback_smoke()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e52_ceo_brain_readback_smoke_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e52_ceo_brain_readback_smoke_result.md').write_text(render_brain_readback_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(run_ceo_brain_readback_smoke(), indent=2, ensure_ascii=False))
