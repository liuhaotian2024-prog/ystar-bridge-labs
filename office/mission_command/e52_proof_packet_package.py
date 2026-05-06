from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .e52_proof_packet_boundary import build_proof_packet_boundary
from .e52_proof_packet_evidence_manifest import build_evidence_manifest

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_DIR = BRIDGE_ROOT / 'products/governed_agent_action_proof_packet'


def _hash_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def proof_packet_json() -> dict[str, Any]:
    boundary = build_proof_packet_boundary()
    evidence = build_evidence_manifest()
    return {
        'packet_id': 'governed_agent_action_proof_packet_e52',
        'packet_version': '0.1-owner-review',
        'created_from_milestones': ['E50A', 'E50B', 'E50C', 'E51', 'E51 Phase 2.5'],
        'selected_route': 'package_governed_agent_action_proof_packet',
        'nearest_alternative': 'external_commercial_observation_now',
        'target_reader': 'owner first, then only an owner-approved first-user reviewer category',
        'core_claim': 'This is a local, owner-reviewable proof packet showing governed agent action allow/deny, evidence organization, readback, anti-drift, and no-overclaim boundaries.',
        'proof_level': 'local_tool_layer_proof_only',
        'supported_claims': [
            'gov-mcp tool-layer ALLOW/DENY was proven locally through a fake FastMCP harness',
            'Y-star-gov and gov-mcp anti-drift validators allow valid linkage and deny broken P0 linkage',
            'capability centerline binding allows valid bindings and denies wrong-centerline P0 cases',
            'CEO brain reads current selected route and proof packet state before next routing',
        ],
        'unsupported_claims': [
            'customer-validation claim', 'paid-demand claim', 'real MCP transport closure claim', 'production-readiness claim', 'enterprise compliance readiness claim', 'expert-feedback claim',
        ],
        'evidence_manifest': 'products/governed_agent_action_proof_packet/evidence_manifest.json',
        'limitations': boundary['explicit_limitations'],
        'no_go_boundaries': {
            'no_outreach': True,
            'no_publication': True,
            'no_customer_validation_claim': True,
            'no_paid_signal_claim': True,
            'no_real_mcp_transport_claim': True,
            'owner_approval_required_before_external_contact_or_publication': True,
        },
        'owner_approval_required_before': ['external contact', 'publication', 'payment', 'product commitment', 'naming any real reviewer'],
        'demo_status': 'E50A local tool-layer proof closed; real MCP transport not claimed',
        'anti_drift_status': 'E51 anti-drift gate passed',
        'capability_binding_status': 'E51 capability centerline binding gate passed',
        'Y_star_gov_validation_status': 'passed',
        'gov_mcp_validation_status': 'ALLOW for valid manifests and DENY for broken fixtures',
        'customer_validation_claimed': False,
        'paid_signal_claimed': False,
        'real_mcp_transport_claimed': False,
        'publication_status': 'not_published',
        'outreach_status': 'not_contacted',
        'next_recommended_milestone': 'E53_owner_review_and_single_first_user_review_approval_gate',
        'no_external_action': True,
    }


def write_product_packet(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    product = root / 'products/governed_agent_action_proof_packet'
    product.mkdir(parents=True, exist_ok=True)
    packet = proof_packet_json()
    files: dict[str, str] = {}
    files['README.md'] = '# Governed Agent Action Proof Packet\n\nThis owner-review packet packages the current local proof that an agent action can be checked, allowed or denied, documented, and closed without claiming customer validation, paid signal, production readiness, or real MCP transport closure.\n\nStart with `executive_brief.md`, then read `limitations_and_no_overclaim.md`, `evidence_chain.md`, and `owner_approval_checklist.md`.\n'
    files['executive_brief.md'] = '# Executive Brief\n\nThe packet is a local proof artifact for owner review. It shows a governed action proof chain: selected commercial route, local tool-layer ALLOW/DENY evidence, CEO brain readback, anti-drift validation, and capability centerline binding.\n\nIt does not prove customer validation, paid signal, real MCP transport closure, production readiness, or compliance certification.\n'
    files['technical_proof.md'] = '# Technical Proof\n\nY-star-gov provides generic validators. gov-mcp exposes them as local tool-layer checks. E50A proved gov-mcp tool-layer ALLOW/DENY through a fake FastMCP harness without mutating real client config. E51 proved runtime linkage and capability binding gates ALLOW valid manifests and DENY broken P0 fixtures.\n\nReal MCP transport is not claimed closed.\n'
    files['demo_script.md'] = '# Local Demo Script\n\nThis script describes the existing local proof artifacts only. Do not run internet installs. Do not mutate Claude, Cursor, Windsurf, or OpenClaw configs. Do not claim real MCP transport.\n\n1. Review E50A fake FastMCP harness output.\n2. Confirm `echo e50a_safe` was allowed through the gov-mcp tool layer.\n3. Confirm `rm -rf /tmp/e50a_nonexistent` was denied through the gov-mcp tool layer.\n4. Review E51 valid manifest ALLOW and broken P0 DENY proofs.\n'
    files['evidence_chain.md'] = '# Evidence Chain\n\nThe canonical evidence map is `evidence_manifest.json`. It links E50A, E50B, E50C, E51, and E51 Phase 2.5 artifacts to supported claims and limitations.\n'
    files['limitations_and_no_overclaim.md'] = '# Limitations And No-Overclaim Boundary\n\nRequired disclaimers: real MCP transport not claimed; no customer validation; no paid signal; no outreach; no publication; owner approval required before external contact/publication; local tool-layer proof only.\n\nForbidden claims: do not say customer validated, production ready, enterprise certified, compliance certified, real MCP transport closed, expert validated, published, contacted, or externally validated.\n'
    files['first_user_review_guide.md'] = '# First-User Review Guide\n\nTarget persona category: AI agent builder, AI ops lead, MCP power user, or governance-minded developer. No real names, emails, profiles, or contact list are included.\n\nA future reviewer would inspect the proof chain, language boundaries, local demo artifacts, and whether the packet is understandable. Useful feedback would focus on clarity, credibility, missing proof, and whether the value object is compelling.\n\nOwner approval is required before any external review.\n'
    files['owner_approval_checklist.md'] = '# Owner Approval Checklist\n\nApprove only if the packet language is accurate, no-overclaim boundaries are clear, evidence paths are understandable, and the first-user review purpose is acceptable.\n\nBefore any external contact or publication, owner must approve the recipient category, exact packet, exact message, stop conditions, and no-claim boundaries.\n'
    files['next_step_options.md'] = '# Next Step Options\n\nRecommendation: run `E53_owner_review_and_single_first_user_review_approval_gate`.\n\nOther possible owner choices after review are more local proof, real MCP transport gate, or proof language revision. Do not treat this as permission to outreach or publish.\n'
    files['first_user_review_packet.md'] = '# First User Review Packet\n\nPurpose: prepare an owner-approved, unsent review packet for a future reviewer category.\n\nReviewer category only: AI agent builder, AI ops lead, MCP power user, or governance/compliance-minded developer.\n\nReview questions: Is the value object understandable? Is the proof chain credible? Are the limitations clear? What proof is missing before trust increases?\n\nAllowed claims: local tool-layer proof, owner-reviewable proof packet, governance boundary demonstration.\n\nForbidden claims: customer-validation claim, paid-demand claim, real MCP transport closure claim, production-readiness claim, expert-feedback claim.\n\nStop conditions: any request for external send/publish/contact without owner approval; any claim beyond local proof.\n'
    files['first_user_review_packet.json'] = json.dumps({
        'packet_id': 'e52_first_user_review_packet',
        'target_persona_categories': ['AI agent builder', 'AI ops lead', 'MCP power user', 'governance-minded developer'],
        'contains_real_contacts': False,
        'outreach_executed': False,
        'publication_executed': False,
        'owner_approval_required': True,
        'review_questions': ['Is the value object understandable?', 'Is the proof chain credible?', 'Are the limitations clear?', 'What proof is missing?'],
        'no_external_action': True,
    }, indent=2, ensure_ascii=False) + '\n'
    files['no_go_boundary_manifest.json'] = json.dumps(packet['no_go_boundaries'], indent=2, ensure_ascii=False) + '\n'
    files['proof_packet.json'] = json.dumps(packet, indent=2, ensure_ascii=False) + '\n'
    # Source artifact manifest after core files are known.
    source_manifest = []
    for rel, content in sorted(files.items()):
        source_manifest.append({'path': f'products/governed_agent_action_proof_packet/{rel}', 'sha256': __import__('hashlib').sha256(content.encode('utf-8')).hexdigest(), 'claim_mapping': 'owner-review proof packet content', 'no_external_action': True})
    files['source_artifact_manifest.json'] = json.dumps({'artifact_id': 'e52_source_artifact_manifest', 'items': source_manifest, 'no_external_action': True}, indent=2, ensure_ascii=False) + '\n'
    for rel, content in files.items():
        (product / rel).write_text(content, encoding='utf-8')
    return packet


if __name__ == '__main__':
    print(json.dumps(proof_packet_json(), indent=2, ensure_ascii=False))
