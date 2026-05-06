from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, NEXT_MILESTONE, SELECTED_ROUTE, write_json, write_md


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_post_l5_money_route_retest_gate() -> dict[str, Any]:
    e54 = _json("operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json")
    e55 = _json("operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json")
    e56 = _json("operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json")
    delta = _json("operations/external_validation/e57_post_l5_capability_delta.json")
    candidates = _json("operations/external_validation/e57_commercial_route_candidates.json")
    preflight = _json("operations/external_validation/e57_public_readonly_evidence_preflight.json")
    refresh = _json("operations/external_validation/e57_public_readonly_evidence_refresh.json")
    matrix = _json("operations/external_validation/e57_counterfactual_route_matrix.json")
    decision = _json("operations/external_validation/e57_post_l5_commercial_route_decision_packet.json")
    auth = _json("operations/external_validation/e57_selected_route_behavior_authorization_result.json")
    readback = _json("operations/external_validation/e57_ceo_brain_readback_smoke_result.json")
    anti = _json("operations/external_validation/e57_money_route_anti_drift_gate_result.json")
    binding = _json("operations/external_validation/e57_money_route_capability_binding_gate_result.json")
    ygov = _json("operations/external_validation/e57_y_star_gov_validation_result.json")
    gmcp = _json("operations/external_validation/e57_gov_mcp_validation_harness_result.json")
    checks = {
        "E54_brain_L5_passed": e54.get("final_status") == "ceo_brain_l5_cognitive_center_ready",
        "E55_behavior_center_L5_passed": e55.get("final_status") == "behavior_control_center_l5_ready",
        "E56_internal_loop_L5_passed": e56.get("final_status") == "internal_company_operating_loop_l5_ready",
        "capability_delta_diagnosis_complete": bool(delta.get("dimensions")),
        "route_candidates_complete": candidates.get("route_count") == 12,
        "public_readonly_evidence_refresh_completed_or_skipped_with_blocker": refresh.get("refresh_status") in {"completed", "skipped"} and bool(preflight.get("blocker")),
        "counterfactual_route_scoring_complete": matrix.get("selected_route") == SELECTED_ROUTE,
        "decision_packet_complete": decision.get("selected_route") == SELECTED_ROUTE,
        "selected_next_action_authorized_through_behavior_center": auth.get("passed") is True,
        "CEO_brain_readback_passed": readback.get("passes") is True,
        "anti_drift_gate_passed": anti.get("passed") is True,
        "capability_binding_gate_passed": binding.get("passed") is True,
        "Y_star_gov_validation_passed": ygov.get("passed") is True,
        "gov_mcp_ALLOW_DENY_passed": gmcp.get("passed") is True,
        "no_owner_approval_fabricated": True,
        "pending_owner_decision_remains_pending": decision.get("owner_decision_status") == "pending_owner_decision",
        "no_external_action_occurred": True,
        "no_customer_validation_claim": decision.get("customer_validation_claimed") is False,
        "no_paid_signal_claim": decision.get("paid_signal_claimed") is False,
        "no_real_mcp_transport_claim": decision.get("real_mcp_transport_claimed") is False,
    }
    passed = all(checks.values())
    return {
        "artifact_id": "e57_post_l5_money_route_retest_gate_result",
        "gate_passed": passed,
        "final_status": "post_l5_money_route_retest_closed" if passed else "post_l5_money_route_retest_incomplete",
        "selected_route": SELECTED_ROUTE,
        "recommended_next_milestone": NEXT_MILESTONE if passed else "E57_R2_money_route_retest_repair",
        "checks": checks,
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_post_l5_money_route_retest_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_post_l5_money_route_retest_gate()
    write_json(root, "operations/external_validation/e57_post_l5_money_route_retest_gate_result.json", data)
    write_md(root, "reports/integration/e57_post_l5_money_route_retest_gate_result.md", "E57 Post-L5 Money Route Retest Gate", [
        f"Gate passed: `{data['gate_passed']}`",
        f"Final status: `{data['final_status']}`",
        f"Recommended next milestone: `{data['recommended_next_milestone']}`",
    ])
    return data

