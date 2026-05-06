from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_DIR = BRIDGE_ROOT / 'products/governed_agent_action_proof_packet'


def build_first_user_review_packet() -> dict[str, Any]:
    packet = {
        'artifact_id': 'e52_first_user_review_packet_result',
        'target_persona_categories': ['AI agent builder', 'AI ops lead', 'MCP power user', 'governance / compliance-minded developer'],
        'contains_real_names': False,
        'contains_emails': False,
        'contains_contact_list': False,
        'outreach_sent': False,
        'publication_done': False,
        'owner_approval_required': True,
        'allowed_claims': ['local tool-layer proof', 'owner-reviewable proof packet', 'governance boundary demonstration'],
        'forbidden_claims': ['customer-validation claim', 'paid-demand claim', 'real MCP transport closure claim', 'production-readiness claim', 'expert-feedback claim'],
        'stop_conditions': ['any request to send/publish/contact without owner approval', 'any unsupported claim', 'any request to identify a real person'],
        'no_external_action': True,
    }
    return packet


def write_first_user_review_packet(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    product = root / 'products/governed_agent_action_proof_packet'
    product.mkdir(parents=True, exist_ok=True)
    data = build_first_user_review_packet()
    # Product files are also written by e52_proof_packet_package; keep this builder idempotent.
    (product / 'first_user_review_packet.json').write_text(json.dumps({k: v for k, v in data.items() if k != 'artifact_id'}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if not (product / 'first_user_review_packet.md').exists():
        (product / 'first_user_review_packet.md').write_text('# First User Review Packet\n\nOwner approval required before any external review.\n', encoding='utf-8')
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e52_first_user_review_packet_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e52_first_user_review_packet_result.md').write_text('# E52 First-User Review Packet\n\nOwner-review packet created. It contains no real contacts and performs no outreach.\n', encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_first_user_review_packet(), indent=2, ensure_ascii=False))
