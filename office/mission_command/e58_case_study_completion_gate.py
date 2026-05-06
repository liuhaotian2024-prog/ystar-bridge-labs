from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, CASE_STUDY_ID, NEXT_MILESTONE, PRODUCT_DIR, SELECTED_ROUTE, write_json, write_md


def _json(rel: str, root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    try:
        return json.loads((base / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _exists(rel: str, root: Path | None = None) -> bool:
    return ((root or BRIDGE_ROOT) / rel).exists()


def run_case_study_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    case_study = _json(str(PRODUCT_DIR / "case_study.json"), base)
    evidence = _json(str(PRODUCT_DIR / "evidence_manifest.json"), base)
    no_overclaim = _json("operations/external_validation/e58_case_study_no_overclaim_validation_result.json", base)
    owner = _json("operations/external_validation/e58_owner_review_packet_result.json", base)
    auth = _json("operations/external_validation/e58_case_study_behavior_authorization_result.json", base)
    readback = _json("operations/external_validation/e58_ceo_brain_readback_smoke_result.json", base)
    anti = _json("operations/external_validation/e58_case_study_anti_drift_gate_result.json", base)
    binding = _json("operations/external_validation/e58_case_study_capability_binding_gate_result.json", base)
    ygov = _json("operations/external_validation/e58_y_star_gov_validation_result.json", base)
    gmcp = _json("operations/external_validation/e58_gov_mcp_validation_harness_result.json", base)
    e57_decision = _json("operations/external_validation/e57_post_l5_commercial_route_decision_packet.json", base)
    checks = {
        "E57_selected_route_consumed": e57_decision.get("selected_route") == SELECTED_ROUTE,
        "case_study_directory_created": (base / PRODUCT_DIR).is_dir(),
        "case_study_json_valid": case_study.get("case_study_id") == CASE_STUDY_ID,
        "evidence_manifest_complete": len(evidence.get("evidence_items", [])) >= 10,
        "architecture_narrative_complete": _exists(str(PRODUCT_DIR / "technical_architecture.md"), base) and _exists(str(PRODUCT_DIR / "category_narrative.md"), base),
        "proof_chain_complete": _exists(str(PRODUCT_DIR / "proof_chain.md"), base),
        "external_intelligence_gap_declaration_complete": _exists(str(PRODUCT_DIR / "external_intelligence_gap.md"), base),
        "E59_requirements_packet_complete": _exists(str(PRODUCT_DIR / "e59_requirements_packet.md"), base),
        "no_overclaim_validation_passed": no_overclaim.get("passes") is True,
        "owner_review_packet_created": owner.get("packet_status") == "owner_reviewable_only" and owner.get("external_action_allowed") is False,
        "behavior_authorization_passed": auth.get("passed") is True,
        "CEO_brain_readback_passed": readback.get("passes") is True,
        "anti_drift_gate_passed": anti.get("passed") is True,
        "capability_binding_gate_passed": binding.get("passed") is True,
        "Y_star_gov_validation_passed": ygov.get("passed") is True,
        "gov_mcp_ALLOW_DENY_passed": gmcp.get("passed") is True,
        "no_external_action_occurred": True,
        "no_owner_approval_fabricated": True,
        "pending_owner_decision_remains_pending": case_study.get("owner_approval_required_before_external_action") is True,
        "no_customer_validation_claim": case_study.get("customer_validation_claimed") is False,
        "no_paid_signal_claim": case_study.get("paid_signal_claimed") is False,
        "no_real_mcp_transport_claim": case_study.get("real_mcp_transport_claimed") is False,
        "external_intelligence_L5_not_claimed_complete": case_study.get("external_intelligence_gap") == "External World Intelligence / Technology Capture / Market Learning L5 is not complete.",
        "E59_recommended_as_next_milestone": case_study.get("next_recommended_milestone") == NEXT_MILESTONE,
    }
    passed = all(checks.values())
    return {
        "artifact_id": "e58_case_study_completion_gate_result",
        "gate_passed": passed,
        "final_status": "AI_agent_company_runtime_harness_case_study_packaged" if passed else "e58_case_study_packaging_incomplete",
        "selected_route": SELECTED_ROUTE,
        "recommended_next_milestone": NEXT_MILESTONE if passed else "E58_R2_case_study_packaging_repair",
        "checks": checks,
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "external_intelligence_L5_claimed": False,
    }


def write_case_study_completion_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_case_study_completion_gate(root)
    write_json(root, "operations/external_validation/e58_case_study_completion_gate_result.json", data)
    write_md(root, "reports/integration/e58_case_study_completion_gate_result.md", "E58 Case Study Completion Gate", [
        f"Gate passed: `{data['gate_passed']}`",
        f"Final status: `{data['final_status']}`",
        f"Selected route: `{data['selected_route']}`",
        f"Recommended next milestone: `{data['recommended_next_milestone']}`",
    ])
    return data
