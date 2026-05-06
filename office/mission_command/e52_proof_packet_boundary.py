from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))

ALLOWED_LANGUAGE = [
    'local proof', 'tool-layer proof', 'owner-reviewable proof packet',
    'governance boundary demonstration', 'first-user-review candidate',
    'evidence-backed but not externally validated',
]
FORBIDDEN_LANGUAGE = [
    'validated by customers', 'customer-approved', 'production-ready', 'enterprise-proven',
    'paid demand', 'real MCP transport closure', 'customer-approved', 'expert-reviewed',
    'compliance-certified',
]


def build_proof_packet_boundary() -> dict[str, Any]:
    return {
        'artifact_id': 'e52_proof_packet_boundary',
        'product_name': 'Governed Agent Action Proof Packet',
        'one_sentence_description': 'A local, evidence-backed packet showing how an agent action can be checked, allowed/denied, documented, and closed without overclaiming customer or production readiness.',
        'current_proof_level': ['local_tool_layer_proof', 'not_real_mcp_transport', 'not_customer_validation', 'not_paid_signal', 'not_production_claim'],
        'current_evidence': [
            'E50A gov-mcp tool-layer allow/deny', 'E50B counterfactual route decision',
            'E50B public-read-only commercial evidence', 'E50C CEO brain readback proof',
            'E51 anti-drift gate', 'E51 capability centerline binding gate',
            'Y-star-gov validators', 'gov-mcp ALLOW/DENY validator proofs',
        ],
        'explicit_limitations': [
            'real MCP transport not claimed', 'no external user has reviewed it', 'no customer validation',
            'no paid signal', 'no publication', 'no outreach', 'no enterprise compliance claim',
            'no production deployment claim',
        ],
        'allowed_language': ALLOWED_LANGUAGE,
        'forbidden_language': FORBIDDEN_LANGUAGE,
        'owner_approval_required_before': ['external contact', 'publication', 'payment', 'product commitment'],
        'no_external_action': True,
    }


def render_boundary_markdown(data: dict[str, Any]) -> str:
    lines = ['# Governed Agent Action Proof Packet Boundary', '', data['one_sentence_description'], '', '## Current Proof Level']
    lines += [f'- {item}' for item in data['current_proof_level']]
    lines += ['', '## Limitations'] + [f'- {item}' for item in data['explicit_limitations']]
    lines += ['', '## Allowed Language'] + [f'- {item}' for item in data['allowed_language']]
    lines += ['', '## Forbidden Language'] + [f'- {item}' for item in data['forbidden_language']]
    lines += ['', 'No external action occurred.', '']
    return '\n'.join(lines)


def write_proof_packet_boundary(output_root: Path | None = None) -> dict[str, Any]:
    data = build_proof_packet_boundary()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e52_proof_packet_boundary.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e52_proof_packet_boundary.md').write_text(render_boundary_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_proof_packet_boundary(), indent=2, ensure_ascii=False))
