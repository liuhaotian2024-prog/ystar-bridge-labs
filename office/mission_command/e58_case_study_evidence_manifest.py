from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, PRODUCT_DIR, write_json, write_md


def build_case_study_evidence_manifest() -> dict[str, Any]:
    rows = [
        ("e50a_tool_layer_allow_deny", "E50A", "operations/external_validation/e50a_mcp_client_blocker_update.json", "gov-mcp tool-layer allow/deny proof", "real MCP transport not claimed", "tool_layer_proof"),
        ("e50b_route_decision", "E50B", "operations/external_validation/e50b_ceo_commercial_decision_packet.json", "counterfactual commercial route decision", "external evidence was public-read-only and limited", "decision_packet"),
        ("e50c_brain_readback", "E50C", "operations/external_validation/e50c_ceo_brain_centerline_smoke_result.json", "CEO brain centerline readback", "milestone-specific before later generic registry", "readback_proof"),
        ("e51_anti_drift", "E51", "operations/external_validation/e51_current_readiness_anti_drift_gate_result.json", "cross-repo runtime linkage governance", "not product-market evidence", "governance_gate"),
        ("e51_capability_binding", "E51", "operations/external_validation/e51_capability_centerline_binding_repair_result.json", "capability centerline binding", "not external validation", "governance_gate"),
        ("e52_proof_packet", "E52", "products/governed_agent_action_proof_packet/proof_packet.json", "Governed Agent Action Proof Packet inheritance", "owner-reviewable only", "product_packet"),
        ("e53_owner_gate", "E53", "operations/external_validation/e53_first_user_review_risk_gate_result.json", "owner-review gate and pending owner decision", "no approval granted", "boundary_gate"),
        ("e54_brain_l5", "E54", "operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json", "CEO brain L5 readiness", "internal proof only", "readiness_gate"),
        ("e55_behavior_l5", "E55", "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json", "behavior control center L5 readiness", "internal proof only", "readiness_gate"),
        ("e56_loop_l5", "E56", "operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json", "internal company operating loop L5 readiness", "dry-run internal only", "readiness_gate"),
        ("e57_route_retest", "E57", "operations/external_validation/e57_post_l5_commercial_route_decision_packet.json", "post-L5 selected route: AI agent company runtime harness case study", "public evidence refresh skipped", "decision_packet"),
    ]
    items = [
        {
            "evidence_id": evidence_id,
            "source_milestone": milestone,
            "source_path": path,
            "claim_supported": claim,
            "limitation": limitation,
            "proof_type": proof_type,
            "readback_status": "read_back_or_inherited",
            "included_in_case_study": True,
            "overclaim_risk": "medium" if milestone in {"E50B", "E57"} else "low",
            "allowed_language": ["internal proof", "owner-reviewable evidence"],
            "forbidden_language": ["customer validation", "paid signal", "real MCP transport closure"],
        }
        for evidence_id, milestone, path, claim, limitation, proof_type in rows
    ]
    return {"artifact_id": "e58_case_study_evidence_manifest", "evidence_count": len(items), "evidence_items": items, "customer_validation_claimed": False, "paid_signal_claimed": False, "real_mcp_transport_claimed": False, "external_action_allowed": False}


def write_case_study_evidence_manifest(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_case_study_evidence_manifest()
    write_json(root, "operations/external_validation/e58_case_study_evidence_manifest.json", data)
    write_json(root, str(PRODUCT_DIR / "evidence_manifest.json"), data)
    write_md(root, "reports/integration/e58_case_study_evidence_manifest.md", "E58 Case Study Evidence Manifest", [f"Evidence items: `{data['evidence_count']}`", "Includes E50A through E57 proof chain."])
    write_md(root, str(PRODUCT_DIR / "evidence_manifest.md"), "Evidence Manifest", [f"Evidence items: `{data['evidence_count']}`", "Every item is internal/owner-reviewable evidence, not external validation."])
    return data

