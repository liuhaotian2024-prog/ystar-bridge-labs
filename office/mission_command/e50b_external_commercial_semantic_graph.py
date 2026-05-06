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

from .e50b_public_observation import build_commercial_evidence_atoms, build_public_source_receipts

ROUTES = [
    'governed_agent_action_proof_packet', 'gov_mcp_integration_service_wedge', 'claude_desktop_mcpb_packaging',
    'ystar_gov_standalone_kernel_wedge', 'k9audit_only_causal_audit_wedge', 'workflow_resale_n8n_czl',
    'enterprise_compliance_pilot', 'ai_agent_bug_bounty_service', 'full_governed_execution_causal_audit_proof_packet_wedge',
]


def build_external_commercial_semantic_graph() -> dict[str, Any]:
    receipts = build_public_source_receipts()
    atoms = build_commercial_evidence_atoms()
    nodes = []
    edges = []
    for route in ROUTES:
        nodes.append({'node_id': f'route:{route}', 'node_type': 'route_opportunity', 'route_id': route})
    for receipt in receipts:
        rid = receipt['receipt_id']
        nodes.append({'node_id': f'evidence:{rid}', 'node_type': 'evidence_receipt', **receipt})
        if receipt['domain'] == 'mcp_tooling':
            target = 'claude_desktop_mcpb_packaging'
        elif receipt['domain'] in {'enterprise_governance', 'agent_governance', 'agent_observability'}:
            target = 'governed_agent_action_proof_packet'
        elif receipt['domain'] == 'security_redteam':
            target = 'ai_agent_bug_bounty_service'
        elif receipt['domain'] == 'workflow_automation':
            target = 'workflow_resale_n8n_czl'
        elif receipt['domain'] == 'audit_compliance':
            target = 'k9audit_only_causal_audit_wedge'
        else:
            target = 'gov_mcp_integration_service_wedge'
        edges.append({'from': f'evidence:{rid}', 'to': f'route:{target}', 'edge_type': 'route_strengthens', 'claim_boundary': 'public evidence only'})
    for atom in atoms:
        nodes.append({'node_id': f'atom:{atom["evidence_id"]}', 'node_type': 'commercial_evidence_atom', **atom})
        edges.append({'from': f'atom:{atom["evidence_id"]}', 'to': f'evidence:{atom["evidence_id"].replace("evidence", "receipt")}', 'edge_type': 'derives_from'})
    nodes.append({'node_id': 'value_object:governed_agent_action_proof_packet', 'node_type': 'value_object', 'buyer_persona': 'AI engineer / agent framework power user', 'overclaim_boundary': 'proof packet is not customer validation, paid signal, compliance certification, or production-readiness proof'})
    edges.append({'from': 'route:governed_agent_action_proof_packet', 'to': 'value_object:governed_agent_action_proof_packet', 'edge_type': 'produces'})
    return {
        'artifact_id': 'e50b_external_commercial_semantic_graph',
        'node_count': len(nodes),
        'edge_count': len(edges),
        'nodes': nodes,
        'edges': edges,
        'routes_connected': ROUTES,
        'no_external_action': True,
        'not_customer_validation': True,
        'not_paid_signal': True,
    }


if __name__ == '__main__':
    print(json.dumps(build_external_commercial_semantic_graph(), indent=2, ensure_ascii=False))
