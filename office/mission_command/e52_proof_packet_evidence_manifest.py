from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .e52_proof_packet_boundary import build_proof_packet_boundary

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_DIR = BRIDGE_ROOT / 'products/governed_agent_action_proof_packet'

SOURCE_SPECS = [
    ('e50a_blocker_update', 'operations/external_validation/e50a_mcp_client_blocker_update.json', 'E50A', 'gov-mcp tool-layer blocker closed', 'tool_layer_proof'),
    ('e50a_local_tool_layer_proof', 'operations/external_validation/e50a_local_tool_layer_proof_result.json', 'E50A', 'ALLOW/DENY proved through local tool-layer harness', 'tool_layer_proof'),
    ('e50a_fake_fastmcp_harness', 'operations/external_validation/e50a_fake_fastmcp_harness_result.json', 'E50A', 'Fake FastMCP captured gov-mcp tools without real client mutation', 'tool_registration_proof'),
    ('e50b_commercial_decision', 'operations/external_validation/e50b_ceo_commercial_decision_packet.json', 'E50B', 'selected route is package_governed_agent_action_proof_packet', 'commercial_decision'),
    ('e50b_counterfactual_matrix', 'operations/external_validation/e50b_counterfactual_money_route_matrix.json', 'E50B', 'counterfactual route comparison selected proof packet packaging', 'counterfactual_matrix'),
    ('e50b_public_receipts', 'operations/external_validation/e50b_public_source_receipts.jsonl', 'E50B', 'public-read-only evidence receipts, not customer validation', 'public_readonly_evidence'),
    ('e50b_evidence_atoms', 'operations/external_validation/e50b_commercial_evidence_atoms.jsonl', 'E50B', 'commercial evidence atoms, not paid signal', 'public_readonly_evidence'),
    ('e50c_brain_smoke', 'operations/external_validation/e50c_ceo_brain_centerline_smoke_result.json', 'E50C', 'CEO brain reads current decision state', 'readback_proof'),
    ('e50c_e51_readiness_gate', 'operations/external_validation/e50c_e51_readiness_gate.json', 'E50C', 'E51 readiness gate passed before anti-drift closure', 'readiness_gate'),
    ('e51_runtime_manifest', 'operations/external_validation/e51_labs_runtime_linkage_manifest.json', 'E51', 'runtime linkage manifest has writer/reader/readback map', 'anti_drift_manifest'),
    ('e51_y_star_validation', 'operations/external_validation/e51_y_star_gov_linkage_validation_result.json', 'E51', 'Y-star-gov validation passed', 'validator_proof'),
    ('e51_gov_mcp_harness', 'operations/external_validation/e51_gov_mcp_runtime_linkage_tool_harness_result.json', 'E51', 'gov-mcp ALLOW/DENY anti-drift proof', 'mcp_tool_proof'),
    ('e51_current_gate', 'operations/external_validation/e51_current_readiness_anti_drift_gate_result.json', 'E51', 'current readiness anti-drift gate passed', 'anti_drift_gate'),
    ('e51_capability_binding_audit', 'operations/external_validation/e51_capability_centerline_binding_audit.json', 'E51 Phase 2.5', 'capabilities classified by centerline', 'capability_binding'),
    ('e51_capability_binding_repair', 'operations/external_validation/e51_capability_centerline_binding_repair_result.json', 'E51 Phase 2.5', 'capability binding gate passed and broken cases denied', 'capability_binding_gate'),
]
COMPLETED_REPORTS = [
    ('e50a_report', '/tmp/ystar_delivery_bridge/completed/e50a_minimal_gov_mcp_local_test_client_r2_20260506T000001Z.report.json', 'E50A', 'completed report', 'delivery_report'),
    ('e50b_report', '/tmp/ystar_delivery_bridge/completed/e50b_counterfactual_commercial_retest_20260506T000001Z.report.json', 'E50B', 'completed report', 'delivery_report'),
    ('e50c_report', '/tmp/ystar_delivery_bridge/completed/e50c_ceo_brain_centerline_reconnection_20260506T000001Z.report.json', 'E50C', 'completed report', 'delivery_report'),
    ('e51_report', '/tmp/ystar_delivery_bridge/completed/e51_cross_repo_runtime_linkage_anti_drift_closure_20260506T000001Z.report.json', 'E51', 'completed report', 'delivery_report'),
    ('e51_binding_report', '/tmp/ystar_delivery_bridge/completed/e51_capability_centerline_binding_addendum_20260506T000001Z.report.json', 'E51 Phase 2.5', 'completed report', 'delivery_report'),
]


def _hash(path: Path) -> str | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        h = hashlib.sha256()
        with path.open('rb') as fh:
            for chunk in iter(lambda: fh.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def _item(evidence_id: str, source_path: str, source_milestone: str, claim_supported: str, proof_type: str) -> dict[str, Any]:
    path = Path(source_path) if source_path.startswith('/') else BRIDGE_ROOT / source_path
    exists = path.exists()
    return {
        'evidence_id': evidence_id,
        'source_path': source_path,
        'source_milestone': source_milestone,
        'claim_supported': claim_supported,
        'proof_type': proof_type,
        'limitations': ['local/internal artifact', 'not customer validation', 'not paid signal', 'not real MCP transport closure'],
        'freshness': 'current_E50_E51_line' if exists else 'missing',
        'sha256': _hash(path),
        'readback_status': 'read_back_or_registered' if exists else 'missing',
        'included_in_packet': exists,
        'overclaim_risk': 'medium' if proof_type in {'public_readonly_evidence', 'delivery_report'} else 'low',
        'allowed_language': ['supports local owner-review proof packet only'],
        'forbidden_language': ['customer validation claim', 'paid demand claim', 'closed transport claim', 'production readiness claim'],
        'exists': exists,
    }


def build_evidence_manifest() -> dict[str, Any]:
    boundary = build_proof_packet_boundary()
    items = [_item(*spec) for spec in SOURCE_SPECS] + [_item(*spec) for spec in COMPLETED_REPORTS]
    return {
        'artifact_id': 'e52_proof_packet_evidence_manifest',
        'packet_product': boundary['product_name'],
        'evidence_count': len(items),
        'included_count': sum(1 for item in items if item['included_in_packet']),
        'missing_evidence': [item for item in items if not item['included_in_packet']],
        'evidence_items': items,
        'customer_validation_claimed': False,
        'paid_signal_claimed': False,
        'real_mcp_transport_claimed': False,
        'no_external_action': True,
    }


def render_evidence_manifest_markdown(data: dict[str, Any]) -> str:
    lines = ['# Evidence Manifest', '', f"Evidence items: {data['evidence_count']}", f"Included: {data['included_count']}", '', '## Included Evidence']
    for item in data['evidence_items']:
        marker = 'included' if item['included_in_packet'] else 'missing'
        lines.append(f"- `{item['evidence_id']}` ({item['source_milestone']}): {marker}; {item['claim_supported']}")
    lines += ['', 'No evidence item is a customer-validation claim, paid-demand claim, or real MCP transport closure claim.', '']
    return '\n'.join(lines)


def write_evidence_manifest(output_root: Path | None = None) -> dict[str, Any]:
    data = build_evidence_manifest()
    root = output_root or BRIDGE_ROOT
    product = root / 'products/governed_agent_action_proof_packet'
    product.mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    for rel in [product / 'evidence_manifest.json', root / 'operations/external_validation/e52_proof_packet_evidence_manifest.json']:
        rel.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    md = render_evidence_manifest_markdown(data)
    (product / 'evidence_manifest.md').write_text(md, encoding='utf-8')
    (root / 'reports/integration/e52_proof_packet_evidence_manifest.md').write_text(md, encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(build_evidence_manifest(), indent=2, ensure_ascii=False))
