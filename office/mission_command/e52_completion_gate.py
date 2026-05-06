from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_DIR = BRIDGE_ROOT / 'products/governed_agent_action_proof_packet'
REQUIRED_FILES = ['README.md','proof_packet.json','executive_brief.md','technical_proof.md','demo_script.md','evidence_chain.md','limitations_and_no_overclaim.md','first_user_review_guide.md','owner_approval_checklist.md','next_step_options.md','source_artifact_manifest.json','no_go_boundary_manifest.json','packet_validation_result.json','evidence_manifest.json','evidence_manifest.md','first_user_review_packet.md','first_user_review_packet.json']


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding='utf-8'))
    except Exception:
        return {}


def run_completion_gate() -> dict[str, Any]:
    proof = _json('products/governed_agent_action_proof_packet/proof_packet.json')
    evidence = _json('products/governed_agent_action_proof_packet/evidence_manifest.json')
    no_overclaim = _json('operations/external_validation/e52_no_overclaim_validation_result.json')
    first_user = _json('operations/external_validation/e52_first_user_review_packet_result.json')
    anti = _json('operations/external_validation/e52_packet_anti_drift_gate_result.json')
    binding = _json('operations/external_validation/e52_capability_binding_gate_result.json')
    ygov = _json('operations/external_validation/e52_y_star_gov_validation_result.json')
    gmcp = _json('operations/external_validation/e52_gov_mcp_validation_harness_result.json')
    brain = _json('operations/external_validation/e52_ceo_brain_readback_smoke_result.json')
    checks = {
        'proof_packet_directory_exists': PRODUCT_DIR.exists(),
        'required_packet_files_exist': all((PRODUCT_DIR / name).exists() for name in REQUIRED_FILES),
        'proof_packet_json_valid': proof.get('packet_id') == 'governed_agent_action_proof_packet_e52',
        'evidence_manifest_complete': evidence.get('included_count', 0) >= 10,
        'no_overclaim_validator_passes': no_overclaim.get('passed') is True,
        'first_user_review_packet_exists': first_user.get('owner_approval_required') is True,
        'owner_approval_checklist_exists': (PRODUCT_DIR / 'owner_approval_checklist.md').exists(),
        'anti_drift_gate_passes': anti.get('passed') is True,
        'capability_binding_gate_passes': binding.get('passed') is True,
        'y_star_gov_validation_passes': ygov.get('passed') is True,
        'gov_mcp_allow_and_deny_proofs_pass': gmcp.get('passed') is True,
        'ceo_brain_readback_passes': brain.get('passes') is True,
        'kg_czl_cieu_artifacts_written': all((BRIDGE_ROOT / rel).exists() for rel in ['operations/knowledge_graph/e52_ceo_kg_read_model_update.json', 'operations/external_validation/e52_czl_closure.json', 'operations/external_validation/e52_cieu_residual_summary.json']),
        'no_outreach_publication_contact_payment_occurred': proof.get('outreach_status') == 'not_contacted' and proof.get('publication_status') == 'not_published',
        'no_real_mcp_transport_claimed': proof.get('real_mcp_transport_claimed') is False,
        'no_customer_validation_claimed': proof.get('customer_validation_claimed') is False,
        'no_paid_signal_claimed': proof.get('paid_signal_claimed') is False,
    }
    passed = all(checks.values())
    return {'artifact_id': 'e52_completion_gate_result', 'gate_passed': passed, 'final_status': 'proof_packet_packaged_for_owner_first_user_review' if passed else 'e52_packet_packaging_incomplete', 'recommended_next_milestone': 'E53_owner_review_and_single_first_user_review_approval_gate' if passed else 'E52_R2_packet_packaging_repair', 'checks': checks, 'no_external_action': True}


def render_completion_gate_markdown(data: dict[str, Any]) -> str:
    lines = ['# E52 Completion Gate', '', f"Gate passed: `{data['gate_passed']}`", f"Final status: `{data['final_status']}`", f"Recommended next milestone: `{data['recommended_next_milestone']}`", '', '## Checks']
    lines += [f'- {key}: {value}' for key, value in data['checks'].items()]
    lines += ['', 'No external action occurred.', '']
    return '\n'.join(lines)


def write_completion_gate(output_root: Path | None = None) -> dict[str, Any]:
    data = run_completion_gate()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e52_completion_gate_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e52_completion_gate_result.md').write_text(render_completion_gate_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(run_completion_gate(), indent=2, ensure_ascii=False))
